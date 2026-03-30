#ifndef TRACKING_ACTION_HH
#define TRACKING_ACTION_HH

#include "G4UserTrackingAction.hh"
#include "globalVars.hh"
#include "G4Track.hh"
#include "G4Threading.hh"
#include "G4SystemOfUnits.hh"
#include "globals.hh"

#include <fstream>
#include <vector>

class TrackingAction : public G4UserTrackingAction {
public:
    TrackingAction();
    ~TrackingAction() override;

    void PreUserTrackingAction(const G4Track* track) override;
    void PostUserTrackingAction(const G4Track* track) override;

private:
    G4int GetLogBinIndex(G4double energy) const;
};

#endif
