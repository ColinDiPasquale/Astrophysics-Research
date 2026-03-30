import numpy as np
import matplotlib.pyplot as plt

def read_spectrum_data(input_file):
    """
    Reads the spectrum data from the input file.
    Assumes two columns: lower bin edge (keV) and counts.
    """
    data = np.loadtxt(input_file, comments="#")
    lower_edges = data[:, 0]
    photon_counts = data[:, 1]

    # Create upper edges
    upper_edges = np.empty_like(lower_edges)
    upper_edges[:-1] = lower_edges[1:]
    if len(lower_edges) > 1:
        bin_width = lower_edges[-1] - lower_edges[-2]
        upper_edges[-1] = lower_edges[-1] + bin_width
    else:
        upper_edges[-1] = lower_edges[-1] + 1.0

    return lower_edges, upper_edges, photon_counts

def create_logarithmic_bins(min_energy, max_energy, n_bins):
    return np.logspace(np.log10(min_energy), np.log10(max_energy), n_bins + 1)

def rebin_photon_counts(lower_edges, upper_edges, photon_counts, new_bin_edges):
    original_bin_centers = (lower_edges + upper_edges) / 2.0
    original_bin_widths = upper_edges - lower_edges
    normalized_counts = photon_counts / original_bin_widths

    new_photon_counts, _ = np.histogram(
        original_bin_centers, bins=new_bin_edges, weights=normalized_counts * original_bin_widths
    )

    new_bin_widths = np.diff(new_bin_edges)
    return new_photon_counts, new_bin_widths

def plot_two_spectra(bin_edges_brems, counts_brems, widths_brems,
                     bin_edges_compton, counts_compton, widths_compton):
    counts_per_width_brems = counts_brems / widths_brems
    counts_per_width_compton = counts_compton / widths_compton

    plt.figure(figsize=(10, 6))
    plt.step(bin_edges_brems[:-1], counts_per_width_brems, where='post', color='red', label='Bremsstrahlung')
    plt.step(bin_edges_compton[:-1], counts_per_width_compton, where='post', color='green', label='Direct Escape')

    plt.xscale('log')
    plt.yscale('log')
    plt.ylim(1e0, 1e4)
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts / Bin Width')
    plt.title('Bremsstrahlung and Direct Escape at 40 days')
    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig('../bremsAndDirect.png', dpi=300)
    print("Plot saved as 'bremsAndDirect.png'")

def main():
    # Parameters
    min_energy = 1.0
    max_energy = 5011.8724
    n_bins = 187

    # Process Bremsstrahlung
    brems_lower, brems_upper, brems_counts = read_spectrum_data('All_brems_spectrum_combined.txt')
    bin_edges_brems = create_logarithmic_bins(min_energy, max_energy, n_bins)
    rebinned_counts_brems, widths_brems = rebin_photon_counts(brems_lower, brems_upper, brems_counts, bin_edges_brems)

    # Process Compton Rays
    compton_lower, compton_upper, compton_counts = read_spectrum_data('All_direct_escape_combined.txt')
    bin_edges_compton = create_logarithmic_bins(min_energy, max_energy, n_bins)
    rebinned_counts_compton, widths_compton = rebin_photon_counts(compton_lower, compton_upper, compton_counts, bin_edges_compton)

    # Plot together
    plot_two_spectra(bin_edges_brems, rebinned_counts_brems, widths_brems,
                     bin_edges_compton, rebinned_counts_compton, widths_compton)

if __name__ == "__main__":
    main()
