#ifndef PRIMARY_GENERATOR_ACTION_HH
#define PRIMARY_GENERATOR_ACTION_HH

#include "G4VUserPrimaryGeneratorAction.hh"
#include <vector>

class G4ParticleGun;

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction {
public:
    PrimaryGeneratorAction();
    virtual ~PrimaryGeneratorAction();

    virtual void GeneratePrimaries(G4Event*);

private:
    G4ParticleGun*        fParticleGun;
    std::vector<double>   fCumWeights; // cumulative Ni-56 mass weights per zone
};

#endif
