"""kuyruk.json içinde onay==true ve zamanı gelmiş gönderileri Instagram'a yayınlar.
Ortam: IG_USER_ID, IG_TOKEN, DEPO_RAW. --kuru: göndermeden dener."""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://graph.facebook.com/v21.0"
KURU = "--kuru" in sys.argv


def cagri(yol, veri=None, get=False):
    veri = dict(veri or {}, access_token=os.environ["IG_TOKEN"])
    q = urllib.parse.urlencode(veri)
    req = urllib.request.Request(f"{API}/{yol}?{q}") if get else urllib.request.Request(f"{API}/{yol}", q.encode())
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def url(dosya):
    return f"{os.environ['DEPO_RAW']}/{urllib.parse.quote(dosya)}"


def hazirla(ig, g):
    t, d = g["tur"], g["dosyalar"]
    if t == "image":
        return cagri(f"{ig}/media", {"image_url": url(d[0]), "caption": g["baslik"]})["id"]
    if t == "reel":
        return cagri(f"{ig}/media", {"media_type": "REELS", "video_url": url(d[0]), "caption": g["baslik"]})["id"]
    cocuklar = [cagri(f"{ig}/media", {"image_url": url(x), "is_carousel_item": "true"})["id"] for x in d]
    return cagri(f"{ig}/media", {"media_type": "CAROUSEL", "children": ",".join(cocuklar), "caption": g["baslik"]})["id"]


def bekle(kap):
    for _ in range(40):
        if cagri(kap, {"fields": "status_code"}, get=True).get("status_code") == "FINISHED":
            return
        time.sleep(15)
    raise RuntimeError("Medya işlenemedi: " + kap)


def main():
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kuyruk.json")
    kuyruk = json.load(open(yol, encoding="utf-8"))
    simdi = datetime.now(timezone.utc)
    for g in kuyruk:
        if g.get("onay") is not True or g.get("durum") == "yayinlandi" or datetime.fromisoformat(g["tarih"]) > simdi:
            continue
        print("Yayınlanacak:", g["id"], g["tur"])
        if KURU:
            continue
        ig = os.environ["IG_USER_ID"]
        kap = hazirla(ig, g)
        bekle(kap)
        g["medya_id"] = cagri(f"{ig}/media_publish", {"creation_id": kap})["id"]
        g["durum"] = "yayinlandi"
        json.dump(kuyruk, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        break  # çalıştırma başına tek gönderi


main()
