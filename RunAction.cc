#include "RunAction.hh"
#include "globalVars.hh"
#include "G4EmCalculator.hh"
#include "G4Gamma.hh"
#include "G4SystemOfUnits.hh"
#include <cmath>

#include "G4Material.hh"
#include "G4NistManager.hh"
#include "G4Element.hh"
#include "G4Isotope.hh"

#include "G4Sphere.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4Box.hh"
#include "G4Electron.hh"
#include "G4EmCalculator.hh"
#include "G4Gamma.hh"
#include "G4Electron.hh"


void RunAction::BeginOfRunAction(const G4Run*) {

    if (!G4Threading::IsMasterThread()) return;

    // Computing optical depth/escape fraction
    G4EmCalculator emCal;
    G4double opticalDepth = 0.0;
    G4int numberOfZones = zoneMaterials.size();

    for (int zone = numberOfZones - 1; zone >= 0; zone--) {
        G4double opacity = emCal.ComputeCrossSectionPerVolume(1 * MeV, G4Gamma::GammaDefinition(), "compt", zoneMaterials[zone]);  
        opticalDepth = opticalDepth + (opacity * (outerRadii[zone] - innerRadii[zone]));
        G4cout << "Zone " << zone << ": Optical Depth: " << opticalDepth << G4endl;
    }

    // G4cout << "Energy (MeV): " << energy / MeV << G4endl;
    G4double directEscapeFraction = std::exp(-opticalDepth);
    G4cout << "Optical depth (tau) for " << particleEnergy << " MeV photon: " << opticalDepth << G4endl;
    G4cout << "Fraction of direct escape of gamma-line: " << directEscapeFraction << G4endl;

    start = std::chrono::high_resolution_clock::now(); // Start stopwatch
    G4cout << "Running simulation..." << G4endl;

}

void RunAction::EndOfRunAction(const G4Run*) {

    if (radiationYield) {

        if (!electronPhotonCounts.empty()) {
            G4double totalPhotons = 0;
            G4double totalEnergy = 0;

            for (const auto& [eID, count] : electronPhotonCounts) {
                totalPhotons += count;
                totalEnergy += electronInitialEnergies[eID];  // or sum of energy lost if you prefer
            }

            G4double avgPhotonsPerElectron = totalPhotons / electronPhotonCounts.size();
            G4double avgEnergyPerPhoton = totalEnergy / totalPhotons;

            G4cout << "Average number of photons created per electron: " << avgPhotonsPerElectron << G4endl;
            G4cout << "Average energy dispersion per photon: " << avgEnergyPerPhoton / keV << " keV" << G4endl;
        }

        if (!bremsPhotonEnergy.empty()) {
            for (const auto& [eID, bremE] : bremsPhotonEnergy) {
                G4double initE = electronInitialEnergies[eID];
                G4double yield = bremE / initE;

                // Round initial energy to nearest bin (e.g. 100 keV)
                G4double binE = std::round(initE / (100. * keV)) * (100. * keV);
                yieldByEnergyBin[binE].push_back(yield);
            }

            // Write to CSV file
            std::string fileName = "Radiation Yields/brems_yield_" + std::to_string(int(particleEnergy * 1000)) + "keV.csv";
            std::ofstream outFile(fileName);


            for (const auto& [binE, yields] : yieldByEnergyBin) {
                G4double sum = 0.0, sumSq = 0.0;
                for (auto y : yields) {
                    sum += y;
                    sumSq += y * y;
                }
                G4double avg = sum / yields.size();
                G4double stddev = std::sqrt(sumSq / yields.size() - avg * avg);

                avg = avg / eventCount;
                stddev = stddev / eventCount;

                outFile << binE / keV << "," << avg << "," << stddev << "\n";
            }

            outFile.close();
        }
    }
    
    if (G4Threading::IsMasterThread()) {

        G4cout << "Simulation complete." << G4endl;
        auto end = std::chrono::high_resolution_clock::now(); // End stopwatch

        std::chrono::duration<double> elapsed = end - start; // Calculate time
        std::cout << "Elapsed time: " << elapsed.count() << " seconds\n"; // Print time
    }
}