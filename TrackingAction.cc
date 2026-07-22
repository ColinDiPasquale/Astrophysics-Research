#include "TrackingAction.hh"
#include "globalVars.hh"
#include "photonTrackingInfo.hh"

#include "G4Gamma.hh"
#include "G4VProcess.hh"
#include "G4SystemOfUnits.hh"
#include "G4Threading.hh"

#include <cmath>
#include <fstream>
#include <iomanip>

TrackingAction::TrackingAction() {
    G4int threadID = G4Threading::G4GetThreadId();

    bremsstrahlungHistogram = new std::vector<G4int>(gNBins, 0);
    comptonizedHistogram    = new std::vector<G4int>(gNBins, 0);
    directEscapeHistogram   = new std::vector<G4int>(gNBins, 0);
    allEmissionsHistogram   = new std::vector<G4int>(gNBins, 0);

    outFileInfo = new std::ofstream("info_" + std::to_string(threadID) + ".txt");
}

TrackingAction::~TrackingAction() {
    G4int threadID = G4Threading::G4GetThreadId();

    (*outFileInfo) << "Total Photons Tracked: " << totalPhotons << "\n\n";
    (*outFileInfo) << "Total Listed Photons: " << (unmodifiedEscapeCounter + modifiedEscapeCounter + bremsstrahlungPhotons + annihilationPhotons) << "\n";
    (*outFileInfo) << "Direct Escape Photons: " << (unmodifiedEscapeCounter + modifiedEscapeCounter) << "\n";
    (*outFileInfo) << "Unmodified Escape Count: " << unmodifiedEscapeCounter << "\n";
    (*outFileInfo) << "Modified Escape Count: " << modifiedEscapeCounter << "\n\n";
    (*outFileInfo) << "Bremsstrahlung: " << bremsstrahlungPhotons << "\n";
    (*outFileInfo) << "Compton: " << comptonPhotons << "\n";
    (*outFileInfo) << "Annihilation: " << annihilationPhotons << "\n\n";
    (*outFileInfo) << "Nickel Decays: " << nickelDecays << "\n";
    (*outFileInfo) << "Cobalt Decays: " << cobaltDecays << "\n\n";
    (*outFileInfo) << "Total Decay Photon Energy (MeV): " << totalDecayPhotonEnergy / CLHEP::MeV << "\n";
    (*outFileInfo) << "158.38 keV Decay Photons: " << count158keV << "\n";
    (*outFileInfo) << "811.85 keV Decay Photons: " << count812keV << "\n";
    (*outFileInfo) << "847 keV Decay Photons: " << count847keV << "\n";
    (*outFileInfo) << "1238.3 keV Decay Photons: " << count1238keV << "\n";
    (*outFileInfo) << "158.38 keV Direct Escape: " << escape158keV << "\n";
    (*outFileInfo) << "811.85 keV Direct Escape: " << escape812keV << "\n";
    (*outFileInfo) << "847 keV Direct Escape: " << escape847keV << "\n";
    (*outFileInfo) << "1238.3 keV Direct Escape: " << escape1238keV << "\n\n";
    (*outFileInfo) << "158.38 keV Decay Photons (Nickel only): " << count158keVNickelOnly << "\n";
    (*outFileInfo) << "811.85 keV Decay Photons (Nickel only): " << count812keVNickelOnly << "\n";
    (*outFileInfo) << "847 keV Decay Photons (Cobalt only): " << count847keVCobaltOnly << "\n";
    (*outFileInfo) << "1238.3 keV Decay Photons (Cobalt only): " << count1238keVCobaltOnly << "\n";
    (*outFileInfo) << "158.38 keV Direct Escape (Nickel only): " << escape158keVNickelOnly << "\n";
    (*outFileInfo) << "811.85 keV Direct Escape (Nickel only): " << escape812keVNickelOnly << "\n";
    (*outFileInfo) << "847 keV Direct Escape (Cobalt only): " << escape847keVCobaltOnly << "\n";
    (*outFileInfo) << "1238.3 keV Direct Escape (Cobalt only): " << escape1238keVCobaltOnly << "\n\n";

    outFileInfo->close();
    delete outFileInfo;
    outFileInfo = nullptr;

    struct HistEntry {
        std::string name;
        std::vector<G4int>* hist;
    };

    std::vector<HistEntry> hists = {
        {"binned_brems_",         bremsstrahlungHistogram},
        {"binned_compton_",       comptonizedHistogram},
        {"binned_direct_escape_", directEscapeHistogram},
        {"binned_everything_",    allEmissionsHistogram},
    };

    for (const auto& entry : hists) {
        std::ofstream out(entry.name + std::to_string(threadID) + ".txt");
        for (G4int i = 0; i < gNBins; ++i) {
            G4double lower  = gEmin * std::pow(10.0, i * gLogBinWidth);
            G4double upper  = gEmin * std::pow(10.0, (i + 1) * gLogBinWidth);
            G4double center = (lower + upper) / 2.0;
            out << std::setprecision(12) << center / CLHEP::keV << " " << (*(entry.hist))[i] << "\n";
        }
        out.close();
    }

    delete bremsstrahlungHistogram;
    delete comptonizedHistogram;
    delete directEscapeHistogram;
    delete allEmissionsHistogram;

    bremsstrahlungHistogram = nullptr;
    comptonizedHistogram    = nullptr;
    directEscapeHistogram   = nullptr;
    allEmissionsHistogram   = nullptr;
}

