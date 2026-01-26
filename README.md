# kwxFetch

This repository provides a reduced-size snapshot of wxWidgets for use with CMake's `FetchContent_Declare`. It is maintained primarily for [KeyWorks Software](https://github.com/KeyWorksRW) projects.

## Purpose

wxWidgets contains ~9,500 files across 666 folders (~156 MB). This repository reduces that to ~4,100 files in 236 folders (~79 MB) by removing:
- Documentation, samples, demos, tests
- Build system files (makefiles, Visual Studio projects, bakefiles)
- Platform-specific directories not needed for CMake builds
- Unused third-party library components

Submodules are pre-inlined, eliminating the need for recursive submodule fetches.

## Usage

```cmake
FetchContent_Declare(
    wxWidgets
    GIT_REPOSITORY "https://github.com/KeyWorksRW/kwxFetch.git"
    GIT_SHALLOW TRUE
)

FetchContent_MakeAvailable(wxWidgets)
```

## Branches

- **dev** — Tracks wxWidgets master, updated weekly (Saturday mornings UTC)

## For KeyWorks Projects

This repository is used by:
- [kwxFFI](https://github.com/KeyWorksRW/kwxFFI) — Foreign Function Interface for wxWidgets
- [wxUiEditor](https://github.com/KeyWorksRW/wxUiEditor) — RAD tool for wxWidgets

And the kwx language binding projects (kwxFortran, kwxGO, kwxJulia, etc.)

## Note

If you need wxWidgets releases (3.2.x stable), consider fetching directly from the [wxWidgets repository](https://github.com/wxWidgets/wxWidgets) using a release tag. This repository tracks development builds.

## License

wxWidgets is distributed under the [wxWindows Library Licence](https://www.wxwidgets.org/about/licence/). See the wxWidgets [README](maintain/wxReadMe.md) for details.
