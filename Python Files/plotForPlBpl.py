import numpy as np
import matplotlib.pyplot as plt
import glob
import os


# ── Configuration — edit these before running ─────────────────────────────────
TIME_DAYS    = 60.0                                  # days since supernova (match your run)
EVENT_COUNT  = 1e7                                   # events per thread (from globalVars.cc)
THREAD_COUNT = 16                                    # threads (from globalVars.cc)
DISTANCE_MPC = 3.5
SIM_DIR      = f"/home/cdipasq/simProfTheMT/Results/t{int(TIME_DAYS)}d"  # directory containing combined spectrum files

REF_FILE_BPL = f"/home/cdipasq/simProfTheMT/PlBpl/BplW7.{int(TIME_DAYS)}"
REF_FILE_PL  = f"/home/cdipasq/simProfTheMT/PlBpl/plW7.{int(TIME_DAYS)}"
# ─────────────────────────────────────────────────────────────────────────────

# Decay chain constants (must match PrimaryGeneratorAction.cc)
LAMBDA_NI = 1.319e-6   # 1/s
LAMBDA_CO = 1.039e-7   # 1/s
N0_NI     = 1.3e55
MPC_TO_CM = 3.0857e24


def decay_rate(t_days):
    t    = t_days * 86400.0
    R_Ni = LAMBDA_NI * N0_NI * np.exp(-LAMBDA_NI * t)
    N_Co = (LAMBDA_NI * N0_NI / (LAMBDA_CO - LAMBDA_NI)) * \
           (np.exp(-LAMBDA_NI * t) - np.exp(-LAMBDA_CO * t))
    return R_Ni + LAMBDA_CO * N_Co


def load_sim_histogram(prefix):
    """Load a combined spectrum file."""
    files = sorted(glob.glob(os.path.join(SIM_DIR, f"{prefix}.txt")))
    if not files:
        raise FileNotFoundError(
            f"No file matching '{prefix}.txt' found in {SIM_DIR!r}.\n"
            "Make sure SIM_DIR points to the results directory containing the combined files."
        )
    data = np.loadtxt(files[0], comments='#')
    energies = data[:, 0]
    counts   = data[:, 1]
    print(f"  {prefix}: {counts.sum():.0f} total counts")
    return energies, counts


def counts_to_flux(energies_keV, counts, R_total, n_events, distance_mpc):
    """
    Convert raw simulation counts to photons/cm²/s/keV.

    flux = (counts / n_events) * R_total / (4π D²) / ΔE
    """
    D_cm   = distance_mpc * MPC_TO_CM
    # bin widths from consecutive log-spaced centers
    widths        = np.empty_like(energies_keV)
    widths[:-1]   = np.diff(energies_keV)
    widths[-1]    = widths[-2]             # repeat last width for final bin
    flux = (counts / n_events) * R_total / (4.0 * np.pi * D_cm**2) / widths
    return flux


def load_reference(filepath):
    """
    Parse a reference spectrum file.
    Returns arrays of mid-energy (keV) and flux (photons/cm²/s/keV).
    Skips rows where flux <= 0 or that can't be parsed as floats.
    """
    energies, fluxes = [], []
    with open(filepath) as f:
        for line in f:
            cols = line.split()
            if len(cols) != 11:        # main data rows have exactly 11 columns
                continue
            try:
                e    = float(cols[1])   # mid-energy bin (keV)
                flux = float(cols[2])   # photon flux (photons/cm²/s/keV)
            except ValueError:
                continue
            if flux > 1e-10:   # 1e-30 is a placeholder for zero in these files
                energies.append(e)
                fluxes.append(flux)
    return np.array(energies), np.array(fluxes)


# ── Main ─────────────────────────────────────────────────────────────────────
R_total  = decay_rate(TIME_DAYS)
N_events = EVENT_COUNT * THREAD_COUNT

print(f"Time:     {TIME_DAYS:.0f} days")
print(f"R_total:  {R_total:.3e} decays/s")
print(f"N_events: {N_events:.3e} total\n")

print("Loading simulation histograms...")
e_brems,  c_brems  = load_sim_histogram("All_brems_spectrum_combined")
e_compt,  c_compt  = load_sim_histogram("All_compton_spectrum_combined")
e_direct, c_direct = load_sim_histogram("All_direct_escape_combined")

flux_brems  = counts_to_flux(e_brems,  c_brems,  R_total, N_events, DISTANCE_MPC)
flux_compt  = counts_to_flux(e_compt,  c_compt,  R_total, N_events, DISTANCE_MPC)
flux_direct = counts_to_flux(e_direct, c_direct, R_total, N_events, DISTANCE_MPC)

print("\nLoading reference files...")
e_bpl, f_bpl = load_reference(REF_FILE_BPL)
e_pl,  f_pl  = load_reference(REF_FILE_PL)
print(f"  BplW7: {len(e_bpl)} points")
print(f"  plW7:  {len(e_pl)} points")

# ── Plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))

# Simulation lines — mask out zero bins to keep the log plot clean
for energies, flux, label, color in [
    (e_brems,  flux_brems,  "Bremsstrahlung", "tab:blue"),
    (e_compt,  flux_compt,  "Compton",        "tab:orange"),
    (e_direct, flux_direct, "Direct Escape",  "tab:green"),
]:
    mask = flux > 0
    ax.plot(energies[mask], flux[mask], label=label, color=color, lw=1.2)

# Reference lines
ax.plot(e_bpl, f_bpl, label="BplW7 (ref)", color="tab:red",    lw=1.2, ls="--")
ax.plot(e_pl,  f_pl,  label="plW7 (ref)",  color="tab:purple", lw=1.2, ls="--")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Energy (keV)", fontsize=12)
ax.set_ylabel(r"Flux (photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)", fontsize=12)
ax.set_title(
    f"X-ray Spectrum — W7 model, t = {TIME_DAYS:.0f} days, D = {DISTANCE_MPC} Mpc",
    fontsize=13
)
ax.legend(fontsize=10)
ax.grid(True, which="both", alpha=0.25)

plt.tight_layout()
outfile = f"spectrum_{TIME_DAYS:.0f}d.png"
plt.savefig(outfile, dpi=150)
plt.show()
print(f"\nSaved {outfile}")
