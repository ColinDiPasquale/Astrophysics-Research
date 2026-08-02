"""
Overplot the simulated (Compton-only) optical depth table against the
tauW7 reference data (total attenuation, 177-zone W7 model), enclosed
mass on the x-axis and tau on the y-axis, one panel per energy.

For each "Optical Depths/t<day>d/" folder that has both
optical_depth_table_t<day>d.txt (written by RunAction) and a tauW7.<day>
reference file, saves one PNG (all 15 energies as subplots) back into
that same day folder.

Run manually, or automatically at the end of a simulation (see main.cc).
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import re

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, "..")
TAU_DIR     = os.path.join(PROJECT_DIR, "Optical Depths")

# Column order as documented in Optical Depths/taudatmod.txt:
#   izn GMrsun taup3keV taup6keV tau1keV tau2keV tau5keV tau10keV tau20keV
#   tau50keV tau100keV tau200keV tau500keV tau847keV tau1000keV tau1238keV tau2000keV
# Our own optical_depth_table files use the same energy order (just labeled
# tau<E>keV instead of taup<E>keV for the first two), so columns line up
# positionally between the two file formats.
ENERGIES_KEV = [3, 6, 1, 2, 5, 10, 20, 50, 100, 200, 500, 847, 1000, 1238, 2000]


def load_sim_table(path):
    return np.genfromtxt(path, names=True)


def load_reference(path):
    data = np.loadtxt(path)
    # Drop the innermost row (menc_Msun == 0, i.e. r = 0): tau there is a
    # numerical artifact (~1e14) that dwarfs every other point on a log
    # axis and isn't physically meaningful for a tau-vs-enclosed-mass plot.
    data = data[data[:, 1] > 0]
    menc = data[:, 1]
    tau_cols = {e: data[:, 2 + i] for i, e in enumerate(ENERGIES_KEV)}
    return menc, tau_cols


def plot_day(day, sim_path, ref_path, out_path):
    sim = load_sim_table(sim_path)
    ref_menc, ref_tau = load_reference(ref_path)

    fig, axes = plt.subplots(5, 3, figsize=(15, 18))
    axes = axes.ravel()

    for i, e in enumerate(ENERGIES_KEV):
        ax = axes[i]
        sim_tau = sim[f"tau{e}keV"]

        ax.plot(sim["menc_Msun"], sim_tau, 'o-', color="tab:blue",
                label="Simulation (Compton only)", ms=3, lw=1.2)
        ax.plot(ref_menc, ref_tau[e], color="tab:orange",
                label="tauW7 reference (total)", lw=1.2, ls="--")

        ax.set_yscale('log')
        ax.set_title(f"{e} keV", fontsize=11)
        ax.set_xlabel(r"Enclosed mass (M$_\odot$)", fontsize=9)
        ax.set_ylabel(r"$\tau$", fontsize=9)
        ax.grid(True, which='both', ls='--', lw=0.4)

    axes[0].legend(fontsize=8, loc="best")
    fig.suptitle(f"Optical depth vs enclosed mass — W7, t = {day} days", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"  Saved: {out_path}")


def main():
    if not os.path.isdir(TAU_DIR):
        print(f"No such directory: {TAU_DIR}")
        return

    for entry in sorted(os.listdir(TAU_DIR)):
        day_dir = os.path.join(TAU_DIR, entry)
        m = re.fullmatch(r"t(\d+)d", entry)
        if not m or not os.path.isdir(day_dir):
            continue
        day = m.group(1)

        sim_path = os.path.join(day_dir, f"optical_depth_table_t{day}d.txt")
        ref_path = os.path.join(day_dir, f"tauW7.{day}")
        if not os.path.isfile(sim_path) or not os.path.isfile(ref_path):
            continue

        print(f"t = {day} days")
        out_path = os.path.join(day_dir, f"tau_vs_menc_t{day}d.png")
        plot_day(day, sim_path, ref_path, out_path)


if __name__ == "__main__":
    main()
