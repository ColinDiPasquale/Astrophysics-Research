import numpy as np
import glob
import os

# === Combine binned bremsstrahlung files ===
bremFiles = glob.glob('binned_brems_*.txt')

if bremFiles:
    combined_energy = None
    combined_counts = None

    for f in bremFiles:
        data = np.loadtxt(f)
        if combined_energy is None:
            combined_energy = data[:, 0]
            combined_counts = data[:, 1]
        else:
            combined_counts += data[:, 1]

    # Save combined bremsstrahlung data
    np.savetxt('All_brems_spectrum_combined.txt',
               np.column_stack((combined_energy, combined_counts)),
               header='Energy(keV) Counts', fmt='%.6e %.6e')

    # Remove original files
    for f in bremFiles:
        os.remove(f)
else:
    print("No bremsstrahlung files found.")


# === Combine binned Compton files ===
comptFiles = glob.glob('binned_compton_*.txt')

if comptFiles:
    combined_energy = None
    combined_counts = None

    for f in comptFiles:
        data = np.loadtxt(f)
        if combined_energy is None:
            combined_energy = data[:, 0]
            combined_counts = data[:, 1]
        else:
            combined_counts += data[:, 1]

    # Save combined Compton data
    np.savetxt('All_compton_spectrum_combined.txt',
               np.column_stack((combined_energy, combined_counts)),
               header='Energy(keV) Counts', fmt='%.6e %.6e')

    # Remove original files
    for f in comptFiles:
        os.remove(f)
else:
    print("No Compton files found.")

# === Combine binned everything files ===
everythingFiles = glob.glob('binned_everything_*.txt')

if everythingFiles:
    combined_energy = None
    combined_counts = None

    for f in everythingFiles:
        data = np.loadtxt(f)
        if combined_energy is None:
            combined_energy = data[:, 0]
            combined_counts = data[:, 1]
        else:
            combined_counts += data[:, 1]

    # Save combined Compton data
    np.savetxt('All_everything_spectrum_combined.txt',
               np.column_stack((combined_energy, combined_counts)),
               header='Energy(keV) Counts', fmt='%.6e %.6e')

    # Remove original files
    for f in everythingFiles:
        os.remove(f)
else:
    print("No everything files found.")

# === Combine binned Direct Escape files ===
directEscapeFiles = glob.glob('binned_direct_escape_*.txt')

if directEscapeFiles:
    combined_energy = None
    combined_counts = None

    for f in directEscapeFiles:
        data = np.loadtxt(f)
        if combined_energy is None:
            combined_energy = data[:, 0]
            combined_counts = data[:, 1]
        else:
            combined_counts += data[:, 1]

    # Save combined Compton data
    np.savetxt('All_direct_escape_combined.txt',
               np.column_stack((combined_energy, combined_counts)),
               header='Energy(keV) Counts', fmt='%.6e %.6e')

    # Remove original files
    for f in directEscapeFiles:
        os.remove(f)
else:
    print("No Direct Escape files found.")

# === Combine binned electron files ===
electronFiles = glob.glob('binned_electrons_*.txt')

if electronFiles:
    combined_energy = None
    combined_counts = None

    for f in electronFiles:
        data = np.loadtxt(f)
        if combined_energy is None:
            combined_energy = data[:, 0]
            combined_counts = data[:, 1]
        else:
            combined_counts += data[:, 1]

    # Save combined Compton data
    np.savetxt('All_electrons_combined.txt',
               np.column_stack((combined_energy, combined_counts)),
               header='Energy(keV) Counts', fmt='%.6e %.6e')

    # Remove original files
    for f in electronFiles:
        os.remove(f)
else:
    print("No Electron files found.")

# === Combine info files ===
infoFiles = glob.glob('info_*.txt')

# Initialize counters
total_photons = 0
unmodified_escape = 0
modified_escape = 0
brems = 0
compton = 0
annihilation = 0

for f in infoFiles:
    with open(f, 'r') as file:
        for line in file:
            if 'Total Photons Tracked:' in line:
                total_photons += int(line.split(':')[1].strip())
            elif 'Unmodified Escape Count:' in line:
                unmodified_escape += int(line.split(':')[1].strip())
            elif 'Modified Escape Count:' in line:
                modified_escape += int(line.split(':')[1].strip())
            elif 'Bremsstrahlung:' in line:
                brems += int(line.split(':')[1].strip())
            elif 'Compton:' in line:
                compton += int(line.split(':')[1].strip())
            elif 'Annihilation:' in line:
                annihilation += int(line.split(':')[1].strip())

# Compute derived value
direct_escape = unmodified_escape + modified_escape
total_listed = direct_escape + brems + annihilation

# Write combined info summary
with open('../Combined_info_summary.txt', 'w') as out:
    out.write(f"Total Photons Tracked: {total_photons}\n\n")
    out.write(f"Total Listed Photons: {total_listed}\n")
    out.write(f"Direct Escape Photons: {direct_escape}\n")
    out.write(f"Unmodified Escape Count: {unmodified_escape}\n")
    out.write(f"Modified Escape Count: {modified_escape}\n\n")
    out.write(f"Bremsstrahlung: {brems}\n")
    out.write(f"Compton: {compton}\n")
    out.write(f"Annihilation: {annihilation}\n")

# Optional: delete original files
for f in infoFiles:
    os.remove(f)

print("Files combined.")