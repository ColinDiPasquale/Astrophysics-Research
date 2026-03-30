#ifndef RUN_ACTION_HH
#define RUN_ACTION_HH

#include "G4UserRunAction.hh"
#include "globalVars.hh"
#include <vector>
#include <chrono>
#include "G4Material.hh"

class RunAction : public G4UserRunAction {
public:
    void BeginOfRunAction(const G4Run*) override;
    void EndOfRunAction(const G4Run*) override;
private:
    std::chrono::time_point<std::chrono::high_resolution_clock> start;
};

#endif