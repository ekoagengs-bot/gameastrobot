from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
import tkinter as tk
from tkinter import messagebox, ttk

APP_NAME = "ASTROBOT PC"
APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "AstroBotPC"
KYTY_DIR = APP_DIR / "KytyPS5"
SETTINGS_FILE = APP_DIR / "settings.json"
RELEASE_API = "https://api.github.com/repos/KytyPS5/KytyPS5/releases/latest"
USER_AGENT = "ASTROBOT-PC/1.0"


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_settings(data: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def http_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_verified(url: str, destination: Path, expected_sha256: str, progress) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    digest = hashlib.sha256()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=60) as response, destination.open("wb") as out:
        total = int(response.headers.get("Content-Length", "0"))
        done = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            digest.update(chunk)
            done += len(chunk)
            progress(done, total)
    actual = digest.hexdigest()
    if expected_sha256 and actual.lower() != expected_sha256.lower():
        destination.unlink(missing_ok=True)
        raise RuntimeError("SHA-256 file KytyPS5 tidak cocok. Arsip dihapus demi keamanan.")


def safe_extract(zip_path: Path, target: Path) -> None:
    target_resolved = target.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for item in archive.infolist():
            member = PurePosixPath(item.filename)
            if member.is_absolute() or ".." in member.parts:
                raise RuntimeError("Arsip KytyPS5 berisi path yang tidak aman.")
            destination = (target / Path(*member.parts)).resolve()
            if target_resolved not in destination.parents and destination != target_resolved:
                raise RuntimeError("Path ekstraksi berada di luar folder aplikasi.")
        archive.extractall(target)


def find_kyty_launcher(root: Path) -> Path | None:
    candidates = list(root.rglob("kyty_launcher.exe"))
    if candidates:
        return candidates[0]
    # Some packaged builds may use a slightly different launcher filename.
    candidates = [p for p in root.rglob("*.exe") if "launcher" in p.name.lower() and "kyty" in p.name.lower()]
    return candidates[0] if candidates else None


