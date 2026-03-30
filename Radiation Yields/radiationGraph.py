import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt

# Folder where the CSV files are located
csv_folder = "."

# Find all files matching the pattern
csv_files = glob.glob(os.path.join(csv_folder, "brems_yield_*keV.csv"))

# Lists to hold the calculated data
energies = []
yields = []
errors = []

# Read each CSV and extract the values
for file in csv_files:
    try:
        # Extract energy from the filename
        match = re.search(r"brems_yield_([0-9.]+)keV\.csv", os.path.basename(file))
        if not match:
            print(f"Skipping file with invalid name format: {file}")
            continue
        energy = float(match.group(1))

        # Read file
        df = pd.read_csv(file, header=None)
        if df.shape[1] < 3:
            print(f"Skipping malformed file: {file}")
            continue

        avg_yield = df.iloc[0, 1]
        std_dev = df.iloc[0, 2]

        if avg_yield > 0:
            energies.append(energy)
            yields.append(avg_yield)
            errors.append(std_dev)
        else:
            print(f"Skipping {file}: avg_yield = {avg_yield}")

    except Exception as e:
        print(f"Failed to process {file}: {e}")

# Sort data by energy
if not energies:
    print("No valid data found.")
    exit()

sorted_data = sorted(zip(energies, yields, errors))
energies, yields, errors = zip(*sorted_data)

# PoEaP Radiation Yield dataset
poeap_data = {
    "Energy_keV": [10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0,
                   100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0,
                   1000.0, 1500.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0,
                   7000.0, 10000.0],
    "RadiationYield": [4.203e-04, 6.151e-04, 8.013e-04, 1.152e-03, 1.478e-03,
                       1.784e-03, 2.073e-03, 2.348e-03, 3.106e-03, 4.212e-03,
                       5.190e-03, 6.923e-03, 8.489e-03, 9.968e-03, 1.140e-02,
                       1.281e-02, 1.697e-02, 2.393e-02, 3.099e-02, 4.527e-02,
                       5.954e-02, 7.361e-02, 8.738e-02, 1.008e-01, 1.389e-01]
}
poeap_df = pd.DataFrame(poeap_data)

# Plotting
plt.figure(figsize=(10, 6))

# Blue line - Calculated Radiation Yield
plt.errorbar(energies, yields, yerr=errors, fmt='o-', capsize=5, color='blue', label="Calculated Radiation Yield")

# Red line - PoEaP Radiation Yield
plt.plot(poeap_df["Energy_keV"], poeap_df["RadiationYield"], 'o-', color='red', label="ICRU Report 37")

# Log-log scale and axis limits
plt.xscale('log')
plt.yscale('log')
plt.xlim(1e0, 1e4)
plt.ylim(1e-5, 1e-1)

# Labels and title
plt.title("Radiation Yield", fontsize=16)
plt.xlabel("Electron Energy (keV)", fontsize=14)
plt.ylabel("Radiation Yield", fontsize=14)

# Grid and legend
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)
plt.legend()
plt.tight_layout()

# Save and show
plt.savefig("radiation_yield_comparison.png", dpi=300)
print("Plot saved as 'radiation_yield_comparison.png'.")