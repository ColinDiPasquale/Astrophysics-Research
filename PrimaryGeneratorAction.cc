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
    if (particleName == "Decays") {
        const G4double lambda_Ni = 1.319e-6;  // 1/s
        const G4double lambda_Co = 1.039e-7;  // 1/s
        const G4double N0_Ni = 1.3e55; // starting ni56

        G4double t = timeSinceSupernova * 24.0 * 3600.0;
        G4double R_Ni = lambda_Ni * N0_Ni * exp(-lambda_Ni * t);

        G4double N_Co = (lambda_Ni * N0_Ni / (lambda_Co - lambda_Ni)) *
                    (exp(-lambda_Ni * t) - exp(-lambda_Co * t));

        G4double R_Co = lambda_Co * N_Co;
        G4double R_tot = R_Ni + R_Co;

        G4double p_Ni = R_Ni / R_tot;
        G4double p_Co = R_Co / R_tot;
        if (G4UniformRand() < p_Ni) { // nickel decay
            nickelDecays++;
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
        else { // cobalt decay
            cobaltDecays++;
            G4GenericIon::GenericIonDefinition();

            G4int Z = 27;
            G4int A = 56;
            G4double excitEnergy = 0.0*keV;
            G4IonTable* ionTable = G4IonTable::GetIonTable();
            G4ParticleDefinition* Co56 = nullptr;
            if (ionTable) {
                Co56 = ionTable->GetIon(Z, A, excitEnergy);
            }

            if (!Co56) {
                G4cerr << "Error: Co-56 is not found" << G4endl;
                return;
            }

            fParticleGun->SetParticleDefinition(Co56);
            fParticleGun->SetParticleEnergy(0 * MeV);
        }
    }
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
