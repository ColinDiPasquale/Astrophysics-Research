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

    // Lazy init — ion table is only ready after G4RunManager::Initialize()
    if (!fNi56 && (particleName == "Decays" || particleName == "Ni56")) {
        G4GenericIon::GenericIonDefinition();
        G4IonTable* ionTable = G4IonTable::GetIonTable();
        fNi56 = ionTable->GetIon(28, 56, 0.0);
        if (particleName == "Decays")
            fCo56 = ionTable->GetIon(27, 56, 0.0);
    }

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

        if (G4UniformRand() < p_Ni) {
            nickelDecays++;
            fParticleGun->SetParticleDefinition(fNi56);
        } else {
            cobaltDecays++;
            fParticleGun->SetParticleDefinition(fCo56);
        }
        fParticleGun->SetParticleEnergy(0 * MeV);
        // No direction needed — ion at rest decays isotropically via G4RadioactiveDecayPhysics
        fParticleGun->SetParticleMomentumDirection(G4ThreeVector(1, 0, 0));
    } else if (particleName == "Ni56") {
        fParticleGun->SetParticleDefinition(fNi56);
        fParticleGun->SetParticleEnergy(0 * MeV);
        fParticleGun->SetParticleMomentumDirection(G4ThreeVector(1, 0, 0));
    } else {
        // photon / electron — direction matters
        G4double cosTheta = 1.0 - 2.0 * G4UniformRand();
        G4double sinTheta = std::sqrt(1.0 - cosTheta * cosTheta);
        G4double phiDir   = CLHEP::twopi * G4UniformRand();
        fParticleGun->SetParticleMomentumDirection(
            G4ThreeVector(sinTheta * std::cos(phiDir), sinTheta * std::sin(phiDir), cosTheta));
    }

    fParticleGun->GeneratePrimaryVertex(Event);
}
