"""Génère les illustrations SVG originales du catalogue (motifs wax, kente, bogolan, vannerie).
Aucune image externe : pas de droits à gérer. Remplaçables par de vraies photos de produits.
    python tools/gen_images.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "frontend" / "assets" / "img"
INDIGO, TERRA, GOLD, GREEN, CREAM, INK, BROWN = "#1c2347", "#b5532b", "#d4a23a", "#2f6b4f", "#f7f1e6", "#231f1c", "#6b3f22"


# ---------- Motifs ----------
def wax_circles(pid, bg=TERRA, c1=GOLD, c2=INDIGO, c3=CREAM, s=56):
    h = s / 2
    return f'''<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
<rect width="{s}" height="{s}" fill="{bg}"/>
<circle cx="{h}" cy="{h}" r="{s*.38}" fill="{c2}"/><circle cx="{h}" cy="{h}" r="{s*.28}" fill="{c1}"/>
<circle cx="{h}" cy="{h}" r="{s*.17}" fill="{c3}"/><circle cx="{h}" cy="{h}" r="{s*.07}" fill="{c2}"/>
<circle cx="0" cy="0" r="{s*.09}" fill="{c3}"/><circle cx="{s}" cy="0" r="{s*.09}" fill="{c3}"/>
<circle cx="0" cy="{s}" r="{s*.09}" fill="{c3}"/><circle cx="{s}" cy="{s}" r="{s*.09}" fill="{c3}"/></pattern>'''


def wax_leaves(pid, bg=INDIGO, c1=GOLD, c2=TERRA, c3=CREAM, s=60):
    return f'''<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
<rect width="{s}" height="{s}" fill="{bg}"/>
<ellipse cx="{s*.3}" cy="{s*.3}" rx="{s*.24}" ry="{s*.1}" fill="{c1}" transform="rotate(-35 {s*.3} {s*.3})"/>
<ellipse cx="{s*.3}" cy="{s*.3}" rx="{s*.12}" ry="{s*.04}" fill="{c2}" transform="rotate(-35 {s*.3} {s*.3})"/>
<ellipse cx="{s*.75}" cy="{s*.75}" rx="{s*.24}" ry="{s*.1}" fill="{c3}" transform="rotate(35 {s*.75} {s*.75})"/>
<circle cx="{s*.78}" cy="{s*.22}" r="{s*.06}" fill="{c2}"/><circle cx="{s*.22}" cy="{s*.8}" r="{s*.05}" fill="{c1}"/></pattern>'''


def wax_diamonds(pid, bg=GREEN, c1=GOLD, c2=CREAM, c3=TERRA, s=48):
    h = s / 2
    return f'''<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
<rect width="{s}" height="{s}" fill="{bg}"/>
<path d="M{h} 2 L{s-2} {h} L{h} {s-2} L2 {h}Z" fill="{c1}"/><path d="M{h} {s*.22} L{s*.78} {h} L{h} {s*.78} L{s*.22} {h}Z" fill="{c3}"/>
<circle cx="{h}" cy="{h}" r="{s*.1}" fill="{c2}"/></pattern>'''


def kente(pid, cols=(GOLD, GREEN, TERRA, INK), s=64):
    q = s / 4
    bands = "".join(f'<rect x="0" y="{i*q}" width="{s}" height="{q}" fill="{c}"/>' for i, c in enumerate(cols))
    blocks = "".join(f'<rect x="{s/2}" y="{i*q}" width="{s/2}" height="{q}" fill="{cols[(i+2)%4]}"/>' for i in range(4))
    lines = "".join(f'<rect x="{s/2 + k*6}" y="0" width="2" height="{s}" fill="{CREAM}" opacity=".55"/>' for k in range(1, 5))
    return f'<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">{bands}{blocks}{lines}</pattern>'


def bogolan(pid, bg=BROWN, fg=CREAM, s=60):
    return f'''<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
<rect width="{s}" height="{s}" fill="{bg}"/>
<path d="M0 10 L10 2 L20 10 L30 2 L40 10 L50 2 L60 10" stroke="{fg}" stroke-width="3" fill="none"/>
<circle cx="10" cy="30" r="3" fill="{fg}"/><circle cx="30" cy="30" r="3" fill="{fg}"/><circle cx="50" cy="30" r="3" fill="{fg}"/>
<path d="M22 44 h16 M30 36 v16" stroke="{fg}" stroke-width="3"/>
<rect x="4" y="46" width="8" height="8" fill="none" stroke="{fg}" stroke-width="2"/><rect x="48" y="46" width="8" height="8" fill="none" stroke="{fg}" stroke-width="2"/></pattern>'''


def weave(pid, a="#c89a5b", b="#a8763d", s=24):
    h = s / 2
    return f'''<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
<rect width="{s}" height="{s}" fill="{a}"/><rect width="{h}" height="{h}" fill="{b}"/><rect x="{h}" y="{h}" width="{h}" height="{h}" fill="{b}"/>
<path d="M0 {h} H{s} M{h} 0 V{s}" stroke="#7a5124" stroke-width="1" opacity=".5"/></pattern>'''


def scene(pid, defs, body, bg="#f3eadb", w=400, h=300):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">
<defs>{defs}
<radialGradient id="{pid}-bg" cx=".5" cy=".42" r=".75"><stop offset="0" stop-color="#fffaf1"/><stop offset="1" stop-color="{bg}"/></radialGradient>
<linearGradient id="{pid}-shade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".18"/><stop offset=".45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".22"/></linearGradient>
<linearGradient id="{pid}-wood" x1="0" x2="1"><stop offset="0" stop-color="#5a3216"/><stop offset=".5" stop-color="#8a5429"/><stop offset="1" stop-color="#4a2810"/></linearGradient>
</defs>
<rect width="{w}" height="{h}" fill="url(#{pid}-bg)"/>
<ellipse cx="{w/2}" cy="{h*.86}" rx="{w*.3}" ry="{h*.045}" fill="#000" opacity=".12"/>
{body}</svg>'''


# ---------- Objets (coordonnées pour un cadre 400x300) ----------
def dress(fill, p):
    return f'''<path d="M170 55 Q200 72 230 55 L246 70 L236 110 Q250 200 285 255 Q200 272 115 255 Q150 200 164 110 L154 70 Z" fill="{fill}" stroke="{INK}" stroke-width="2"/>
<path d="M170 55 Q200 72 230 55 L246 70 L236 110 Q250 200 285 255 Q200 272 115 255 Q150 200 164 110 L154 70 Z" fill="url(#{p}-shade)"/>
<path d="M164 110 Q200 122 236 110" stroke="{GOLD}" stroke-width="5" fill="none"/>'''


def boubou(fill, p):
    return f'''<path d="M150 50 L250 50 L330 120 L300 150 L262 120 L268 262 L132 262 L138 120 L100 150 L70 120 Z" fill="{fill}" stroke="{INK}" stroke-width="2"/>
<path d="M150 50 L250 50 L330 120 L300 150 L262 120 L268 262 L132 262 L138 120 L100 150 L70 120 Z" fill="url(#{p}-shade)"/>
<path d="M182 50 Q200 80 218 50" fill="#fffaf1" stroke="{INK}" stroke-width="2"/>
<path d="M175 60 Q200 150 225 60 M185 70 Q200 130 215 70" stroke="{GOLD}" stroke-width="3" fill="none"/>
<path d="M190 150 l10 12 l10 -12 l-10 -12 z" fill="{GOLD}"/>'''


def bag(fill, p):
    return f'''<path d="M160 120 Q160 60 200 60 Q240 60 240 120" stroke="{BROWN}" stroke-width="9" fill="none"/>
<path d="M120 115 L280 115 L262 262 L138 262 Z" fill="{fill}" stroke="{INK}" stroke-width="2"/>
<path d="M120 115 L280 115 L262 262 L138 262 Z" fill="url(#{p}-shade)"/>
<rect x="120" y="115" width="160" height="14" fill="{INK}" opacity=".85"/>'''


def cushion(fill, p):
    return f'''<path d="M110 80 Q200 60 290 80 Q312 165 290 250 Q200 270 110 250 Q88 165 110 80Z" fill="{fill}" stroke="{CREAM}" stroke-width="6"/>
<path d="M110 80 Q200 60 290 80 Q312 165 290 250 Q200 270 110 250 Q88 165 110 80Z" fill="url(#{p}-shade)"/>
<circle cx="200" cy="165" r="10" fill="{CREAM}" stroke="{INK}" stroke-width="2"/>'''


def throw(fill, p):
    fr = "".join(f'<line x1="{x}" y1="250" x2="{x}" y2="266" stroke="{CREAM}" stroke-width="3"/>' for x in range(96, 306, 9))
    return f'''<rect x="90" y="150" width="220" height="100" rx="6" fill="{fill}" stroke="{INK}" stroke-width="2"/>
<rect x="100" y="95" width="200" height="70" rx="6" fill="{fill}" stroke="{INK}" stroke-width="2"/>
<rect x="110" y="55" width="180" height="55" rx="6" fill="{fill}" stroke="{INK}" stroke-width="2"/>
<rect x="90" y="150" width="220" height="100" fill="url(#{p}-shade)"/>{fr}'''


def jar(p, label="KARITÉ"):
    return f'''<rect x="140" y="120" width="120" height="140" rx="18" fill="#efe3c8" stroke="{INK}" stroke-width="2"/>
<rect x="140" y="120" width="120" height="140" rx="18" fill="url(#{p}-shade)"/>
<rect x="132" y="92" width="136" height="40" rx="8" fill="url(#{p}-wood)" stroke="{INK}" stroke-width="2"/>
<rect x="152" y="165" width="96" height="58" fill="{CREAM}" stroke="{TERRA}" stroke-width="2"/>
<text x="200" y="200" text-anchor="middle" font-family="Georgia,serif" font-size="17" fill="{TERRA}" font-weight="700">{label}</text>
<path d="M160 116 Q200 70 240 116" fill="#f7efdc" opacity=".9"/>'''


def soap(p):
    return f'''<rect x="110" y="150" width="180" height="90" rx="26" fill="#3b2a1e" stroke="{INK}" stroke-width="2"/>
<rect x="110" y="150" width="180" height="90" rx="26" fill="url(#{p}-shade)"/>
<ellipse cx="200" cy="190" rx="52" ry="22" fill="none" stroke="#7a5a3e" stroke-width="4"/>
<path d="M175 190 h50 M200 175 v30" stroke="#7a5a3e" stroke-width="4"/>
<path d="M120 140 q40 -50 90 -30 q30 -40 70 -10" stroke="{GREEN}" stroke-width="6" fill="none"/>
<ellipse cx="300" cy="120" rx="22" ry="10" fill="{GREEN}" transform="rotate(-30 300 120)"/>'''


def sack(p, label="CAFÉ TOUBA"):
    beans = "".join(f'<ellipse cx="{x}" cy="{y}" rx="9" ry="6" fill="#4a2a14" transform="rotate({r} {x} {y})"/>'
                    for x, y, r in [(95, 255, 20), (115, 262, -30), (300, 258, 40), (318, 250, -10), (285, 266, 0)])
    return f'''<path d="M140 80 L260 80 L272 262 L128 262 Z" fill="#c9a170" stroke="{INK}" stroke-width="2"/>
<path d="M140 80 L260 80 L272 262 L128 262 Z" fill="url(#{p}-shade)"/>
<path d="M140 80 L150 64 L250 64 L260 80" fill="#b88c5a" stroke="{INK}" stroke-width="2"/>
<rect x="152" y="140" width="96" height="70" fill="{CREAM}" stroke="{INDIGO}" stroke-width="2"/>
<text x="200" y="172" text-anchor="middle" font-family="Georgia,serif" font-size="12" font-weight="700" fill="{INDIGO}">{label}</text>
<text x="200" y="192" text-anchor="middle" font-family="Georgia,serif" font-size="10" fill="{TERRA}">Dakar · 500 g</text>{beans}'''


def bottle(p, label="BAOBAB"):
    return f'''<rect x="168" y="70" width="64" height="40" rx="6" fill="{INK}"/>
<path d="M180 110 L220 110 L246 150 L246 262 L154 262 L154 150 Z" fill="#a8641f" stroke="{INK}" stroke-width="2" opacity=".95"/>
<path d="M180 110 L220 110 L246 150 L246 262 L154 262 L154 150 Z" fill="url(#{p}-shade)"/>
<rect x="164" y="175" width="72" height="60" fill="{CREAM}" stroke="{GOLD}" stroke-width="2"/>
<text x="200" y="210" text-anchor="middle" font-family="Georgia,serif" font-size="13" font-weight="700" fill="{GREEN}">{label}</text>
<path d="M290 160 q20 -40 10 -90 M290 160 q-30 -30 -20 -70" stroke="{GREEN}" stroke-width="5" fill="none"/>'''


def basket(p):
    return f'''<path d="M90 140 Q200 120 310 140 Q300 250 200 262 Q100 250 90 140Z" fill="url(#{p}-weave)" stroke="#6b4420" stroke-width="3"/>
<path d="M90 140 Q200 120 310 140 Q300 250 200 262 Q100 250 90 140Z" fill="url(#{p}-shade)"/>
<ellipse cx="200" cy="138" rx="110" ry="20" fill="#7a5124" stroke="#6b4420" stroke-width="3"/>
<path d="M92 160 Q200 182 308 160" stroke="{TERRA}" stroke-width="7" fill="none"/>
<path d="M98 190 Q200 212 302 190" stroke="{INDIGO}" stroke-width="7" fill="none"/>'''


def bowl_flowers(p):
    petals = "".join(f'<path d="M{x} {y} q12 -18 24 0 q-12 14 -24 0z" fill="{c}" transform="rotate({r} {x+12} {y})"/>'
                     for x, y, r, c in [(150, 160, 10, "#8d1b2c"), (175, 150, -20, "#a3243a"), (200, 158, 30, "#7a1626"),
                                        (225, 148, -10, "#9b2035"), (165, 175, 40, "#a3243a"), (205, 172, -35, "#8d1b2c"),
                                        (230, 168, 15, "#7a1626"), (185, 140, 0, "#b02a42")])
    return f'''{petals}<path d="M110 170 Q200 180 290 170 Q280 250 200 258 Q120 250 110 170Z" fill="url(#{p}-wood)" stroke="{INK}" stroke-width="2"/>
<path d="M120 200 Q200 214 280 200" stroke="{GOLD}" stroke-width="3" fill="none" opacity=".7"/>'''


def mask(p):
    return f'''<path d="M200 40 Q262 60 262 150 Q258 238 200 268 Q142 238 138 150 Q138 60 200 40Z" fill="url(#{p}-wood)" stroke="{INK}" stroke-width="2"/>
<path d="M160 120 Q178 108 192 122 Q178 132 160 120Z M208 122 Q222 108 240 120 Q222 132 208 122Z" fill="{INK}"/>
<path d="M200 128 L192 190 L208 190 Z" fill="#4a2810"/>
<path d="M180 214 Q200 226 220 214" stroke="{INK}" stroke-width="4" fill="none"/>
<path d="M170 70 Q200 58 230 70 M175 86 Q200 76 225 86" stroke="{GOLD}" stroke-width="3" fill="none"/>
<circle cx="150" cy="170" r="4" fill="{CREAM}"/><circle cx="250" cy="170" r="4" fill="{CREAM}"/>'''


def fabric_stack(p, fills):
    out = ""
    for i, f in enumerate(fills):
        y = 210 - i * 38
        out += f'<rect x="{100 + i*6}" y="{y}" width="{200 - i*12}" height="40" rx="5" fill="{f}" stroke="{INK}" stroke-width="2"/>'
        out += f'<rect x="{100 + i*6}" y="{y}" width="{200 - i*12}" height="40" rx="5" fill="url(#{p}-shade)"/>'
    return out


# ---------- Catalogue ----------
def product_svgs():
    items = {}
    p = "boubou"; items[p] = scene(p, wax_diamonds(f"{p}-m", bg="#e9e2d0", c1=GOLD, c2="#fffaf1", c3="#c9b98f"),
                                   boubou(f"url(#{p}-m)", p))
    p = "panier-thies"; items[p] = scene(p, weave(f"{p}-weave"), basket(p))
    p = "cafe-touba"; items[p] = scene(p, "", sack(p))
    p = "karite"; items[p] = scene(p, "", jar(p))
    p = "savon-noir"; items[p] = scene(p, "", soap(p))
    p = "robe-wax"; items[p] = scene(p, wax_circles(f"{p}-m"), dress(f"url(#{p}-m)", p))
    p = "cabas-pagne"; items[p] = scene(p, wax_leaves(f"{p}-m"), bag(f"url(#{p}-m)", p))
    p = "plaid-bogolan"; items[p] = scene(p, bogolan(f"{p}-m"), throw(f"url(#{p}-m)", p))
    p = "coussin-bogolan"; items[p] = scene(p, bogolan(f"{p}-m", bg="#3a2a20"), cushion(f"url(#{p}-m)", p))
    p = "bissap"; items[p] = scene(p, "", bowl_flowers(p))
    p = "huile-baobab"; items[p] = scene(p, "", bottle(p))
    p = "masque"; items[p] = scene(p, "", mask(p), bg="#eadfca")
    return items


def duo(left, right):
    return (f'<g transform="translate(-10 70) scale(.72)">{left}</g>'
            f'<g transform="translate(122 70) scale(.72)">{right}</g>')


def category_svgs():
    c = {}
    p = "vetements"; c[p] = scene(p, wax_circles(f"{p}-a") + wax_leaves(f"{p}-b") + kente(f"{p}-c") + wax_diamonds(f"{p}-d"),
                                 fabric_stack(p, [f"url(#{p}-a)", f"url(#{p}-c)", f"url(#{p}-b)", f"url(#{p}-d)"]))
    p = "artisanat"; c[p] = scene(p, weave(f"{p}-weave"), duo(mask(p), basket(p)))
    p = "cosmetiques"; c[p] = scene(p, "", duo(jar(p), bottle(p)))
    p = "epicerie"; c[p] = scene(p, "", duo(sack(p, "ÉPICES &amp; CAFÉ"), bowl_flowers(p)))
    p = "maison"; c[p] = scene(p, bogolan(f"{p}-m") + bogolan(f"{p}-n", bg="#3a2a20"), duo(throw(f"url(#{p}-m)", p), cushion(f"url(#{p}-n)", p)))
    return c


def hero_svg():
    defs = wax_circles("h-a", s=80) + wax_leaves("h-b", s=90) + kente("h-c", s=72) + weave("h-weave")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 560" role="img" aria-label="Tissus wax, panier tressé et beurre de karité">
<defs>{defs}<linearGradient id="h-shade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".2"/><stop offset=".5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient>
<linearGradient id="h-wood" x1="0" x2="1"><stop offset="0" stop-color="#5a3216"/><stop offset=".5" stop-color="#8a5429"/><stop offset="1" stop-color="#4a2810"/></linearGradient></defs>
<rect width="640" height="560" fill="url(#h-b)"/>
<path d="M0 0 H640 V560 H0Z" fill="#1c2347" opacity=".25"/>
<path d="M60 40 Q320 10 580 40 L600 520 Q320 560 40 520 Z" fill="url(#h-a)"/>
<path d="M60 40 Q320 10 580 40 L600 520 Q320 560 40 520 Z" fill="url(#h-shade)"/>
<path d="M40 380 Q320 330 600 380 L600 520 Q320 560 40 520 Z" fill="url(#h-c)"/>
<path d="M40 380 Q320 330 600 380" stroke="#f7f1e6" stroke-width="6" fill="none"/>
<g transform="translate(250 200) scale(.95)">
<ellipse cx="200" cy="270" rx="150" ry="18" fill="#000" opacity=".25"/>
<path d="M90 140 Q200 120 310 140 Q300 250 200 262 Q100 250 90 140Z" fill="url(#h-weave)" stroke="#6b4420" stroke-width="3"/>
<path d="M90 140 Q200 120 310 140 Q300 250 200 262 Q100 250 90 140Z" fill="url(#h-shade)"/>
<ellipse cx="200" cy="138" rx="110" ry="20" fill="#7a5124" stroke="#6b4420" stroke-width="3"/>
<path d="M92 160 Q200 182 308 160" stroke="#b5532b" stroke-width="7" fill="none"/><path d="M98 190 Q200 212 302 190" stroke="#1c2347" stroke-width="7" fill="none"/></g>
<g transform="translate(20 230) scale(.85)">
<ellipse cx="200" cy="268" rx="90" ry="12" fill="#000" opacity=".25"/>
<rect x="140" y="120" width="120" height="140" rx="18" fill="#efe3c8" stroke="#231f1c" stroke-width="2"/>
<rect x="132" y="92" width="136" height="40" rx="8" fill="url(#h-wood)" stroke="#231f1c" stroke-width="2"/>
<rect x="152" y="165" width="96" height="58" fill="#f7f1e6" stroke="#b5532b" stroke-width="2"/>
<text x="200" y="200" text-anchor="middle" font-family="Georgia,serif" font-size="17" fill="#b5532b" font-weight="700">KARITÉ</text></g>
</svg>'''


def band_svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 40" preserveAspectRatio="none">
<defs>{kente("band", s=40)}</defs><rect width="1200" height="40" fill="url(#band)"/></svg>'''


def pattern_tile():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240">
<defs>{bogolan("t", bg="#2a1c14", fg="#d9c3a0", s=60)}</defs><rect width="240" height="240" fill="url(#t)"/></svg>'''


def main():
    for sub, items in (("products", product_svgs()), ("categories", category_svgs())):
        d = OUT / sub
        d.mkdir(parents=True, exist_ok=True)
        for name, svg in items.items():
            (d / f"{name}.svg").write_text(svg, encoding="utf-8")
    (OUT / "hero.svg").write_text(hero_svg(), encoding="utf-8")
    (OUT / "kente-band.svg").write_text(band_svg(), encoding="utf-8")
    (OUT / "bogolan-tile.svg").write_text(pattern_tile(), encoding="utf-8")
    print("Images générées dans", OUT)


if __name__ == "__main__":
    main()
