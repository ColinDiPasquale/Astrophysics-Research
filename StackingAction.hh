#ifndef STACKINGACTION_HH
#define STACKINGACTION_HH

#include "G4UserStackingAction.hh"
#include "G4ClassificationOfNewTrack.hh"

class G4Track;

class StackingAction : public G4UserStackingAction {
public:
    StackingAction() = default;
    ~StackingAction() override = default;

    G4ClassificationOfNewTrack ClassifyNewTrack(const G4Track* track) override;
};

#endif
