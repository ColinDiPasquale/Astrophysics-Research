#include "G4VUserTrackInformation.hh"

class PhotonTrackInfo : public G4VUserTrackInformation {
public:
    PhotonTrackInfo() : hasCompton(false) {}
    bool hasCompton;
};