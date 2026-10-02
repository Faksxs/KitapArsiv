#!/usr/bin/env python3
"""Yandex Disk paylasim klasoru -> data/yandex.js (arama indeksi).

Kaynak: https://disk.yandex.com.tr/d/GXdwZeTBdhaTZg
("kitap ve kahve kokusuna aittir" - harf klasorleri icinde ~5 bin epub)

Kullanim:
    python build-yandex.py

Taramadan sonra yandex.html'i tarayicida acman yeterli.
Indirme baglantilari tiklanma aninda Yandex API'den alinir
(CORS acik, anahtar gerekmez), bu yuzden indekste sadece
dosya yolu saklanir.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import time
import urllib.parse
import urllib.request

from build import fold

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "data" / "yandex.js"

PUBLIC_LINK = "https://disk.yandex.com.tr/d/GXdwZeTBdhaTZg"
API = "https://cloud-api.yandex.net/v1/disk/public/resources"


def api(path: str, limit: int = 500, offset: int = 0) -> dict:
    qs = urllib.parse.urlencode(
        {"public_key": PUBLIC_LINK, "path": path, "limit": limit, "offset": offset}
    )
    last: Exception | None = None
    for bekle in (1, 2, 4, 8, 16):
        try:
            req = urllib.request.Request(
                API + "?" + qs, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - 429/limit icin bekle-tekrar dene
            last = exc
            time.sleep(bekle)
    raise RuntimeError(f"API hatasi ({path}): {last}")


def list_all(path: str) -> list[dict]:
    out: list[dict] = []
    off = 0
    while True:
        data = api(path, limit=500, offset=off)
        emb = data.get("_embedded", {})
        items = emb.get("items", [])
        out.extend(items)
        off += len(items)
        if off >= emb.get("total", 0):
            break
    time.sleep(0.2)  # anonim limite takilmamak icin kisa bekleme
    return out


def boyut_str(size: int | None) -> str:
    if not size:
        return ""
    if size < 1024:
        return f"{size} B"
    if size < 1048576:
        return f"{size / 1024:.0f} KB"
    return f"{size / 1048576:.1f} MB"


def main() -> None:
    kitaplar: list[list] = []
    harf_sayilari: dict[str, int] = {}
    ust = list_all("/")
    kuyruk = [it["path"] for it in ust if it["type"] == "dir"]
    print(f"{len(kuyruk)} harf klasoru bulundu")
    for harf_path in kuyruk:
        harf = harf_path.strip("/")
        for it in list_all(harf_path):
            if it["type"] == "dir":
                yazar = it["path"]
                for f in list_all(yazar):
                    if f["type"] == "dir":
                        continue  # 3. seviyeden derinde klasor yok (taramada 0 cikti)
                    ad = f["name"]
                    klasor = yazar.strip("/")
                    kitaplar.append(
                        [ad, boyut_str(f.get("size")), klasor, fold(ad), f["path"]]
                    )
            else:
                ad = it["name"]
                kitaplar.append(
                    [ad, boyut_str(it.get("size")), harf, fold(ad), it["path"]]
                )
        harf_sayilari[harf] = sum(1 for k in kitaplar if k[2] == harf or k[2].startswith(harf + "/"))
        print(f"  {harf}: toplam {len(kitaplar)} kayit")
    out = {
        "guncelleme": datetime.date.today().isoformat(),
        "kaynak": PUBLIC_LINK,
        "ad": "kitap ve kahve kokusuna aittir",
        "harfSayilari": harf_sayilari,
        "kitaplar": kitaplar,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text("window.YANDEX=" + payload + ";\n", encoding="utf-8")
    print(f"{len(kitaplar)} kitap -> {OUT}")
    print(f"dosya boyutu: {OUT.stat().st_size / 1048576:.1f} MB")


if __name__ == "__main__":
    main()
