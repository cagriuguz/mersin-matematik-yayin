"""Instagram token'ını 60 gün daha uzatır. Yeni token eskisinden farklıysa kasaya yazar (GH_PAT gerekir); yoksa hata verip durur."""
import hashlib, json, os, subprocess, sys, urllib.parse, urllib.request
eski = os.environ["IG_TOKEN"]
q = urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": eski})
with urllib.request.urlopen(f"https://graph.instagram.com/refresh_access_token?{q}", timeout=60) as r:
    s = json.load(r)
yeni = s["access_token"]
print("kalan gün:", round(s.get("expires_in", 0) / 86400), "| token", "AYNI" if yeni == eski else "DEĞİŞTİ")
if yeni != eski:
    if not os.environ.get("GH_TOKEN"):
        sys.exit("Token değişti ama GH_PAT yok: kasaya yazılamadı, elle güncelle.")
    subprocess.run(["gh", "secret", "set", "IG_TOKEN", "-R", os.environ["GITHUB_REPOSITORY"]], input=yeni.encode(), check=True)
    print("IG_TOKEN kasada güncellendi")
