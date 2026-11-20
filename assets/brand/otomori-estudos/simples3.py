"""Leva 'simples' 3 (19/11): o D3 (森 no disco) com mais cara de disco de vinil.
Disco branco, sulcos e rótulo recortados na cor do fundo, 森 branco no rótulo."""
import math
from pathlib import Path

import simples2 as s2

AQUI = Path(__file__).parent
V = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"'


def circ(r):
    return f"M{256 + r} 256 A{r} {r} 0 1 0 {256 - r} 256 A{r} {r} 0 1 0 {256 + r} 256 Z"


def disco(raios):
    # Círculos aninhados com evenodd: alterna tinta e recorte (sulcos e rótulo).
    return f'<path fill="currentColor" fill-rule="evenodd" d="{" ".join(circ(r) for r in raios)}"/>'


def setor(r0, r1, a0, a1):
    p = lambda r, a: f"{256 + r*math.cos(math.radians(a)):.1f} {256 + r*math.sin(math.radians(a)):.1f}"
    return f"M{p(r1, a0)} A{r1} {r1} 0 0 1 {p(r1, a1)} L{p(r0, a1)} A{r0} {r0} 0 0 0 {p(r0, a0)} Z"


def brilho(cor):
    # Reflexo de vinil: duas fatias opostas na cor do fundo, meio transparentes.
    d = setor(140, 222, -60, -30) + " " + setor(140, 222, 120, 150)
    return f'<path fill="{cor}" fill-opacity=".45" d="{d}"/>'


def ideias(cor):
    m = lambda lado: f'<path fill="currentColor" d="{s2.glifo("森", lado, 256, 256)}"/>'
    return [
        ("V1 · Disco com sulcos", "Disco cheio, dois sulcos e o rótulo no meio com o 森.",
         f'<svg {V}>{disco([236, 206, 194, 172, 162, 124])}{m(150)}</svg>'),
        ("V2 · Disco com brilho", "Sem sulcos: o reflexo em duas fatias é o que diz 'vinil'.",
         f'<svg {V}>{disco([236, 124])}{brilho(cor)}{m(150)}</svg>'),
        ("V3 · Rótulo grande", "Um sulco só e o rótulo maior, para o 森 aguentar mais em tamanho pequeno.",
         f'<svg {V}>{disco([240, 200, 188, 150])}{m(190)}</svg>'),
        ("V4 · Sulcos e brilho", "As duas marcas de vinil juntas.",
         f'<svg {V}>{disco([236, 206, 194, 172, 162, 124])}{brilho(cor)}{m(150)}</svg>'),
    ]


def tam(s, p):
    return s.replace("<svg ", f'<svg width="{p}" height="{p}" ', 1)


def icone(s, p, cor):
    pad = round(p * 0.1)
    return (f'<div class="ic" style="background:{cor};width:{p}px;height:{p}px;border-radius:{round(p*.22)}px;padding:{pad}px">'
            f'{tam(s, p - 2*pad)}</div>')


secoes = ""
for i in range(4):
    blocos, nome, porque = "", "", ""
    for cnome, cor in s2.CORES:
        nome, porque, s = ideias(cor)[i]
        peq = "".join(f'<div class="c">{icone(s, p, cor)}<span>{p}</span></div>' for p in (32, 24, 16))
        zoom = (f'<div class="c"><canvas data-cor="{cor}" width="128" height="128"></canvas><span>16 real ×8</span>'
                f'<template>{s}</template></div>')
        blocos += (f'<div class="cor"><div class="l">{icone(s, 150, cor)}<div class="bar">{peq}</div>{zoom}</div>'
                   f'<small>{cnome} {cor}</small></div>')
    secoes += f'<section><h2>{nome}</h2><p>{porque}</p><div class="dupla">{blocos}</div></section>'

html = s2.html.split("<body>")[0] + f"<body>{secoes}" + """
<script>
for (const cv of document.querySelectorAll('canvas')) {
  const src = cv.parentElement.querySelector('template').innerHTML.replace(/currentColor/g, '#fff')
  const p = 16, t = document.createElement('canvas'); t.width = t.height = p
  const c = t.getContext('2d'), img = new Image()
  img.onload = () => { c.fillStyle = '#202020'; c.fillRect(0,0,p,p); c.fillStyle = cv.dataset.cor
    c.beginPath(); c.roundRect(0,0,p,p,3.5); c.fill(); const pad = 1.6; c.drawImage(img,pad,pad,p-2*pad,p-2*pad)
    const x = cv.getContext('2d'); x.imageSmoothingEnabled = false; x.drawImage(t,0,0,128,128) }
  img.src = 'data:image/svg+xml,' + encodeURIComponent(src)
}
</script></body></html>"""
(AQUI / "simples3.html").write_text(html, encoding="utf-8")
print("ok")
