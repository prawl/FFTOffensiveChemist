"""Loader + plural helper for data/grenades.json (the single hand-edited source)."""
import json

from .paths import GRENADES


def load_grenades():
    """Return the parsed grenades.json document ({_meta, grenades:[...], remedy:{...}})."""
    return json.loads(GRENADES.read_text(encoding="utf-8"))


def plural(name):
    """English plural for the item table's NamePlural column (e.g. 'Venom Flask' -> 'Venom Flasks')."""
    low = name.lower()
    return low + ("es" if low.endswith(("s", "x", "z", "ch", "sh")) else "s")
