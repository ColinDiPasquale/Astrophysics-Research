#include "SteppingAction.hh"
#include "globalVars.hh"
#include "photonTrackingInfo.hh"

#include "G4Track.hh"
#include "G4Step.hh"
#include "G4SystemOfUnits.hh"
#include "G4VProcess.hh"
#include "G4Gamma.hh"

SteppingAction::SteppingAction() {}
SteppingAction::~SteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
    G4Track* track = step->GetTrack();

    if (track->GetKineticEnergy() < energyLowerLimit)
        track->SetTrackStatus(fStopAndKill);

    if (track->GetDefinition() != G4Gamma::GammaDefinition()) return;

    auto proc = step->GetPostStepPoint()->GetProcessDefinedStep();
    if (!proc) return;

    if (proc->GetProcessName() == "compt") {
        auto info = (PhotonTrackInfo*) track->GetUserInformation();
        if (info) info->hasCompton = true;
    }
}
