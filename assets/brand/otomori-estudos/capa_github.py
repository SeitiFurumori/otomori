"""Capa do GitHub (social preview, 1280x640): fundo roxo da marca, disco branco,
nome, assinatura e o app ao lado. Uso: python capa_github.py <msedge.exe>"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.parents[2]
EDGE = sys.argv[1]
OUTFIT = (AQUI / "fonte-nome" / "Outfit-wght-.ttf").as_uri()
DISCO = (AQUI / "otomori-disco.svg").read_text(encoding="utf-8").replace(
    "<svg ", '<svg width="132" height="132" style="color:#fff;display:block" ', 1)
FOTO = (RAIZ / "assets" / "screenshots" / "lume.png").as_uri()

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Outfit;src:url('{OUTFIT}')}}
html,body{{margin:0;width:1280px;height:640px;overflow:hidden}}
body{{background:#8b63f6;font-family:Outfit;color:#fff;position:relative}}
.txt{{position:absolute;left:40px;top:0;bottom:0;width:480px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
h1{{font-weight:600;font-size:92px;letter-spacing:-2px;margin:26px 0 0;line-height:1}}
.frase{{font-size:32px;font-weight:500;margin:14px 0 0;opacity:.95}}
.sub{{font-size:21px;font-weight:400;margin:30px 0 0;opacity:.82;line-height:1.45}}
.app{{position:absolute;left:560px;top:96px;width:900px;border-radius:14px;
  box-shadow:0 30px 70px rgba(30,10,80,.45),0 0 0 1px rgba(255,255,255,.18)}}
</style></head><body>
<div class="txt">{DISCO}<h1>Otomori</h1><p class="frase">O som fica. O peso não.</p>
<p class="sub">Player leve para o Spotify no Windows.<br>Áudio em Rust, interface em WebView2,<br>instalador de 3 MB.</p></div>
<img class="app" src="{FOTO}">
</body></html>"""
pagina = AQUI / "capa-github.html"
pagina.write_text(html, encoding="utf-8")
saida = AQUI.parent / "otomori-capa-github.png"
subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                "--virtual-time-budget=3000", f"--screenshot={saida}", "--window-size=1280,640", pagina.as_uri()], check=True)
print(saida)
