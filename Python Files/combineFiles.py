import numpy as np
import glob
import os
import math

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

# === Combine info files ===
infoFiles = glob.glob('info_*.txt')

# Initialize counters
total_photons = 0
unmodified_escape = 0
modified_escape = 0
brems = 0
compton = 0
annihilation = 0
nickelDecays = 0
cobaltDecays = 0
totalDecayPhotonEnergy = 0.0
count158keV = 0
count812keV = 0
count847keV = 0
count1238keV = 0
escape158keV = 0
escape812keV = 0
escape847keV = 0
escape1238keV = 0

for f in infoFiles:
    with open(f, 'r') as file:
        for line in file:
            if 'Total Photons Tracked:' in line:
                total_photons += float(line.split(':')[1].strip())
            elif 'Unmodified Escape Count:' in line:
                unmodified_escape += float(line.split(':')[1].strip())
            elif 'Modified Escape Count:' in line:
                modified_escape += float(line.split(':')[1].strip())
            elif 'Bremsstrahlung:' in line:
                brems += float(line.split(':')[1].strip())
            elif 'Compton:' in line:
                compton += float(line.split(':')[1].strip())
            elif 'Annihilation:' in line:
                annihilation += float(line.split(':')[1].strip())
            elif 'Nickel Decays:' in line:
                nickelDecays += float(line.split(':')[1].strip())
            elif 'Cobalt Decays:' in line:
                cobaltDecays += float(line.split(':')[1].strip())
            elif 'Total Decay Photon Energy (MeV):' in line:
                totalDecayPhotonEnergy += float(line.split(':')[1].strip())
            elif '158.58 keV Decay Photons:' in line:
                count158keV += float(line.split(':')[1].strip())
            elif '811.85 keV Decay Photons:' in line:
                count812keV += float(line.split(':')[1].strip())
            elif '847 keV Decay Photons:' in line:
                count847keV += float(line.split(':')[1].strip())
            elif '1238.3 keV Decay Photons:' in line:
                count1238keV += float(line.split(':')[1].strip())
            elif '158.58 keV Direct Escape:' in line:
                escape158keV += float(line.split(':')[1].strip())
            elif '811.85 keV Direct Escape:' in line:
                escape812keV += float(line.split(':')[1].strip())
            elif '847 keV Direct Escape:' in line:
                escape847keV += float(line.split(':')[1].strip())
            elif '1238.3 keV Direct Escape:' in line:
                escape1238keV += float(line.split(':')[1].strip())

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
    out.write(f"Annihilation: {annihilation}\n\n")
    out.write(f"Nickel Decays: {nickelDecays}\n")
    out.write(f"Cobalt Decays: {cobaltDecays}\n\n")
    out.write(f"Total Decay Photon Energy (MeV): {totalDecayPhotonEnergy}\n")
    out.write(f"158.58 keV Decay Photons: {count158keV}\n")
    out.write(f"811.85 keV Decay Photons: {count812keV}\n")
    out.write(f"847 keV Decay Photons: {count847keV}\n")
    out.write(f"1238.3 keV Decay Photons: {count1238keV}\n")
    out.write(f"158.58 keV Direct Escape: {escape158keV}\n")
    out.write(f"811.85 keV Direct Escape: {escape812keV}\n")
    out.write(f"847 keV Direct Escape: {escape847keV}\n")
    out.write(f"1238.3 keV Direct Escape: {escape1238keV}\n")

    # Photon rates at each time point
    M_SUN_G  = 1.98847e33
    N_AVO    = 6.022e23
    A_NI56   = 55.94
    M_NI56_SOLAR = 0.58
    N0_Ni    = M_NI56_SOLAR * M_SUN_G * N_AVO / A_NI56   # 1.242e55
    lam_Ni   = math.log(2) / (6.075  * 86400)
    lam_Co   = math.log(2) / (77.27  * 86400)
    total_decays = nickelDecays + cobaltDecays

    # Rates at THIS simulation's time (from counts)
    import re as _re
    _gv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../globalVars.cc')
    with open(_gv_path) as _f:
        _src = _f.read()
    t_sim = float(_re.search(r'timeSinceSupernova\s*=\s*([0-9.]+)', _src).group(1))
    t_s   = t_sim * 86400
    R_Ni_sim = lam_Ni * N0_Ni * math.exp(-lam_Ni * t_s)
    N_Co_sim = (lam_Ni * N0_Ni / (lam_Co - lam_Ni)) * (math.exp(-lam_Ni * t_s) - math.exp(-lam_Co * t_s))
    R_tot_sim = R_Ni_sim + lam_Co * N_Co_sim

    out.write(f"\n--- Simulated Photon Line Rates at t={t_sim:.0f}d (photons/s) ---\n")
    out.write(f"N158keVLineCreated: {(count158keV / total_decays) * R_tot_sim:.6e}\n")
    out.write(f"N812keVLineCreated: {(count812keV / total_decays) * R_tot_sim:.6e}\n")
    out.write(f"N847keVLineCreated: {(count847keV / total_decays) * R_tot_sim:.6e}\n")
    out.write(f"N1238keVLineCreated: {(count1238keV / total_decays) * R_tot_sim:.6e}\n")

    DISTANCE_CM = 1.0 * 3.086e24  # 1 Mpc in cm
    sphere_area = 4 * math.pi * DISTANCE_CM**2
    out.write(f"\n--- Simulated Escape Fluxes at t={t_sim:.0f}d (ph/cm^2/s) ---\n")
    out.write(f"F158keVDirectEscape: {(escape158keV / total_decays) * R_tot_sim / sphere_area:.6e}\n")
    out.write(f"F812keVDirectEscape: {(escape812keV / total_decays) * R_tot_sim / sphere_area:.6e}\n")
    out.write(f"F847keVDirectEscape: {(escape847keV / total_decays) * R_tot_sim / sphere_area:.6e}\n")
    out.write(f"F1238keVDirectEscape: {(escape1238keV / total_decays) * R_tot_sim / sphere_area:.6e}\n")

# Optional: delete original files
for f in infoFiles:
    os.remove(f)

print("Files combined.")