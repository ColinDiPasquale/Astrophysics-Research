"""
Plot gamma-ray line escape flux (ph/cm^2/s) vs time for 158, 812, 847, 1238 keV.

Simulation points come from Results/t<N>d/Combined_info_summary.txt.
Analytical curves come from:
  Supernova Models/tfluxni56.W7_1Mpc_0p5894MsunNi56   (cols: t, F158, F812, fesc158, fesc812)
  Supernova Models/fluxco56.W7_1Mpc_0p5894MsunNi56    (cols: t, F847, F1238)
If those files are absent the script still plots the simulation-only points.
"""
import os
import re
import math
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR  = os.path.join(SCRIPT_DIR, "..")
RESULTS_DIR  = os.path.join(PROJECT_DIR, "Results")
MODELS_DIR   = os.path.join(PROJECT_DIR, "Supernova Models")
OUT_DIR      = os.path.join(PROJECT_DIR, "Graphs", "Current")
os.makedirs(OUT_DIR, exist_ok=True)

DISTANCE_CM  = 1.0 * 3.086e24   # 1 Mpc in cm
SPHERE_AREA  = 4 * math.pi * DISTANCE_CM**2

LAM_NI = 1.319e-6   # 1/s
LAM_CO = 1.039e-7   # 1/s
N0_NI  = 1.3e55

def R_total(t_days):
    t    = t_days * 86400
    R_Ni = LAM_NI * N0_NI * math.exp(-LAM_NI * t)
    N_Co = (LAM_NI * N0_NI / (LAM_CO - LAM_NI)) * \
           (math.exp(-LAM_NI * t) - math.exp(-LAM_CO * t))
    return R_Ni + LAM_CO * N_Co


def parse_summary(path):
    vals = {}
    with open(path) as f:
        for line in f:
            for key in ('Nickel Decays', 'Cobalt Decays',
                        '158.58 keV Direct Escape',
                        '811.85 keV Direct Escape',
                        '847 keV Direct Escape',
                        '1238.3 keV Direct Escape'):
                if line.startswith(key + ':'):
                    vals[key] = float(line.split(':')[1].strip())
    return vals


# --- Collect simulation results ---
sim_days  = []
sim_F158  = []
sim_F812  = []
sim_F847  = []
sim_F1238 = []

for entry in sorted(os.listdir(RESULTS_DIR)):
    m = re.match(r'^t(\d+)d$', entry)
    if not m:
        continue
    t_day = int(m.group(1))
    summary_path = os.path.join(RESULTS_DIR, entry, "Combined_info_summary.txt")
    if not os.path.isfile(summary_path):
        continue
    v = parse_summary(summary_path)
    total_decays = v.get('Nickel Decays', 0) + v.get('Cobalt Decays', 0)
    if total_decays == 0:
        continue
    R_tot = R_total(t_day)
    sim_days.append(t_day)
    # flux in ph/cm^2/s (escape counts normalized by total events × rate / area)
    sim_F158.append( (v.get('158.58 keV Direct Escape', 0) / total_decays) * R_tot / SPHERE_AREA)
    sim_F812.append( (v.get('811.85 keV Direct Escape', 0) / total_decays) * R_tot / SPHERE_AREA)
    sim_F847.append( (v.get('847 keV Direct Escape',    0) / total_decays) * R_tot / SPHERE_AREA)
    sim_F1238.append((v.get('1238.3 keV Direct Escape', 0) / total_decays) * R_tot / SPHERE_AREA)

sim_days  = np.array(sim_days,  dtype=float)
sim_F158  = np.array(sim_F158)
sim_F812  = np.array(sim_F812)
sim_F847  = np.array(sim_F847)
sim_F1238 = np.array(sim_F1238)

# --- Load analytical files (if available) ---
NI_FILE = os.path.join(SCRIPT_DIR, "tfluxni56.W7_1Mpc_0p5894MsunNi56")
CO_FILE = os.path.join(SCRIPT_DIR, "tfluxco56.W7_1Mpc_0p5894MsunNi56")

import re as _re
_fortran_fix = _re.compile(r'(\d)([-+])(\d+)')

def load_fortran_table(filepath):
    """Load a space-delimited float table that may contain Fortran-style
    exponents such as 1.011-195 (missing the E)."""
    rows = []
    with open(filepath) as f:
        for line in f:
            cols = line.split()
            if not cols:
                continue
            try:
                rows.append([float(_fortran_fix.sub(r'\1E\2\3', c)) for c in cols])
            except ValueError:
                continue
    return np.array(rows)

ana_t_ni = ana_F158 = ana_F812 = None
ana_t_co = ana_F847 = ana_F1238 = None

FLUX_MIN = 1e-20   # ignore unphysically tiny values that distort the log axis

if os.path.isfile(NI_FILE):
    data = load_fortran_table(NI_FILE)
    ana_t_ni = data[:, 0]
    ana_F158 = data[:, 1]
    ana_F812 = data[:, 2]
    good = (ana_F158 > FLUX_MIN) | (ana_F812 > FLUX_MIN)
    ana_t_ni, ana_F158, ana_F812 = ana_t_ni[good], ana_F158[good], ana_F812[good]
    print(f"Loaded analytical Ni56 escape fluxes from {NI_FILE}")
