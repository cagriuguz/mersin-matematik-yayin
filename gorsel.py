"""Metin kartlarını arka plan üstüne basar. Kullanım: python3 gorsel.py  -> medya/ içine PNG yazar."""
import os
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
RENK = {"A": ((20, 36, 72), (150, 120, 60)), "B": ((250, 244, 230), (200, 170, 100)), "C": ((20, 36, 72), (60, 100, 160))}
ALT = "Çağrı Hoca | Mersin Matematik"


def sar(d, metin, f, genislik):
    satirlar = []
    for par in metin.split("\n"):
        if not par:
            satirlar.append("")
            continue
        s = ""
        for k in par.split(" "):
            dene = (s + " " + k).strip()
            if d.textlength(dene, font=f) <= genislik:
                s = dene
            else:
                satirlar.append(s)
                s = k
        satirlar.append(s)
    return satirlar


def kart(arka, etiket, metin, no, toplam, yol):
    im = Image.open(os.path.join(KOK, "medya", "arka", arka + ".png")).convert("RGB").resize((W, H))
    d = ImageDraw.Draw(im)
    ana, vurgu = RENK[arka]
    kutu_w, kutu_h = 800, 760
    for boy in range(104, 39, -2):
        f = ImageFont.truetype(FONT, boy)
        satir = sar(d, metin, f, kutu_w)
        h = len(satir) * int(boy * 1.3)
        if h <= kutu_h:
            break
    y = 640 - h // 2
    for s in satir:
        d.text((W // 2, y), s, font=f, fill=ana, anchor="ma")
        y += int(boy * 1.3)
    fe = ImageFont.truetype(FONT, 30)
    d.text((W // 2, 190), etiket.upper(), font=fe, fill=vurgu, anchor="ma")
    d.text((W // 2, 1240), ALT, font=fe, fill=vurgu, anchor="ma")
    d.text((W // 2, 1285), f"{no}/{toplam}", font=ImageFont.truetype(FONT, 26), fill=vurgu, anchor="ma")
    im.save(yol)


POSTLAR = {
    "h1-p1": ("A", "Öğretme anlayışım", [
        "Matematiği ezberletmem.\nDüşündürürüm.",
        "Ezber:\n“Bu tip soruda şunu yap.”\n\nDüşünme:\n“Soru ne istiyor, elimde ne var?”",
        "Ezber, soru değişince çöker.\n\nDüşünme, soru değişince de çalışır.",
        "Önce soruyu okur, sonra “İlk adım ne olabilir?” diye sorarım.\n\nFormül en sona kalır.",
        "Sen matematiği ezberle mi çalışıyorsun, düşünerek mi?\n\nYorumda yaz.\nKaydet, sınav öncesi dön."]),
    "h1-p2": ("B", "Yanlış mı, eksik mi?", [
        "Yanlış yaptı = konuyu bilmiyor.\n\nGerçekten mi?",
        "Üç farklı yanlış var:\n\n1. Bilgi eksiği\n2. Okuma / dikkat hatası\n3. Karar hatası",
        "Aynı yanlış, farklı çözüm ister.\n\nHer yanlışa yeni konu anlatmak zaman kaybıdır.",
        "Soruyu yanlış okuyana konu tekrarı değil, okuma alışkanlığı gerekir.",
        "Bu hatayı yapan bir öğrenciye gönder."]),
    "h1-p3": ("C", "Haftanın sorusu", [
        "Kenar uzunlukları pozitif tam sayı (cm) olan bir dikdörtgenin alanı (cm²), çevresine (cm) sayısal olarak eşittir.\n\nKaç farklı dikdörtgen vardır?",
        "Deneme-yanılma burada seni yarı yolda bırakabilir.\n\nKarar ver: önce eşitliği yaz.",
        "Kenarlar a ve b olsun.\n\na · b = 2(a + b)\n\nDüzenle:\n(a − 2)(b − 2) = 4",
        "4 = 1 · 4 = 2 · 2\n\n(a, b) = (3, 6) ve (4, 4)\n\n(6, 3) aynı dikdörtgendir.",
        "Cevap: 2\n\nBu bir işlem değil, karar sorusu: deneme yerine çarpanlara ayır.\n\nİkinci çözümü ister misiniz?"]),
    "h2-p1": ("B", "Bildiği soruyu yapamıyor", [
        "Bildiği soruyu neden yapamaz?",
        "Çünkü bilmek ile kullanmak aynı şey değildir.\n\nFormülü bilir; ne zaman kullanacağını bilmez.",
        "Soru tanıdık görünmeyince ilk adımı bulamaz.\n\nBilgi var, başlangıç yok.",
        "Çözüm: her soruda önce şunu sor:\n“Verilen ne, istenen ne?”\n\nSonra formüle bak.",
        "Sence öğrenci burada neden yanılıyor?\n\nYorumda yaz. Bu durumdaki bir öğrenciye gönder."]),
    "h2-p2": ("A", "Dikkat hatası mı?", [
        "“Dikkat hatası yaptı.”\n\nGerçekten dikkat mi?",
        "Çoğu zaman sorun dikkat eksikliği değil, kontrol alışkanlığı eksikliğidir.",
        "İşareti atlamak, soruyu yarım okumak, birimi unutmak…\n\nHepsi bir kontrol adımıyla yakalanır.",
        "Çocuğa “dikkat et” demek yetmez.\n\nNeye dikkat edeceğini göstermek gerekir:\nişaret, birim, istenen.",
        "Bu hatayı yapan bir öğrenciye gönder.\n\nKaydet, sınav öncesi kontrol listesi olarak kullan."]),
}

if __name__ == "__main__":
    for ad, (arka, etiket, slaytlar) in POSTLAR.items():
        for i, m in enumerate(slaytlar, 1):
            kart(arka, etiket, m, i, len(slaytlar), os.path.join(KOK, "medya", f"{ad}-{i}.png"))
    print("tamam")
