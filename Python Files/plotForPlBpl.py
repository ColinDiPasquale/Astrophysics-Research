"""
Overplot Geant4 escape spectra with the plW7 and BplW7 analytical reference
spectra for each available time step in Results/.

Run this script after all batch simulations are complete.
Outputs one PNG per time step into Graphs/Current/.
"""
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, "..")
RESULTS_DIR = os.path.join(PROJECT_DIR, "Results")
PLBPL_DIR   = os.path.join(PROJECT_DIR, "PlBpl")
OUT_DIR     = os.path.join(PROJECT_DIR, "Graphs", "Current")
os.makedirs(OUT_DIR, exist_ok=True)

DISTANCE_MPC = 1
MPC_TO_CM    = 3.0857e24

LAM_NI = 1.319e-6   # 1/s
LAM_CO = 1.039e-7   # 1/s
N0_NI  = 1.3e55


def decay_rate(t_days):
    t    = t_days * 86400.0
    R_Ni = LAM_NI * N0_NI * np.exp(-LAM_NI * t)
    N_Co = (LAM_NI * N0_NI / (LAM_CO - LAM_NI)) * \
           (np.exp(-LAM_NI * t) - np.exp(-LAM_CO * t))
    return R_Ni + LAM_CO * N_Co


def load_sim_histogram(path):
    data    = np.loadtxt(path, comments='#')
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


def load_reference(filepath):
    lo_edges, fluxes = [], []
    with open(filepath) as f:
        for line in f:
            cols = line.split()
            if len(cols) != 11:
                continue
            try:
                lo   = float(cols[0])
                flux = float(cols[2])
            except ValueError:
                continue
            if flux > 1e-10:
                lo_edges.append(lo)
                fluxes.append(flux)
    return np.array(lo_edges), np.array(fluxes)


def process_time_step(t_day, sim_dir, n_events):
    print(f"\n--- t = {t_day} days ---")

    # Check reference files exist
    ref_bpl = os.path.join(PLBPL_DIR, f"BplW7.{t_day}")
    ref_pl  = os.path.join(PLBPL_DIR, f"plW7.{t_day}")
    if not os.path.isfile(ref_bpl) or not os.path.isfile(ref_pl):
        print(f"  Reference files missing for t={t_day}d, skipping.")
        return

    R_tot = decay_rate(t_day)
    print(f"  R_total = {R_tot:.3e} decays/s")

    # Load simulation spectra
    loaded = {}
    for prefix, label in [
        ("All_brems_spectrum_combined",  "brems"),
        ("All_compton_spectrum_combined", "compt"),
        ("All_direct_escape_combined",    "direct"),
    ]:
        fpath = os.path.join(sim_dir, f"{prefix}.txt")
        if not os.path.isfile(fpath):
            print(f"  Missing {prefix}.txt — skipping component.")
            loaded[label] = None
            continue
        e, c = load_sim_histogram(fpath)
        e, c, w = rebin(e, c)
        loaded[label] = (e, counts_to_flux(w, c, R_tot, n_events, DISTANCE_MPC))
        print(f"  {prefix}: {c.sum():.0f} counts")

    # Load reference spectra
    e_bpl, f_bpl = load_reference(ref_bpl)
    e_pl,  f_pl  = load_reference(ref_pl)
    print(f"  BplW7: {len(e_bpl)} points  |  plW7: {len(e_pl)} points")

    fig, ax = plt.subplots(figsize=(11, 6))

    sim_series = [
        ("brems",  "Bremsstrahlung", "tab:red"),
        ("compt",  "Compton",        "tab:blue"),
        ("direct", "Direct Escape",  "tab:green"),
    ]
    for key, label, color in sim_series:
        if loaded[key] is None:
            continue
        energies, flux = loaded[key]
        mask = flux > 0
        ax.step(energies[mask], flux[mask], where='post',
                label=label, color=color, lw=1.2)

    ax.step(e_bpl, f_bpl, where='post', label="BplW7 (ref)", color="tab:orange", lw=1.4, ls="--")
    ax.step(e_pl,  f_pl,  where='post', label="plW7 (ref)",  color="tab:purple", lw=1.4, ls="--")

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Energy (keV)', fontsize=12)
    ax.set_ylabel(r"Flux (photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)", fontsize=12)
    ax.set_title(f"Escape Spectrum — W7, t = {t_day} days, D = {DISTANCE_MPC} Mpc", fontsize=13)
    ax.grid(True, which='both', ls='--', lw=0.5)
    ax.legend(fontsize=10)
    fig.tight_layout()

    outfile = os.path.join(OUT_DIR, f"spectrum_vs_ref_{t_day}d.png")
    fig.savefig(outfile, dpi=300)
    plt.close(fig)
    print(f"  Saved: {outfile}")


# ── Main: loop over all Results/t<N>d directories ────────────────────────────
TARGET_DAYS = [20, 30, 40, 60, 80, 100]   # as requested by professor

for entry in sorted(os.listdir(RESULTS_DIR)):
    match = re.match(r'^t(\d+)d$', entry)
    if not match:
        continue
    t_day   = int(match.group(1))
    if t_day not in TARGET_DAYS:
        continue
    sim_dir = os.path.join(RESULTS_DIR, entry)

    # Read n_events from the Combined_info_summary.txt
    summary = os.path.join(sim_dir, "Combined_info_summary.txt")
    n_events = 0
    if os.path.isfile(summary):
        with open(summary) as sf:
            for line in sf:
                if line.startswith('Nickel Decays:'):
                    n_events += float(line.split(':')[1].strip())
                elif line.startswith('Cobalt Decays:'):
                    n_events += float(line.split(':')[1].strip())
    if n_events == 0:
        print(f"t={t_day}d: could not determine n_events from summary, skipping.")
        continue

    process_time_step(t_day, sim_dir, n_events)

print("\nAll done.")
