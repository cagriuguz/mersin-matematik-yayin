"""Yayın kontrolü: kuyruk.json'a göre profilde olması gerekenler gerçekten çıktı mı.
SORUN varsa çıkış kodu 1 (GitHub Actions başarısız olur, GitHub e-posta atar). Aynı sorun için bir kez uyarır.
Ortam: IG_TOKEN (yalnız yazdırılmaz). --kuru: Instagram'a sormaz. --durum DOSYA: uyarı kaydı. --simdi ISO: test saati."""
import json, os, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

KURU = "--kuru" in sys.argv
def arg(ad, varsayilan):
    return sys.argv[sys.argv.index(ad) + 1] if ad in sys.argv else varsayilan
KUYRUK = arg("--kuyruk", "kuyruk.json")
DURUM = arg("--durum", "kontrol-uyari.json")
SIMDI = datetime.fromisoformat(arg("--simdi", datetime.now(timezone.utc).isoformat()))
GEC = timedelta(minutes=45)
GERI = timedelta(days=7)  # yayinlandi olanları yalnız son 7 günde API'den sına


def var_mi(medya_id):
    """True/False; API erişim hatası (token vb.) ise ('hata', mesaj)."""
    q = urllib.parse.urlencode({"fields": "id,timestamp", "access_token": os.environ["IG_TOKEN"]})
    try:
        urllib.request.urlopen(f"https://graph.instagram.com/v21.0/{medya_id}?{q}", timeout=30).read()
        return True
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode()).get("error", {})
        except Exception:
            err = {}
        if e.code == 404 or err.get("code") == 100:
            return False
        return ("hata", f"HTTP {e.code} kod {err.get('code')} {err.get('message', '')[:80]}")
    except Exception as e:
        return ("hata", str(e)[:80])


def main():
    kuyruk = json.load(open(KUYRUK, encoding="utf-8"))
    sorunlar = {}
    for g in kuyruk:
        t = datetime.fromisoformat(g["tarih"])
        if g.get("onay") is not True or g.get("yedek") or g.get("durum") == "planlandi":
            continue
        if g.get("durum") != "yayinlandi":
            if t + GEC < SIMDI:
                sorunlar[g["id"]] = f"{g['id']}: {g['tarih'][:16]} yayınlanmadı (45 dk geçti)"
        elif g.get("medya_id") and not KURU and SIMDI - GERI < t <= SIMDI:
            r = var_mi(g["medya_id"])
            if r is False:
                sorunlar[g["id"]] = f"{g['id']}: yayınlandı görünüyor ama Instagram'da bulunamadı (medya_id)"
            elif isinstance(r, tuple):
                sorunlar["api"] = f"Instagram API denetimi başarısız ({r[1]})"
    try:
        eski = json.load(open(DURUM, encoding="utf-8"))
    except Exception:
        eski = {}
    yeni = {k: eski.get(k, SIMDI.isoformat()) for k in sorunlar}  # çözülenler kayıttan düşer
    yenilar = [v for k, v in sorunlar.items() if k not in eski]
    json.dump(yeni, open(DURUM, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for v in sorunlar.values():
        print("SORUN:", v)
    if not sorunlar:
        print("Sorun yok.")
    sys.exit(1 if yenilar else 0)  # yalnız YENİ sorun uyarı üretir


main()
