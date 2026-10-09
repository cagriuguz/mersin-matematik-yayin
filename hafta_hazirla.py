"""Sıradaki hazırlanmamış haftanın kartlarını basar ve kuyruk.json'a onay=true olarak ekler.
Kullanım (Actions içinde, ayrı bir dalda çalışır; PR birleştirilince = onay): python3 hafta_hazirla.py
Çıktı: GITHUB_OUTPUT'a hafta=N ve ozet (PR gövdesi için dosya: pr_govde.md)."""
import json, os, glob
from datetime import datetime, timedelta, timezone
import kart

KOK = os.path.dirname(os.path.abspath(__file__))
kuyruk_yol = os.path.join(KOK, "kuyruk.json")
kuyruk = json.load(open(kuyruk_yol, encoding="utf-8"))
mevcut = {g["id"] for g in kuyruk}

for yol in sorted(glob.glob(os.path.join(KOK, "icerik", "hafta-*.json"))):
    hafta = json.load(open(yol, encoding="utf-8"))
    yeni = [g for g in hafta["gonderiler"] if g["id"] not in mevcut]
    if not yeni:
        continue
    ilk = min(datetime.fromisoformat(g["tarih"]) for g in yeni)
    if ilk - datetime.now(timezone.utc) > timedelta(days=10):
        print("sıradaki hafta henüz erken:", hafta["hafta"])
        break
    govde = [f"# Hafta {hafta['hafta']} onayı\n", "Birleştir (Merge) = bu gönderilerin hepsini onaylıyorum. Onaylamadıklarını PR'dan çıkarmak için bana yaz.\n"]
    for g in yeni:
        klasor = os.path.join(KOK, "medya", "uretim")
        dosyalar = [os.path.relpath(p, KOK) for p in kart.gonderi_ciz(g["kartlar"], g["id"], klasor)]
        kuyruk.append({"id": g["id"], "tarih": g["tarih"], "tur": "carousel", "dosyalar": dosyalar, "baslik": g["baslik"], "onay": True})
        govde.append(f"## {g['id']} · {g['tarih'][:10]} 20:00\n{g['baslik']}\n")
        govde += [f"![]({'https://raw.githubusercontent.com/' + os.environ.get('GITHUB_REPOSITORY', 'cagriuguz/mersin-matematik-yayin') + '/' + os.environ.get('DAL', 'main') + '/' + d})" for d in dosyalar[:5]]
    json.dump(sorted(kuyruk, key=lambda g: g["tarih"]), open(kuyruk_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(os.path.join(KOK, "pr_govde.md"), "w", encoding="utf-8").write("\n".join(govde))
    print(f"hafta={hafta['hafta']}")
    if os.environ.get("GITHUB_OUTPUT"):
        open(os.environ["GITHUB_OUTPUT"], "a").write(f"hafta={hafta['hafta']}\n")
    break
else:
    print("hazırlanacak hafta kalmadı")
