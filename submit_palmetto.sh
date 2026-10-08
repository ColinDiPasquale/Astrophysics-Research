#!/bin/bash
# Submit one Slurm job per time step on Palmetto, all running at once.
# Each day gets its own copy of the source in runs/t<N>d/ (with its own
# globalVars.cc and build/), so the jobs never touch each other's files.
# Outputs are archived into Results/t<N>d/ exactly like run_batch.sh does,
# and a final job makes the cross-time-step plots once every run has ended.
#
# Usage:  ./submit_palmetto.sh            (create run dirs and submit)
#         ./submit_palmetto.sh --dry-run  (create run dirs only, submit nothing)

# ── Configure here ─────────────────────────────────────────────────────────────
DAYS=(10 20 30 40 50 60 70 80 90 100 120 200)  # one job per entry
EVENTS=1e9          # decay events per time step
THREADS=32          # cores requested per job; also patched into threadCount
NZONES=177          # 20 or 177
WALLTIME=24:00:00   # per job
MEM=32G             # per job
CONSTRAINT=genoa    # node feature to require (see: sinfo -o "%N %f"); empty for any node

# Commands every job runs first to get Geant4 and cmake.
ENV_BUILD='
module load gcc/12.3.0
module load spack
spack load geant4@11.2.2
'
# Commands that add Python. Run only after the build: with the conda
# environment active the linker picks up conda's libtinfo instead of the
# spack one and the link fails with undefined NCURSES6_TINFO references.
# Loaded last so python3 is the conda one and not one spack puts on PATH.
ENV_PYTHON='
module load anaconda3
source activate astro
'
# ──────────────────────────────────────────────────────────────────────────────

DRY_RUN=0
[ "$1" = "--dry-run" ] && DRY_RUN=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_ROOT="$SCRIPT_DIR/runs"
RESULTS_DIR="$SCRIPT_DIR/Results"

mkdir -p "$RUN_ROOT" "$RESULTS_DIR"

JOB_IDS=()

for DAY in "${DAYS[@]}"; do
    MODEL_NAME="model52_W7_${NZONES}shells_CSiNi56_t${DAY}d.dat"
    MODEL="$SCRIPT_DIR/Supernova Models/$MODEL_NAME"
    if [ ! -f "$MODEL" ]; then
        echo "ERROR: Model file not found: $MODEL"
        echo "Skipping t = ${DAY} days."
        continue
    fi

    # Fresh copy of the source for this day
    RUN_DIR="$RUN_ROOT/t${DAY}d"
    rm -rf "$RUN_DIR/build"
    mkdir -p "$RUN_DIR/build" "$RUN_DIR/Supernova Models"
    cp "$SCRIPT_DIR"/*.cc "$SCRIPT_DIR"/*.hh "$SCRIPT_DIR/CMakeLists.txt" "$RUN_DIR/"
    cp -r "$SCRIPT_DIR/Python Files" "$RUN_DIR/"
    cp "$MODEL" "$RUN_DIR/Supernova Models/"

    # Patch this copy's globalVars.cc
    GLOBALVARS="$RUN_DIR/globalVars.cc"
    sed -i "s/const G4double timeSinceSupernova = [0-9.]*/const G4double timeSinceSupernova = ${DAY}.0/" "$GLOBALVARS"
    sed -i "s/const G4long eventCount = [0-9eE+.]*/const G4long eventCount = ${EVENTS}/" "$GLOBALVARS"
    sed -i "s/const G4int threadCount = [0-9]*/const G4int threadCount = ${THREADS}/" "$GLOBALVARS"
    sed -i "s/const G4int nZones = [0-9]*/const G4int nZones = ${NZONES}/" "$GLOBALVARS"
    sed -i "s|const G4String projectDir = \".*\";|const G4String projectDir = \"${RUN_DIR}\";|" "$GLOBALVARS"

    OUT="$RESULTS_DIR/t${DAY}d"

    CONSTRAINT_LINE=""
    [ -n "$CONSTRAINT" ] && CONSTRAINT_LINE="#SBATCH --constraint=${CONSTRAINT}"

    # Job script for this day. Unescaped variables are filled in now;
    # escaped ones (\$) are evaluated when the job runs.
    cat > "$RUN_DIR/job.sh" <<EOF
#!/bin/bash
#SBATCH --job-name=sn_t${DAY}d
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=${THREADS}
#SBATCH --mem=${MEM}
#SBATCH --time=${WALLTIME}
#SBATCH --output=${RUN_DIR}/slurm-%j.out
${CONSTRAINT_LINE}
${ENV_BUILD}

cd "${RUN_DIR}/build" || exit 1

echo "Building..."
cmake .. > cmake.log || { echo "ERROR: cmake failed, see ${RUN_DIR}/build/cmake.log"; exit 1; }
make -j${THREADS} --quiet || { echo "ERROR: Build failed for t = ${DAY} days."; exit 1; }

