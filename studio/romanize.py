"""Hinglish Romanization engine: ported from ClipKaro.

Provides standard Roman phonetic transliteration and creator-style respelling
for Hindi (Devanagari) and Urdu in video captions and titles.

Creators write Hinglish in chats and subtitles using informal phonetic Roman spellings:
"nahi" instead of "nahin", "kyunki" instead of "kyonki", "wahan" instead of "vahaan".
This module maps standard transcriptions to creator conventions, supports custom
per-project romanize dictionary tables, and integrates with PeakCut's algorithmic
Devanagari/Urdu transliterator (`studio.roman`).
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from . import roman

ROMAN_FOR = ("hinglish", "hi", "ur", "hindi", "urdu")
_PUNCT = {"।": ".", "॥": "."}

# The Hinglish speech model respellings: how Hindi creators actually type words in subtitles.
ROMAN_RESPELL = {
    "nahin": "nahi", "nahi": "nahi", "vah": "wo", "vo": "wo", "yah": "ye", "ham": "hum", "kuchh": "kuch",
    "achchha": "accha", "achchhi": "acchi", "achchhe": "acche", "mainne": "maine", "kyonki": "kyunki",
    "kyon": "kyun", "pahle": "pehle", "pahla": "pehla", "pahli": "pehli", "zyaada": "zyada",
    "vahaan": "wahan", "yahaan": "yahan", "jahaan": "jahan", "kahaan": "kahan", "hamen": "humein",
    "hamaare": "hamare", "hamaara": "hamara", "hamaari": "hamari", "hamne": "humne", "hamko": "humko",
    "tumhaara": "tumhara", "tumhaare": "tumhare", "tumhaari": "tumhari", "shaayad": "shayad", "thik": "theek",
    "chiz": "cheez", "chizen": "cheezein", "chizon": "cheezon", "kaaphi": "kaafi", "chaahie": "chahiye",
    "jaega": "jayega", "jaegi": "jayegi", "jaenge": "jayenge", "vagairah": "wagairah", "ismen": "ismein",
    "usmen": "usmein", "jismen": "jismein", "inmen": "inmein", "unmen": "unmein", "vaala": "wala",
    "vaali": "wali", "vaale": "wale", "vaise": "waise", "vaisa": "waisa", "vahi": "wahi", "vajah": "wajah",
    "vaapas": "wapas", "baahar": "bahar", "daadi": "dadi", "unhonne": "unhone", "inhonne": "inhone",
    "oopar": "upar", "dikhaaya": "dikhaya", "bataaya": "bataya", "gaanv": "gaon", "islie": "isliye",
    "isilie": "isliye", "khaana": "khana", "khaane": "khane", "bachche": "bacche", "bachchon": "bacchon",
    "dekhana": "dekhna", "aavaaz": "awaaz", "sirph": "sirf", "taraph": "taraf", "jivan": "jeevan",
    "shuroo": "shuru", "chaahoonga": "chahunga", "chaahta": "chahta", "chaahti": "chahti",
    "chaahte": "chahte", "pichhe": "peeche", "mahsoos": "mehsoos", "bachapan": "bachpan",
    "dauraan": "dauran", "dhyaan": "dhyan", "baaten": "baatein", "pitaaji": "pitaji", "ajib": "ajeeb",
    "kahaani": "kahani", "mitha": "meetha", "nae": "naye", "niklata": "nikalta", "khatm": "khatam",
    "unhen": "unhe", "inhen": "inhe", "sochate": "sochte", "rakhata": "rakhta", "karib": "kareeb",
    "donon": "dono", "dhire": "dheere", "karoonga": "karunga", "dekhie": "dekhiye", "karie": "kariye",
    "lijie": "lijiye", "dijie": "dijiye", "boliye": "boliye", "gae": "gaye", "gai": "gayi", "aae": "aaye",
    "aai": "aayi", "rupe": "rupaye", "jaata": "jata", "jaati": "jati", "jaate": "jate", "jaana": "jana",
    "aata": "aata", "raavan": "Ravan", "raam": "Ram", "bhaarat": "Bharat", "hanumaan": "Hanuman",
    "zindagi": "zindagi", "ekdam": "ekdum", "vagaira": "wagaira", "hamesha": "hamesha", "baare": "baare",
    "saare": "saare", "saari": "saari", "poora": "poora", "poori": "poori", "kahte": "kehte", "kah": "keh",
    "kahna": "kehna", "kaha": "kaha", "samajh": "samajh", "aaainge": "aayenge", "aaenge": "aayenge",
    "sakoonga": "sakunga", "hoonga": "hunga", "loonga": "lunga", "doonga": "dunga", "boloon": "bolun",
}


def has_devanagari(text: str) -> bool:
    """Check if string contains Devanagari script characters."""
    return roman.has_hindi(text)


def split_word(w: str) -> tuple[str, str, str]:
    """'"करेंगे।' -> ('"', 'करेंगे', '।'): leading punctuation, core word, trailing punctuation."""
    t = unicodedata.normalize("NFC", str(w or ""))
    i, j = 0, len(t)
    while i < j and unicodedata.category(t[i])[0] not in "LMN":
        i += 1
    while j > i and unicodedata.category(t[j - 1])[0] not in "LMN":
        j -= 1
    return t[:i], t[i:j], t[j:]


def variant(core: str) -> str:
    """Lookup key: NFC normalized and without nukta, so ज़रूर and जरूर share one entry."""
    return unicodedata.normalize("NFC", str(core or "")).replace("़", "")


def key_of(core: str) -> str:
    """Lookup key: Devanagari as written (no nukta), English letters in lower case."""
    return variant(core) if has_devanagari(core) else variant(core).lower()


def respelled(core: str, table: dict | None = None) -> str | None:
    """The creator spelling of an English-letter word, preserving initial capitalization."""
    tbl = table if table is not None else ROMAN_RESPELL
    v = tbl.get(key_of(core))
    if not v or v == core:
        return None
    if core[:1].isupper() and v[:1].islower():
        return v[:1].upper() + v[1:]
    return v


def load_table(source: dict | str | Path | None = None) -> dict:
    """Build romanization table: ROMAN_RESPELL + custom map from file or dict."""
    table = {k: v for k, v in ROMAN_RESPELL.items() if v != k}
    if not source:
        return table

    custom = {}
    if isinstance(source, dict):
        custom = source
    elif isinstance(source, (str, Path)):
        p = Path(source)
        if p.is_dir():
            p = p / "romanize.json"
        if p.is_file():
            try:
                custom = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                custom = {}

    if isinstance(custom, dict):
        for k, v in custom.items():
            if isinstance(v, str) and v.strip() and not str(k).startswith("_"):
                table[key_of(str(k))] = v.strip()
    return table


def apply(words: list[dict], table: dict | None = None, fallback_algorithmic: bool = True) -> tuple[list[dict], list[str]]:
    """Convert caption word tokens with Hindi/Urdu text to Roman Hinglish.

    Each word token is a dict with at least {'w': word, 's': start, 'e': end}.
    Returns (updated_words, missing_words).
    """
    tbl = load_table(table)
    out: list[dict] = []
    missing: list[str] = []

    for w in words:
        raw_w = str(w.get("w", ""))
        pre, core, post = split_word(raw_w)
        if not core:
            out.append(dict(w))
            continue

        if has_devanagari(core):
            r = tbl.get(variant(core))
            if r:
                fixed = pre + r + "".join(_PUNCT.get(c, c) for c in post)
                out.append({**w, "w": fixed, "orig": raw_w})
            elif fallback_algorithmic:
                algo = roman.to_roman(core)
                fixed = pre + algo + "".join(_PUNCT.get(c, c) for c in post)
                out.append({**w, "w": fixed, "orig": raw_w})
            else:
                missing.append(core)
                out.append(dict(w))
        elif roman.needs_roman(core):
            algo = roman.to_roman(core)
            fixed = pre + algo + "".join(_PUNCT.get(c, c) for c in post)
            out.append({**w, "w": fixed, "orig": raw_w})
        else:
            # English word or Hinglish model respelling
            resp = respelled(core, tbl) or core
            fixed = "".join(_PUNCT.get(c, c) for c in pre) + resp + "".join(_PUNCT.get(c, c) for c in post)
            out.append({**w, "w": fixed, "orig": raw_w} if fixed != raw_w else dict(w))

    return out, missing


def romanize_text(text: str, custom_map: dict | None = None) -> str:
    """Full-text romanization applying Hinglish respellings and Devanagari transliteration."""
    if not text:
        return ""
    table = load_table(custom_map)
    tokens = text.split(" ")
    out_tokens = []
    for tok in tokens:
        pre, core, post = split_word(tok)
        if not core:
            out_tokens.append(tok)
            continue
        if has_devanagari(core):
            r = table.get(variant(core))
            if r:
                out_tokens.append(pre + r + "".join(_PUNCT.get(c, c) for c in post))
            else:
                algo = roman.to_roman(core)
                out_tokens.append(pre + algo + "".join(_PUNCT.get(c, c) for c in post))
        elif roman.needs_roman(core):
            out_tokens.append(pre + roman.to_roman(core) + "".join(_PUNCT.get(c, c) for c in post))
        else:
            resp = respelled(core, table) or core
            out_tokens.append("".join(_PUNCT.get(c, c) for c in pre) + resp + "".join(_PUNCT.get(c, c) for c in post))
    return " ".join(out_tokens)


def wants_roman(language: str | None, setting: str = "roman") -> bool:
    """Check if Roman Hinglish captions are requested for this language."""
    lang = (language or "").strip().lower()
    return lang in ROMAN_FOR and setting == "roman"


def for_captions(meta: dict, table: dict | None = None) -> dict:
    """Transform clip meta words into Roman Hinglish captions."""
    if not meta or "words" not in meta:
        return meta
    words_out, _ = apply(meta["words"], table)
    return {**meta, "words": words_out}
