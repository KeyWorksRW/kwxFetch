# kwxFetch

This repository provides a reduced-size snapshot of wxWidgets for use with CMake's `FetchContent_Declare`. It is maintained primarily for [KeyWorks Software](https://github.com/KeyWorksRW) projects.

## Purpose

wxWidgets contains ~9,500 files across 666 folders (~156 MB). This repository reduces that to ~4,100 files in 236 folders (~79 MB) by removing:
- Documentation, samples, demos, tests
- Build system files (makefiles, Visual Studio projects, bakefiles)
- Platform-specific directories not needed for CMake builds
- Unused third-party library components

Submodules are pre-inlined, eliminating the need for recursive submodule fetches.

## Releases

Two release archives are published automatically each Saturday as `.tar.xz` files.
CMake 3.15+ decompresses `.tar.xz` natively on Windows, Linux, and macOS — no system tools required.

| Release tag | Tracks | Rebuild |   |
|---|---|---|---|
| `wx-3.2-latest` | wxWidgets `3.2` branch (stable) | Only when `wxRELEASE_NUMBER` increments | ~6-month cadence |
| `wx-dev-latest` | wxWidgets `master` branch | Every Saturday | Bleeding edge |

## Usage

Replace `KeyWorksRW` with your actual org/username if forked.

### Stable (3.2.x)

```cmake
FetchContent_Declare(
    wxWidgets
    URL https://github.com/KeyWorksRW/kwxFetch/releases/download/wx-3.2-latest/kwxFetch-source.tar.xz
)

FetchContent_MakeAvailable(wxWidgets)
```

### Bleeding Edge (master)

```cmake
FetchContent_Declare(
    wxWidgets
    URL https://github.com/KeyWorksRW/kwxFetch/releases/download/wx-dev-latest/kwxFetch-source.tar.xz
)

FetchContent_MakeAvailable(wxWidgets)
```

## For KeyWorks Projects

This repository is used by:
- [kwxFFI](https://github.com/KeyWorksRW/kwxFFI) — Foreign Function Interface for wxWidgets
- [wxUiEditor](https://github.com/KeyWorksRW/wxUiEditor) — RAD tool for wxWidgets

And the kwx language binding projects (kwxFortran, kwxGO, kwxJulia, etc.)

## License

wxWidgets is distributed under the [wxWindows Library Licence](https://www.wxwidgets.org/about/licence/).
