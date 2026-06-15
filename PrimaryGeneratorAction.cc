#include "PrimaryGeneratorAction.hh"
#include "globalVars.hh"

#include "G4ParticleGun.hh"
#include "G4Gamma.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"
#include "G4IonTable.hh"
#include "G4GenericIon.hh"

#include <algorithm>
#include <numeric>

PrimaryGeneratorAction::PrimaryGeneratorAction() {
    fParticleGun = new G4ParticleGun(1);

    if (particleName == "photon")
        fParticleGun->SetParticleDefinition(G4Gamma::GammaDefinition());

    fParticleGun->SetParticleEnergy(particleEnergy);

}

PrimaryGeneratorAction::~PrimaryGeneratorAction() {
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* Event) {
    // Build cumulative Ni-56 mass weight distribution on first call (geometry is ready by then)
    if (fCumWeights.empty() && !zoneNi56Fractions.empty()) {
        fCumWeights.resize(zoneNi56Fractions.size());
        for (size_t i = 0; i < zoneNi56Fractions.size(); i++) {
            G4double rIn  = innerRadii[i];
            G4double rOut = outerRadii[i];
            G4double shellVol = rOut*rOut*rOut - rIn*rIn*rIn; // proportional to 4/3 pi (r_out^3 - r_in^3)
            fCumWeights[i] = zoneDensitiesGCC[i] * zoneNi56Fractions[i] * shellVol;
        }
        // Convert to cumulative distribution
        for (size_t i = 1; i < fCumWeights.size(); i++)
            fCumWeights[i] += fCumWeights[i-1];
        G4double total = fCumWeights.back();
        for (auto& w : fCumWeights) w /= total;
    }

    G4double r, cosT, sinT, phi;
    if (!fCumWeights.empty() && (particleName == "Decays" || particleName == "Ni56")) {
        // Sample zone weighted by Ni-56 mass
        G4double u = G4UniformRand();
        int zone = (int)(std::lower_bound(fCumWeights.begin(), fCumWeights.end(), u) - fCumWeights.begin());
        zone = std::min(zone, (int)fCumWeights.size() - 1);

        // Sample uniform position within that shell
        G4double rIn3  = innerRadii[zone] * innerRadii[zone] * innerRadii[zone];
        G4double rOut3 = outerRadii[zone] * outerRadii[zone] * outerRadii[zone];
        r    = std::cbrt(rIn3 + G4UniformRand() * (rOut3 - rIn3));
        cosT = 1.0 - 2.0 * G4UniformRand();
        sinT = std::sqrt(1.0 - cosT * cosT);
        phi  = CLHEP::twopi * G4UniformRand();
    } else {
        // Uniform in volume (photon modes)
        r    = sphereRadius * std::cbrt(G4UniformRand());
        cosT = 1.0 - 2.0 * G4UniformRand();
        sinT = std::sqrt(1.0 - cosT * cosT);
        phi  = CLHEP::twopi * G4UniformRand();
    }

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
        // photon — direction matters
        G4double cosTheta = 1.0 - 2.0 * G4UniformRand();
        G4double sinTheta = std::sqrt(1.0 - cosTheta * cosTheta);
        G4double phiDir   = CLHEP::twopi * G4UniformRand();
        fParticleGun->SetParticleMomentumDirection(
            G4ThreeVector(sinTheta * std::cos(phiDir), sinTheta * std::sin(phiDir), cosTheta));
    }

    fParticleGun->GeneratePrimaryVertex(Event);
}