else:
    print(f"Analytical file not found: {NI_FILE}")

if os.path.isfile(CO_FILE):
    data = load_fortran_table(CO_FILE)
    ana_t_co  = data[:, 0]
    ana_F847  = data[:, 1]
    ana_F1238 = data[:, 2]
    good = (ana_F847 > FLUX_MIN) | (ana_F1238 > FLUX_MIN)
    ana_t_co, ana_F847, ana_F1238 = ana_t_co[good], ana_F847[good], ana_F1238[good]
    print(f"Loaded analytical Co56 escape fluxes from {CO_FILE}")
else:
    print(f"Analytical file not found: {CO_FILE}")


# ─── Plot 1: 158 keV and 812 keV (Ni56 lines) ────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(10, 6))

if ana_t_ni is not None:
    mask = ana_F158 > FLUX_MIN
    ax1.plot(ana_t_ni[mask], ana_F158[mask], color='tab:blue',   lw=2, label='158 keV (analytical)')
    mask = ana_F812 > FLUX_MIN
    ax1.plot(ana_t_ni[mask], ana_F812[mask], color='tab:orange', lw=2, label='812 keV (analytical)')

if len(sim_days):
    mask = sim_F158 > 0
    ax1.scatter(sim_days[mask], sim_F158[mask], color='tab:blue',   marker='o', s=60, zorder=5, label='158 keV (Geant4)')
    mask = sim_F812 > 0
    ax1.scatter(sim_days[mask], sim_F812[mask], color='tab:orange', marker='s', s=60, zorder=5, label='812 keV (Geant4)')

# Zoom x-axis around simulation points (±15 days padding), fall back to 10–110 if no sim data
if len(sim_days):
    x_lo, x_hi = sim_days.min() - 15, sim_days.max() + 15
else:
    x_lo, x_hi = 10, 110

def zoom_axes(ax, t_arrays, f_arrays, x_lo, x_hi):
    """Set y limits based only on data within [x_lo, x_hi]."""
    vals = []
    for t, f in zip(t_arrays, f_arrays):
        if t is None or f is None:
            continue
        mask = (t >= x_lo) & (t <= x_hi) & (f > FLUX_MIN)
        if mask.any():
            vals.extend(f[mask].tolist())
    if vals:
        ymin, ymax = min(vals), max(vals)
        ax.set_ylim(ymin * 0.3, ymax * 3)

ax1.set_xlim(x_lo, x_hi)
zoom_axes(ax1,
          [ana_t_ni, ana_t_ni, sim_days, sim_days],
          [ana_F158, ana_F812, sim_F158, sim_F812],
          x_lo, x_hi)
ax1.set_yscale('log')
ax1.set_xlabel('Time (days)', fontsize=12)
ax1.set_ylabel(r'Escape Flux (photons cm$^{-2}$ s$^{-1}$)', fontsize=12)
ax1.set_title('Ni56 Gamma-line Escape Flux — W7, 1 Mpc, 0.58 M$_\odot$ Ni56', fontsize=13)
ax1.grid(True, which='both', ls='--', lw=0.5)
ax1.legend(fontsize=10)
fig1.tight_layout()
out1 = os.path.join(OUT_DIR, "F158_F812_W7_1Mpc_0p5894MsunNi56_sim.png")
fig1.savefig(out1, dpi=300)
plt.close(fig1)
print(f"Saved: {out1}")


# ─── Plot 2: 847 keV and 1238 keV (Co56 lines) ───────────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 6))

if ana_t_co is not None:
    mask = ana_F847 > FLUX_MIN
    ax2.plot(ana_t_co[mask],  ana_F847[mask],  color='tab:green', lw=2, label='847 keV (analytical)')
    mask = ana_F1238 > FLUX_MIN
    ax2.plot(ana_t_co[mask],  ana_F1238[mask], color='tab:red',   lw=2, label='1238 keV (analytical)')

if len(sim_days):
    mask = sim_F847 > 0
    ax2.scatter(sim_days[mask], sim_F847[mask],  color='tab:green', marker='^', s=60, zorder=5, label='847 keV (Geant4)')
    mask = sim_F1238 > 0
    ax2.scatter(sim_days[mask], sim_F1238[mask], color='tab:red',   marker='D', s=60, zorder=5, label='1238 keV (Geant4)')

ax2.set_xlim(x_lo, x_hi)
zoom_axes(ax2,
          [ana_t_co, ana_t_co, sim_days, sim_days],
          [ana_F847, ana_F1238, sim_F847, sim_F1238],
          x_lo, x_hi)
ax2.set_yscale('log')
ax2.set_xlabel('Time (days)', fontsize=12)
ax2.set_ylabel(r'Escape Flux (photons cm$^{-2}$ s$^{-1}$)', fontsize=12)
ax2.set_title('Co56 Gamma-line Escape Flux — W7, 1 Mpc, 0.58 M$_\odot$ Ni56', fontsize=13)
ax2.grid(True, which='both', ls='--', lw=0.5)
ax2.legend(fontsize=10)
fig2.tight_layout()
out2 = os.path.join(OUT_DIR, "F847_F1238_vs_t_W7_1Mpc_0p5894MsunNi56_sim.png")
fig2.savefig(out2, dpi=300)
plt.close(fig2)
print(f"Saved: {out2}")
