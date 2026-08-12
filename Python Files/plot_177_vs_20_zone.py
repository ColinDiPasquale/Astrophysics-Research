"""
Overplot Geant4 escape spectra from the 177-zone run (Results/) against the
20-zone run (20d/) for each available time step.

Run this after both batch simulations are complete.
Outputs one PNG per time step into Results/ZoneComparison/.
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import re

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR  = os.path.join(SCRIPT_DIR, "..")
DIR_177      = os.path.join(PROJECT_DIR, "Results")
DIR_20       = os.path.join(PROJECT_DIR, "20d")
OUT_DIR      = os.path.join(PROJECT_DIR, "Results", "ZoneComparison")
BATCH_SCRIPT = os.path.join(PROJECT_DIR, "run_batch.sh")
os.makedirs(OUT_DIR, exist_ok=True)

DISTANCE_MPC = 3.5
MPC_TO_CM    = 3.0857e24

LAM_NI = 1.319e-6   # 1/s
LAM_CO = 1.039e-7   # 1/s
N0_NI  = 1.3e55


def read_days_from_batch_script(path):
    """Parse the DAYS=(...) array out of run_batch.sh so this script always
    covers the same set of days the batch run actually simulated."""
    with open(path) as f:
        text = f.read()
    m = re.search(r'DAYS=\(([^)]*)\)', text)
    if not m:
        raise ValueError(f"Could not find DAYS=(...) array in {path}")
    return [int(tok) for tok in m.group(1).split()]


def decay_rate(t_days):
    t    = t_days * 86400.0
    R_Ni = LAM_NI * N0_NI * np.exp(-LAM_NI * t)
    N_Co = (LAM_NI * N0_NI / (LAM_CO - LAM_NI)) * \
           (np.exp(-LAM_NI * t) - np.exp(-LAM_CO * t))
    return R_Ni + LAM_CO * N_Co


def load_sim_histogram(path):
    data = np.loadtxt(path, comments='#')
    return data[:, 0], data[:, 1]


def rebin(energies_keV, counts, n_bins=187):
    e_min  = energies_keV[0]
    e_max  = energies_keV[-1]
    edges  = np.logspace(np.log10(e_min), np.log10(e_max), n_bins + 1)
    new_counts = np.zeros(n_bins)
    indices = np.searchsorted(edges, energies_keV, side='right') - 1
    indices = np.clip(indices, 0, n_bins - 1)
    for i, c in zip(indices, counts):
        new_counts[i] += c
    return edges[:-1], new_counts, np.diff(edges)


def counts_to_flux(widths, counts, R_total, n_events, distance_mpc):
    D_cm = distance_mpc * MPC_TO_CM
    return (counts / n_events) * R_total / (4.0 * np.pi * D_cm**2) / widths


def read_n_events(summary_path):
    n_events = 0.0
    with open(summary_path) as sf:
        for line in sf:
            if line.startswith('Nickel Decays:'):
                n_events += float(line.split(':')[1].strip())
            elif line.startswith('Cobalt Decays:'):
                n_events += float(line.split(':')[1].strip())
    return n_events


def load_run_spectra(sim_dir, R_tot, n_events):
    loaded = {}
    for prefix, label in [
        ("All_brems_spectrum_combined",  "brems"),
        ("All_compton_spectrum_combined", "compt"),
        ("All_direct_escape_combined",    "direct"),
    ]:
        fpath = os.path.join(sim_dir, f"{prefix}.txt")
        if not os.path.isfile(fpath):
            loaded[label] = None
            continue
        e, c = load_sim_histogram(fpath)
        e, c, w = rebin(e, c)
        loaded[label] = (e, counts_to_flux(w, c, R_tot, n_events, DISTANCE_MPC))
    return loaded


def process_time_step(t_day):
    print(f"\n--- t = {t_day} days ---")

    dir_177 = os.path.join(DIR_177, f"t{t_day}d")
    dir_20  = os.path.join(DIR_20,  f"t{t_day}d")
    if not os.path.isdir(dir_177) or not os.path.isdir(dir_20):
        print(f"  Missing run directory for t={t_day}d, skipping.")
        return

    summary_177 = os.path.join(dir_177, "Combined_info_summary.txt")
    summary_20  = os.path.join(dir_20,  "Combined_info_summary.txt")
    if not os.path.isfile(summary_177) or not os.path.isfile(summary_20):
        print(f"  Missing Combined_info_summary.txt for t={t_day}d, skipping.")
        return

    n_events_177 = read_n_events(summary_177)
    n_events_20  = read_n_events(summary_20)
    if n_events_177 == 0 or n_events_20 == 0:
        print(f"  Could not determine n_events for t={t_day}d, skipping.")
        return

    R_tot = decay_rate(t_day)
    print(f"  R_total = {R_tot:.3e} decays/s")

    loaded_177 = load_run_spectra(dir_177, R_tot, n_events_177)
    loaded_20  = load_run_spectra(dir_20,  R_tot, n_events_20)

    fig, ax = plt.subplots(figsize=(11, 6))

    sim_series = [
        ("brems",  "Bremsstrahlung", "tab:red"),
        ("compt",  "Compton",        "tab:blue"),
        ("direct", "Direct Escape",  "tab:green"),
    ]
    for key, label, color in sim_series:
        if loaded_177.get(key) is not None:
            energies, flux = loaded_177[key]
            mask = flux > 0
            ax.step(energies[mask], flux[mask], where='post',
                    label=f"{label} (177 zone)", color=color, lw=1.2)
        if loaded_20.get(key) is not None:
            energies, flux = loaded_20[key]
            mask = flux > 0
            ax.step(energies[mask], flux[mask], where='post',
                    label=f"{label} (20 zone)", color=color, lw=1.4, ls="--")

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Energy (keV)', fontsize=12)
    ax.set_ylabel(r"Flux (photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)", fontsize=12)
    ax.set_title(f"Escape Spectrum — W7, t = {t_day} days, D = {DISTANCE_MPC} Mpc\n"
                 f"177-zone vs 20-zone", fontsize=13)
    ax.grid(True, which='both', ls='--', lw=0.5)
    ax.legend(fontsize=9)
    fig.tight_layout()

    outfile = os.path.join(OUT_DIR, f"spectrum_177_vs_20_{t_day}d.png")
    fig.savefig(outfile, dpi=300)
    plt.close(fig)
    print(f"  Saved: {outfile}")


# ── Main: loop over every day in run_batch.sh's DAYS array ──────────────────
for t_day in read_days_from_batch_script(BATCH_SCRIPT):
    process_time_step(t_day)

print("\nAll done.")
