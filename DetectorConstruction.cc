#include "DetectorConstruction.hh"
#include "globalVars.hh"

#include "G4Sphere.hh"
#include "G4Gamma.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4NistManager.hh"
#include "G4SystemOfUnits.hh"

DetectorConstruction::DetectorConstruction() : G4VUserDetectorConstruction() {}

DetectorConstruction::~DetectorConstruction() {}

G4VPhysicalVolume* DetectorConstruction::Construct() {
    G4NistManager* nist = G4NistManager::Instance();

    // World volume
    G4Material* vacuum = nist->FindOrBuildMaterial("G4_Galactic");

    createGeometry(geometryFile, zoneMaterials, innerRadii, outerRadii, sphereRadius, worldSize);

    G4Sphere* solidWorld = new G4Sphere("World", 0 * cm, worldSize, 0., 360 * deg, 0., 180 * deg);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, vacuum, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(0, G4ThreeVector(), logicWorld, "World", 0, false, 0);

    // Constructing the star
    for (int zone = minZone; zone <= maxZone; zone++) {
        std::string sphereName = "zoneSphere" + std::to_string(zone);

        G4Sphere* zoneSphere = new G4Sphere(sphereName, innerRadii[zone], outerRadii[zone], 0., 360 * deg, 0., 180 * deg);
        G4LogicalVolume* zoneLogic = new G4LogicalVolume(zoneSphere, zoneMaterials[zone], sphereName);
        G4VPhysicalVolume* zonePlacement = new G4PVPlacement(0, G4ThreeVector(), zoneLogic, sphereName, logicWorld, false, 0, true);
    }
    
    return physWorld;
}
