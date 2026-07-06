#include "globalVars.hh"
#include <map>

// Global constants
const G4int threadCount = 16;
const G4long eventCount = 1e6;

const G4double timeSinceSupernova = 200.0; // In days
const G4double densityMultiplier = 1.0;

const G4String particleName = "Decays";
const G4double particleEnergy = 0 * MeV;

const G4int energyLowerLimit = 1 * keV;

const G4double gEmin = 1.0 * keV;
const G4double gEmax = 4.0 * MeV;
const G4int gNBins = 10000;
const G4double gLogBinWidth = std::log10(gEmax / gEmin) / gNBins;

// Particle counters
G4ThreadLocal G4double unmodifiedEscapeCounter = 0;
G4ThreadLocal G4double modifiedEscapeCounter = 0;
G4ThreadLocal G4double bremsstrahlungPhotons = 0;
G4ThreadLocal G4double comptonPhotons = 0;
G4ThreadLocal G4double annihilationPhotons = 0;
G4ThreadLocal G4double totalPhotons = 0;
G4ThreadLocal G4double nickelDecays = 0;
G4ThreadLocal G4double cobaltDecays = 0;
G4ThreadLocal G4bool isNickelEvent = false;
G4ThreadLocal G4double totalDecayPhotonEnergy = 0;
G4ThreadLocal G4double count158keV = 0;
G4ThreadLocal G4double count812keV = 0;
G4ThreadLocal G4double count847keV = 0;
G4ThreadLocal G4double count1238keV = 0;
G4ThreadLocal G4double escape158keV = 0;
G4ThreadLocal G4double escape812keV = 0;
G4ThreadLocal G4double escape847keV = 0;
G4ThreadLocal G4double escape1238keV = 0;

// Histograms
G4ThreadLocal std::vector<G4int>* bremsstrahlungHistogram = nullptr;
G4ThreadLocal std::vector<G4int>* comptonizedHistogram = nullptr;
G4ThreadLocal std::vector<G4int>* directEscapeHistogram = nullptr;
G4ThreadLocal std::vector<G4int>* allEmissionsHistogram = nullptr;
G4ThreadLocal std::ofstream* outFileInfo = nullptr;

// Geometry
std::vector<double> zoneNi56Fractions;
std::vector<double> zoneDensitiesGCC;
const G4String geometryFile = "/home/cdipasq/simProfTheMT/Supernova Models/model52_W7_20shells_CSiNi56_t"
    + std::to_string((int)timeSinceSupernova) + "d.dat";
std::vector<G4Material*> zoneMaterials;
std::vector<double> innerRadii;
std::vector<double> outerRadii;
double sphereRadius = 0.0;
double worldSize = 0.0;


// TODO:
// do the word doc
// dot plot of numCreated in sim vs time (for 158, 847 kev, etc)
// dot plot of directEscape in sim vs time (for 158, 847 kev, etc)
// try to fix the binning offset issue in the plots that are made with plotForPlBpl