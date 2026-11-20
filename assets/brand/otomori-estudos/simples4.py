"""Leva 'simples' 4 (19/11): o V2 (disco com brilho) com textura de vinil,
fios concêntricos bem finos na cor do fundo. Em 32 px para baixo os fios
viram só um tom; por isso cada um é mostrado também sem textura no pequeno."""
from pathlib import Path

import simples2 as s2
from simples3 import brilho, disco, icone, tam

AQUI = Path(__file__).parent
V = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"'


def fios(cor, passo, largura, opac):
    r, cs = 130.0, []
    while r < 232:
        cs.append(f'<circle cx="256" cy="256" r="{r:.1f}"/>')
        r += passo
    return f'<g fill="none" stroke="{cor}" stroke-width="{largura}" stroke-opacity="{opac}">{"".join(cs)}</g>'


def mori():
    return f'<path fill="currentColor" d="{s2.glifo("森", 150, 256, 256)}"/>'


def base(cor, textura):
    return f'<svg {V}>{disco([236, 124])}{textura}{brilho(cor)}{mori()}</svg>'


def ideias(cor):
    return [
        ("T1 · Fios bem finos", "Fio de 1,2 a cada 5 unidades, quase sumindo: a textura só aparece de perto.",
         base(cor, fios(cor, 5, 1.2, .22))),
        ("T2 · Fios finos marcados", "Mesmo espaçamento, fio um pouco mais forte.",
         base(cor, fios(cor, 5, 1.4, .4))),
        ("T3 · Fios mais abertos", "Menos fios, mais espaçados: lê como sulco a uma distância maior.",
         base(cor, fios(cor, 9, 2, .35))),
    ]


simples = lambda cor: base(cor, "")  # versão para 32 px para baixo

secoes = ""
for i in range(3):
    blocos = ""
    for cnome, cor in s2.CORES:
        nome, porque, s = ideias(cor)[i]
        peq = "".join(f'<div class="c">{icone(s, p, cor)}<span>{p}</span></div>' for p in (32, 24, 16))
        peq_s = "".join(f'<div class="c">{icone(simples(cor), p, cor)}<span>{p}</span></div>' for p in (32, 24, 16))
        blocos += (f'<div class="cor"><div class="l">{icone(s, 260, cor)}<div class="col">'
                   f'<div class="bar">{peq}</div><small>com textura</small>'
                   f'<div class="bar">{peq_s}</div><small>sem textura</small></div></div>'
                   f'<small>{cnome} {cor}</small></div>')
    secoes += f'<section><h2>{nome}</h2><p>{porque}</p><div class="dupla">{blocos}</div></section>'

html = (s2.html.split("<body>")[0].replace("</style>", ".col{display:grid;gap:4px;justify-items:start}</style>")
        + f"<body>{secoes}</body></html>")
(AQUI / "simples4.html").write_text(html, encoding="utf-8")
print("ok")
