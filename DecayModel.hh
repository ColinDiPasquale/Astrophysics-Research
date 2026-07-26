#ifndef DECAY_MODEL_HH
#define DECAY_MODEL_HH

#include "globals.hh"
#include "G4SystemOfUnits.hh"
#include <vector>

struct GammaEmission {
    G4int    id;
    G4String label;
    G4double energy;
    G4double probabilityPerDecay;
};

// Each line is sampled independently against its probabilityPerDecay every
// time its parent isotope decays, so a single decay can emit zero, one, or
// several of these gammas in cascade (mirrors real gamma-gamma cascades
// without needing a full decay-scheme/cascade model).
extern const std::vector<GammaEmission> kNi56Lines;

// DDEP/LNHB evaluated Co-56 nuclear gamma lines. Absolute yields per parent
// decay — do not renormalize to sum to one.
extern const std::vector<GammaEmission> kCo56Lines;

// Evaluated beta-plus branch: a selected beta-plus decay produces one
// positron, which (in the local-annihilation approximation) yields a
// correlated, back-to-back pair of 511 keV photons — handled separately
// from kCo56Lines since it isn't a single independent line.
extern const G4double kCo56PositronBranchingRatio;

#endif
