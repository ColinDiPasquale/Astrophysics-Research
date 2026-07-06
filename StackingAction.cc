#include "StackingAction.hh"
#include "globalVars.hh"

#include "G4Track.hh"
#include "G4ParticleDefinition.hh"
#include "G4IonTable.hh"

G4ClassificationOfNewTrack StackingAction::ClassifyNewTrack(const G4Track* track) {
    // When the primary was Ni56, kill any Co56 secondaries so the decay chain
    // stops at Co56 and we don't double-count the 847/1238 keV lines.
    if (isNickelEvent && track->GetParentID() > 0) {
        const G4ParticleDefinition* pd = track->GetParticleDefinition();
        if (pd->GetAtomicNumber() == 27 && pd->GetAtomicMass() == 56)
            return fKill;
    }
    return fUrgent;
}
