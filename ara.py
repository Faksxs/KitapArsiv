#!/usr/bin/env python3
"""Terminalden arama: python ara.py "yazar veya kitap adı"."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
ARSENAL = ROOT / "data" / "arsiv.js"


def load() -> dict:
    txt = ARSENAL.read_text(encoding="utf-8")
    return json.loads(txt[txt.index("=") + 1 : txt.rstrip().rindex(";")])


def main() -> None:
    if len(sys.argv) < 2:
        print('kullanim: python ara.py "ahmet hamdi tanpinar"')
        sys.exit(1)
    data = load()
    linkler = data["kutuphaneler"]
    q = sys.argv[1]
    from build import fold

    tokens = fold(q).split()
    hits = []
    for ad, boyut, lib, kat in data["kitaplar"]:
        if all(t in kat for t in tokens):
            hits.append((sum(kat.index(t) for t in tokens), ad, boyut, lib))
    hits.sort()
    print(f"{len(hits)} sonuc")
    for _, ad, boyut, lib in hits[:40]:
        link = linkler.get(str(lib), "")
        print(f"[{lib:>2}] {boyut:<9} {ad}")
        if link:
            print(f"      {link}/{ad.replace(' ', '%20')}")


if __name__ == "__main__":
    main()
