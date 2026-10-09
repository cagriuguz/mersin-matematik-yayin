"""Premium kart basıcı (bulutta ve yerelde aynı çıktıyı verir; ChatGPT gerekmez).

Kart tanımı: {"etiket": "HAFTANIN SORUSU" (isteğe bağlı), "satirlar": [...]}
Satır biçimleri:
  "Düz yazı"        -> kalın başlık yazısı
  "i: Metin"        -> italik alt yazı (küçük)
  "m: a · b = 2(a + b)" -> büyük matematik satırı (yıldız arası *a* italik olur)
  "---"             -> ince altın ayraç
Metin içinde *x* = italik parça.
"""
import os, random, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

KOK = os.path.dirname(os.path.abspath(__file__))
YAZI = os.path.join(KOK, "yazi")
W, H = 1080, 1350
KAGIT, LACI, ALTIN = (247, 243, 233), (20, 33, 70), (188, 148, 62)
ALT_YAZI = "ÇAĞRI HOCA | MERSİN MATEMATİK"
SOL, SAG = 120, W - 120  # yazı alanı
ICERIK_UST, ICERIK_ALT = 190, 1150


def font(italik, boyut, kalinlik=700):
    f = ImageFont.truetype(os.path.join(YAZI, "PlayfairDisplay-Italic.ttf" if italik else "PlayfairDisplay.ttf"), boyut)
    try:
        f.set_variation_by_axes([kalinlik])
    except Exception:
        pass
    return f


