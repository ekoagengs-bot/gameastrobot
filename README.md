# ASTROBOT PC

Windows launcher and setup companion for legally obtained PlayStation game dumps. This is **not itself a PS5 emulator**. It launches an emulator installed separately by the user.

## Features
- Select an external emulator executable and a game entry file.
- Launch the emulator with the selected file as an argument.
- System information: Windows, CPU, RAM, display adapters, Vulkan runtime availability.
- Saved local configuration in %APPDATA%\AstroBotPC.
- No game, firmware, keys, BIOS, or proprietary system files are bundled or downloaded.

## Requirements
- Windows 10/11 x64
- Python 3.10+ (Tkinter included with the standard Windows installer)
- A separately installed compatible emulator
- Official current GPU driver; Vulkan capability depends on the emulator and GPU.

## Run
Install Python from https://www.python.org/downloads/windows/, enable "Add Python to PATH", then double-click `run.bat`.

## Build standalone EXE
Run `build.bat`. PyInstaller is installed for the packaging step and the executable is created at `dist\ASTROBOT-PC.exe`.

## Important
PS5 emulation is experimental. Compatibility and performance vary and are not guaranteed. The launcher does not decrypt games, bypass console security, or provide system software. Use only game dumps and system files you are legally entitled to use. Follow the selected emulator's official instructions for supported formats.

## Project layout
- `src/astrobot_pc.py` – application
- `run.bat` – run from source
- `build.bat` – package to EXE
- `requirements-build.txt` – build dependency

## License
ASTROBOT PC source: MIT. Third-party emulator software remains under its own license.