# Python is needed from here on (main.cc calls the scripts via std::system).
# The anaconda module puts its own lib/ on LD_LIBRARY_PATH, whose older
# libstdc++ breaks the Geant4 libraries, so restore the build-time value.
# conda's python3 stays first on PATH and finds its own libraries by itself.
BUILD_LD_LIBRARY_PATH="\$LD_LIBRARY_PATH"
${ENV_PYTHON}
export LD_LIBRARY_PATH="\$BUILD_LD_LIBRARY_PATH"
export MPLBACKEND=Agg
# Days for the cross-time-step scripts main.cc calls (run_batch.sh is not copied here)
export SN_DAYS="${DAY}"

# Runs the simulation, then combineFiles.py and plotSpectra.py via main.cc
echo "Running simulation..."
RUN_START=\$SECONDS
./SupernovaSimulation
SIM_EXIT=\$?
RUN_ELAPSED=\$(( SECONDS - RUN_START ))
RUN_MINS=\$(( RUN_ELAPSED / 60 ))
RUN_SECS=\$(( RUN_ELAPSED % 60 ))

if [ \$SIM_EXIT -ne 0 ]; then
    echo "ERROR: Simulation exited with code \$SIM_EXIT for t = ${DAY} days (after \${RUN_MINS}m \${RUN_SECS}s)."
    exit 1
fi

# The cross-time-step scripts leave an empty Results/ in this run copy;
# the real results go to ${RESULTS_DIR}
rm -rf "${RUN_DIR}/Results"

# Archive outputs for this day into the main project
mkdir -p "${OUT}" "${SCRIPT_DIR}/Optical Depths/t${DAY}d" "${SCRIPT_DIR}/Graphs/Current"
cp "${RUN_DIR}/Combined_info_summary.txt"      "${OUT}/"
cp "${RUN_DIR}/build"/All_*_combined.txt       "${OUT}/"
cp "${RUN_DIR}/Graphs/Current"/*_${DAY}.png    "${OUT}/" 2>/dev/null
cp "${RUN_DIR}/Graphs/Current"/*_${DAY}.png    "${SCRIPT_DIR}/Graphs/Current/" 2>/dev/null
cp "${RUN_DIR}/Optical Depths/t${DAY}d"/*      "${SCRIPT_DIR}/Optical Depths/t${DAY}d/"

echo "t=${DAY}d  events=${EVENTS}  time=\${RUN_MINS}m \${RUN_SECS}s  date=\$(date '+%Y-%m-%d %H:%M')" >> "${RESULTS_DIR}/run_log.txt"
echo "Completed t = ${DAY} days in \${RUN_MINS}m \${RUN_SECS}s. Outputs archived to ${OUT}"
EOF

    if [ $DRY_RUN -eq 1 ]; then
        echo "t = ${DAY}d: prepared $RUN_DIR (not submitted)"
        continue
    fi

    JOB_ID=$(sbatch --parsable "$RUN_DIR/job.sh")
    if [ -z "$JOB_ID" ]; then
        echo "ERROR: sbatch failed for t = ${DAY} days."
        continue
    fi
    JOB_IDS+=("$JOB_ID")
    echo "t = ${DAY}d: submitted job $JOB_ID"
done

# Cross-time-step plots, run once after every simulation job has ended
cat > "$RUN_ROOT/plots.sh" <<EOF
#!/bin/bash
#SBATCH --job-name=sn_plots
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=${RUN_ROOT}/slurm-plots-%j.out
${ENV_PYTHON}
export MPLBACKEND=Agg
# Plot the days simulated here, not the DAYS list in run_batch.sh
export SN_DAYS="${DAYS[*]}"

python3 "${SCRIPT_DIR}/Python Files/plotForPlBpl.py"
python3 "${SCRIPT_DIR}/Python Files/plot_tau_vs_menc.py"
python3 "${SCRIPT_DIR}/Python Files/plot_escape_flux_vs_time.py"
python3 "${SCRIPT_DIR}/Python Files/plot_line_rates_vs_time.py"
EOF

if [ $DRY_RUN -eq 1 ]; then
    echo "Dry run: nothing submitted. Job scripts are in $RUN_ROOT/t<N>d/job.sh"
    exit 0
fi

if [ ${#JOB_IDS[@]} -eq 0 ]; then
    echo "No simulation jobs were submitted."
    exit 1
fi

DEPENDENCY="afterany:$(IFS=:; echo "${JOB_IDS[*]}")"
PLOT_ID=$(sbatch --parsable --dependency="$DEPENDENCY" "$RUN_ROOT/plots.sh")
echo "Plot job $PLOT_ID will run after all ${#JOB_IDS[@]} simulation jobs end."
echo "Check progress with: squeue -u \$USER"
