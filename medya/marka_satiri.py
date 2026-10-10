"""Kartlara alt marka satiri basar: CAGRI HOCA | MERSIN MATEMATIK (Playfair Display, OFL). Kullanim: python3 marka_satiri.py girdi.png cikti.png"""
import sys
from PIL import Image, ImageDraw, ImageFont
Y_ARG=int(sys.argv[3]) if len(sys.argv)>3 else None
YAZI="ÇAĞRI HOCA | MERSİN MATEMATİK"; BOY=25; ARALIK=5.5; Y_ORTA=Y_ARG or 1303; RENK=(10,27,60)
f=ImageFont.truetype("/Users/cagriuguz/Desktop/Instagram-Otomasyon/yazi/PlayfairDisplay.ttf",BOY)
im=Image.open(sys.argv[1]).convert("RGB"); d=ImageDraw.Draw(im)
w=sum(d.textlength(c,font=f)+ARALIK for c in YAZI)-ARALIK; x=(im.width-w)/2
for c in YAZI:
    d.text((x,Y_ORTA),c,font=f,fill=RENK,anchor="lm"); x+=d.textlength(c,font=f)+ARALIK
im.save(sys.argv[2])
