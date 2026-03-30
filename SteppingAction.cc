#include "SteppingAction.hh"
#include "globalVars.hh"

#include "G4Track.hh"
#include "G4Step.hh"
#include "G4SystemOfUnits.hh"
#include "G4VProcess.hh"
#include "G4ParticleDefinition.hh"
#include "G4ParticleTypes.hh"
#include "G4ios.hh"
#include "photonTrackingInfo.hh"

#include <map>

SteppingAction::SteppingAction() {}

SteppingAction::~SteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
    G4Track* track = step->GetTrack();

    if (zoneOptimization) {
        G4ThreeVector position = track->GetPosition();
        G4double radius = position.mag();
        if (radius <= innerRadii[optimalZone]) track->SetTrackStatus(fStopAndKill);
    }

    // Kill low-energy particles
    if (track->GetKineticEnergy() < energyLowerLimit) {
        track->SetTrackStatus(fStopAndKill);
    }

    // Mark comptonized photons
    if (track->GetDefinition() != G4Gamma::GammaDefinition()) return;

    auto proc = step->GetPostStepPoint()->GetProcessDefinedStep();
    if (!proc) return;

    if (proc->GetProcessName() == "compt") {
        auto info = (PhotonTrackInfo*) track->GetUserInformation();
        if (info) info->hasCompton = true;
    }

    if (radiationYield) {

        // Electron primary check
        if (track->GetDefinition() == G4Electron::Definition() && track->GetParentID() == 0) {
            G4int trackID = track->GetTrackID();
            if (electronInitialEnergies.find(trackID) == electronInitialEnergies.end()) {
                electronInitialEnergies[trackID] = track->GetKineticEnergy();
            }
        }


        // Secondary creation check
        const std::vector<const G4Track*>* secondaries = step->GetSecondaryInCurrentStep();
        if (!secondaries) return;

        for (const auto& sec : *secondaries) {
            if (sec->GetDefinition() == G4Gamma::Definition()) {
                G4int parentID = sec->GetParentID();
                // Only associate with parent electrons
                if (electronInitialEnergies.find(parentID) != electronInitialEnergies.end()) {
                    electronPhotonCounts[parentID]++;
                    bremsPhotonEnergy[parentID] += sec->GetKineticEnergy();
                }
            }
        }
    }
}
