"""Biblioteca de ilustração isométrica (SVG) para os cards de serviço do deck Nouvenn × Vivo.

Convenções
- Coordenadas 3D em "unidades": x cresce para a direita-baixo, y para a esquerda-baixo, z para cima.
- Pintura pelo algoritmo do pintor: desenhe do fundo para a frente (menor x+y primeiro, maior z depois).
- Cada cena é montada com scene([...]) e recebe viewBox recortado automaticamente.
- Cores: use as paletas abaixo (W, G, STEEL, TEAL, BLUE, NAVY, VIVO, BRASS, GREEN, ASPH) para manter o mesmo estilo
  da maquete 3D do deck (brancos frios, cinza-azulado, teal Nouvenn, roxo Vivo).
- Classes de animação disponíveis (CSS já no deck): .pulse (anéis que expandem, use em <g> com <circle r>),
  .led (pisca), .wv (ondas piscando), .glow (pulsa opacidade lenta).
"""
import math

C30 = math.cos(math.pi / 6)
U = 22.0  # px por unidade
_bb = [1e9, 1e9, -1e9, -1e9]  # acumulador: tudo que for desenhado até o próximo scene()


def _track(X, Y, pad=0.0):
    if True:
        _bb[0] = min(_bb[0], X - pad); _bb[1] = min(_bb[1], Y - pad)
        _bb[2] = max(_bb[2], X + pad); _bb[3] = max(_bb[3], Y + pad)


def P(x, y, z=0.0):
    """Projeta (x,y,z) em pixels do SVG."""
    X = (x - y) * C30 * U
    Y = (x + y) * 0.5 * U - z * U
    _track(X, Y)
    return (X, Y)


def extend(X, Y, pad):
    """Inclui no recorte um ponto já projetado com folga (para círculos, textos, ondas)."""
    _track(X, Y, pad)


def pts(*p):
    return ' '.join(f'{a:.1f},{b:.1f}' for a, b in p)


# ---------- cor ----------
def _hex(c):
    c = c.lstrip('#'); return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def mix(c1, c2, t):
    a, b = _hex(c1), _hex(c2)
    return '#' + ''.join(f'{round(a[i] + (b[i] - a[i]) * t):02X}' for i in range(3))


def shades(base):
    """Retorna (topo, esquerda, direita) a partir de uma cor base: topo mais claro, direita mais escura."""
    return (mix(base, '#FFFFFF', .28), base, mix(base, '#0B2A30', .18))


W = ('#FFFFFF', '#E6EEF1', '#CFDCE1')      # concreto/fachada clara
G = ('#F0F5F6', '#D6E2E5', '#BFCDD2')      # cinza claro
STEEL = ('#C9D5DA', '#9FB2BA', '#82979F')  # metal / tubos
TEAL = ('#3ED6C8', '#11A89C', '#0B867D')
BLUE = ('#C9A4FF', '#9B5CF6', '#7A3CE0')   # hardware Nouvenn em violeta (destaque)
NAVY = ('#1E7480', '#0D5560', '#08414A')
VIVO = ('#B04EE0', '#8A2BC4', '#660099')   # roxo Vivo
BRASS = ('#F4DFA8', '#D6AE5C', '#B48C3E')
GREEN = ('#A7DDB0', '#7CC98B', '#5DAE70')
ASPH = ('#9AA8AE', '#7E8C93', '#6A777E')   # asfalto
GLASS = '#A8DAEB'
INK = '#0E2F38'


# ---------- primitivas ----------
def face(points3d, fill, stroke=None, sw=0.8, extra=''):
    p = [P(*q) for q in points3d]
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ''
    return f'<polygon points="{pts(*p)}" fill="{fill}"{st}{extra}/>'


def box(x, y, z, w, d, h, cols, edge=True, top_extra=''):
    """Prisma retangular. cols = (topo, esquerda, direita). Desenha só as 3 faces visíveis."""
    top, left, right = cols
    e = (lambda c: mix(c, '#0B2A30', .22)) if edge else (lambda c: None)
    s = face([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], left, e(left))
    s += face([(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)], right, e(right))
    s += face([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], top, e(top), extra=top_extra)
    return s


