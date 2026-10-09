"""Token ve hesap numarasını yalnızca okuyarak dener (hiçbir şey yayınlamaz)."""
import json, os, urllib.parse, urllib.request
q = urllib.parse.urlencode({"fields": "username,account_type", "access_token": os.environ["IG_TOKEN"]})
with urllib.request.urlopen(f"https://graph.instagram.com/v21.0/{os.environ['IG_USER_ID']}?{q}", timeout=60) as r:
    print(json.load(r))
