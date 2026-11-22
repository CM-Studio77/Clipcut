# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
"""The speech-to-text model: downloaded once, by itself, the first time it is needed.

Nothing has to be run by hand. (python -m studio.fetch_model still works, for getting it ahead of time.) It is
about 480 MB. It is unpacked next to where it will live and moved into place only when it is whole, so a download
that was cut off can never leave half a model behind."""
import hashlib
import os
import shutil
import tarfile
import threading
import urllib.request
from pathlib import Path

from . import config

URL = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{config.ASR_MODEL_NAME}.tar.bz2"
AR_URL = config.env("PEAKCUT_ASR_MODEL_AR_URL") or "https://huggingface.co/peakcut/speech-models/resolve/1111111111111111111111111111111111111111/sherpa-onnx-nemo-fastconformer-ar-int8.tar.bz2"
AR_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

# lang -> (label, folder_name, url, size_mb, size_bytes, sha256_hash)
MODELS = {
    "en": ("English", config.ASR_MODEL_NAME, URL, 480, 503316480, ""),
    "ar": ("Arabic", "sherpa-onnx-nemo-fastconformer-ar-int8", AR_URL, 480, 503316480, AR_HASH),
}

_locks = {k: threading.Lock() for k in MODELS}
_lock = _locks["en"]
state = {
    "doing": False, "percent": 0, "error": "",
    "en": {"doing": False, "percent": 0, "error": ""},
    "ar": {"doing": False, "percent": 0, "error": ""},
}


def known(lang: str) -> bool:
    return lang in MODELS


def folder(lang: str = "en") -> Path:
    name = MODELS[lang][1] if lang in MODELS else config.ASR_MODEL_NAME
    return config.MODELS_DIR / name


def ready(lang: str = "en") -> bool:
    """Is the whole model there: the word list and all three parts?"""
    d = folder(lang)
    if not (d / "tokens.txt").is_file():
        return False
    return all(any(d.glob(f"{part}*.onnx")) for part in ("encoder", "decoder", "joiner"))


def status(lang: str = "en") -> str:
    if ready(lang):
        return "ready"
    if state.get(lang, {}).get("doing"):
        return "downloading"
    return "missing"


def ensure(lang: str = "en", start: bool = True) -> None:
    """Make sure the model is on this computer, downloading it if it is not."""
    if ready(lang):
        return
    if not start:
        m_name = MODELS.get(lang, (lang.title(),))[0]
        raise RuntimeError(f"Speech models for {m_name} are not downloaded yet. Open Settings, Speech models to download.")
    if lang not in MODELS:
        raise ValueError(f"Unknown language model: {lang}")

    with _locks.setdefault(lang, threading.Lock()):
        if ready(lang):
            return
        m = MODELS[lang]
        dest = folder(lang)
        download_url = m[2]
        expected_hash = m[5]

        st = state.setdefault(lang, {"doing": False, "percent": 0, "error": ""})
        st.update(doing=True, percent=0, error="")
        state["doing"] = True

        print(f"\n  Downloading the speech model ({m[0]}, about {m[3]} MB)...\n", flush=True)
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        tmp = config.MODELS_DIR / f"{m[1]}.tar.bz2"
        part = config.MODELS_DIR / f"{m[1]}.unpacking"
        hasher = hashlib.sha256()

        try:
            req = download_url
            with urllib.request.urlopen(req, timeout=60) as resp:
                headers = getattr(resp, "headers", {})
                total = int(headers.get("Content-Length", 0) if isinstance(headers, dict) else (headers.get("Content-Length") or 0)) if headers else 0
                got_bytes = 0
                with open(tmp, "wb") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        hasher.update(chunk)
                        got_bytes += len(chunk)
                        if total > 0:
                            p = min(99, int(got_bytes * 100 / total))
                            st["percent"] = p
                            state["percent"] = p

            got_hash = hasher.hexdigest()
            if expected_hash and got_hash != expected_hash:
                raise ValueError(f"Downloaded file has SHA-256 fingerprint {got_hash}, not the one it expects ({expected_hash}). Nothing was unpacked.")

            shutil.rmtree(part, ignore_errors=True)
            part.mkdir(parents=True, exist_ok=True)
            with tarfile.open(tmp, "r:bz2") as t:
                for member in t.getmembers():
                    if (member.isfile() or member.isdir()) and not member.name.startswith(("/", "..")) and ".." not in member.name.split("/"):
                        t.extract(member, part)
            got = part / m[1]
            if not got.is_dir():
                if (part / "tokens.txt").is_file():
                    got = part
                else:
                    raise OSError("the download did not contain the model")
            shutil.rmtree(dest, ignore_errors=True)
            got.rename(dest)
            print(f"  Speech model {m[0]} ready.\n", flush=True)
        except Exception as e:
            err_msg = str(e)
            if "SHA-256" in err_msg:
                st["error"] = f"Downloaded archive fingerprint ({got_hash}) is not the expected one ({expected_hash})."
            else:
                st["error"] = err_msg[-200:]
            state["error"] = st["error"]
            raise RuntimeError(f"PeakCut couldn't download its speech model (about 480 MB, needed once): {e}. "
                               f"Check the internet connection and free disk space, then try again by running: python -m studio.fetch_model") from e
        finally:
            st["doing"] = False
            state["doing"] = False
            tmp.unlink(missing_ok=True)
            shutil.rmtree(part, ignore_errors=True)


def main():
    if ready():
        print("Speech model already present.")
        return
    ensure()


if __name__ == "__main__":
    main()
