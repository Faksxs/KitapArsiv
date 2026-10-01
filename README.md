# KitapArşiv — Yerel Arama

Reddit'te paylaşılan 55 kütüphanelik e-kitap arşivinin Google Sheet dizinini
(63.636 kayıt) tarayıcıda aranabilir hale getirir. Aradığınız yazar/kitap hangi
kütüphanede, tek tıkla o kütüphanenin Yandex Disk klasörü ya da doğrudan dosya
sayfası açılır.

## Kullanım

1. `ara.bat` çift tıklayın (ya da `index.html` dosyasını tarayıcıda açın).
2. Arama kutusuna yazar ya da kitap adını yazın. Türkçe yazım farkları
   (`ı/i`, `ş/s`, `ğ/g`, `ç/c`, `ö/o`, `ü/u`) ve noktalama önemsenmez:
   `tanpinar` ↔ `Tanpınar`, `bes sehir` ↔ `Beş Şehir`.
3. Sonuç satırındaki düğmeler:
   - **Dosyayı aç** — dosyanın Yandex Disk önizleme sayfası
   - **Klasör** — bulunduğu kütüphanenin tam klasörü
   - **Kopyala** — dosya adını panoya kopyalar (başka arşivde aramak için)

Kısayollar: `/` arama kutusuna odaklanır, `Esc` temizler, `Enter` ilk sonucu açar.

### Komut satırı

```bat
python ara.py "ahmet hamdi tanpinar"
```

## Dosyalar

| Dosya | Görevi |
|---|---|
| `index.html` | Arayüz (tek dosya, bağımlılık yok, sunucu gerekmez) |
| `data/arsiv.js` | 63.636 kayıtlık arama indeksi (build.py üretir) |
| `data/kitaplar.csv` | Google Sheet'ten indirilen ham CSV (önbellek) |
| `build.py` | Sheet'i indirip indeksi yeniden üretir |
| `ara.py` | Terminalde arama |
| `kutuphaneler.json` | Kütüphane no → Yandex Disk klasör linki |

## Veriyi yenileme

Google Sheet'e yeni kitap eklendiğinde:

```bat
python build.py
```

Sayfa `Ctrl+F5` ile yenilendiğinde güncel indeks yüklenir.

## Kütüphane linkleri (51–55 eksik)

Linkler Reddit postundan çıkarıldı: [r/secilmiskitap — E-Kitap Arşivi](https://www.reddit.com/r/secilmiskitap/comments/1k76y3m/ekitap_arsivi/).

Post yalnızca 1–50. kütüphanelerin linklerini içeriyor; 51–55 paylaşılmamış.
Bu kütüphanelerdeki kitaplar aramada görünür ama düğmeler "Link yok" durumundadır.
Linki bulduğunuzda `kutuphaneler.json` içine ekleyip `python build.py` çalıştırın:

```json
"51": "https://disk.yandex.az/d/LINK"
```

## Kapsam

Arama + doğru dosyaya link verme. Arşivin toplu otomatik indirilmesi (tüm
kütüphaneleri çekme) bu araçta yoktur; indirme işlemi Yandex Disk'te sizin
kontrolünüzde kalır.
