from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "ASTROBOT PC"
APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "AstroBotPC"
SETTINGS_FILE = APP_DIR / "settings.json"


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_settings(data: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_memory_gb() -> str:
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return f"{status.ullTotalPhys / (1024 ** 3):.1f} GB"
    except (AttributeError, OSError):
        pass
    return "Unavailable"


class AstroBotPC(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1000x700")
        self.minsize(860, 600)
        self.configure(bg="#101827")
        self.settings = load_settings()
        self.emulator_var = tk.StringVar(value=self.settings.get("emulator", ""))
        self.game_var = tk.StringVar(value=self.settings.get("game", ""))
        self.status_var = tk.StringVar(value="Ready")
        self._setup_style()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._log("ASTROBOT PC started.")
        self._log("Launcher only: install a compatible emulator separately.")

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#101827")
        style.configure("Panel.TFrame", background="#19263a")
        style.configure("TLabel", background="#101827", foreground="#e7edf7",
                        font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 25, "bold"),
                        foreground="#ffffff", background="#101827")
        style.configure("Muted.TLabel", foreground="#9eb0c8", background="#101827")
        style.configure("PanelTitle.TLabel", background="#19263a",
                        foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Accent.TButton", background="#18a6a0",
                        foreground="#ffffff", borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#117c78")])
        style.configure("TEntry", fieldbackground="#0c1524", foreground="#e7edf7")
        style.configure("TNotebook", background="#101827", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 9), background="#19263a",
                        foreground="#d8e5f7")
        style.map("TNotebook.Tab", background=[("selected", "#18a6a0")],
                  foreground=[("selected", "#ffffff")])

    def _build(self) -> None:
        base = ttk.Frame(self, padding=22)
        base.pack(fill="both", expand=True)
        ttk.Label(base, text="ASTROBOT PC", style="Title.TLabel").pack(anchor="w")
        ttk.Label(base, text="PLAYSTATION GAME LAUNCHER  |  WINDOWS",
                  style="Muted.TLabel").pack(anchor="w", pady=(2, 16))

        self.tabs = ttk.Notebook(base)
        self.tabs.pack(fill="both", expand=True)
        home = ttk.Frame(self.tabs, padding=18)
        system = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(home, text="  HOME  ")
        self.tabs.add(system, text="  SYSTEM CHECK  ")
        self._build_home(home)
        self._build_system(system)

        foot = ttk.Frame(base)
        foot.pack(fill="x", pady=(12, 0))
        ttk.Label(foot, textvariable=self.status_var, style="Muted.TLabel").pack(side="left")
        ttk.Label(foot, text="Experimental compatibility is not guaranteed",
                  style="Muted.TLabel").pack(side="right")

    def _panel(self, parent: ttk.Frame, title: str) -> ttk.Frame:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        ttk.Label(panel, text=title, style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 12))
        return panel

    def _build_home(self, parent: ttk.Frame) -> None:
        panel = self._panel(parent, "GAME CONFIGURATION")
        panel.pack(fill="x", pady=(0, 14))
        self._path_row(panel, "Emulator executable", self.emulator_var, self._browse_emulator)
        self._path_row(panel, "Game entry file", self.game_var, self._browse_game)
        ttk.Label(panel,
                  text="Select an emulator installed separately and a game entry file from a game dump you legally own.",
                  background="#19263a", foreground="#9eb0c8", wraplength=850).pack(anchor="w", pady=(8, 12))
        actions = ttk.Frame(panel, style="Panel.TFrame")
        actions.pack(fill="x")
        ttk.Button(actions, text="LAUNCH GAME", style="Accent.TButton",
                   command=self._launch).pack(side="left")
        ttk.Button(actions, text="SAVE SETTINGS", command=self._save).pack(side="left", padx=9)
        ttk.Button(actions, text="CLEAR LOG", command=self._clear_log).pack(side="right")

        log_panel = self._panel(parent, "ACTIVITY LOG")
        log_panel.pack(fill="both", expand=True)
        self.log = tk.Text(log_panel, bg="#0b1321", fg="#cbd8eb",
                           insertbackground="#ffffff", relief="flat",
                           font=("Consolas", 9), wrap="word", height=14)
        self.log.pack(fill="both", expand=True)
        self.log.configure(state="disabled")

    def _path_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar, browse) -> None:
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, style="PanelTitle.TLabel", width=22).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(row, text="Browse", command=browse).pack(side="right")

    def _browse_emulator(self) -> None:
        path = filedialog.askopenfilename(
            title="Select emulator executable",
            filetypes=[("Windows executable", "*.exe"), ("All files", "*.*")])
        if path:
            self.emulator_var.set(path)
            self._save()

    def _browse_game(self) -> None:
        path = filedialog.askopenfilename(
            title="Select game entry file",
            filetypes=[("Game executable", "eboot.bin"), ("All files", "*.*")])
        if path:
            self.game_var.set(path)
            self._save()

    def _save(self) -> None:
        self.settings["emulator"] = self.emulator_var.get().strip()
        self.settings["game"] = self.game_var.get().strip()
        try:
            save_settings(self.settings)
            self.status_var.set("Settings saved")
            self._log("Settings saved.")
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))

    def _launch(self) -> None:
        emulator = Path(self.emulator_var.get().strip()).expanduser()
        game = Path(self.game_var.get().strip()).expanduser()
        if not emulator.is_file():
            messagebox.showerror("Emulator not found", "Choose an existing emulator .exe.")
            return
        if not game.is_file():
            messagebox.showerror("Game file not found", "Choose a valid game entry file.")
            return
        if not messagebox.askyesno(
            "Confirm launch",
            "Start the selected emulator with the selected game file as an argument?\n\n"
            "The emulator must support this launch format."):
            return
        self._save()
        try:
            subprocess.Popen([str(emulator), str(game)], cwd=str(emulator.parent),
                             shell=False)
            self.status_var.set("Emulator started")
            self._log(f"Started: {emulator.name}")
            self._log(f"Game entry: {game}")
        except OSError as exc:
            self.status_var.set("Launch failed")
            self._log(f"Launch error: {exc}")
            messagebox.showerror("Launch failed", str(exc))

    def _build_system(self, parent: ttk.Frame) -> None:
        panel = self._panel(parent, "DETECTED SYSTEM")
        panel.pack(fill="x")
        rows = [
            ("Operating system", f"{platform.system()} {platform.release()} ({platform.machine()})"),
            ("CPU", platform.processor() or "Not reported by Windows"),
            ("Physical memory", get_memory_gb()),
            ("Python runtime", sys.version.split()[0]),
            ("Vulkan loader", self._vulkan_status()),
        ]
        for label, value in rows:
            row = ttk.Frame(panel, style="Panel.TFrame")
            row.pack(fill="x", pady=6)
            ttk.Label(row, text=label, style="PanelTitle.TLabel", width=23).pack(side="left")
            ttk.Label(row, text=value, background="#19263a",
                      foreground="#d1deef").pack(side="left", padx=8)
        ttk.Button(parent, text="REFRESH CHECK", command=self._refresh_system).pack(anchor="w", pady=14)
        ttk.Label(parent,
                  text="Note: Vulkan loader presence does not confirm Vulkan 1.3 support or game compatibility. Use the GPU vendor's official driver.",
                  style="Muted.TLabel", wraplength=800).pack(anchor="w")

    def _vulkan_status(self) -> str:
        if platform.system() != "Windows":
            return "Windows check only"
        system_root = Path(os.environ.get("WINDIR", r"C:\Windows"))
        candidates = [
            system_root / "System32" / "vulkan-1.dll",
            system_root / "SysWOW64" / "vulkan-1.dll",
        ]
        return "Loader DLL found" if any(p.is_file() for p in candidates) else "Loader DLL not found"

    def _refresh_system(self) -> None:
        self.tabs.select(1)
        self._log(f"System check refreshed: {platform.platform()}")
        self.status_var.set("System information refreshed")

    def _log(self, text: str) -> None:
        if not hasattr(self, "log"):
            return
        self.log.configure(state="normal")
        self.log.insert("end", f"[{__import__('datetime').datetime.now():%H:%M:%S}] {text}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _close(self) -> None:
        self._save()
        self.destroy()


if __name__ == "__main__":
    if os.name != "nt":
        print("ASTROBOT PC is designed for Windows.")
    AstroBotPC().mainloop()
