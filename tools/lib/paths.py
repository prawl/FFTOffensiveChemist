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
# diff their output against these to prove only the grenade rows changed -- so the baseline MUST
# be true vanilla. It is DERIVED from VANILLA_EN_PAC below on every nxd build (see patch_names.py
# / patch_ability_names.py refresh_pristine), never hand-placed: a manual decode from a modded
# install silently poisons every other row of the shipped name table.
VANILLA_PAC_DIR = ROOT / "working" / "vanilla_pac"                  # pac extracts land here
PRISTINE_ITEM_SQLITE = ROOT / "working" / "item.en.sqlite"          # vanilla item.en, all 261 rows
PRISTINE_ABILITY_NXD = VANILLA_PAC_DIR / "nxd" / "ability.en.nxd"   # vanilla ability.en nxd

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

# Vanilla source of truth for the .en.nxd NAME tables: the game's base localized data pac.
# Both item.en.nxd and ability.en.nxd live inside it (encrypted; every FF16Tools call needs
# -g fft). The nxd builders re-derive their pristine baseline from this on every build, so a
# modded working/ cache can't poison the shipped names. FFT_VANILLA_EN_PAC overrides the path.
VANILLA_EN_PAC = Path(os.environ.get(
    "FFT_VANILLA_EN_PAC",
    str(STEAM_FFT / "data" / "enhanced" / "0004.en.pac")))