class AstroBotPC(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("960x680")
        self.minsize(820, 580)
        self.configure(bg="#101827")
        self.settings = load_settings()
        self.kyty_path: Path | None = None
        self.status_var = tk.StringVar(value="Memeriksa instalasi KytyPS5…")
        self.release_var = tk.StringVar(value="KytyPS5: belum terpasang")
        self._setup_style()
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._log("ASTROBOT PC siap.")
        self._locate_kyty()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#101827")
        style.configure("Panel.TFrame", background="#19263a")
        style.configure("TLabel", background="#101827", foreground="#e7edf7", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 27, "bold"), foreground="#ffffff", background="#101827")
        style.configure("Muted.TLabel", foreground="#9eb0c8", background="#101827")
        style.configure("PanelTitle.TLabel", background="#19263a", foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=9)
        style.configure("Accent.TButton", background="#18a6a0", foreground="#ffffff", borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#117c78")])
        style.configure("TNotebook", background="#101827", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 9), background="#19263a", foreground="#d8e5f7")
        style.map("TNotebook.Tab", background=[("selected", "#18a6a0")])

    def _build(self) -> None:
        base = ttk.Frame(self, padding=22)
        base.pack(fill="both", expand=True)
        ttk.Label(base, text="ASTROBOT PC", style="Title.TLabel").pack(anchor="w")
        ttk.Label(base, text="KYTYPS5 INTEGRATED WINDOWS EDITION", style="Muted.TLabel").pack(anchor="w", pady=(2, 16))

        panel = self._panel(base, "EMULATOR")
        panel.pack(fill="x", pady=(0, 14))
        ttk.Label(panel, text="ASTROBOT PC mengelola dan menjalankan KytyPS5 dalam satu paket aplikasi.", background="#19263a", foreground="#d5e1f2", wraplength=850).pack(anchor="w")
        ttk.Label(panel, textvariable=self.release_var, background="#19263a", foreground="#83d8ca", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 8))
        self.progress = ttk.Progressbar(panel, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 10))
        actions = ttk.Frame(panel, style="Panel.TFrame")
        actions.pack(fill="x")
        self.install_btn = ttk.Button(actions, text="INSTALL / UPDATE KYTYPS5", style="Accent.TButton", command=self._install_kyty)
        self.install_btn.pack(side="left")
        self.launch_btn = ttk.Button(actions, text="OPEN KYTYPS5", command=self._launch_kyty, state="disabled")
        self.launch_btn.pack(side="left", padx=10)
        ttk.Button(actions, text="OPEN DATA FOLDER", command=self._open_data_folder).pack(side="right")

        tabs = ttk.Notebook(base)
        tabs.pack(fill="both", expand=True)
        system = ttk.Frame(tabs, padding=16)
        logtab = ttk.Frame(tabs, padding=16)
        tabs.add(system, text="  SYSTEM CHECK  ")
        tabs.add(logtab, text="  LOG  ")
        self._build_system(system)
        self.log = tk.Text(logtab, bg="#0b1321", fg="#cbd8eb", insertbackground="#ffffff", relief="flat", font=("Consolas", 9), wrap="word")
        self.log.pack(fill="both", expand=True)
        self.log.configure(state="disabled")

        foot = ttk.Frame(base)
        foot.pack(fill="x", pady=(10, 0))
        ttk.Label(foot, textvariable=self.status_var, style="Muted.TLabel").pack(side="left")
        ttk.Label(foot, text="Eksperimental • kompatibilitas game tidak dijamin", style="Muted.TLabel").pack(side="right")

    def _panel(self, parent, title: str):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        ttk.Label(panel, text=title, style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 12))
        return panel

    def _build_system(self, parent) -> None:
        panel = self._panel(parent, "INFORMASI WINDOWS")
        panel.pack(fill="x")
        rows = [
            ("Windows", f"{platform.system()} {platform.release()} ({platform.machine()})"),
            ("CPU", platform.processor() or "Tidak terdeteksi"),
            ("RAM", self._memory_gb()),
            ("Vulkan loader", self._vulkan_status()),
            ("Folder KytyPS5", str(KYTY_DIR)),
        ]
        for label, value in rows:
            row = ttk.Frame(panel, style="Panel.TFrame")
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label, style="PanelTitle.TLabel", width=20).pack(side="left")
            ttk.Label(row, text=value, background="#19263a", foreground="#d1deef", wraplength=650).pack(side="left", padx=8)

        ttk.Label(parent, text="ASTRO BOT dan game lain harus berasal dari dump milik Anda sendiri. Aplikasi ini tidak menyertakan game, firmware, kunci, atau file sistem PlayStation.", style="Muted.TLabel", wraplength=820).pack(anchor="w", pady=(14, 0))

    def _memory_gb(self) -> str:
        try:
            import ctypes
            class M(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = M()
            m.dwLength = ctypes.sizeof(M)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return f"{m.ullTotalPhys / (1024 ** 3):.1f} GB"
        except (AttributeError, OSError):
            pass
        return "Tidak tersedia"

    def _vulkan_status(self) -> str:
        root = Path(os.environ.get("WINDIR", r"C:\Windows"))
        found = any((root / part / "vulkan-1.dll").is_file() for part in ("System32", "SysWOW64"))
        return "Loader DLL ditemukan" if found else "Loader DLL tidak ditemukan"

    def _locate_kyty(self) -> None:
        self.kyty_path = find_kyty_launcher(KYTY_DIR) if KYTY_DIR.exists() else None
        if self.kyty_path:
            self.release_var.set(f"KytyPS5 terpasang: {self.kyty_path.name}")
            self.launch_btn.configure(state="normal")
            self.status_var.set("KytyPS5 siap dijalankan")
        else:
            self.release_var.set("KytyPS5 belum terpasang")
            self.launch_btn.configure(state="disabled")
            self.status_var.set("Klik Install / Update KytyPS5")

    def _install_kyty(self) -> None:
        self.install_btn.configure(state="disabled")
        self.launch_btn.configure(state="disabled")
        self.progress.configure(value=0)
        self.status_var.set("Mengunduh rilis resmi KytyPS5…")
        threading.Thread(target=self._install_worker, daemon=True).start()

    def _install_worker(self) -> None:
        archive = APP_DIR / "KytyPS5-windows.zip"
        staging = APP_DIR / "KytyPS5-staging"
        try:
            release = http_json(RELEASE_API)
            assets = release.get("assets", [])
            asset = next((a for a in assets if a.get("name", "").endswith("Windows-x64.zip")), None)
            if not asset:
                raise RuntimeError("Rilis resmi tidak menyediakan paket Windows-x64.zip.")
            digest = (asset.get("digest") or "").removeprefix("sha256:")
            self.after(0, lambda: self.release_var.set(f"Mengunduh {release.get('tag_name', 'KytyPS5 latest')}"))
            download_verified(asset["browser_download_url"], archive, digest, self._download_progress)
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True, exist_ok=True)
            safe_extract(archive, staging)
            launcher = find_kyty_launcher(staging)
            if not launcher:
                raise RuntimeError("kyty_launcher.exe tidak ditemukan di dalam paket rilis.")
            if KYTY_DIR.exists():
                shutil.rmtree(KYTY_DIR)
            staging.rename(KYTY_DIR)
            archive.unlink(missing_ok=True)
            self.after(0, self._install_success)
        except Exception as exc:
            self.after(0, lambda message=str(exc): self._install_failed(message))
        finally:
            try:
                if archive.exists():
                    archive.unlink()
                if staging.exists():
                    shutil.rmtree(staging)
            except OSError:
                pass

    def _download_progress(self, done: int, total: int) -> None:
        if total > 0:
            value = min(100, int(done * 100 / total))
            self.after(0, lambda v=value: self.progress.configure(value=v))
            self.after(0, lambda d=done, t=total: self.status_var.set(f"Mengunduh KytyPS5: {d // (1024*1024)} / {t // (1024*1024)} MB"))

    def _install_success(self) -> None:
        self.install_btn.configure(state="normal")
        self._locate_kyty()
        self.progress.configure(value=100)
        self._log("KytyPS5 berhasil diunduh dari rilis resmi dan diverifikasi SHA-256.")
        messagebox.showinfo("Instalasi selesai", "KytyPS5 berhasil dipasang di dalam folder data ASTROBOT PC.")

    def _install_failed(self, message: str) -> None:
        self.install_btn.configure(state="normal")
        self._locate_kyty()
        self.status_var.set("Instalasi KytyPS5 gagal")
        self._log(f"Install error: {message}")
        messagebox.showerror("Gagal memasang KytyPS5", message)

    def _launch_kyty(self) -> None:
        self._locate_kyty()
        if not self.kyty_path:
            messagebox.showwarning("KytyPS5 belum tersedia", "Klik Install / Update KytyPS5 terlebih dahulu.")
            return
        try:
            subprocess.Popen([str(self.kyty_path)], cwd=str(self.kyty_path.parent), shell=False)
            self.status_var.set("KytyPS5 dijalankan")
            self._log(f"Menjalankan {self.kyty_path}")
        except OSError as exc:
            messagebox.showerror("Tidak dapat menjalankan KytyPS5", str(exc))
            self._log(f"Launch error: {exc}")

    def _open_data_folder(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(APP_DIR))
        else:
            messagebox.showinfo("Folder data", str(APP_DIR))

    def _log(self, message: str) -> None:
        if not hasattr(self, "log"):
            return
        self.log.configure(state="normal")
        from datetime import datetime
        self.log.insert("end", f"[{datetime.now():%H:%M:%S}] {message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _close(self) -> None:
        self.destroy()


if __name__ == "__main__":
    if os.name != "nt":
        print("ASTROBOT PC dirancang untuk Windows.")
    AstroBotPC().mainloop()
