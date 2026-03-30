#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iostream>

// Geant4
#include "G4Material.hh"
#include "G4Element.hh"
#include "G4Isotope.hh"
#include "G4NistManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4Threading.hh"
#include "G4ios.hh"
#include "globalVars.hh"

// -----------------------------
// Struct to hold one shell row
// -----------------------------
struct ShellRow {
    int shell;
    double rzo_cm;
    double vel_cm_s;
    double rho_g_cc;
    double X_C;
    double X_Si;
    double X_Ni56;
    double Menc_Msun;
};

// ------------------------------------
// Reads your .dat file into vector rows
// ------------------------------------
std::vector<ShellRow> ReadZoneFileDAT(const std::string& filename)
{
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
    }

    std::vector<ShellRow> rows;
    std::string line;

    while (std::getline(file, line)) {

        // skip empty lines
        if (line.empty()) continue;

        // skip comment lines
        if (line[0] == '#') continue;

        // skip header line (starts with "shell")
        if (line.rfind("shell", 0) == 0) continue;

        std::stringstream ss(line);

        ShellRow row{};
        ss >> row.shell
           >> row.rzo_cm
           >> row.vel_cm_s
           >> row.rho_g_cc
           >> row.X_C
           >> row.X_Si
           >> row.X_Ni56
           >> row.Menc_Msun;

        // if parsing failed, ignore line
        if (ss.fail()) continue;

        rows.push_back(row);
    }

    return rows;
}

// -------------------------------------------------------------------
// Creates materials and geometry info like OLDcreateGeometry()
// but using the columns from the .dat file
// -------------------------------------------------------------------
void createGeometry(const std::string& filename,
                                       std::vector<G4Material*>& zoneMaterials,
                                       std::vector<double>& innerRadii,
                                       std::vector<double>& outerRadii,
                                       double& sphereRadius,
                                       double& worldSize)
{
    if (!G4Threading::IsMasterThread()) return;

    auto shellData = ReadZoneFileDAT(filename);

    if (shellData.empty()) {
        throw std::runtime_error("No valid data rows read from file.");
    }

    int minZone = 0;
    int maxZone = (int)shellData.size() - 1;

    G4NistManager* nist = G4NistManager::Instance();

    // Elements we need
    G4Element* C  = nist->FindOrBuildElement("C");
    G4Element* Si = nist->FindOrBuildElement("Si");

    // --- Ni56 isotope definition ---
    G4Isotope* Ni56 = new G4Isotope("Ni56", 28, 56, 55.94213 * g / mole);
    G4Element* Ni = new G4Element("Ni", "Ni", 1);
    Ni->AddIsotope(Ni56, 100.0 * perCent);

    for (int zone = minZone; zone <= maxZone; zone++) {

        std::string materialName = "zoneMaterial" + std::to_string(zone);

        // Outer boundary directly from file
        double rOuter = shellData[zone].rzo_cm;

        // Inner boundary is previous zone's outer radius
        double rInner = 0.0;
        if (zone > 0) {
            rInner = shellData[zone - 1].rzo_cm;
        }

        // Store radii in Geant4 units
        innerRadii.push_back(rInner * cm);
        outerRadii.push_back(rOuter * cm);

        // Density already correct at snapshot time
        double zoneDensity = densityMultiplier * shellData[zone].rho_g_cc;

        // Composition
        double X_C  = shellData[zone].X_C;
        double X_Si = shellData[zone].X_Si;
        double X_Ni = shellData[zone].X_Ni56;

        // Normalize just in case
        double X_sum = X_C + X_Si + X_Ni;
        if (X_sum <= 0.0) {
            throw std::runtime_error("Bad composition sum in zone " + std::to_string(zone));
        }

        X_C  /= X_sum;
        X_Si /= X_sum;
        X_Ni /= X_sum;

        // Create material
        G4Material* zoneMaterial = new G4Material(materialName,
                                                  zoneDensity * g / cm3,
                                                  3);

        zoneMaterial->AddElement(C,  X_C  * 100.0 * perCent);
        zoneMaterial->AddElement(Si, X_Si * 100.0 * perCent);
        zoneMaterial->AddElement(Ni, X_Ni * 100.0 * perCent);

        zoneMaterials.push_back(zoneMaterial);

        G4cout << "Zone " << zone
               << " rho=" << zoneDensity
               << " g/cc, rInner=" << rInner
               << " cm, rOuter=" << rOuter
               << " cm"
               << G4endl;
    }

    sphereRadius = outerRadii[maxZone];
    worldSize = 1.01 * sphereRadius;
}