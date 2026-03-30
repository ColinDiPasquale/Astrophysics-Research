#include "globalVars.hh"

// Global constants
const G4int threadCount = 16;
const G4long eventCount = 1e7;
// 1e5 = 100 thousand
// 1e9 = 1 billion

const G4int minZone = 0;
const G4int maxZone = 19; // Max is 19
const G4double timeSinceSupernova = 40.0f; // In days
const G4double densityMultiplier = 1.0;

// Additional Constants

const bool radiationYield = false;
const bool ironSphere = false;
const bool zoneOptimization = false;

const G4int optimalZone = 10;

const G4String particleName = "Ni56";
const G4double particleEnergy = 1 * MeV; // Automatically 0 if Ni56

const G4int energyLowerLimit = 1 * keV;

const G4double gEmin = 1.0 * keV;
const G4double gEmax = 4.0 * MeV;
const G4int gNBins = 10000;
const G4double gLogBinWidth = std::log10(gEmax / gEmin) / gNBins;

const G4double ironSphereRadius = 1e6 * cm;
const G4double ironSphereDensity = 1e6 * g / cm3;

const G4double rMin = 1.0e9 * cm;
const G4double rMax = 1.0e16 * cm;
const G4int rNBins = 10000;
const G4double logRBinWidth = std::log10(rMax / rMin) / rNBins;

// Particle counters

G4ThreadLocal G4double unmodifiedEscapeCounter = 0;
G4ThreadLocal G4double modifiedEscapeCounter = 0;
G4ThreadLocal G4double bremsstrahlungPhotons = 0;
G4ThreadLocal G4double comptonPhotons = 0;
G4ThreadLocal G4double annihilationPhotons = 0;
G4ThreadLocal G4double counter = 0;
G4ThreadLocal G4double totalPhotons = 0;
G4ThreadLocal G4double totalElectronsKilled = 0;
G4ThreadLocal G4double totalElectronRadius = 0;

// Histograms
G4ThreadLocal std::vector<G4int>* bremsstrahlungHistogram = nullptr;
G4ThreadLocal std::vector<G4int>* comptonizedHistogram = nullptr;
G4ThreadLocal std::vector<G4int>* directEscapeHistogram = nullptr;
G4ThreadLocal std::vector<G4int>* allEmissionsHistogram = nullptr;
G4ThreadLocal std::vector<G4int>* electronHistogram = nullptr;
G4ThreadLocal std::ofstream* outFileInfo = nullptr;
std::map<G4int, G4double> bremsPhotonEnergy;
std::map<G4double, std::vector<G4double>> yieldByEnergyBin;

// Global zone creation

const G4String geometryFile = "/home/cdipasq/simProfTheMT/Supernova Models/model52_W7_20shells_CSiNi56_t40d.dat";
std::vector<G4Material*> zoneMaterials;
std::vector<double> innerRadii;
std::vector<double> outerRadii;
double sphereRadius = 0.0;
double worldSize = 0.0;

const G4double particleX = G4UniformRand() * sphereRadius;
const G4double particleY = G4UniformRand() * sphereRadius;
const G4double particleZ = G4UniformRand() * sphereRadius;

// Testing
#include <map>
#include "G4Types.hh"

std::map<G4int, G4int> electronPhotonCounts;
std::map<G4int, G4double> electronInitialEnergies;

// Things to ask Dr. The
// What should the photon energy value be for calculating the optical depth? Currently it is 1.72 MeV which is decay from Ni56 to Co56
// Where should I start cutting off simulations of photons to save computational time?
// Anything else to add?
// Can we go through getting it on the cluster