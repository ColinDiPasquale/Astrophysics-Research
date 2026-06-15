#include "PhysicsList.hh"

#include "G4EmLivermorePhysics.hh"
#include "G4DecayPhysics.hh"
#include "G4RadioactiveDecayPhysics.hh"
#include "G4LossTableManager.hh"
#include "G4UAtomicDeexcitation.hh"
PhysicsList::PhysicsList() : G4VModularPhysicsList() {
    RegisterPhysics(new G4EmLivermorePhysics());
    RegisterPhysics(new G4RadioactiveDecayPhysics());
    RegisterPhysics(new G4DecayPhysics());
}

PhysicsList::~PhysicsList() {}

void PhysicsList::ConstructProcess()
{
    G4VModularPhysicsList::ConstructProcess();

    G4LossTableManager* man = G4LossTableManager::Instance();
    G4VAtomDeexcitation* deex = new G4UAtomicDeexcitation();
    deex->SetFluo(false);
    deex->SetAuger(false);
    deex->SetPIXE(false);
    man->SetAtomDeexcitation(deex);
}