def cyl(x, y, z, r, h, cols, edge=True):
    """Cilindro vertical centrado em (x,y), base em z. cols = (topo, lateral, sombra)."""
    top, side, dark = cols
    cx, cy = P(x, y, z)
    rx, ry = r * U * 1.22, r * U * 0.70
    th = h * U
    extend(cx, cy - th, rx)
    extend(cx, cy, rx)
    gid = f'g{abs(hash((x, y, z, r, h, side))) % 10**8}'
    st = f' stroke="{mix(side, "#0B2A30", .25)}" stroke-width=".8"' if edge else ''
    return (f'<defs><linearGradient id="{gid}" x1="0" x2="1"><stop offset="0" stop-color="{mix(side, "#FFFFFF", .25)}"/>'
            f'<stop offset=".55" stop-color="{side}"/><stop offset="1" stop-color="{dark}"/></linearGradient></defs>'
            f'<path d="M{cx - rx:.1f},{cy - th:.1f} L{cx - rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 0 0 {cx + rx:.1f},{cy:.1f} '
            f'L{cx + rx:.1f},{cy - th:.1f} Z" fill="url(#{gid})"{st}/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy - th:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{top}"{st}/>')


def pipe(a3, b3, r, col='#A9BEC6'):
    """Tubo entre dois pontos 3D (linha grossa com brilho)."""
    a, b = P(*a3), P(*b3)
    w = 2 * r * U
    hl = mix(col, '#FFFFFF', .55)
    dk = mix(col, '#0B2A30', .3)
    return (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{dk}" stroke-width="{w + 1.6:.1f}" stroke-linecap="round"/>'
            f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            f'<line x1="{a[0]:.1f}" y1="{a[1] - w * .22:.1f}" x2="{b[0]:.1f}" y2="{b[1] - w * .22:.1f}" stroke="{hl}" stroke-width="{max(1.2, w * .22):.1f}" stroke-linecap="round" opacity=".9"/>')


def line3(a3, b3, col, w=2.0, extra=''):
    a, b = P(*a3), P(*b3)
    return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{extra}/>'


def dot(p3, r, fill, cls='', style=''):
    c = P(*p3); extend(c[0], c[1], r)
    k = f' class="{cls}"' if cls else ''
    s = f' style="{style}"' if style else ''
    return f'<circle{k}{s} cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r}" fill="{fill}"/>'


def shadow(x, y, w, d, op=.18):
    """Sombra suave no chão sob um objeto de base w×d."""
    c = P(x + w / 2, y + d / 2, 0)
    rx = (w + d) * C30 * U * .62; ry = (w + d) * .5 * U * .55
    return f'<ellipse cx="{c[0]:.1f}" cy="{c[1] + 3:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="rgba(6,54,61,{op})" filter="url(#isoBlur)"/>'


def win_left(x, y, z, w, d, h, rows, cols_n=None, col=GLASS):
    """Janelas em faixa na fachada esquerda (plano y = y+d)."""
    out = ''
    for i in range(rows):
        z0 = z + h * (i + .28) / (rows + .15); z1 = z0 + h * .42 / (rows + .15)
        out += face([(x + .18, y + d + .001, z0), (x + w - .18, y + d + .001, z0), (x + w - .18, y + d + .001, z1), (x + .18, y + d + .001, z1)], col)
    return out


def win_right(x, y, z, w, d, h, rows, col='#C2E6F2'):
    out = ''
    for i in range(rows):
        z0 = z + h * (i + .28) / (rows + .15); z1 = z0 + h * .42 / (rows + .15)
        out += face([(x + w + .001, y + .18, z0), (x + w + .001, y + d - .18, z0), (x + w + .001, y + d - .18, z1), (x + w + .001, y + .18, z1)], col)
    return out


def building(x, y, w, d, h, rows, cols=W, roof=True):
    s = box(x, y, 0, w, d, h, cols) + win_left(x, y, 0, w, d, h, rows) + win_right(x, y, 0, w, d, h, rows)
    if roof:
        s += box(x + .15, y + .15, h, w - .3, d - .3, .08, G)
    return s


def tree(x, y, s=1.0):
    c = P(x, y, 0)
    extend(c[0], c[1] - 26 * s, 12 * s)
    return (f'<ellipse cx="{c[0]:.1f}" cy="{c[1] + 2:.1f}" rx="{9 * s:.1f}" ry="{4 * s:.1f}" fill="rgba(6,54,61,.15)"/>'
            f'<line x1="{c[0]:.1f}" y1="{c[1]:.1f}" x2="{c[0]:.1f}" y2="{c[1] - 12 * s:.1f}" stroke="#8A7A64" stroke-width="{2.6 * s:.1f}" stroke-linecap="round"/>'
            f'<circle cx="{c[0]:.1f}" cy="{c[1] - 18 * s:.1f}" r="{9 * s:.1f}" fill="{GREEN[1]}"/>'
            f'<circle cx="{c[0] - 3 * s:.1f}" cy="{c[1] - 21 * s:.1f}" r="{5 * s:.1f}" fill="{GREEN[0]}"/>')


