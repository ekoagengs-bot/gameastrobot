# ASTROBOT Emulator — Windows PS5 emulator fork

ASTROBOT Emulator is an independent Windows-focused community fork project
based on the open-source **KytyPS5** PlayStation 5 translation layer. The
native engine source is tracked as a pinned Git submodule at
`engine/kytyps5`; the build uses KytyPS5's supported fork metadata so builds
identify this repository as the fork.

> **Development status:** initial upstream source integration is in place.
> The native engine build is provided through GitHub Actions. Astro Bot
> compatibility and performance are not guaranteed, and this project does not
> yet contain title-specific engine patches.

## Download the native Windows build

1. Open the [ASTROBOT Emulator Engine workflow](https://github.com/ekoagengs-bot/gameastrobot/actions/workflows/build-engine-windows.yml).
2. Select **Run workflow** and wait for the build to complete successfully.
3. Download the `ASTROBOT-Emulator-Windows-x64` artifact from the completed run.
4. Extract the ZIP. The native launcher is `kyty_launcher.exe`.

To use the ASTROBOT PC desktop front end, extract the engine package into
`%APPDATA%\\AstroBotPC\\ASTROBOT-Emulator`, open ASTROBOT PC, and click
**OPEN EMULATOR**. The app checks this native fork folder first. The separate
**INSTALL OFFICIAL KYTYPS5 (FALLBACK)** option downloads the upstream release
and is not the ASTROBOT fork build.

## Build from source

See [docs/BUILD_ENGINE.md](docs/BUILD_ENGINE.md). Clone with
`git clone --recurse-submodules` and build the native Qt launcher using the
provided Windows workflow or the documented CMake commands.

## Engine and attribution

- Upstream project: https://github.com/KytyPS5/KytyPS5
- Pinned source revision: `613317216495ad7c98ea0e3743cded89d4596062`
- License: GPL-2.0-only
- Notices and redistribution guidance: [docs/UPSTREAM_AND_LICENSE.md](docs/UPSTREAM_AND_LICENSE.md)

## System requirements

- Windows 10/11 x64
- Vulkan 1.3-capable GPU and a current graphics driver
- For building: Visual Studio 2022 C++/Clang tools, CMake, Ninja, Qt 6,
  glslangValidator and Python 3

## Legal and compatibility notice

This is an independent community fork and is not affiliated with Sony
Interactive Entertainment or PlayStation. It does not distribute commercial
games, PlayStation firmware, encryption keys, BIOS, or other proprietary
system software. Use only game dumps and system files you are legally
entitled to use. Read the upstream license and preserve all required notices.
