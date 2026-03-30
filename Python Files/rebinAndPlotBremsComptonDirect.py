import numpy as np
import matplotlib.pyplot as plt

def read_spectrum_data(input_file):
    """
    Reads spectrum data from file.
    Assumes two columns: lower bin edge (keV) and counts.
    """
    data = np.loadtxt(input_file, comments="#")
    lower_edges = data[:, 0]
    photon_counts = data[:, 1]

    # Create upper edges
    upper_edges = np.empty_like(lower_edges)
    upper_edges[:-1] = lower_edges[1:]
    if len(lower_edges) > 1:
        upper_edges[-1] = lower_edges[-1] + (lower_edges[-1] - lower_edges[-2])
    else:
        upper_edges[-1] = lower_edges[-1] + 1.0

    return lower_edges, upper_edges, photon_counts


def create_logarithmic_bins(min_energy, max_energy, n_bins):
    return np.logspace(np.log10(min_energy), np.log10(max_energy), n_bins + 1)


def rebin_photon_counts(lower_edges, upper_edges, photon_counts, new_bin_edges):
    centers = 0.5 * (lower_edges + upper_edges)
    widths = upper_edges - lower_edges

    # Preserve total counts
    new_counts, _ = np.histogram(
        centers,
        bins=new_bin_edges,
        weights=photon_counts
    )

    new_widths = np.diff(new_bin_edges)
    return new_counts, new_widths


def plot_three_spectra(edges1, counts1, widths1, label1,
                       edges2, counts2, widths2, label2,
                       edges3, counts3, widths3, label3):

    y1 = counts1 / widths1
    y2 = counts2 / widths2
    y3 = counts3 / widths3

    plt.figure(figsize=(10, 6))

    plt.step(edges1[:-1], y1, where='post', color='red', label=label1)
    plt.step(edges2[:-1], y2, where='post', color='blue', label=label2)
    plt.step(edges3[:-1], y3, where='post', color='green', label=label3)

    plt.xscale('log')
    plt.yscale('log')
    plt.ylim(1e0, 1e4)
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts / Bin Width')
    plt.title('Brems, Compton, & Direct Escape at 40 Days')

    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig('../bremsAndComptAndDirect.png', dpi=300)

    print("Plot saved as 'bremsAndComptAndDirect.png'")


def main():
    # Parameters
    min_energy = 1.0
    max_energy = 5011.8724
    n_bins = 187

    # Create common bin edges
    new_edges = create_logarithmic_bins(min_energy, max_energy, n_bins)

    # --- Bremsstrahlung ---
    b_lower, b_upper, b_counts = read_spectrum_data('All_brems_spectrum_combined.txt')
    b_counts, b_widths = rebin_photon_counts(b_lower, b_upper, b_counts, new_edges)

    # --- Compton ---
    c_lower, c_upper, c_counts = read_spectrum_data('All_compton_spectrum_combined.txt')
    c_counts, c_widths = rebin_photon_counts(c_lower, c_upper, c_counts, new_edges)

    # --- Direct Escape ---
    d_lower, d_upper, d_counts = read_spectrum_data('All_direct_escape_combined.txt')
    d_counts, d_widths = rebin_photon_counts(d_lower, d_upper, d_counts, new_edges)

    # Plot all three
    plot_three_spectra(
        new_edges, b_counts, b_widths, "Bremsstrahlung",
        new_edges, c_counts, c_widths, "Compton",
        new_edges, d_counts, d_widths, "Direct Escape"
    )


if __name__ == "__main__":
    main()