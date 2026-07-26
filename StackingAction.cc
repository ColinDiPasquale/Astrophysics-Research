#include "StackingAction.hh"

#include "G4Track.hh"

// Decay-line gammas are now generated directly as primaries in
// PrimaryGeneratorAction (no G4RadioactiveDecayPhysics), so no Ni56/Co56 ion
// tracks are ever produced here to filter out.
G4ClassificationOfNewTrack StackingAction::ClassifyNewTrack(const G4Track*) {
    return fUrgent;
}
