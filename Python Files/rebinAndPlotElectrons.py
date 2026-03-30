import numpy as np
import matplotlib.pyplot as plt

def read_compton_data(input_file):
    """
    Reads the Brems spectrum data from the input file.
    
    The input file is assumed to have two columns:
      - First column: lower bin edges.
      - Second column: photon counts.
    
    The upper bin edges are derived by taking the next lower edge 
    as the upper edge of the current bin. For the last bin, we assume 
    the same bin width as the previous bin.
    
    :param input_file: Path to the input file.
    :return: Arrays of lower bin edges, upper bin edges, and photon counts.
    """
    data = np.loadtxt(input_file)
    lower_edges = data[:, 0]
    photon_counts = data[:, 1]
    
    # Create an array for upper edges
    upper_edges = np.empty_like(lower_edges)
    # For bins 0 to N-2, upper edge = next lower edge
    upper_edges[:-1] = lower_edges[1:]
    # For the last bin, assume the same width as the previous bin
    if len(lower_edges) > 1:
        bin_width = lower_edges[-1] - lower_edges[-2]
        upper_edges[-1] = lower_edges[-1] + bin_width
    else:
        upper_edges[-1] = lower_edges[-1] + 1.0  # Fallback if only one bin exists

    return lower_edges, upper_edges, photon_counts

def create_logarithmic_bins(min_energy, max_energy, n_bins):
    """
    Creates logarithmic bin edges between min_energy and max_energy.
    
    :param min_energy: Minimum energy (keV)
    :param max_energy: Maximum energy (keV)
    :param n_bins: Number of logarithmic bins.
    :return: Array of bin edges.
    """
    return np.logspace(np.log10(min_energy), np.log10(max_energy), n_bins + 1)

def rebin_photon_counts(lower_edges, upper_edges, photon_counts, new_bin_edges):
    """
    Rebins the photon counts into new logarithmic bins.
    
    Original bin centers and widths are computed from lower_edges and upper_edges.
    The counts are normalized by the original bin widths and then rebinned.
    
    :param lower_edges: Original lower bin edges.
    :param upper_edges: Original upper bin edges.
    :param photon_counts: Photon counts in original bins.
    :param new_bin_edges: New bin edges for rebinning.
    :return: Rebinned photon counts and new bin widths.
    """
    # Compute centers and widths of original bins
    original_bin_centers = (lower_edges + upper_edges) / 2.0
    original_bin_widths = upper_edges - lower_edges

    # Normalize counts to get counts per keV in each original bin
    normalized_counts = photon_counts / original_bin_widths

    # Rebin the data using a histogram weighted by the original bin widths
    new_photon_counts, _ = np.histogram(
        original_bin_centers, bins=new_bin_edges, weights=normalized_counts * original_bin_widths
    )

    new_bin_widths = np.diff(new_bin_edges)
    
    return new_photon_counts, new_bin_widths

def write_rebinned_data(output_file, bin_edges, photon_counts, bin_widths):
    """
    Writes the rebinned photon data to an output file.
    
    Each line in the output file contains the lower edge, upper edge, 
    and the photon counts divided by the bin width.
    
    :param output_file: Path to the output file.
    :param bin_edges: New bin edges.
    :param photon_counts: Rebinned photon counts.
    :param bin_widths: Widths of the new bins.
    """
    with open(output_file, 'w') as file:
        for i in range(len(photon_counts)):
            lower_edge = bin_edges[i]
            upper_edge = bin_edges[i + 1]
            count_per_width = photon_counts[i] / bin_widths[i] if bin_widths[i] != 0 else 0
            file.write(f"{lower_edge:.6e} {upper_edge:.6e} {count_per_width:.6e}\n")

def plot_histogram(bin_edges, photon_counts, bin_widths):
    """
    Plots a histogram of photon counts per bin width versus energy.
    
    :param bin_edges: New bin edges.
    :param photon_counts: Rebinned photon counts.
    :param bin_widths: Widths of the new bins.
    """
    counts_per_width = photon_counts / bin_widths
    plt.figure(figsize=(10, 6))
    plt.step(bin_edges[:-1], counts_per_width, where='post', color='blue', 
             label='Photon Counts / Bin Width')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Photon Count / Bin Width')
    plt.title('Rebinned All Electrons Spectrum')
    plt.grid(True, which='both', ls='--', lw=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig('rebinned_electrons_spectrum.png', dpi=300)
    print("Plot saved as 'rebinned_electrons_spectrum.png'")

def main():
    input_file = 'All_electrons_combined.txt'
    output_file = '187binned_electrons.dat'
    
    # Parameters for rebinning
    min_energy = 1.0         # in keV
    max_energy = 5011.8724   # in keV
    n_bins = 187             # target number of bins

    # Read original data
    lower_edges, upper_edges, photon_counts = read_compton_data(input_file)

    # Create new logarithmic bins
    new_bin_edges = create_logarithmic_bins(min_energy, max_energy, n_bins)

    # Rebin the photon counts into the new bins
    rebinned_counts, new_bin_widths = rebin_photon_counts(lower_edges, upper_edges, photon_counts, new_bin_edges)

    # Write the rebinned data to an output file
    write_rebinned_data(output_file, new_bin_edges, rebinned_counts, new_bin_widths)

    # Plot the rebinned spectrum
    plot_histogram(new_bin_edges, rebinned_counts, new_bin_widths)

if __name__ == "__main__":
    main()

