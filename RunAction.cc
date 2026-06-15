#include "RunAction.hh"
#include "globalVars.hh"

#include "G4EmCalculator.hh"
#include "G4Gamma.hh"
#include "G4SystemOfUnits.hh"
#include "G4Threading.hh"

#include <cmath>

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

    start = std::chrono::high_resolution_clock::now();
    G4cout << "Running simulation..." << G4endl;
}

void RunAction::EndOfRunAction(const G4Run*) {
    if (!G4Threading::IsMasterThread()) return;

    G4cout << "Simulation complete." << G4endl;
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    G4cout << "Elapsed time: " << elapsed.count() << " seconds" << G4endl;
}
