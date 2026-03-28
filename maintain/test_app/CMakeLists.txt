cmake_minimum_required(VERSION 3.20)
project(wxtest LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# This test app is meant to be built:
# 1. From within the wxWidgets build tree (add_subdirectory), or
# 2. After installing wxWidgets and setting wxWidgets_DIR
#
# For testing kwxFetch, we add this to the main CMake build

# Detect if we're being built as part of wxWidgets
if(TARGET wx::core)
    # Built as subdirectory of wxWidgets
    add_executable(wxtest WIN32 main.cpp)
    target_link_libraries(wxtest PRIVATE wx::core wx::base)
else()
    # Standalone build - use FindwxWidgets module
    find_package(wxWidgets REQUIRED COMPONENTS core base)
    include(${wxWidgets_USE_FILE})
    add_executable(wxtest WIN32 main.cpp)
    target_link_libraries(wxtest PRIVATE ${wxWidgets_LIBRARIES})
endif()
