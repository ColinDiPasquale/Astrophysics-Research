import numpy as np
import matplotlib.pyplot as plt

def read_compton_data(input_file):
    """
    Reads the Compton spectrum data from the input file.
    
    The input file is assumed to have two columns:
      - First column: lower bin edges.
      - Second column: photon counts.
    
    The upper bin edges are derived by taking the next lower edge 
    as the upper edge of the current bin. For the last bin, we assume 
    the same bin width as the previous bin.
    """
    data = np.loadtxt(input_file)
    lower_edges = data[:, 0]
    photon_counts = data[:, 1]
    
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

def write_rebinned_data(output_file, bin_edges, photon_counts, bin_widths):
    with open(output_file, 'w') as file:
        for i in range(len(photon_counts)):
            lower_edge = bin_edges[i]
            upper_edge = bin_edges[i + 1]
            count_per_width = photon_counts[i] / bin_widths[i] if bin_widths[i] != 0 else 0
            file.write(f"{lower_edge:.6e} {upper_edge:.6e} {count_per_width:.6e}\n")

def plot_histogram(bin_edges, photon_counts, bin_widths):
    counts_per_width = photon_counts / bin_widths
    plt.figure(figsize=(10, 6))
    plt.step(bin_edges[:-1], counts_per_width, where='post', color='blue', label='Compton Counts / Bin Width')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Photon Count / Bin Width')
    plt.title('Full Photon Spectrum at 40 Days')
    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig('../full_spectrum.png', dpi=300)
    print("Plot saved as 'full_spectrum.png'")

def main():
    input_file = 'All_everything_spectrum_combined.txt'  # change to your actual input file
    output_file = '187binned_everything.dat'
    
    min_energy = 1.0         # in keV
    max_energy = 5011.8724   # in keV
    n_bins = 187

    lower_edges, upper_edges, photon_counts = read_compton_data(input_file)
    new_bin_edges = create_logarithmic_bins(min_energy, max_energy, n_bins)
    rebinned_counts, new_bin_widths = rebin_photon_counts(lower_edges, upper_edges, photon_counts, new_bin_edges)
    write_rebinned_data(output_file, new_bin_edges, rebinned_counts, new_bin_widths)
    plot_histogram(new_bin_edges, rebinned_counts, new_bin_widths)

if __name__ == "__main__":
    main()