def buyut(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def parcala(metin, temel_italik):
    """*x* parçalarını (metin, italik) çiftlerine ayırır."""
    out = []
    for i, p in enumerate(re.split(r"\*", metin)):
        if p:
            out.append((p, temel_italik != (i % 2 == 1)))
    return out


def olc(d, parcalar, boyut, kalinlik):
    return sum(d.textlength(t, font=font(it, boyut, kalinlik)) for t, it in parcalar)


def sar(d, metin, boyut, kalinlik, italik, genislik):
    """Kelime kelime satır kırar; satırlar parça listesi olarak döner."""
    kelimeler, satirlar, cur = metin.split(" "), [], ""
    for k in kelimeler:
        dene = (cur + " " + k).strip()
        if olc(d, parcala(dene, italik), boyut, kalinlik) <= genislik or not cur:
            cur = dene
        else:
            satirlar.append(cur)
            cur = k
    satirlar.append(cur)
    return satirlar


def zemin():
    rnd = random.Random(7)
    img = Image.new("RGB", (W, H), KAGIT)
    g = Image.effect_noise((W, H), 14).convert("L").filter(ImageFilter.GaussianBlur(1.6))
    g = g.point(lambda v: int(v * 0.12))
    img = Image.composite(Image.new("RGB", (W, H), (222, 214, 196)), img, g)
    return img


def cerceve(d):
    d.rectangle([30, 30, W - 30, H - 30], outline=ALTIN, width=2)
    d.rectangle([42, 42, W - 42, H - 42], outline=ALTIN, width=1)
    for x, y, sx, sy in [(30, 30, 1, 1), (W - 30, 30, -1, 1), (30, H - 30, 1, -1), (W - 30, H - 30, -1, -1)]:
        d.line([(x, y + sy * 70), (x + sx * 36, y + sy * 70), (x + sx * 36, y + sy * 36), (x + sx * 70, y + sy * 36), (x + sx * 70, y)], fill=ALTIN, width=2)


def aralikli(d, xmerkez, y, metin, boyut, aralik):
    f = font(False, boyut, 600)
    genislik = sum(d.textlength(c, font=f) for c in metin) + aralik * (len(metin) - 1)
    x = xmerkez - genislik / 2
    for c in metin:
        d.text((x, y), c, font=f, fill=LACI)
        x += d.textlength(c, font=f) + aralik
    return genislik


SON_OLCEK = [1.0]


def kart_ciz(kart, no, toplam, yol):
    img = zemin()
    d = ImageDraw.Draw(img)
    cerceve(d)
    if kart.get("etiket"):
        gen = aralikli(d, W / 2, 98, buyut(kart["etiket"]), 24, 9)
        d.line([(W / 2 - gen / 2 - 110, 113), (W / 2 - gen / 2 - 30, 113)], fill=ALTIN, width=2)
        d.line([(W / 2 + gen / 2 + 30, 113), (W / 2 + gen / 2 + 110, 113)], fill=ALTIN, width=2)

    # satırları ölç; sığana kadar küçült
    olcek = 1.0
    while True:
        bloklar, toplam_h = [], 0
        for s in kart["satirlar"]:
            if s == "---":
                bloklar.append(("ayirac", None, 0, 0, 0, 60))
                toplam_h += 60
                continue
            tur, boyut, kal, it = "h", 88, 700, False
            if s.startswith("i: "):
                tur, boyut, kal, it, s = "i", 54, 400, True, s[3:]
            elif s.startswith("m: "):
                tur, boyut, kal, it, s = "m", 92, 400, False, s[3:]
            boyut = int(boyut * olcek)
            for satir in sar(d, s, boyut, kal, it, SAG - SOL):
                bloklar.append((tur, satir, boyut, kal, it, int(boyut * 1.32)))
                toplam_h += int(boyut * 1.32)
        if toplam_h <= ICERIK_ALT - ICERIK_UST or olcek < 0.45:
            break
        olcek -= 0.04

    SON_OLCEK[0] = olcek
    y = ICERIK_UST + (ICERIK_ALT - ICERIK_UST - toplam_h) / 2
    for tur, satir, boyut, kal, it, yuks in bloklar:
        if tur == "ayirac":
            d.line([(W / 2 - 90, y + 30), (W / 2 + 90, y + 30)], fill=ALTIN, width=2)
            d.polygon([(W / 2, y + 22), (W / 2 + 8, y + 30), (W / 2, y + 38), (W / 2 - 8, y + 30)], fill=ALTIN)
        else:
            parcalar = parcala(satir, it)
            x = W / 2 - olc(d, parcalar, boyut, kal) / 2
            for t, pit in parcalar:
                f = font(pit, boyut, kal)
                d.text((x, y), t, font=f, fill=LACI)
                x += d.textlength(t, font=f)
        y += yuks

    # alt imza + sayfa no
    gen = aralikli(d, W / 2 - 20, 1233, ALT_YAZI, 22, 5)
    d.line([(W / 2 - 20 - gen / 2 - 100, 1246), (W / 2 - 20 - gen / 2 - 28, 1246)], fill=ALTIN, width=2)
    d.line([(W / 2 - 20 + gen / 2 + 28, 1246), (W / 2 - 20 + gen / 2 + 100, 1246)], fill=ALTIN, width=2)
    d.text((W - 125, 1258), f"{no}/{toplam}", font=font(False, 26, 500), fill=LACI, anchor="ra")
    img.save(yol)


def gonderi_ciz(kartlar, onek, klasor):
    os.makedirs(klasor, exist_ok=True)
    yollar = []
    for i, k in enumerate(kartlar, 1):
        yol = os.path.join(klasor, f"{onek}-{i}.png")
        kart_ciz(k, i, len(kartlar), yol)
        yollar.append(yol)
    return yollar


if __name__ == "__main__":
    import json, sys
    ornek = [{"etiket": "Haftanın sorusu", "satirlar": ["Kenarlar *a* ve *b* olsun.", "m: *a* · *b* = 2(*a* + *b*)", "m: (*a* – 2)(*b* – 2) = 4"]},
             {"satirlar": ["Matematiği ezberletmem.", "i: Düşündürürüm."]}]
    gonderi_ciz(ornek, "deneme", sys.argv[1] if len(sys.argv) > 1 else "/tmp/kart-deneme")
