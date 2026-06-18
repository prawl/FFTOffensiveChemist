"""Machine + repo paths shared by the tools layer.

ROOT is the repo checkout (lib sits one level below tools/, hence parents[2]). The Steam,
FF16Tools, and vanilla-icon paths are this box's installs; the pure-Python steps
(generate.py, gate.py) stay inside ROOT and never touch them.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRENADES = ROOT / "data" / "grenades.json"   # the only hand-edited source

# Deployable mod tree: the sparse modloader tables + the full-table .en.nxd name overrides + icons.
MOD_TABLES = ROOT / "mod" / "FFTIVC" / "tables" / "enhanced"
MOD_NXD_DIR = ROOT / "mod" / "FFTIVC" / "data" / "enhanced" / "nxd"
MOD_ITEM_NXD = MOD_NXD_DIR / "item.en.nxd"
MOD_ABILITY_NXD = MOD_NXD_DIR / "ability.en.nxd"
MOD_ICON_DIR = ROOT / "mod" / "FFTIVC" / "data" / "enhanced" / "ui" / "ffto" / "icon"

# Pristine vanilla decode caches (local-only, gitignored under working/). The .en.nxd builds
# diff their output against these to prove only the grenade rows changed.
PRISTINE_ITEM_SQLITE = ROOT / "working" / "item.en.sqlite"          # vanilla item.en, all 261 rows
PRISTINE_ABILITY_NXD = ROOT / "working" / "nxd_ability" / "ability.en.nxd"  # vanilla ability.en nxd

# FF16Tools CLI (sqlite-to-nxd / nxd-to-sqlite / tex-conv / img-conv; base game pacs are
# encrypted, every call needs -g fft). FF16TOOLS_CLI overrides it so a version bump is one
# env edit instead of a hunt through scripts.
FF16 = Path(os.environ.get(
    "FF16TOOLS_CLI",
    r"C:\Users\ptyRa\Downloads\FF16Tools.CLI-1.13.2-win-x64\win-x64\FF16Tools.CLI.exe"))

# Vanilla menu-icon source (decrypted Pac Files dump) for recolor_icons.py.
VANILLA_ICONS = Path(os.environ.get(
    "FFT_VANILLA_ICONS",
    r"C:\Users\ptyRa\OneDrive\Desktop\Pac Files\0008\ui\ffto\icon"))

# Steam install: the live Reloaded mods folder BuildLinked.ps1 deploys into.
STEAM_FFT = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
                 r"\FINAL FANTASY TACTICS - The Ivalice Chronicles")
RELOADED_MODS = STEAM_FFT / "Reloaded" / "Mods"
