import matplotlib.pyplot as plt

# Raw data block
data = """
6.187E-04   2.48430e+12
1.785E-02   2.34505e+12
5.603E-02   6.69626e+12
8.879E-02   4.53323e+12
1.047E-01   4.147667e+12
1.326E-01   8.89876e+12
1.907E-01   1.64581e+13
2.334E-01   7.60875e+12
3.068E-01   1.61362e+13
3.410E-01   2.19200e+13
4.049E-01   2.27312e+13
4.524E-01   2.87251e+13
4.953E-01   2.07539e+13
5.551E-01   2.58448e+13
6.222E-01   2.43207e+13
6.991E-01   4.91717e+13
7.557E-01   4.81064e+13
7.985E-01   6.41099e+13
8.461E-01   7.20816e+13
9.046E-01   8.04365e+13
9.738E-01   1.17305e+14
1.013E+00   1.22377e+14
1.055E+00   1.32974e+14
1.100E+00   1.79979e+14
1.143E+00   2.24659e+14
1.175E+00   1.43411e+14
1.207E+00   1.81793e+14
1.241E+00   2.12739e+14
1.280E+00   1.68037e+14
1.319E+00   1.82945e+14
1.356E+00   2.93136e+15
1.370E+00   8.74224e+15
1.376E+00   1.28822e+16
1.377E+00   4.06196e+16
1.377E+00   1.50515e+17
1.377E+00   1.54875e+18
"""

# Parse data
density = []
radius = []

for line in data.strip().split("\n"):
    d, r = line.split()
    density.append(float(d))
    radius.append(float(r))

# Plot
plt.figure(figsize=(10, 6))
plt.plot(density, radius, marker='o', linestyle='-', color='blue')
plt.xlabel("Interior Radial Mass")
plt.ylabel("Electron Range / Radius")
plt.yscale('log')
plt.title("Range of Electrons in W7 Model")
plt.grid(True)
plt.tight_layout()

# Save to file
plt.savefig("electron_range_spectrum.png", dpi=300)
plt.close()

print("Plot saved to 'electron_range_spectrum.png'")
