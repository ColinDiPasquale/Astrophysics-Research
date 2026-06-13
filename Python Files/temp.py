import numpy as np
import matplotlib.pyplot as plt

# ── Physical constants ─────────────────────────────────────────────────────────
M_SUN_G    = 1.98847e33       # g / solar mass
N_AVO      = 6.022e23         # Avogadro's number
A_NI56     = 55.94            # atomic mass of Ni-56 (g/mol)
T_HALF_NI  = 6.075  * 86400  # Ni-56 half-life in seconds (6.075 days)
T_HALF_CO  = 77.27  * 86400  # Co-56 half-life in seconds (77.27 days)
LAMBDA_NI  = np.log(2) / T_HALF_NI
LAMBDA_CO  = np.log(2) / T_HALF_CO


def compute_decay_rates(M_Ni56_solar, t_days):
    """
    Returns (dN_Ni/dt, dN_Co/dt) in decays/s at time t_days,
    using the Bateman equations for the Ni56 -> Co56 -> Fe56 chain.

    M_Ni56_solar : initial Ni-56 mass in solar masses
    t_days       : time after explosion in days
    """
    N0 = M_Ni56_solar * M_SUN_G * N_AVO / A_NI56  # total initial Ni-56 nuclei
    t  = t_days * 86400                             # convert to seconds

    # Number of Ni-56 nuclei remaining
    N_Ni = N0 * np.exp(-LAMBDA_NI * t)

    # Number of Co-56 nuclei (Bateman)
    N_Co = N0 * (LAMBDA_NI / (LAMBDA_CO - LAMBDA_NI)) * \
           (np.exp(-LAMBDA_NI * t) - np.exp(-LAMBDA_CO * t))

    dN_Ni_dt = LAMBDA_NI * N_Ni   # Ni-56 decays/s
    dN_Co_dt = LAMBDA_CO * N_Co   # Co-56 decays/s

    return dN_Ni_dt, dN_Co_dt


def read_spectrum_data(input_file):
    """
    Reads spectrum data from file.
    Assumes two columns: lower bin edge (keV) and counts.
    """
    data = np.loadtxt(input_file, comments="#")
    lower_edges   = data[:, 0]
    photon_counts = data[:, 1]

    upper_edges        = np.empty_like(lower_edges)
    upper_edges[:-1]   = lower_edges[1:]
    if len(lower_edges) > 1:
        upper_edges[-1] = lower_edges[-1] + (lower_edges[-1] - lower_edges[-2])
    else:
        upper_edges[-1] = lower_edges[-1] + 1.0

    return lower_edges, upper_edges, photon_counts


def create_logarithmic_bins(min_energy, max_energy, n_bins):
    return np.logspace(np.log10(min_energy), np.log10(max_energy), n_bins + 1)


def rebin_photon_counts(lower_edges, upper_edges, photon_counts, new_bin_edges):
    centers = 0.5 * (lower_edges + upper_edges)

    new_counts, _ = np.histogram(
        centers,
        bins=new_bin_edges,
        weights=photon_counts
    )

    new_widths = np.diff(new_bin_edges)
    return new_counts, new_widths


def to_flux(counts, widths, n_events, decay_rate, sphere_area):
    """
    Converts raw Geant4 tallies to flux in photons/s/keV/cm^2.

    counts      : rebinned photon counts (raw tally)
    widths      : bin widths in keV
    n_events    : number of decay events simulated in Geant4
    decay_rate  : physical decay rate at t_obs (decays/s), Ni + Co combined
    sphere_area : 4 * pi * distance^2 in cm^2
    """
    return (counts / n_events) * (decay_rate / widths) / sphere_area


def plot_three_spectra(edges, b_flux, c_flux, d_flux):
    plt.figure(figsize=(10, 6))

    plt.step(edges[:-1], b_flux, where='post', color='red',   label='Bremsstrahlung')
    plt.step(edges[:-1], c_flux, where='post', color='blue',  label='Compton')
    plt.step(edges[:-1], d_flux, where='post', color='green', label='Direct Escape')

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Energy (keV)')
    plt.ylabel(r'Flux (photons s$^{-1}$ keV$^{-1}$ cm$^{-2}$)')
    plt.title('Brems, Compton, & Direct Escape at 40 Days (W7)')

    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig('../bremsAndComptAndDirect.png', dpi=300)

    print("Plot saved as 'bremsAndComptAndDirect.png'")


def main():
    # ── Simulation parameters ──────────────────────────────────────────────────
    N_EVENTS     = 1e7          # number of decay events simulated in Geant4
    M_NI56_SOLAR = 0.58        # W7 Ni-56 ejecta mass in solar masses
    T_OBS_DAYS   = 40.0        # time of observation in days
    DISTANCE_CM  = 3.086e24    # 1 Mpc in cm

    # ── Derived quantities ─────────────────────────────────────────────────────
    dN_Ni_dt, dN_Co_dt = compute_decay_rates(M_NI56_SOLAR, T_OBS_DAYS)
    decay_rate_total    = dN_Ni_dt + dN_Co_dt
    sphere_area         = 4 * np.pi * DISTANCE_CM**2

    print(f"Ni-56 decay rate at {T_OBS_DAYS} days : {dN_Ni_dt:.3e} decays/s")
    print(f"Co-56 decay rate at {T_OBS_DAYS} days : {dN_Co_dt:.3e} decays/s")
    print(f"Total decay rate                       : {decay_rate_total:.3e} decays/s")
    print(f"Sphere area at 1 Mpc                   : {sphere_area:.3e} cm^2")

    # ── Binning ────────────────────────────────────────────────────────────────
    new_edges = create_logarithmic_bins(1.0, 5011.8724, 187)

    # ── Load & rebin ───────────────────────────────────────────────────────────
    b_lo, b_hi, b_raw = read_spectrum_data('All_brems_spectrum_combined.txt')
    b_counts, b_widths = rebin_photon_counts(b_lo, b_hi, b_raw, new_edges)

    c_lo, c_hi, c_raw = read_spectrum_data('All_compton_spectrum_combined.txt')
    c_counts, c_widths = rebin_photon_counts(c_lo, c_hi, c_raw, new_edges)

    d_lo, d_hi, d_raw = read_spectrum_data('All_direct_escape_combined.txt')
    d_counts, d_widths = rebin_photon_counts(d_lo, d_hi, d_raw, new_edges)

    # ── Convert to flux ────────────────────────────────────────────────────────
    b_flux = to_flux(b_counts, b_widths, N_EVENTS, decay_rate_total, sphere_area)
    c_flux = to_flux(c_counts, c_widths, N_EVENTS, decay_rate_total, sphere_area)
    d_flux = to_flux(d_counts, d_widths, N_EVENTS, decay_rate_total, sphere_area)

    plot_three_spectra(new_edges, b_flux, c_flux, d_flux)


if __name__ == "__main__":
    main()