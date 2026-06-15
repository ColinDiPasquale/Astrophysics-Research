#include "globalVars.hh"

#include "G4MTRunManager.hh"
#include "G4UImanager.hh"

#include "DetectorConstruction.hh"
#include "PhysicsList.hh"
#include "ActionInitialization.hh"

int main(int argc, char** argv) {
    G4MTRunManager* runManager = new G4MTRunManager();
    runManager->SetNumberOfThreads(threadCount);

    runManager->SetUserInitialization(new DetectorConstruction());
    runManager->SetUserInitialization(new PhysicsList());
    runManager->SetUserInitialization(new ActionInitialization());
    runManager->Initialize();

    G4UImanager* UI = G4UImanager::GetUIpointer();
    UI->ApplyCommand("/control/verbose 0");
    UI->ApplyCommand("/run/verbose 0");
    UI->ApplyCommand("/event/verbose 0");
    UI->ApplyCommand("/tracking/verbose 0");

    UI->ApplyCommand("/run/beamOn " + std::to_string(eventCount));

    delete runManager;

    std::system("python3 \"../Python Files/combineFiles.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotEverything.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotBremsCompton.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotBremsDirect.py\"");
    std::system("python3 \"../Python Files/rebinAndPlotBremsComptonDirect.py\"");
    std::system("python3 \"../Python Files/temp.py\"");

    G4cout << "Done" << G4endl;
    return 0;
}
