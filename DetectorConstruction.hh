#ifndef DETECTOR_CONSTRUCTION_HH
#define DETECTOR_CONSTRUCTION_HH

#include "globalVars.hh"
#include "G4VUserDetectorConstruction.hh"
#include "G4Material.hh"
#include <fstream>
#include <numeric>
#include <cmath>

class DetectorConstruction : public G4VUserDetectorConstruction {
public:
    DetectorConstruction();
    virtual ~DetectorConstruction();

    virtual G4VPhysicalVolume* Construct();

private:
};

#endif