def waves(p3, col, size=1.0, cls='wv'):
    """Ícone de sinal sem fio (dois arcos) saindo de um ponto 3D."""
    c = P(*p3); extend(c[0] + 18 * size, c[1], 16 * size)
    a, b = 8 * size, 14 * size
    return (f'<g class="{cls}" fill="none" stroke="{col}" stroke-width="{2.2 * size:.1f}" stroke-linecap="round">'
            f'<path d="M{c[0] + 6 * size:.1f},{c[1] - a * .75:.1f} a{a:.1f},{a:.1f} 0 0 1 0,{a * 1.5:.1f}"/>'
            f'<path d="M{c[0] + 11 * size:.1f},{c[1] - b * .75:.1f} a{b:.1f},{b:.1f} 0 0 1 0,{b * 1.5:.1f}" opacity=".6"/></g>')


def pulse(p3, col, r=14):
    c = P(*p3); extend(c[0], c[1], r * 1.9)
    return (f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="3.6" fill="{col}"/>'
            f'<g class="pulse" fill="none" stroke="{col}" stroke-width="2.2" transform="translate({c[0]:.1f},{c[1]:.1f})">'
            f'<circle r="{r}"/><circle r="{r}" style="animation-delay:.9s"/></g>')


def label(p3, text, col=INK, size=11, weight=600, anchor='middle'):
    c = P(*p3); extend(c[0], c[1] - size / 2, len(text) * size * .32 + 4)
    return f'<text x="{c[0]:.1f}" y="{c[1]:.1f}" text-anchor="{anchor}" font-family="Poppins,Segoe UI,sans-serif" font-weight="{weight}" font-size="{size}" fill="{col}">{text}</text>'


def tile(n=4.0, m=None, ground='#F4F9F9', walk='#EAF3F1'):
    """Base da cena: placa de n×m com espessura e calçada interna."""
    m = m or n
    c = P(n / 2, m / 2, -.4)
    s = f'<ellipse cx="{c[0]:.1f}" cy="{c[1] + 12:.1f}" rx="{(n + m) * C30 * U * .56:.1f}" ry="{(n + m) * .5 * U * .42:.1f}" fill="rgba(6,54,61,.20)" filter="url(#isoBlur)"/>'
    s += box(0, 0, -.42, n, m, .42, ('#F8FBFB', '#DCE8EA', '#C6D7DA'))
    s += face([(.22, .22, 0), (n - .22, .22, 0), (n - .22, m - .22, 0), (.22, m - .22, 0)], walk)
    return s


def scene(objs, n=4.0, m=None, base=True, pad=8):
    """Monta a cena e recorta o viewBox ao conteúdo.
    IMPORTANTE: o recorte considera tudo que foi desenhado desde o scene() anterior. Construa os objetos de cada cena
    logo antes de chamá-la (ex.: SCENES = [scene([a()]), scene([b()])]) e não reaproveite strings prontas entre cenas;
    se precisar, chame reset_bbox() antes de começar a montar uma cena."""
    body = (tile(n, m) if base else '') + ''.join(objs if isinstance(objs, (list, tuple)) else [objs])
    x0, y0, x1, y1 = _bb
    reset_bbox()
    x0 -= pad; y0 -= pad; x1 += pad; y1 += pad + 14  # +14: sombra da base
    return (f'<svg class="isoS" viewBox="{x0:.0f} {y0:.0f} {x1 - x0:.0f} {y1 - y0:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{body}</svg>')


def reset_bbox():
    _bb[:] = [1e9, 1e9, -1e9, -1e9]


# ---------- peças comuns (reutilize nos cinco serviços) ----------
def vivo_tower(cx=2.0, cy=2.0, H=4.8, shelter=True):
    """Torre celular treliçada com antenas roxas Vivo, micro-ondas e pulso de sinal no topo."""
    b = .55
    s = shadow(cx - b, cy - b, 2 * b, 2 * b, .14)
    if shelter:
        s += shadow(cx + .55, cy - 1.55, 1.1, .85) + box(cx + .55, cy - 1.55, 0, 1.1, .85, .85, W)
        s += face([(cx + 1.651, cy - 1.35, .2), (cx + 1.651, cy - .95, .2), (cx + 1.651, cy - .95, .62), (cx + 1.651, cy - 1.35, .62)], STEEL[1])
    legs = [(-b, -b), (b, -b), (b, b), (-b, b)]
    for dx, dy in legs[:2]:
        s += line3((cx + dx, cy + dy, 0), (cx + dx * .18, cy + dy * .18, H), '#8796A0', 2.2)
    for k in (.9, 1.8, 2.7, 3.5):
        f = 1 - k / H * .82
        ring = [P(cx + dx * f, cy + dy * f, k) for dx, dy in legs + legs[:1]]
        s += f'<polyline points="{pts(*ring)}" fill="none" stroke="#A9B6BD" stroke-width="1.5"/>'
        if k < 3.5:
            f2 = 1 - (k + .9) / H * .82
            s += line3((cx - b * f, cy + b * f, k), (cx + b * f2, cy + b * f2, k + .9), '#B7C3C9', 1.1)
    for dx, dy in legs[2:]:
        s += line3((cx + dx, cy + dy, 0), (cx + dx * .18, cy + dy * .18, H), '#7A8992', 2.4)
    # antenas setoriais roxas
    for ox, oy in ((-.28, .02), (.04, -.3), (.12, .14)):
        s += box(cx + ox, cy + oy, H - 1.25, .16, .2, .78, VIVO)
    # micro-ondas
    d = P(cx - .25, cy + .3, H - 2.0)
    s += f'<ellipse cx="{d[0]:.1f}" cy="{d[1]:.1f}" rx="5.5" ry="7" fill="#EEF3F5" stroke="#8796A0" stroke-width="1"/>'
    s += line3((cx, cy, H - .1), (cx, cy, H + .5), '#7A8992', 2)
    s += pulse((cx, cy, H + .55), VIVO[1], 15)
    return s


