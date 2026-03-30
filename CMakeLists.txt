cmake_minimum_required(VERSION 3.16)
project(SupernovaSimulation)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Geant4 with multithreading support
find_package(Geant4 REQUIRED COMPONENTS
    geant4
    geant4_ui
    geant4_vis
    geant4_mt
)

# Include Geant4 headers
include(${Geant4_USE_FILE})

# Source files
file(GLOB sources ${PROJECT_SOURCE_DIR}/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/*.hh)

# Executable
add_executable(SupernovaSimulation ${sources} ${headers})

# Link to Geant4 libraries (automatically includes MT libs if found)
target_link_libraries(SupernovaSimulation ${Geant4_LIBRARIES})

# Install rules (optional)
install(TARGETS SupernovaSimulation DESTINATION bin)
