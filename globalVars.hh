#ifndef GLOBAL_VARS_HH
#define GLOBAL_VARS_HH

#include "globals.hh"
#include "G4SystemOfUnits.hh"
#include "G4Material.hh"
#include "G4NistManager.hh"
#include "G4Element.hh"
#include "G4Isotope.hh"
#include "G4EmCalculator.hh"
#include <map>
#include "G4Types.hh"
#include "Randomize.hh"


#include <fstream>
#include <string>
#include <vector>

// Global constants
extern const G4int threadCount;
extern const G4long eventCount;
extern const G4String particleName;
extern const G4double particleEnergy;
extern const G4double particleX;
extern const G4double particleY;
extern const G4double particleZ;
extern const G4int energyLowerLimit;
extern const G4int minZone;
extern const G4int maxZone;
extern const G4double timeSinceSupernova;
extern const bool radiationYield;
extern const bool ironSphere;
extern const bool zoneOptimization;
extern const G4int optimalZone;

// Particle counters
extern G4ThreadLocal G4double unmodifiedEscapeCounter;
extern G4ThreadLocal G4double modifiedEscapeCounter;
extern G4ThreadLocal G4double bremsstrahlungPhotons;
extern G4ThreadLocal G4double comptonPhotons;
extern G4ThreadLocal G4double annihilationPhotons;
extern G4ThreadLocal G4double counter;
extern G4ThreadLocal G4double totalPhotons;
extern G4ThreadLocal G4double totalElectronsKilled;
extern G4ThreadLocal G4double totalElectronRadius;

// Binning constants
extern const G4double gEmin;
extern const G4double gEmax;
extern const G4int gNBins;
extern const G4double gLogBinWidth;

extern const G4double rMin;
extern const G4double rMax;
extern const G4int rNBins;
extern const G4double logRBinWidth;

// Histograms
extern G4ThreadLocal std::vector<G4int>* bremsstrahlungHistogram;
extern G4ThreadLocal std::vector<G4int>* comptonizedHistogram;
extern G4ThreadLocal std::vector<G4int>* directEscapeHistogram;
extern G4ThreadLocal std::vector<G4int>* allEmissionsHistogram;
extern G4ThreadLocal std::vector<G4int>* electronHistogram;
extern G4ThreadLocal std::ofstream* outFileInfo;

// Geometry data
extern const G4String geometryFile;
extern std::vector<std::vector<double>> zoneData;
extern std::vector<double> innerRadii;
extern std::vector<double> outerRadii;
extern std::vector<double> zoneDensityArray;
extern std::vector<G4Material*> zoneMaterials;
extern G4double sphereRadius;
extern G4double worldSize;
extern const G4double ironSphereRadius;
extern const G4double ironSphereDensity;
extern const G4double densityMultiplier;

// Function declarations
void createGeometry(const std::string& filename,
                                       std::vector<G4Material*>& zoneMaterials,
                                       std::vector<double>& innerRadii,
                                       std::vector<double>& outerRadii,
                                       double& sphereRadius,
                                       double& worldSize);

// Misc/Testing
extern std::map<G4int, G4int> electronPhotonCounts;
extern std::map<G4int, G4double> electronInitialEnergies;
extern std::map<G4int, G4double> bremsPhotonEnergy;
extern std::map<G4double, std::vector<G4double>> yieldByEnergyBin;

#endif