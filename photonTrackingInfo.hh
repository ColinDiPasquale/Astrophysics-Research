#include "G4VUserTrackInformation.hh"

class PhotonTrackInfo : public G4VUserTrackInformation {
public:
    PhotonTrackInfo() : hasCompton(false), originalEnergy(-1.0) {}
    bool hasCompton;
    double originalEnergy;  // keV at creation, for escape-fraction counting
};