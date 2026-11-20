"""Leva 'simples' 2 (19/11): ele escolheu o D (森 em fonte firme), sem preto,
com cor (azul do Kosame ou roxo do Otomori) e algum sinal de música.
Ícone = quadrado colorido com símbolo branco. Testado em 256, 32, 24, 16 px."""
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

AQUI = Path(__file__).parent
ft = instantiateVariableFont(TTFont(AQUI / "fonte-noto" / "NotoSansJP-wght.ttf"), {"wght": 900})
GS = ft.getGlyphSet()
CMAP = ft.getBestCmap()
FONTE_NOME = (AQUI / "fonte-nome" / "Outfit-wght-.ttf").as_uri()

CORES = [("Azul do Kosame", "#1c5cb8"), ("Roxo do Otomori", "#8b63f6")]


def glifo(ch: str, lado: float, cx: float, cy: float) -> str:
    g = GS[CMAP[ord(ch)]]
    b = BoundsPen(GS); g.draw(b)
    x0, y0, x1, y1 = b.bounds
    s = lado / max(x1 - x0, y1 - y0)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    p = SVGPathPen(GS, ntos=lambda n: f"{n:.1f}")
    g.draw(TransformPen(p, (s, 0, 0, -s, cx - mx * s, cy + my * s)))
    return p.getCommands()


def arco(cx, cy, r, a0, a1, w):
    import math
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    return (f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" '
            f'stroke="currentColor" stroke-width="{w}" stroke-linecap="round"/>')


V = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"'
IDEIAS = [
    ("D1 · 森 só", "O D da leva anterior, agora em cor. A música fica no nome e na cor, não no desenho.",
     f'<svg {V}><path fill="currentColor" d="{glifo("森", 470, 256, 256)}"/></svg>'),
    ("D2 · 森 que soa", "O 森 com duas ondas de som saindo pela direita, como um alto-falante.",
     f'<svg {V}><path fill="currentColor" d="{glifo("森", 340, 196, 256)}"/>'
     + arco(330, 256, 110, -42, 42, 34) + arco(330, 256, 170, -40, 40, 34) + '</svg>'),
    ("D3 · 森 no disco", "O 森 no centro de um disco de vinil: anel grosso por fora, um sulco fino por dentro.",
     f'<svg {V}><circle cx="256" cy="256" r="228" fill="none" stroke="currentColor" stroke-width="40"/>'
     f'<path fill="currentColor" d="{glifo("森", 270, 256, 256)}"/></svg>'),
    ("D4 · 音 (som)", "O outro lado do nome: 音 = som, o 'Oto' de Otomori. Menos traços que 森, mais limpo pequeno.",
     f'<svg {V}><path fill="currentColor" d="{glifo("音", 470, 256, 256)}"/></svg>'),
]


def tam(s, p):
    return s.replace("<svg ", f'<svg width="{p}" height="{p}" ', 1)


def icone(s, p, cor):
    pad = round(p * 0.17)
    return (f'<div class="ic" style="background:{cor};width:{p}px;height:{p}px;border-radius:{round(p*.22)}px;padding:{pad}px">'
            f'{tam(s, p - 2*pad)}</div>')


secoes = ""
for nome, porque, s in IDEIAS:
    blocos = ""
    for cnome, cor in CORES:
        peq = "".join(f'<div class="c">{icone(s, p, cor)}<span>{p}</span></div>' for p in (32, 24, 16))
        zoom = f'<div class="c"><canvas data-cor="{cor}" width="128" height="128"></canvas><span>16 real ×8</span></div>'
        lock = f'<div class="lock" style="color:{cor}">{tam(s, 52)}<b>otomori</b></div>'
        blocos += (f'<div class="cor"><div class="l">{icone(s, 150, cor)}<div class="bar">{peq}</div>{zoom}</div>'
                   f'<div class="l2">{lock}<small>{cnome} {cor}</small></div></div>')
    secoes += f'<section><h2>{nome}</h2><p>{porque}</p><div class="dupla">{blocos}</div><template>{s}</template></section>'

html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@font-face{{font-family:Outfit;src:url('{FONTE_NOME}')}}
body{{margin:0;padding:22px 32px;background:#f4f3ef;font:15px/1.4 'Segoe UI',sans-serif;color:#222;width:1220px}}
section{{background:#fff;border-radius:14px;padding:14px 18px;margin-bottom:12px}}
h2{{font-size:18px;margin:0}} p{{margin:2px 0 10px;color:#666}}
.dupla{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.l{{display:flex;gap:16px;align-items:center}} .l2{{display:flex;align-items:center;gap:16px;margin-top:10px}}
.bar{{display:flex;gap:10px;align-items:center;background:#202020;padding:8px 10px;border-radius:8px}}
.ic{{color:#fff;box-sizing:border-box;display:grid;place-items:center}}
.c{{display:grid;justify-items:center;gap:3px}} .c span{{font-size:10px;color:#999}}
.lock{{display:flex;align-items:center;gap:10px}} .lock b{{font:600 40px Outfit;letter-spacing:-1px}}
small{{color:#999}} canvas{{image-rendering:pixelated;border:1px solid #ddd}}
</style></head><body>{secoes}
<script>
// 16 px real: quadrado colorido + símbolo branco, rasterizado no tamanho de verdade e ampliado sem suavizar.
for (const sec of document.querySelectorAll('section')) {{
  const src = sec.querySelector('template').innerHTML.replace(/currentColor/g, '#fff')
  for (const cv of sec.querySelectorAll('canvas')) {{
    const p = 16, t = document.createElement('canvas'); t.width = t.height = p
    const c = t.getContext('2d'), img = new Image()
    img.onload = () => {{ c.fillStyle = '#202020'; c.fillRect(0,0,p,p); c.fillStyle = cv.dataset.cor
      c.beginPath(); c.roundRect(0,0,p,p,3.5); c.fill(); const pad = 16*.17; c.drawImage(img,pad,pad,p-2*pad,p-2*pad)
      const x = cv.getContext('2d'); x.imageSmoothingEnabled = false; x.drawImage(t,0,0,128,128) }}
    img.src = 'data:image/svg+xml,' + encodeURIComponent(src)
  }}
}}
</script></body></html>"""
(AQUI / "simples2.html").write_text(html, encoding="utf-8")
print("ok")
