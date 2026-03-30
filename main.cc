#include "globalVars.hh"

#include "G4MTRunManager.hh"
#include "G4UImanager.hh"
#include <chrono>

#include "DetectorConstruction.hh"
#include "PhysicsList.hh"
#include "PrimaryGeneratorAction.hh"
#include "SteppingAction.hh"
#include "TrackingAction.hh"
#include "RunAction.hh"
#include "ActionInitialization.hh"

int main(int argc, char** argv) {
    // Create multithreaded run manager
    G4MTRunManager* runManager = new G4MTRunManager();
    runManager->SetNumberOfThreads(threadCount); // Set number of threads

    if (!ironSphere) {
        // Create geometry (used for optical depth calculations)
    }
    
    // User initialization classes
    runManager->SetUserInitialization(new DetectorConstruction());
    runManager->SetUserInitialization(new PhysicsList());

    // User action classes
    runManager->SetUserInitialization(new ActionInitialization());
    runManager->Initialize();

    // Apply initial commands
    G4UImanager* UImanager = G4UImanager::GetUIpointer();
    UImanager->ApplyCommand("/run/initialize");
    UImanager->ApplyCommand("/control/verbose 0");
    UImanager->ApplyCommand("/run/verbose 0");
    UImanager->ApplyCommand("/event/verbose 0");
    UImanager->ApplyCommand("/tracking/verbose 0");

    UImanager->ApplyCommand("/run/beamOn " + std::to_string(eventCount));

    delete runManager;

    std::system("python3 \"../Python Files/combineFiles.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotEverything.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotBremsCompton.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotBremsDirect.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotBremsComptonDirect.py\"");

    G4cout << "Done" << G4endl;

    return 0;
}