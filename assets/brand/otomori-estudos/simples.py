"""Leva 'simples e limpo' (19/11): símbolos de uma silhueta só, como Discord,
Steam, Riot e Monstercat. Cada um testado em 256, 32, 24 e 16 px, claro e
escuro, com os pixels reais de 16 px ampliados."""
from pathlib import Path

AQUI = Path(__file__).parent
FONTE_JP = (AQUI / "fonte-noto" / "NotoSansJP-wght.ttf").as_uri()
FONTE_NOME = (AQUI / "fonte-nome" / "Outfit-wght-.ttf").as_uri()

# Todos em viewBox 512, tinta = currentColor.
V = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"'
IDEIAS = [
    ("A · Três árvores",
     "森 são três 木. Três pinheiros estreitos, na mesma posição do caractere.",
     f'<svg {V}><g fill="currentColor">'
     '<path d="M256 30 L322 250 L190 250 Z"/>'
     '<path d="M148 222 L224 482 L72 482 Z"/>'
     '<path d="M364 222 L440 482 L288 482 Z"/></g></svg>'),
    ("B · Floresta que toca",
     "Três barras de equalizador com a ponta de pinheiro: som (音) e floresta (森) num sinal só.",
     f'<svg {V}><g fill="currentColor">'
     '<path d="M56 470 V250 L126 160 L196 250 V470 Z"/>'
     '<path d="M186 470 V170 L256 50 L326 170 V470 Z" transform="translate(0 0)"/>'
     '<path d="M316 470 V290 L386 200 L456 290 V470 Z"/></g></svg>'),
    ("C · O com pinheiro",
     "O de Otomori cheio, com um pinheiro recortado. Funciona como o Steam: um disco que se reconhece de longe.",
     f'<svg {V}><path fill="currentColor" fill-rule="evenodd" d="'
     'M256 24 a232 232 0 1 0 0.01 0 Z '
     'M256 92 L330 200 L296 200 L366 316 L282 316 L282 410 L230 410 L230 316 L146 316 L216 200 L182 200 Z"/></svg>'),
    ("D · 森 em fonte firme",
     "O mesmo 森 de hoje, sem pincel e sem anel: Noto Sans JP no peso mais grosso.",
     f'<svg {V}><text x="256" y="430" text-anchor="middle" font-family="NotoJP" font-weight="900" '
     'font-size="440" fill="currentColor">森</text></svg>'),
]


def tam(s: str, p: int) -> str:
    return s.replace("<svg ", f'<svg width="{p}" height="{p}" ', 1)


def icone(s: str, p: int) -> str:
    # Símbolo branco no quadrado escuro, como o ícone do app hoje.
    pad = round(p * 0.2)
    return (f'<div class="ic" style="width:{p}px;height:{p}px;border-radius:{round(p*.22)}px;padding:{pad}px">'
            f'{tam(s, p - 2*pad)}</div>')


linhas = ""
for nome, porque, s in IDEIAS:
    grande = f'<div class="g">{icone(s, 200)}<div class="lock">{tam(s, 64)}<b>otomori</b></div></div>'
    peq = "".join(f'<div class="c">{tam(s, p)}<span>{p}</span></div>' for p in (32, 24, 16))
    peq_e = "".join(f'<div class="c e">{tam(s, p)}<span>{p}</span></div>' for p in (32, 24, 16))
    zoom = '<div class="c"><canvas data-p="16" width="128" height="128"></canvas><span>16 px real, ampliado 8×</span></div>'
    oculto = f'<div class="src" hidden>{tam(s, 16)}</div>'
    linhas += (f'<section><h2>{nome}</h2><p>{porque}</p><div class="l">{grande}'
               f'<div class="col"><div class="l">{peq}</div><div class="l">{peq_e}</div></div>{oculto}{zoom}</div></section>')

html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@font-face{{font-family:NotoJP;src:url('{FONTE_JP}')}}
@font-face{{font-family:Outfit;src:url('{FONTE_NOME}')}}
body{{margin:0;padding:24px 36px;background:#f4f3ef;font:15px/1.4 'Segoe UI',sans-serif;color:#222;width:1180px}}
section{{background:#fff;border-radius:14px;padding:16px 20px;margin-bottom:14px}}
h2{{font-size:18px;margin:0}} p{{margin:2px 0 12px;color:#666}}
.l{{display:flex;gap:22px;align-items:center}} .col{{display:grid;gap:8px}}
.g{{display:flex;gap:28px;align-items:center;margin-right:16px}}
.ic{{background:#16181d;color:#fff;box-sizing:border-box;display:grid;place-items:center}}
.lock{{display:flex;align-items:center;gap:14px;color:#111}}
.lock b{{font:600 52px Outfit;letter-spacing:-1px}}
.c{{display:grid;justify-items:center;gap:4px;color:#111;padding:8px;border-radius:8px;background:#f4f3ef}}
.c.e{{background:#202020;color:#fff}} .c span{{font-size:11px;color:#999}}
canvas{{image-rendering:pixelated;border:1px solid #ddd}}
</style></head><body>{linhas}
<script>
document.fonts.ready.then(() => {{
 for (const sec of document.querySelectorAll('section')) {{
  const svg = sec.querySelector('.src svg'), cv = sec.querySelector('canvas'), p = 16
  // Texto não sobrevive como imagem SVG isolada: desenha o 16 px real via canvas a partir do DOM visível.
  const vis = sec.querySelectorAll('.c:not(.e) svg'); const alvo = vis[vis.length-1]
  const t = document.createElement('canvas'); t.width = t.height = p; const c = t.getContext('2d')
  c.fillStyle = '#fff'; c.fillRect(0,0,p,p)
  const txt = alvo.querySelector('text')
  const fim = () => {{ const x = cv.getContext('2d'); x.imageSmoothingEnabled = false; x.drawImage(t,0,0,128,128) }}
  if (txt) {{ c.fillStyle = '#111'; c.font = `900 ${{440*p/512}}px NotoJP`; c.textAlign = 'center'; c.fillText('森', p/2, 430*p/512); fim() }}
  else {{ const img = new Image(); img.onload = () => {{ c.drawImage(img,0,0,p,p); fim() }}
    img.src = 'data:image/svg+xml,' + encodeURIComponent(new XMLSerializer().serializeToString(svg).replace(/currentColor/g,'#111')) }}
 }}
}})
</script></body></html>"""
(AQUI / "simples.html").write_text(html, encoding="utf-8")
print("ok")
