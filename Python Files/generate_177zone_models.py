"""
Generate the 177-zone analog of the model52_W7_20shells_CSiNi56_t<N>d.dat
files, evolving the raw 177-zone W7 model (Supernova Models/177 Zones/) to
each simulation timestep under homologous expansion with shell-mass
conservation -- same method used for the 20-zone model.

Source data: Supernova Models/177 Zones/model52_W7_columns.dat
  columns: rzo_cm vel_cm_s dns_g_cc <29 isotope mass fractions>
  isotope order: H He C N O Ne Mg Si S Ar Ca Ti Cr Fe56 Co56 Ni56 Ni57
                 Co57 Fe57 B F Fe58 Na Al P Cl K Sc V

Composition buckets (partition of the 29 tracked isotopes, Ni56 isolated
for radioactive-decay physics, matching the 20-zone scheme):
  C-bucket  (unburned / lightly-processed): H He C N O Ne Mg Na Al B F P
  Si-bucket (explosive Si/O burning + stable iron group): Si S Ar Ca Ti Cr
             Cl K Sc V Fe56 Co56 Ni57 Co57 Fe57 Fe58
  Ni56      (isolated)

Output: Supernova Models/model52_W7_177shells_CSiNi56_t<N>d.dat
"""

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Supernova Models" / "177 Zones" / "model52_W7_columns.dat"
OUT_DIR = ROOT / "Supernova Models"

T0_DAYS = 2.3148148148148149e-04
DAYS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 200]
SECONDS_PER_DAY = 86400.0
MSUN = 1.989e33

ISOTOPES = [
    "H", "He", "C", "N", "O", "Ne", "Mg", "Si", "S", "Ar", "Ca", "Ti", "Cr",
    "Fe56", "Co56", "Ni56", "Ni57", "Co57", "Fe57", "B", "F", "Fe58", "Na",
    "Al", "P", "Cl", "K", "Sc", "V",
]

C_BUCKET = ["H", "He", "C", "N", "O", "Ne", "Mg", "Na", "Al", "B", "F", "P"]
SI_BUCKET = [
    "Si", "S", "Ar", "Ca", "Ti", "Cr", "Cl", "K", "Sc", "V",
    "Fe56", "Co56", "Ni57", "Co57", "Fe57", "Fe58",
]
NI56 = "Ni56"

assert set(C_BUCKET) | set(SI_BUCKET) | {NI56} == set(ISOTOPES)
assert len(C_BUCKET) + len(SI_BUCKET) + 1 == len(ISOTOPES)


def main():
    data = np.loadtxt(SRC)
    n = data.shape[0]

    r0 = data[:, 0]            # rzo_cm at t0
    v = data[:, 1]              # vel_cm_s (time-independent, homologous)
    rho0 = data[:, 2]           # dns_g_cc at t0
    isotope_cols = {name: data[:, 3 + i] for i, name in enumerate(ISOTOPES)}

    # Shell mass from t0 snapshot, conserved for all later times.
    r_in0 = np.concatenate(([0.0], r0[:-1]))
    vol0 = 4.0 / 3.0 * np.pi * (r0**3 - r_in0**3)
    shell_mass_g = rho0 * vol0
    menc_msun = np.cumsum(shell_mass_g) / MSUN

    total_tracked = sum(isotope_cols.values())
    x_c = sum(isotope_cols[e] for e in C_BUCKET) / total_tracked
    x_si = sum(isotope_cols[e] for e in SI_BUCKET) / total_tracked
    x_ni56 = isotope_cols[NI56] / total_tracked

    v_in = np.concatenate(([0.0], v[:-1]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for t_days in DAYS:
        t_sec = t_days * SECONDS_PER_DAY
        r_out = v * t_sec
        r_in = v_in * t_sec
        vol = 4.0 / 3.0 * np.pi * (r_out**3 - r_in**3)
        rho = shell_mass_g / vol

        out_path = OUT_DIR / f"model52_W7_177shells_CSiNi56_t{t_days}d.dat"
        with open(out_path, "w") as f:
            f.write("# 177-shell model evolved to new time with shell-mass conservation\n")
            f.write(f"# t0_days = {T0_DAYS!r}\n")
            f.write(f"# t_days  = {float(t_days):.16e}\n")
            f.write("# Shell masses: m_i = (Menc_out - Menc_in) * Msun\n")
            f.write("# Boundary evolution: r_out uses v_out; r_in uses previous shell v_out (continuous boundaries)\n")
            f.write("# rho(t) = m_i / [4/3 pi (r_out^3 - r_in^3)]\n")
            f.write("# Columns:\tshell\trzo_cm\tvel_cm_s\trho_g_cc\tX_C_bucket\tX_Si_bucket\tX_Ni56\tMenc_Msun\n")
            f.write("shell\trzo_cm\tvel_cm_s\trho_g_cc\tX_C_bucket\tX_Si_bucket\tX_Ni56\tMenc_Msun\n")
            for i in range(n):
                f.write(
                    f"{i + 1}\t{r_out[i]:.8e}\t{v[i]:.8e}\t{rho[i]:.8e}\t"
                    f"{x_c[i]:.8e}\t{x_si[i]:.8e}\t{x_ni56[i]:.8e}\t{menc_msun[i]:.8e}\n"
                )
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
