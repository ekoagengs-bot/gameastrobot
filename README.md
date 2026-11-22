# ASTROBOT PC — KytyPS5 Integrated Edition

ASTROBOT PC is a Windows desktop front end that installs, updates, and launches the official KytyPS5 Windows build from inside one application.

**Important architecture note:** the ASTROBOT PC executable is the single user-facing app. On first use it downloads the official KytyPS5 Windows x64 release into its private application-data folder, verifies the release asset's published SHA-256 digest, extracts it, and launches Kyty's own launcher. Kyty remains a separately licensed third-party component; its binaries are not copied into this repository or merged into our source.

## Features
- Install/update KytyPS5 from the official GitHub Releases API.
- Download the Windows x64 release only.
- Verify SHA-256 when the release publishes a digest.
- Safe ZIP extraction (rejects path traversal).
- Launch KytyPS5 from the ASTROBOT PC interface.
- Basic Windows, CPU, RAM and Vulkan-loader information.
- Store emulator files and settings under `%APPDATA%\AstroBotPC`.

## Quick start
1. Download this repository as ZIP and extract it.
2. Install Python 3.10+ for Windows if you want to run from source.
3. Double-click `run.bat`.
4. Click **INSTALL / UPDATE KYTYPS5** and wait for the official release download.
5. Click **OPEN KYTYPS5**. Use Kyty's own interface and follow its official documentation for adding/launching supported game dumps.

## Build a single ASTROBOT PC EXE
Run `build.bat`. The output is `dist\ASTROBOT-PC.exe`.

The EXE is the single front-end application; on first run it obtains the KytyPS5 runtime from the official release. This avoids redistributing third-party binaries in this repository and allows the emulator to be updated independently.

## Official emulator
- Project: https://github.com/KytyPS5/KytyPS5
- Releases: https://github.com/KytyPS5/KytyPS5/releases
- License: KytyPS5 is GPL-2.0. Review its license and notices before redistributing a combined package.

## System requirements
- Windows 10/11 x64
- Vulkan 1.3-capable GPU and current vendor driver (required by KytyPS5)
- Internet access for the first KytyPS5 installation/update
- ASTROBOT PC source run: Python 3.10+ (Tkinter included in standard Windows installer)

## Legal and compatibility notice
KytyPS5 is experimental and game compatibility/performance is not guaranteed. ASTROBOT PC does not include or download games, PlayStation firmware, encryption keys, BIOS, or other proprietary system files. Use only game dumps and system files you are legally entitled to use. Follow KytyPS5's official documentation and compatibility list. ASTROBOT PC is an independent community front end and is not affiliated with Sony or the KytyPS5 developers.

## Local application data
`%APPDATA%\AstroBotPC\KytyPS5` — installed emulator files.
