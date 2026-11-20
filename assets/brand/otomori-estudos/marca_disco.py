"""Marca final de 19/11: o disco de vinil (T3 da leva 'simples' 4).

Símbolo de uma cor só (currentColor). Os sulcos, o brilho e o rótulo são
recortes por máscara, então o fundo aparece por eles em qualquer superfície:
no ícone (disco branco no quadrado roxo) e no app (disco na cor de destaque).

Gera:
  otomori-disco.svg           símbolo completo (com fios), 48 px para cima
  otomori-disco-pequeno.svg   sem fios, para 32 px para baixo
  otomori-assinatura.svg      símbolo + nome, currentColor (fonte do Marca.svelte)
  ../otomori-assinatura-clara.svg / -escura.svg   para o README (símbolo roxo)
"""
import math
import re
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

AQUI = Path(__file__).parent
ROXO = "#8b63f6"

ft = instantiateVariableFont(TTFont(AQUI / "fonte-noto" / "NotoSansJP-wght.ttf"), {"wght": 900})
GS, CMAP = ft.getGlyphSet(), ft.getBestCmap()


def glifo(ch, lado, cx, cy):
    g = GS[CMAP[ord(ch)]]
    b = BoundsPen(GS); g.draw(b)
    x0, y0, x1, y1 = b.bounds
    s = lado / max(x1 - x0, y1 - y0)
    p = SVGPathPen(GS, ntos=lambda n: f"{n:.1f}")
    g.draw(TransformPen(p, (s, 0, 0, -s, cx - (x0 + x1) / 2 * s, cy + (y0 + y1) / 2 * s)))
    return p.getCommands()


def setor(r0, r1, a0, a1):
    p = lambda r, a: f"{256 + r*math.cos(math.radians(a)):.1f} {256 + r*math.sin(math.radians(a)):.1f}"
    return f"M{p(r1, a0)} A{r1} {r1} 0 0 1 {p(r1, a1)} L{p(r0, a1)} A{r0} {r0} 0 0 0 {p(r0, a0)} Z"


MORI = glifo("森", 150, 256, 256)


def simbolo_interno(id_mask: str, com_fios: bool) -> str:
    """Conteúdo do símbolo em coordenadas 0..512 (sem a tag <svg>)."""
    fios = ""
    if com_fios:
        r, cs = 130.0, []
        while r < 232:
            cs.append(f'<circle cx="256" cy="256" r="{r:.0f}"/>')
            r += 9
        fios = f'<g fill="none" stroke="#000" stroke-width="2" stroke-opacity=".35">{"".join(cs)}</g>'
    brilho = f'<path fill="#000" fill-opacity=".45" d="{setor(140, 222, -60, -30)} {setor(140, 222, 120, 150)}"/>'
    return (f'<mask id="{id_mask}" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">'
            f'<circle cx="256" cy="256" r="236" fill="#fff"/><circle cx="256" cy="256" r="124" fill="#000"/>'
            f'{fios}{brilho}</mask>'
            f'<circle cx="256" cy="256" r="236" mask="url(#{id_mask})"/>'
            f'<path d="{MORI}"/>')


V = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor"'
(AQUI / "otomori-disco.svg").write_text(f'<svg {V}>{simbolo_interno("otomori-vinil", True)}</svg>\n', encoding="utf-8")
(AQUI / "otomori-disco-pequeno.svg").write_text(f'<svg {V}>{simbolo_interno("otomori-vinil-p", False)}</svg>\n', encoding="utf-8")

# Assinatura: mesmo layout da anterior (símbolo 120 px + "otomori" em Outfit já em curva).
antiga = (AQUI / "otomori-assinatura.svg").read_text(encoding="utf-8")
nome = re.search(r'</g>(<path d="M179[^"]*"/>)', antiga) or re.search(r'</g>(<path d="[^"]*"/>)\s*</svg>', antiga)
NOME = nome.group(1)


def assinatura(cor_simbolo: str, cor_nome: str, id_mask: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 456 120" fill="{cor_nome}">'
            f'<g transform="scale(0.234375)" fill="{cor_simbolo}">{simbolo_interno(id_mask, True)}</g>{NOME}</svg>\n')


(AQUI / "otomori-assinatura.svg").write_text(assinatura("currentColor", "currentColor", "otomori-vinil-a"), encoding="utf-8")
(AQUI.parent / "otomori-assinatura-clara.svg").write_text(assinatura(ROXO, "#f3f2ee", "otomori-vinil-c"), encoding="utf-8")
(AQUI.parent / "otomori-assinatura-escura.svg").write_text(assinatura(ROXO, "#16171c", "otomori-vinil-e"), encoding="utf-8")
print("ok")
