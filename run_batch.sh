#!/bin/bash
# Run the simulation for each day in DAYS, rebuild between runs,
# and archive outputs into Results/t<N>d/ so nothing is overwritten.

# ── Configure here ─────────────────────────────────────────────────────────────
DAYS=(10 20 30 40 50 60 70 80 90 100 120 200)  # days since supernova to simulate
EVENTS=1e6          # total decay events passed to /run/beamOn (distributed across threads by Geant4)
THREADS=16          # must match threadCount in globalVars.cc
# ──────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
GLOBALVARS="$SCRIPT_DIR/globalVars.cc"
RESULTS_DIR="$SCRIPT_DIR/Results"
EXECUTABLE="$BUILD_DIR/SupernovaSimulation"

mkdir -p "$RESULTS_DIR"

for DAY in "${DAYS[@]}"; do
    echo ""
    echo "=========================================="
    echo " Starting simulation: t = ${DAY} days"
    echo "=========================================="

    # Check that the model file exists before wasting time building
    MODEL="$SCRIPT_DIR/Supernova Models/model52_W7_20shells_CSiNi56_t${DAY}d.dat"
    if [ ! -f "$MODEL" ]; then
        echo "ERROR: Model file not found: $MODEL"
        echo "Skipping t = ${DAY} days."
        continue
    fi

    # Patch globalVars.cc
    sed -i "s/const G4double timeSinceSupernova = [0-9.]*/const G4double timeSinceSupernova = ${DAY}.0/" "$GLOBALVARS"
    sed -i "s/const G4long eventCount = [0-9eE+.]*/const G4long eventCount = ${EVENTS}/" "$GLOBALVARS"
    echo "Set timeSinceSupernova = ${DAY}.0, eventCount = ${EVENTS}"

    # Rebuild
    echo "Building..."
    make -C "$BUILD_DIR" -j"$THREADS" --quiet
    if [ $? -ne 0 ]; then
        echo "ERROR: Build failed for t = ${DAY} days. Skipping."
        continue
    fi

    # Run simulation (also triggers Python scripts via std::system calls in main.cc)
    echo "Running simulation..."
    RUN_START=$SECONDS
    cd "$BUILD_DIR"
    "$EXECUTABLE"
    SIM_EXIT=$?
    cd "$SCRIPT_DIR"
    RUN_ELAPSED=$(( SECONDS - RUN_START ))
    RUN_MINS=$(( RUN_ELAPSED / 60 ))
    RUN_SECS=$(( RUN_ELAPSED % 60 ))

    if [ $SIM_EXIT -ne 0 ]; then
        echo "ERROR: Simulation exited with code $SIM_EXIT for t = ${DAY} days (after ${RUN_MINS}m ${RUN_SECS}s)."
        continue
    fi

    echo "Run time: ${RUN_MINS}m ${RUN_SECS}s"

    # Archive outputs for this day
    OUT="$RESULTS_DIR/t${DAY}d"
    mkdir -p "$OUT"

    cp "$SCRIPT_DIR/Combined_info_summary.txt"   "$OUT/" 2>/dev/null
    cp "$BUILD_DIR"/All_*_combined.txt            "$OUT/" 2>/dev/null
    cp "$SCRIPT_DIR/Graphs/Current"/*_${DAY}.png "$OUT/" 2>/dev/null

    echo "t=${DAY}d  events=${EVENTS}  time=${RUN_MINS}m ${RUN_SECS}s  date=$(date '+%Y-%m-%d %H:%M')" >> "$RESULTS_DIR/run_log.txt"

    echo "Outputs archived to $OUT"
    echo "Completed t = ${DAY} days in ${RUN_MINS}m ${RUN_SECS}s."
done

echo ""
echo "=========================================="
echo " All runs complete."
echo "=========================================="
