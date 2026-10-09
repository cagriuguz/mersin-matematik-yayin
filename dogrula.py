"""Token ve hesap numarasını yalnızca okuyarak dener (hiçbir şey yayınlamaz)."""
import json, os, urllib.parse, urllib.request
q = urllib.parse.urlencode({"fields": "username,account_type", "access_token": os.environ["IG_TOKEN"]})
with urllib.request.urlopen(f"https://graph.instagram.com/v21.0/{os.environ['IG_USER_ID']}?{q}", timeout=60) as r:
    print(json.load(r))

# Yayınlamadan deneme: görselden taslak kapsül oluşturur (media_publish ÇAĞRILMAZ; 24 saatte kendiliğinden silinir).
img = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/main/medya/v2/h1-p1-1.png"
veri = urllib.parse.urlencode({"image_url": img, "is_carousel_item": "true", "access_token": os.environ["IG_TOKEN"]}).encode()
with urllib.request.urlopen(urllib.request.Request(f"https://graph.instagram.com/v21.0/{os.environ['IG_USER_ID']}/media", veri), timeout=60) as r:
    print("kapsul:", json.load(r))
