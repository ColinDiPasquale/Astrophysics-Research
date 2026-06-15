#include "PrimaryGeneratorAction.hh"
#include "globalVars.hh"

#include "G4ParticleGun.hh"
#include "G4Electron.hh"
#include "G4Gamma.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"
#include "G4IonTable.hh"
#include "G4GenericIon.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction() {
    fParticleGun = new G4ParticleGun(1);

    if (particleName == "photon")
        fParticleGun->SetParticleDefinition(G4Gamma::GammaDefinition());
    else if (particleName == "electron")
        fParticleGun->SetParticleDefinition(G4Electron::ElectronDefinition());

    fParticleGun->SetParticleEnergy(particleEnergy);
}

PrimaryGeneratorAction::~PrimaryGeneratorAction() {
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* Event) {
    // Random position inside the sphere, uniform in volume
    G4double r    = sphereRadius * std::cbrt(G4UniformRand());
    G4double cosT = 1.0 - 2.0 * G4UniformRand();
    G4double sinT = std::sqrt(1.0 - cosT * cosT);
    G4double phi  = CLHEP::twopi * G4UniformRand();
    fParticleGun->SetParticlePosition(G4ThreeVector(
        r * sinT * std::cos(phi),
        r * sinT * std::sin(phi),
        r * cosT));

    if (particleName == "Decays") {
        const G4double lambda_Ni = 1.319e-6; // 1/s
        const G4double lambda_Co = 1.039e-7; // 1/s
        const G4double N0_Ni    = 1.3e55;

        G4double t     = timeSinceSupernova * 24.0 * 3600.0;
        G4double R_Ni  = lambda_Ni * N0_Ni * std::exp(-lambda_Ni * t);
        G4double N_Co  = (lambda_Ni * N0_Ni / (lambda_Co - lambda_Ni)) *
                         (std::exp(-lambda_Ni * t) - std::exp(-lambda_Co * t));
        G4double R_tot = R_Ni + lambda_Co * N_Co;
        G4double p_Ni  = R_Ni / R_tot;

        G4IonTable* ionTable = G4IonTable::GetIonTable();
        G4GenericIon::GenericIonDefinition();

        if (G4UniformRand() < p_Ni) {
            nickelDecays++;
            G4ParticleDefinition* Ni56 = ionTable->GetIon(28, 56, 0.0);
            if (!Ni56) { G4cerr << "Error: Ni-56 not found" << G4endl; return; }
            fParticleGun->SetParticleDefinition(Ni56);
        } else {
            cobaltDecays++;
            G4ParticleDefinition* Co56 = ionTable->GetIon(27, 56, 0.0);
            if (!Co56) { G4cerr << "Error: Co-56 not found" << G4endl; return; }
            fParticleGun->SetParticleDefinition(Co56);
        }
        fParticleGun->SetParticleEnergy(0 * MeV);
    }

    if (particleName == "Ni56") {
        G4GenericIon::GenericIonDefinition();
        G4ParticleDefinition* Ni56 = G4IonTable::GetIonTable()->GetIon(28, 56, 0.0);
        if (!Ni56) { G4cerr << "Error: Ni-56 not found" << G4endl; return; }
        fParticleGun->SetParticleDefinition(Ni56);
        fParticleGun->SetParticleEnergy(0 * MeV);
    }

    G4double cosTheta = 1.0 - 2.0 * G4UniformRand();
    G4double sinTheta = std::sqrt(1.0 - cosTheta * cosTheta);
    G4double phiDir   = CLHEP::twopi * G4UniformRand();
    fParticleGun->SetParticleMomentumDirection(
        G4ThreeVector(sinTheta * std::cos(phiDir), sinTheta * std::sin(phiDir), cosTheta));

    fParticleGun->GeneratePrimaryVertex(Event);
}
