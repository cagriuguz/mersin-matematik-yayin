"""Haftalık onay ekranı: python3 onay.py  -> tarayıcıda her gönderi için OLSUN / OLMASIN."""
import json, os, subprocess, threading, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

KOK = os.path.dirname(os.path.abspath(__file__))
KUYRUK = os.path.join(KOK, "kuyruk.json")

SAYFA = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Haftalık onay</title><style>
body{font:16px system-ui;max-width:640px;margin:0 auto;padding:16px;background:#f6f6f4;color:#222}
.k{background:#fff;border-radius:14px;padding:14px;margin:14px 0;box-shadow:0 1px 4px #0002}
.k img,.k video{width:100%;border-radius:10px}.n{font-weight:700;font-size:20px}
.t{color:#666;font-size:14px}pre{white-space:pre-wrap;font:inherit}
button{font-size:18px;padding:12px 0;border:0;border-radius:10px;width:49%;cursor:pointer}
.e{background:#cfe9d6}.h{background:#f3d0d0}.sec.e{outline:3px solid #2e8b57}.sec.h{outline:3px solid #c0392b}
#g{position:sticky;bottom:8px;width:100%;background:#222;color:#fff}</style>
<h2>Bu hafta: <span id=say></span></h2><div id=l></div><button id=g onclick=gonder()>Bitti – kaydet</button>
<script>
let Q=[],K={};
fetch('/liste').then(r=>r.json()).then(d=>{Q=d;K={};Q.forEach(g=>K[g.id]=null);ciz()});
function ciz(){document.getElementById('say').textContent=Q.length+' gönderi';
document.getElementById('l').innerHTML=Q.map((g,i)=>`<div class=k><div class=n>${i+1}</div>
<div class=t>${g.tarih.replace('T',' ').slice(0,16)} · ${g.tur}</div>
${g.dosyalar.map(f=>f.endsWith('.mp4')?`<video src="/${f}" controls></video>`:`<img src="/${f}">`).join('')}
<pre>${g.baslik}</pre>
<button class="e ${K[g.id]===true?'sec':''}" onclick="s('${g.id}',true)">OLSUN</button>
<button class="h ${K[g.id]===false?'sec':''}" onclick="s('${g.id}',false)">OLMASIN</button></div>`).join('')}
function s(id,v){K[id]=v;ciz()}
function gonder(){if(Object.values(K).includes(null)){alert('Seçmediğin gönderi var.');return}
fetch('/kaydet',{method:'POST',body:JSON.stringify(K)}).then(r=>r.text()).then(t=>{document.body.innerHTML='<h2>'+t+'</h2>'})}
</script>"""


class H(BaseHTTPRequestHandler):
    def _yaz(self, kod, tip, veri):
        self.send_response(kod); self.send_header("Content-Type", tip); self.end_headers(); self.wfile.write(veri)

    def do_GET(self):
        if self.path == "/":
            return self._yaz(200, "text/html; charset=utf-8", SAYFA.encode())
        if self.path == "/liste":
            q = json.load(open(KUYRUK, encoding="utf-8"))
            bekleyen = [g for g in q if g.get("onay") is None]
            return self._yaz(200, "application/json", json.dumps(bekleyen).encode())
        yol = os.path.realpath(os.path.join(KOK, self.path.lstrip("/").split("?")[0]))
        if yol.startswith(os.path.join(KOK, "medya")) and os.path.isfile(yol):
            return self._yaz(200, "application/octet-stream", open(yol, "rb").read())
        self._yaz(404, "text/plain", b"yok")

    def do_POST(self):
        k = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        q = json.load(open(KUYRUK, encoding="utf-8"))
        for g in q:
            if g["id"] in k:
                g["onay"] = k[g["id"]]
        json.dump(q, open(KUYRUK, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        sonuc = subprocess.run("git add -A && git commit -qm onay && git push -q", shell=True, cwd=KOK, capture_output=True, text=True)
        self._yaz(200, "text/plain; charset=utf-8", ("Kaydedildi ve gönderildi ✔" if sonuc.returncode == 0 else "Kaydedildi (internete gönderilemedi: " + sonuc.stderr[:120] + ")").encode("utf-8"))
        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    threading.Timer(0.8, lambda: webbrowser.open("http://localhost:8771")).start()
    HTTPServer(("127.0.0.1", 8771), H).serve_forever()