def noumind_dc(ox=.6, oy=.6, w=2.8, d=2.4, h=1.5):
    """Prédio de dados Nouvenn com racks no terraço e nuvem nouMIND."""
    s = shadow(ox, oy, w, d) + box(ox, oy, 0, w, d, h, W)
    s += win_left(ox, oy, 0, w, d, h, 2) + win_right(ox, oy, 0, w, d, h, 2)
    s += box(ox + .12, oy + .12, h, w - .24, d - .24, .06, G)
    n = 3
    for i in range(n):
        x = ox + .35 + i * (w - .5) / n
        s += box(x, oy + .5, h + .06, .5, d - 1.0, .62, NAVY)
        for k in range(3):
            s += dot((x + .501, oy + .62 + k * (d - 1.2) / 3, h + .45), 1.9, '#5EF2E2', 'led', f'animation-delay:{(i * 3 + k) * .17:.2f}s')
    c = P(ox + w / 2, oy + d / 2, h + 1.9)
    extend(c[0], c[1], 40)
    s += (f'<g transform="translate({c[0]:.1f},{c[1]:.1f})"><path d="M-34,12 a14,14 0 0 1 4,-25 a20,20 0 0 1 38,-5 a13,13 0 0 1 22,20 a10,10 0 0 1 -6,10z" '
          f'fill="#FFFFFF" stroke="{TEAL[1]}" stroke-width="2.4"/>'
          f'<text x="0" y="6" text-anchor="middle" font-family="Poppins,Segoe UI,sans-serif" font-weight="600" font-size="12.5" fill="{TEAL[2]}">nou<tspan font-weight="500">MIND</tspan></text></g>')
    s += line3((ox + w / 2, oy + d / 2, h + .7), (ox + w / 2, oy + d / 2, h + 1.25), TEAL[1], 1.6, ' stroke-dasharray="3 3"')
    return s


def screen_y(x0, x1, y, z0, z1, frame=INK, bg='#0B3F47'):
    """Tela plana virada para a esquerda (plano y constante). Retorna (svg, f) onde f(u,v)->ponto 3D na tela (u,v em 0..1)."""
    s = face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], bg, frame, 1.6)
    def f(u, v):
        return (x0 + (x1 - x0) * u, y + .001, z0 + (z1 - z0) * v)
    return s, f


def screen_x(y0, y1, x, z0, z1, frame=INK, bg='#0B3F47'):
    """Tela plana virada para a direita (plano x constante)."""
    s = face([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], bg, frame, 1.6)
    def f(u, v):
        return (x + .001, y0 + (y1 - y0) * u, z0 + (z1 - z0) * v)
    return s, f


def bars_on(f, values, col='#5EF2E2', hi=None, hi_col='#F2C27A'):
    """Gráfico de barras desenhado numa tela retornada por screen_x/screen_y."""
    s = ''
    n = len(values)
    for i, v in enumerate(values):
        u0 = .1 + i * .8 / n; u1 = u0 + .8 / n * .62
        s += face([f(u0, .12), f(u1, .12), f(u1, .12 + v * .72), f(u0, .12 + v * .72)], hi_col if i == hi else col)
    return s


def line_on(f, values, col='#5EF2E2', w=2.0):
    p = [P(*f(.08 + i * .84 / (len(values) - 1), .15 + v * .7)) for i, v in enumerate(values)]
    return f'<polyline points="{pts(*p)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'


DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
        '<filter id="isoBlur" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="5"/></filter>'
        '</defs></svg>')
