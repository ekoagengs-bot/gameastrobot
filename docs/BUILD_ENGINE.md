# Building the native ASTROBOT Emulator

The native PS5 translation/emulation engine is based on the pinned KytyPS5 source
submodule at `engine/kytyps5`. The source is not copied into this repository;
Git checks it out at the exact commit recorded by the submodule entry.

## Windows build

Requirements follow the upstream KytyPS5 build instructions:

- Windows 10/11 x64
- Git with submodule support
- Visual Studio 2022 / Build Tools with C++ workload and Clang tools
- CMake 3.22+, Ninja
- Qt 6.10.3 MSVC 2022 x64 (Concurrent, Network, Widgets)
- glslangValidator
- Python 3

From an x64 Visual Studio developer terminal:

```powershell
git clone --recurse-submodules https://github.com/ekoagengs-bot/gameastrobot.git
cd gameastrobot
git submodule update --init --recursive

cmake -S engine/kytyps5 -B _Build/astrobot -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang-cl -DCMAKE_CXX_COMPILER=clang-cl -DKYTY_BUILD_ORIGIN=Fork -DKYTY_BUILD_REPOSITORY=ekoagengs-bot/gameastrobot -DKYTY_PROJECT_NAME=ASTROBOT -DCMAKE_PREFIX_PATH="C:/Qt/6.10.3/msvc2022_64"

cmake --build _Build/astrobot --target launcher --parallel
cmake --install _Build/astrobot --prefix _Build/astrobot/install
```

The repository workflow **Build ASTROBOT Emulator Engine (Windows)** performs
this build on GitHub Actions. Run it from the Actions tab; download the
`ASTROBOT-Emulator-Windows-x64` artifact when the run succeeds.

## Current development boundary

This first integration pins and builds the upstream native engine with its
supported fork metadata. It does not yet claim game-specific patches or
improved Astro Bot compatibility. Engine changes should be small, tested,
clearly marked with author/date notices, and kept compatible with GPL-2.0.

See [UPSTREAM_AND_LICENSE.md](UPSTREAM_AND_LICENSE.md) for attribution and
redistribution requirements.