void TrackingAction::PreUserTrackingAction(const G4Track* track) {
    if (track->GetDefinition() != G4Gamma::GammaDefinition()) return;

    auto info = new PhotonTrackInfo();
    const_cast<G4Track*>(track)->SetUserInformation(info);

    const G4VProcess* process = track->GetCreatorProcess();
    if (!process || process->GetProcessName() != "Radioactivation") return;

    G4double energy = track->GetKineticEnergy();
    G4double energyKeV = energy / CLHEP::keV;
    info->originalEnergy = energyKeV;

    totalDecayPhotonEnergy += energy;

    if (std::abs(energyKeV - 158.38) < .05)  count158keV++;
    if (std::abs(energyKeV - 811.844) < .05)  count812keV++;
    if (std::abs(energyKeV - 846.771)  < .05)  count847keV++;
    if (std::abs(energyKeV - 1238.31) < .05)  count1238keV++;
    if (isNickelEvent && std::abs(energyKeV - 158.38) < .05)  count158keVNickelOnly++;
    if (isNickelEvent && std::abs(energyKeV - 811.844) < .05)  count812keVNickelOnly++;
    if (isCobaltEvent && std::abs(energyKeV - 846.771)  < .05)  count847keVCobaltOnly++;
    if (isCobaltEvent && std::abs(energyKeV - 1238.31) < .05)  count1238keVCobaltOnly++;
}

void TrackingAction::PostUserTrackingAction(const G4Track* track) {
    if (track->GetDefinition() != G4Gamma::GammaDefinition()) return;

    G4ThreeVector position = track->GetPosition();
    if (position.mag() < sphereRadius) return;

    G4double energy = track->GetKineticEnergy();
    G4int binIndex = GetLogBinIndex(energy);
    if (binIndex < 0) return;

    const G4VProcess* process = track->GetCreatorProcess();
    if (!process) {
        G4cout << "Photon with no creator process." << G4endl;
        return;
    }

    (*allEmissionsHistogram)[binIndex]++;
    totalPhotons++;

    G4String processName = process->GetProcessName();
    auto info = (PhotonTrackInfo*) track->GetUserInformation();

    if (processName == "eBrem") { // Bremsstrahlung
        (*bremsstrahlungHistogram)[binIndex]++;
        bremsstrahlungPhotons++;
    } else if (processName == "Radioactivation") { // Nuclear decay
        (*directEscapeHistogram)[binIndex]++;
        if (info && info->hasCompton) {
            modifiedEscapeCounter++;
            (*comptonizedHistogram)[binIndex]++;
            comptonPhotons++;
        } else {
            unmodifiedEscapeCounter++;
        }
        // Use original emission energy so scattered photons still count toward
        // the line that produced them (matches analytical escape-fraction definition).
        G4double eKeV = (info && info->originalEnergy > 0) ? info->originalEnergy
                                                            : energy / CLHEP::keV;
        if (std::abs(eKeV - 158.38)  < .05)  escape158keV++;
        if (std::abs(eKeV - 811.844) < .05)  escape812keV++;
        if (std::abs(eKeV - 846.771) < .05)  escape847keV++;
        if (std::abs(eKeV - 1238.31) < .05)  escape1238keV++;
        if (isNickelEvent && std::abs(eKeV - 158.38)  < .05)  escape158keVNickelOnly++;
        if (isNickelEvent && std::abs(eKeV - 811.844) < .05)  escape812keVNickelOnly++;
        if (isCobaltEvent && std::abs(eKeV - 846.771) < .05)  escape847keVCobaltOnly++;
        if (isCobaltEvent && std::abs(eKeV - 1238.31) < .05)  escape1238keVCobaltOnly++;
    } else if (processName == "annihil") { // Annihilation
        annihilationPhotons++;
    } else { // Misc
        G4cout << "Unhandled process: " << processName << "  Energy: " << energy << G4endl;
    }
}

G4int TrackingAction::GetLogBinIndex(G4double energy) const {
    if (energy < gEmin || energy >= gEmax) return -1;
    return static_cast<G4int>(std::log10(energy / gEmin) / gLogBinWidth);
}
