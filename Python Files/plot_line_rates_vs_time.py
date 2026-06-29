"""
Plot gamma-ray line creation rate (photons/s) vs time for 158, 812, 847, 1238 keV.
Simulation points are read from Results/t<N>d/Combined_info_summary.txt.
Analytical curves use the formulas from the professor's PDF.
"""
import os
import re
import math
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, "..")
RESULTS_DIR = os.path.join(PROJECT_DIR, "Results")
OUT_DIR     = os.path.join(PROJECT_DIR, "Graphs", "Current")
os.makedirs(OUT_DIR, exist_ok=True)

# Physical constants (from professor's PDF)
HALF_LIFE_NI56 = 6.095          # days
TAU_NI56       = HALF_LIFE_NI56 / math.log(2)   # = 8.86437 d
HALF_LIFE_CO56 = 77.23          # days
TAU_CO56       = HALF_LIFE_CO56 / math.log(2)   # = 111.419 d

LAMBDA_NI56 = 1.0 / (TAU_NI56 * 24 * 3600)     # s^-1
LAMBDA_CO56 = 1.0 / (TAU_CO56 * 24 * 3600)     # s^-1

M_SUN_G    = 1.9892e33
NI56_MASS  = 0.58 * M_SUN_G   # 0.5894 Msun rounded to 0.58 in model
A_NI56     = 55.94
N_AVO      = 6.023e23
TOTAL_NI56_NUCLEI = (NI56_MASS / A_NI56) * N_AVO

# Branching fractions
B158  = 1.00
B812  = 0.885
B847  = 1.00
B1238 = 0.6760


def fCo56(t_days):
    t = t_days * 86400
    return (LAMBDA_NI56 / (LAMBDA_CO56 - LAMBDA_NI56)) * \
           (math.exp(-t / (TAU_NI56 * 86400)) - math.exp(-t / (TAU_CO56 * 86400)))


def analytical_rates(t_days):
    t = t_days * 86400
    exp_ni = math.exp(-t / (TAU_NI56 * 86400))
    f_co   = fCo56(t_days)
    N158  = TOTAL_NI56_NUCLEI * exp_ni * B158  / (TAU_NI56 * 86400)
    N812  = TOTAL_NI56_NUCLEI * exp_ni * B812  / (TAU_NI56 * 86400)
    N847  = TOTAL_NI56_NUCLEI * f_co  * B847  / (TAU_CO56 * 86400)
    N1238 = TOTAL_NI56_NUCLEI * f_co  * B1238 / (TAU_CO56 * 86400)
    return N158, N812, N847, N1238


# --- Helper: same decay-rate formula used in PrimaryGeneratorAction.cc ---
LAM_NI_CODE = 1.319e-6   # 1/s  (matches globalVars / PrimaryGeneratorAction.cc)
LAM_CO_CODE = 1.039e-7   # 1/s
N0_NI_CODE  = 1.3e55

def R_total_code(t_days):
    t     = t_days * 86400
    R_Ni  = LAM_NI_CODE * N0_NI_CODE * math.exp(-LAM_NI_CODE * t)
    N_Co  = (LAM_NI_CODE * N0_NI_CODE / (LAM_CO_CODE - LAM_NI_CODE)) * \
            (math.exp(-LAM_NI_CODE * t) - math.exp(-LAM_CO_CODE * t))
    return R_Ni + LAM_CO_CODE * N_Co


def parse_summary(path):
    vals = {}
    with open(path) as f:
        for line in f:
            for key in ('Nickel Decays', 'Cobalt Decays',
                        '158.58 keV Decay Photons',
                        '811.85 keV Decay Photons',
                        '847 keV Decay Photons',
                        '1238.3 keV Decay Photons'):
                if line.startswith(key + ':'):
                    vals[key] = float(line.split(':')[1].strip())
    return vals


# --- Collect simulation results ---
sim_days  = []
sim_N158  = []
sim_N812  = []
sim_N847  = []
sim_N1238 = []

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
    R_tot = R_total_code(t_day)
    sim_days.append(t_day)
    sim_N158.append((v.get('158.58 keV Decay Photons', 0) / total_decays) * R_tot)
    sim_N812.append((v.get('811.85 keV Decay Photons', 0) / total_decays) * R_tot)
    sim_N847.append((v.get('847 keV Decay Photons', 0)    / total_decays) * R_tot)
    sim_N1238.append((v.get('1238.3 keV Decay Photons', 0) / total_decays) * R_tot)

sim_days  = np.array(sim_days)
sim_N158  = np.array(sim_N158)
sim_N812  = np.array(sim_N812)
sim_N847  = np.array(sim_N847)
sim_N1238 = np.array(sim_N1238)

# --- Analytical curves ---
t_ana = np.linspace(10, 110, 500)
ana_N158  = np.array([analytical_rates(t)[0] for t in t_ana])
ana_N812  = np.array([analytical_rates(t)[1] for t in t_ana])
ana_N847  = np.array([analytical_rates(t)[2] for t in t_ana])
ana_N1238 = np.array([analytical_rates(t)[3] for t in t_ana])

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 6))

colors = {'158': 'tab:blue', '812': 'tab:orange', '847': 'tab:green', '1238': 'tab:red'}

ax.plot(t_ana, ana_N158,  color=colors['158'],  lw=2,   label='158 keV (Ni56, analytical)')
ax.plot(t_ana, ana_N812,  color=colors['812'],  lw=2,   label='812 keV (Ni56, analytical)')
ax.plot(t_ana, ana_N847,  color=colors['847'],  lw=2,   label='847 keV (Co56, analytical)')
ax.plot(t_ana, ana_N1238, color=colors['1238'], lw=2,   label='1238 keV (Co56, analytical)')

if len(sim_days):
    ax.scatter(sim_days, sim_N158,  color=colors['158'],  marker='o', s=60, zorder=5, label='158 keV (Geant4)')
    ax.scatter(sim_days, sim_N812,  color=colors['812'],  marker='s', s=60, zorder=5, label='812 keV (Geant4)')
    ax.scatter(sim_days, sim_N847,  color=colors['847'],  marker='^', s=60, zorder=5, label='847 keV (Geant4)')
    ax.scatter(sim_days, sim_N1238, color=colors['1238'], marker='D', s=60, zorder=5, label='1238 keV (Geant4)')
else:
    print("No simulation results found in Results/. Run the batch first.")

ax.set_yscale('log')
ax.set_xlabel('Time (days)', fontsize=12)
ax.set_ylabel(r'Gamma-ray Line Creation Rate (photons s$^{-1}$)', fontsize=12)
ax.set_title('Gamma-ray Line Creation Rate vs. Time — W7 model, 0.58 M$_\odot$ Ni56', fontsize=13)
ax.grid(True, which='both', ls='--', lw=0.5)
ax.legend(fontsize=9)
fig.tight_layout()

outfile = os.path.join(OUT_DIR, "NCreated_vs_time_W7.png")
fig.savefig(outfile, dpi=300)
plt.close(fig)
print(f"Saved: {outfile}")
