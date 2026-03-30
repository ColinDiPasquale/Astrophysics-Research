#include "TrackingAction.hh"
#include "G4Gamma.hh"
#include "G4Electron.hh"
#include "G4VProcess.hh"
#include "G4SystemOfUnits.hh"
#include "G4Threading.hh"
#include "globalVars.hh"
#include "photonTrackingInfo.hh"

#include <cmath>
#include <fstream>
#include <sstream>

TrackingAction::TrackingAction() {
    G4int threadID = G4Threading::G4GetThreadId();

    bremsstrahlungHistogram = new std::vector<G4int>(gNBins, 0);
    comptonizedHistogram = new std::vector<G4int>(gNBins, 0);
    directEscapeHistogram = new std::vector<G4int>(gNBins, 0);
    allEmissionsHistogram = new std::vector<G4int>(gNBins, 0);
    electronHistogram = new std::vector<G4int>(gNBins, 0);

    outFileInfo = new std::ofstream("info_" + std::to_string(threadID) + ".txt");
}

TrackingAction::~TrackingAction() {
    G4int threadID = G4Threading::G4GetThreadId();

    // Output file info
    (*outFileInfo) << "Total Photons Tracked: " << totalPhotons << "\n" << std::endl;
    (*outFileInfo) << "Total Listed Photons: " << (unmodifiedEscapeCounter + modifiedEscapeCounter + bremsstrahlungPhotons + annihilationPhotons) << std::endl;
    (*outFileInfo) << "Direct Escape Photons: " << (unmodifiedEscapeCounter + modifiedEscapeCounter) << std::endl;
    (*outFileInfo) << "Unmodified Escape Count: " << unmodifiedEscapeCounter << std::endl;
    (*outFileInfo) << "Modified Escape Count: " << modifiedEscapeCounter << "\n" << std::endl;
    (*outFileInfo) << "Bremsstrahlung: " << bremsstrahlungPhotons << std::endl;
    (*outFileInfo) << "Compton: " << comptonPhotons << std::endl;
    (*outFileInfo) << "Annihilation: " << annihilationPhotons << std::endl;

    outFileInfo->close();
    delete outFileInfo;
    outFileInfo = nullptr;

    // Histograms
    struct HistEntry {
        std::string name;
        std::vector<G4int>* hist;
    };

    std::vector<HistEntry> hists = {
        {"binned_brems_", bremsstrahlungHistogram},
        {"binned_compton_", comptonizedHistogram},
        {"binned_direct_escape_", directEscapeHistogram},
        {"binned_everything_", allEmissionsHistogram},
        {"binned_electrons_", electronHistogram}
    };

    // Creating all the histogram bins
    for (const auto& entry : hists) {
        std::ofstream out(entry.name + std::to_string(threadID) + ".txt");

        for (G4int i = 0; i < gNBins; ++i) {
            G4double lower = gEmin * std::pow(10.0, i * gLogBinWidth);
            G4double upper = gEmin * std::pow(10.0, (i + 1) * gLogBinWidth);
            G4double center = (lower + upper) / 2.0;

            out << std::setprecision(12)
                << center / CLHEP::keV << " "
                << (*(entry.hist))[i] << "\n";
        }

        out.close();
    }

    // Cleanup
    delete bremsstrahlungHistogram;
    delete comptonizedHistogram;
    delete directEscapeHistogram;
    delete allEmissionsHistogram;
    delete electronHistogram;

    bremsstrahlungHistogram = nullptr;
    comptonizedHistogram = nullptr;
    directEscapeHistogram = nullptr;
    allEmissionsHistogram = nullptr;
    electronHistogram = nullptr;
}

void TrackingAction::PreUserTrackingAction(const G4Track* track) {
    G4ParticleDefinition* particle = track->GetDefinition();
    if (particle == G4Electron::ElectronDefinition( )) {
        G4double energy = track->GetKineticEnergy();
        G4int trackNumber = track->GetTrackID();
        const G4VProcess* process = track->GetCreatorProcess();
        G4int binIndex = GetLogBinIndex(energy);
        if (binIndex < 0) return; // Outside binning range
        (*electronHistogram)[binIndex]++;
    }

    if (track->GetDefinition() == G4Gamma::GammaDefinition()) {
        auto info = new PhotonTrackInfo();
        const_cast<G4Track*>(track)->SetUserInformation(info);
    }
}

void TrackingAction::PostUserTrackingAction(const G4Track* track) {
    // Getting basic particle info
    G4ParticleDefinition* particle = track->GetDefinition();
    G4ThreeVector position = track->GetPosition();
    G4int trackNumber = track->GetTrackID();
    G4double radius = position.mag();

    // For electrons
    if (particle == G4Electron::ElectronDefinition()) {
        totalElectronRadius += radius;
        totalElectronsKilled++;
    }

    // For photons
    if (particle == G4Gamma::GammaDefinition()) {

        if (radius >= sphereRadius) {
            G4double energy = track->GetKineticEnergy();
            const G4VProcess* process = track->GetCreatorProcess();
            
            // Getting bin # for photon
            G4int binIndex = GetLogBinIndex(energy);
            if (binIndex < 0) return; // Outside binning range

            // Every photon gets added to the emissions histogram and counted for total photons
            (*allEmissionsHistogram)[binIndex]++;
            totalPhotons++;

            // Gets how photon was created
            G4String processName = process->GetProcessName();
            if (process) {
                auto info = (PhotonTrackInfo*) track->GetUserInformation();

                if (processName == "eBrem") { // If it is a bremsstrahlung
                    (*bremsstrahlungHistogram)[binIndex]++;
                    bremsstrahlungPhotons++;
                
                } else if (processName == "Radioactivation") { // If it was created by Ni56/Co56 decay
                    (*directEscapeHistogram)[binIndex]++; // All radiodecay photons are "source" photons, so they are considered direct escape
                    if (info && info->hasCompton) { // If it underwent compton scattering in its lifetime
                        modifiedEscapeCounter++;
                        (*comptonizedHistogram)[binIndex]++; // Add to comptonized histogram (will be very similar to direct escape histogram)
                        comptonPhotons++;
                    }
                    else unmodifiedEscapeCounter++; 
                } else if (processName == "compt") { // Shouldn't ever happen in theory
                    G4cout << "compt" << G4endl;
                } else if (processName == "annihil") { // Happens rarely but still happens. Is already added to all emissions histogram
                    annihilationPhotons++;
                } else {
                    G4cout << "Name: " << processName << "     Energy: " << energy << G4endl; // Failsafe
                }
            } else {
                G4cout << "Photon with no creator process." << G4endl; // Failsafe
            }
        } 
    }
}

G4int TrackingAction::GetLogBinIndex(G4double energy) const {
    if (energy < gEmin || energy >= gEmax) return -1;
    return static_cast<G4int>(std::log10(energy / gEmin) / gLogBinWidth);
}

// Need to find ratio between ni56 and co56
// Then make twice as many bins as currently, so i can have all photons from ni and all from cobalt
// Then apply the ratio, then combine the ni and co bins back together, then divide by the # of source particles
// Then graph. 
// Remeber, we are taking a snapshot at t=40 days, not cumulative 0->40 days. So thats why we divide by # of source particles,
// because we want as many simulations as possible so its accurate but the # of source particles shouldn't affect the flux