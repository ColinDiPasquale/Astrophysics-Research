import numpy as np
import matplotlib.pyplot as plt
import os
import re

# ── Output directory ───────────────────────────────────────────────────────────
OUT_DIR = "../Graphs/Current"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Read simulation parameters from globalVars.cc ─────────────────────────────
def read_globalvars(path="../globalVars.cc"):
    with open(path) as f:
        src = f.read()
    event_count = float(re.search(r'eventCount\s*=\s*([0-9eE+\-.]+)\s*;', src).group(1))
    t_obs       = float(re.search(r'timeSinceSupernova\s*=\s*([0-9eE+\-.]+)', src).group(1))
    return event_count, t_obs

N_EVENTS, T_OBS_DAYS = read_globalvars()
print(f"Read from globalVars.cc — eventCount: {N_EVENTS:,.0f}. Time since supernova: {T_OBS_DAYS} days")

# ── Fixed simulation parameters ────────────────────────────────────────────────
M_NI56_SOLAR = 0.58         # initial Ni-56 mass in solar masses (W7)
DISTANCE_CM  = 3.5 * 3.086e24  # 3.5 Mpc in cm

# ── Binning ────────────────────────────────────────────────────────────────────
N_BINS    = 187
E_MIN_KEV = 1.0
E_MAX_KEV = 5011.8724

# ── Physical constants ─────────────────────────────────────────────────────────
M_SUN_G   = 1.98847e33
N_AVO     = 6.022e23
A_NI56    = 55.94
LAMBDA_NI = np.log(2) / (6.075  * 86400)
LAMBDA_CO = np.log(2) / (77.27  * 86400)


def compute_decay_rates(M_Ni56_solar, t_days):
    N0       = M_Ni56_solar * M_SUN_G * N_AVO / A_NI56
    t        = t_days * 86400
    N_Ni     = N0 * np.exp(-LAMBDA_NI * t)
    N_Co     = N0 * (LAMBDA_NI / (LAMBDA_CO - LAMBDA_NI)) * \
               (np.exp(-LAMBDA_NI * t) - np.exp(-LAMBDA_CO * t))
    return LAMBDA_NI * N_Ni, LAMBDA_CO * N_Co


def load_combined(filename):
    data   = np.loadtxt(filename, comments="#")
    edges  = data[:, 0]
    counts = data[:, 1]
    uppers = np.empty_like(edges)
    uppers[:-1] = edges[1:]
    uppers[-1]  = edges[-1] + (edges[-1] - edges[-2])
    return edges, uppers, counts


def rebin(lo, hi, counts, new_edges):
    centers    = 0.5 * (lo + hi)
    new_counts, _ = np.histogram(centers, bins=new_edges, weights=counts)
    return new_counts, np.diff(new_edges)


def to_flux(counts, widths, decay_rate, sphere_area):
    return (counts / N_EVENTS) * (decay_rate / widths) / sphere_area


def save_plot(filename, title, series):
    """
    series: list of (flux_array, color, label)
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    for flux, color, label in series:
        ax.step(new_edges[:-1], flux, where='post', color=color, label=label)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Energy (keV)')
    ax.set_ylabel(r'Flux (photons s$^{-1}$ keV$^{-1}$ cm$^{-2}$)')
    ax.set_title(title)
    ax.grid(True, which='both', ls='--', lw=0.5)
    ax.legend()
    fig.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


# ── Derived quantities ─────────────────────────────────────────────────────────
dN_Ni, dN_Co    = compute_decay_rates(M_NI56_SOLAR, T_OBS_DAYS)
decay_rate_total = dN_Ni + dN_Co
sphere_area      = 4 * np.pi * DISTANCE_CM**2

print(f"Ni-56 decay rate at {T_OBS_DAYS} days: {dN_Ni:.3e} decays/s")
print(f"Co-56 decay rate at {T_OBS_DAYS} days: {dN_Co:.3e} decays/s")
print(f"Total decay rate:                       {decay_rate_total:.3e} decays/s")

# ── New bin edges ──────────────────────────────────────────────────────────────
new_edges = np.logspace(np.log10(E_MIN_KEV), np.log10(E_MAX_KEV), N_BINS + 1)

# ── Load, rebin, convert ───────────────────────────────────────────────────────
b_counts, b_widths = rebin(*load_combined("All_brems_spectrum_combined.txt"),   new_edges)
c_counts, c_widths = rebin(*load_combined("All_compton_spectrum_combined.txt"),  new_edges)
d_counts, d_widths = rebin(*load_combined("All_direct_escape_combined.txt"),     new_edges)

b_flux = to_flux(b_counts, b_widths, decay_rate_total, sphere_area)
c_flux = to_flux(c_counts, c_widths, decay_rate_total, sphere_area)
d_flux = to_flux(d_counts, d_widths, decay_rate_total, sphere_area)

day_label = f"{int(T_OBS_DAYS)} Days (W7)"

# ── Plots ──────────────────────────────────────────────────────────────────────
save_plot(
    "brems_compton_direct.png",
    f"Bremsstrahlung, Compton & Direct Escape at {day_label}",
    [(b_flux, 'red',   'Bremsstrahlung'),
     (c_flux, 'blue',  'Compton'),
     (d_flux, 'green', 'Direct Escape')],
)

save_plot(
    "brems_compton.png",
    f"Bremsstrahlung & Compton at {day_label}",
    [(b_flux, 'red',  'Bremsstrahlung'),
     (c_flux, 'blue', 'Compton')],
)

save_plot(
    "brems_direct.png",
    f"Bremsstrahlung & Direct Escape at {day_label}",
    [(b_flux, 'red',   'Bremsstrahlung'),
     (d_flux, 'green', 'Direct Escape')],
)

save_plot(
    "compton_direct.png",
    f"Compton & Direct Escape at {day_label}",
    [(c_flux, 'blue',  'Compton'),
     (d_flux, 'green', 'Direct Escape')],
)
