#include "RunAction.hh"
#include "globalVars.hh"

#include "G4EmCalculator.hh"
#include "G4Gamma.hh"
#include "G4SystemOfUnits.hh"
#include "G4Threading.hh"

#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <vector>

void RunAction::BeginOfRunAction(const G4Run*) {
    if (!G4Threading::IsMasterThread()) return;

    G4EmCalculator emCal;
    G4double opticalDepth = 0.0;
    G4int numberOfZones = zoneMaterials.size();

    for (int zone = numberOfZones - 1; zone >= 0; zone--) {
        G4double opacity = emCal.ComputeCrossSectionPerVolume(1 * MeV, G4Gamma::GammaDefinition(), "compt", zoneMaterials[zone]);
        opticalDepth += opacity * (outerRadii[zone] - innerRadii[zone]);
        G4cout << "Zone " << zone << ": Optical Depth: " << opticalDepth << G4endl;
    }

    G4double directEscapeFraction = std::exp(-opticalDepth);
    G4cout << "Optical depth (tau) at 1 MeV: " << opticalDepth << G4endl;
    G4cout << "Direct escape fraction: " << directEscapeFraction << G4endl;

    WriteOpticalDepthTable();

    start = std::chrono::high_resolution_clock::now();
    G4cout << "Running simulation..." << G4endl;
}

// Writes, per zone, the Compton-scattering optical depth from that zone
// out to the surface (i.e. what a photon born there must traverse to
// escape), at a fixed grid of energies. Zone 0 is innermost. One file is
// written per simulated time (timeSinceSupernova) so re-running at a
// different day doesn't clobber earlier tables.
void RunAction::WriteOpticalDepthTable() {
    static const std::vector<G4int> tableEnergiesKeV = {
        3, 6, 1, 2, 5, 10, 20, 50, 100, 200, 500, 847, 1000, 1238, 2000
    };
    constexpr int colWidth = 16;

    G4EmCalculator emCal;
    G4int numberOfZones = zoneMaterials.size();
    std::vector<std::vector<G4double>> cumulativeTau(
        numberOfZones, std::vector<G4double>(tableEnergiesKeV.size(), 0.0));

    for (size_t iE = 0; iE < tableEnergiesKeV.size(); ++iE) {
        G4double energy = tableEnergiesKeV[iE] * keV;
        G4double opticalDepth = 0.0;
        for (int zone = numberOfZones - 1; zone >= 0; zone--) {
            G4double opacity = emCal.ComputeCrossSectionPerVolume(energy, G4Gamma::GammaDefinition(), "compt", zoneMaterials[zone]);
            opticalDepth += opacity * (outerRadii[zone] - innerRadii[zone]);
            cumulativeTau[zone][iE] = opticalDepth;
        }
    }

    std::string dayLabel = "t" + std::to_string((int)timeSinceSupernova) + "d";
    std::filesystem::path outDir = std::filesystem::path("/home/cdipasq/AstrophysicsResearch/Optical Depths") / dayLabel;
    std::filesystem::create_directories(outDir);
    std::string fileName = "optical_depth_table_" + dayLabel + ".txt";
    std::ofstream out(outDir / fileName);

    out << std::left << std::setw(6) << "izn"
        << std::right << std::setw(colWidth) << "menc_Msun"
        << std::right << std::setw(colWidth) << "radius_cm";
    for (G4int e : tableEnergiesKeV) {
        std::ostringstream label;
        label << "tau" << e << "keV";
        out << std::right << std::setw(colWidth) << label.str();
    }
    out << "\n";

    out << std::scientific << std::setprecision(6);
    for (int zone = 0; zone < numberOfZones; zone++) {
        out << std::left << std::setw(6) << zone
            << std::right << std::setw(colWidth) << zoneEnclosedMassMsun[zone]
            << std::right << std::setw(colWidth) << outerRadii[zone] / cm;
        for (size_t iE = 0; iE < tableEnergiesKeV.size(); ++iE) {
            out << std::right << std::setw(colWidth) << cumulativeTau[zone][iE];
        }
        out << "\n";
    }
}

void RunAction::EndOfRunAction(const G4Run*) {
    if (!G4Threading::IsMasterThread()) return;

    G4cout << "Simulation complete." << G4endl;
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    G4cout << "Elapsed time: " << elapsed.count() << " seconds" << G4endl;
}
