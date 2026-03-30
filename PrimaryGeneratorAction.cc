#include "PrimaryGeneratorAction.hh"
#include "globalVars.hh"

#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4Electron.hh"
#include "G4Gamma.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"
#include "G4IonTable.hh"
#include "G4GenericIon.hh"
#include "G4RunManager.hh"
#include "G4UnitsTable.hh"
#include "G4ios.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction()
{
    fParticleGun = new G4ParticleGun(1);

    if (particleName == "photon") {
        fParticleGun->SetParticleDefinition(G4Gamma::GammaDefinition());
    }
    else if (particleName == "electron") {
        fParticleGun->SetParticleDefinition(G4Electron::ElectronDefinition());
    }
    fParticleGun->SetParticlePosition(G4ThreeVector(particleX, particleY, particleZ));
    fParticleGun->SetParticleEnergy(particleEnergy);
}

PrimaryGeneratorAction::~PrimaryGeneratorAction() {
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* Event) {
    if (particleName == "Ni56") {
        G4GenericIon::GenericIonDefinition();

        G4int Z = 28;
        G4int A = 56;
        G4double excitEnergy = 0.0*keV;
        G4IonTable* ionTable = G4IonTable::GetIonTable();
        G4ParticleDefinition* Ni56 = nullptr;
        if (ionTable) {
            Ni56 = ionTable->GetIon(Z, A, excitEnergy);
        }

        if (!Ni56) {
            G4cerr << "Error: Ni-56 is not found" << G4endl;
            return;
        }

        fParticleGun->SetParticleDefinition(Ni56);
        fParticleGun->SetParticleEnergy(0 * MeV);
    }

    G4double theta = std::acos(1.0 - 2.0 * G4UniformRand());
    G4double phi   = 2.0 * CLHEP::pi * G4UniformRand();
    G4double sinTheta = std::sin(theta);
    G4double cosTheta = std::cos(theta);
    G4double sinPhi = std::sin(phi);
    G4double cosPhi = std::cos(phi);
    G4ThreeVector direction(sinTheta * cosPhi, sinTheta * sinPhi, cosTheta);

    fParticleGun->SetParticleMomentumDirection(direction);
    fParticleGun->GeneratePrimaryVertex(Event);
}
