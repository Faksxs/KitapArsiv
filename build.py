#!/usr/bin/env python3
"""Google Sheet CSV -> data/arsiv.js (arama indeksi)."""
from __future__ import annotations

import csv
import datetime
import io
import json
import pathlib
import re
import sys
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SHEET_ID = "1N04dyNeGk0aYOhEHmg_rSu5vnuN5eNZAvXezBfvAbJo"
GID = "194035655"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
OUT = ROOT / "data" / "arsiv.js"
CACHE = ROOT / "data" / "kitaplar.csv"

TR_MAP = str.maketrans({
    "ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g",
    "ü": "u", "Ü": "u", "ö": "o", "Ö": "o", "ç": "c", "Ç": "c",
})
FOLD_RE = re.compile(r"[^a-z0-9]")


def fold(text: str) -> str:
    t = unicodedata.normalize("NFD", text.translate(TR_MAP).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return FOLD_RE.sub(" ", t)


def load_csv() -> str:
    if len(sys.argv) > 1:
        return pathlib.Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    try:
        req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8-sig")
    except Exception as exc:  # noqa: BLE001
        if CACHE.exists():
            print(f"cevrimdisi onbellek kullanildi ({exc})")
            return CACHE.read_text(encoding="utf-8")
        raise
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(raw, encoding="utf-8")
    return raw


def parse(raw: str) -> list[list]:
    rows: list[list] = []
    for rec in csv.reader(io.StringIO(raw)):
        if len(rec) < 3:
            continue
        ad = rec[0].strip()
        if not ad or ad.lower() == "kitap":
            continue
        boyut = rec[1].strip()
        m = re.search(r"\d+", rec[2])
        lib = int(m.group()) if m else 0
        rows.append([ad, boyut, lib])
    return rows


def main() -> None:
    raw = load_csv()
    rows = parse(raw)
    links = json.loads((ROOT / "kutuphaneler.json").read_text(encoding="utf-8"))
    payload_date = (
        datetime.date.fromtimestamp(CACHE.stat().st_mtime).isoformat()
        if CACHE.exists()
        else datetime.date.today().isoformat()
    )
    out = {
        "guncelleme": payload_date,
        "kaynak": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}",
        "kutuphaneler": links.get("kutuphaneler", {}),
        "kutuphaneSayilari": {},
        "kitaplar": [[ad, boyut, lib, fold(ad)] for ad, boyut, lib in rows],
    }
    for _, _, lib in rows:
        out["kutuphaneSayilari"][str(lib)] = out["kutuphaneSayilari"].get(str(lib), 0) + 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text("window.ARSIV=" + payload + ";\n", encoding="utf-8")
    print(f"{len(rows)} kitap, {len(out['kutuphaneler'])} kütüphane linki -> {OUT}")
    print(f"dosya boyutu: {OUT.stat().st_size / 1048576:.1f} MB")


if __name__ == "__main__":
    main()
