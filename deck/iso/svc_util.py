from iso_lib import *
"""Cenas isométricas do slide de serviço "Monitoramento e gestão de utilidades".

1. Medidor que já existe   2. SPC · AquaCap · NIC   3. Rede Vivo   4. SPC Manager   5. Rateio e gestão
"""
import math

# ---------- cores locais ----------
GAS = ('#E6EBED', '#BCC6CB', '#9DA9AF')        # carcaça do medidor de gás
YEL = '#F2C230'                                 # tubulação de gás
LCD = '#CFEBD0'                                 # visor de medidor
AMBER = '#F2A93B'                               # alerta / destaque
CABLE = '#1E2B31'


# ---------- helpers ----------
def rect_y(x0, x1, y, z0, z1, fill, stroke=None, sw=.8):
    """Retângulo no plano y = const (face voltada para a esquerda-baixo)."""
    return face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], fill, stroke, sw)


def rect_x(y0, y1, x, z0, z1, fill, stroke=None, sw=.8):
    """Retângulo no plano x = const (face voltada para a direita-baixo)."""
    return face([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], fill, stroke, sw)


def circ(c3, r, plane, fill, stroke=None, sw=.8, n=32):
    cx, cy, cz = c3
    p = []
    for k in range(n):
        t = 2 * math.pi * k / n
        a, b = r * math.cos(t), r * math.sin(t)
        p.append((cx + a, cy + b, cz) if plane == 'z' else (cx + a, cy, cz + b) if plane == 'y' else (cx, cy + a, cz + b))
    return face(p, fill, stroke, sw)


def cable(a3, b3, sag=8, col=CABLE, w=1.7):
    a, b = P(*a3), P(*b3)
    mx, my = (a[0] + b[0]) / 2 - sag * .4, (a[1] + b[1]) / 2 + sag
    return (f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{mx:.1f},{my:.1f} {b[0]:.1f},{b[1]:.1f}" fill="none" stroke="{col}" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


def elbow(p3, r, col):
    """Junta arredondada de tubo (bolinha)."""
    c = P(*p3)
    return (f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r * U + .8:.1f}" fill="{mix(col, "#0B2A30", .3)}"/>'
            f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r * U:.1f}" fill="{col}"/>')


# ---------- peças da cena de medição ----------
WALL_H = 2.02
PY, ZC = .64, .74               # linha d'água: profundidade e altura do eixo
METERS = (1.14, 2.02, 2.90)     # x dos hidrômetros
WATER = '#A9BEC6'
RX = 3.4                        # subida da linha d'água


def walls(n, m):
    s = box(0, 0, 0, n, .22, WALL_H, W)                       # parede do fundo (direita)
    s += rect_y(0.22, n, .221, 0, .14, '#D5E1E5')               # rodapé
    s += box(0, .22, 0, .22, m - .22, WALL_H, W)               # parede lateral (esquerda)
    s += rect_x(.22, m, .221, 0, .14, '#C3D2D7')
    return s


def hidrometro(mx, y=PY, zc=ZC, dev=None):
    s = pipe((mx - .44, y, zc), (mx + .44, y, zc), .105, BRASS[1])      # roscas de latão
    s += cyl(mx, y, zc - .22, .3, .39, BRASS)                            # corpo de latão
    top = zc + .17
    s += cyl(mx, y, top, .28, .12, ('#FFFFFF', '#F3F7F8', '#C3D0D6'))   # anel branco
    t2 = top + .12
    if dev == 'aquacap':
        s += cyl(mx, y, t2, .295, .36, BLUE)                             # tampa AquaCap
        s += circ((mx, y, t2 + .36), .22, 'z', mix(BLUE[0], '#FFFFFF', .15))
        s += dot((mx + .08, y + .28, t2 + .22), 1.9, '#5EF2E2', 'led')
    else:
        s += circ((mx, y, t2), .215, 'z', '#FFFFFF', '#2B4750', 1.1)     # mostrador
        s += circ((mx, y, t2), .15, 'z', '#E2F1F6')
        s += line3((mx, y, t2), (mx + .12, y - .07, t2), '#D0574B', 1.5)  # ponteiro
        s += circ((mx - .08, y + .07, t2), .04, 'z', '#2B4750')
    return s


def valve(x, y=PY, zc=ZC):
    s = cyl(x, y, zc - .14, .14, .28, BRASS)
    s += line3((x, y, zc + .14), (x, y, zc + .27), '#4B5E66', 1.6)
    s += circ((x, y, zc + .28), .15, 'z', '#C9473D', '#8E2A22', .9)
    s += circ((x, y, zc + .28), .06, 'z', '#8E2A22')
    return s


def water_line(stage):
    s = ''
    # suportes da parede até o tubo
    for bx in (1.58, 2.46):
        s += pipe((bx, .22, ZC), (bx, PY, ZC), .04, '#9FB2BA')
    # linha principal sai da parede lateral e sobe na parede do fundo
    s += box(.22, PY - .14, ZC - .14, .08, .28, .28, STEEL)              # flange na parede
    s += pipe((.3, PY, ZC), (RX, PY, ZC), .1, WATER)
    s += pipe((RX, PY, ZC), (RX, PY, 1.72), .1, WATER)
    s += pipe((RX, PY, 1.72), (RX, .22, 1.72), .1, WATER)
    s += elbow((RX, PY, ZC), .1, WATER) + elbow((RX, PY, 1.72), .1, WATER)
    s += valve(.6)
    devs = {'base': (None, None, None), 'nouvenn': ('spc', 'aquacap', 'aquacap')}[stage]
    for mx, d in zip(METERS, devs):
        if d == 'spc':
            s += spc_wall(mx)
        s += hidrometro(mx, dev='aquacap' if d == 'aquacap' else None)
        if d == 'spc':
            s += cable((mx + .18, PY - .12, ZC + .29), (mx - .17, .42, 1.3), sag=6)
            s += dot((mx + .18, PY - .12, ZC + .29), 2.1, CABLE)
            s += waves((mx + .34, .32, 1.66), BLUE[1], .78)
        if d == 'aquacap' and mx == METERS[1]:
            s += waves((mx + .26, PY - .1, ZC + 1.0), BLUE[1], .74)
    return s


def spc_wall(mx):
    """SPC Nouvenn na parede acima do hidrômetro: caixa azul com frente prateada."""
    x0, z0 = mx - .5, 1.3
    s = box(x0, .22, z0, .66, .2, .42, BLUE)
    s += rect_y(x0 + .07, x0 + .59, .421, z0 + .07, z0 + .35, '#E4EBEF', '#AFC0C7', .7)
    s += dot((x0 + .52, .422, z0 + .28), 1.6, '#5EF2E2', 'led')
    return s


def gas_meter(stage):
    x0, y0, z0, w, d, h = 3.8, .22, .5, .7, .42, .8
    s = pipe((x0 + .17, .43, 0), (x0 + .17, .43, z0 + .05), .075, YEL)                # entrada (vem do piso)
    s += box(x0, y0, z0, w, d, h, GAS)
    s += box(x0 + .05, y0 + .05, z0 + h, w - .1, d - .1, .05, ('#F4F7F8', '#D3DBDE', '#B7C2C7'))
    yf = y0 + d + .001
    s += rect_y(x0 + .12, x0 + w - .12, yf, z0 + .44, z0 + .62, '#22343B')           # visor
    s += rect_y(x0 + .16, x0 + w - .16, yf + .001, z0 + .48, z0 + .58, '#E8F0EC')
    s += rect_y(x0 + .12, x0 + w - .26, yf, z0 + .12, z0 + .32, '#D9E1E4', '#A9B6BC', .6)  # plaqueta
    s += pipe((x0 + w - .17, .43, z0 + h + .02), (x0 + w - .17, .43, 1.74), .075, YEL)   # saída
    s += pipe((x0 + w - .17, .43, 1.74), (x0 + w - .17, .22, 1.74), .075, YEL)
    s += elbow((x0 + w - .17, .43, 1.74), .075, YEL)
    s += line3((x0 + w - .17, .43, 1.45), (x0 + w - .17 + .2, .43 + .2, 1.45), '#C0392B', 2.4)  # alavanca do registro
    if stage == 'nouvenn':
        s += box(x0 + w, y0 + .1, z0 + .2, .14, .26, .4, BLUE)                         # SPC no medidor de gás
        s += rect_x(y0 + .14, y0 + .32, x0 + w + .141, z0 + .26, z0 + .54, '#E4EBEF')
        s += waves((x0 + w + .2, y0 + .3, z0 + .78), BLUE[1], .8)
    return s


def energy_panel(stage, m):
    """Quadro de energia na parede lateral (face voltada para +x) com medidor branco e visor."""
    y0, y1, z0, z1 = .5, 1.6, .96, 1.86
    s = box(.22, y0, z0, .16, y1 - y0, z1 - z0, ('#E9EFF2', '#C9D6DB', '#B4C4CA'))     # caixa do quadro
    s += rect_x(y0 + .08, y1 - .08, .381, z0 + .08, z1 - .08, '#D7E2E6', '#A9BCC3', .7)
    s += pipe((.32, (y0 + y1) / 2, z1), (.32, (y0 + y1) / 2, WALL_H), .06, '#B6C6CC')  # eletroduto
    # medidor (caixinha branca)
    my0, my1, mz0, mz1 = .68, 1.42, 1.06, 1.74
    s += box(.38, my0, mz0, .16, my1 - my0, mz1 - mz0, ('#FFFFFF', '#F2F6F7', '#DFE8EB'))
    xf = .541
    s += rect_x(my0 + .1, my1 - .1, xf, mz0 + .44, mz1 - .1, '#2B4750')               # visor
    s += rect_x(my0 + .14, my1 - .14, xf + .001, mz0 + .48, mz1 - .14, LCD)
    s += circ((xf, my0 + .22, mz0 + .2), .07, 'x', '#C7D3D8')
    s += circ((xf, my1 - .22, mz0 + .2), .05, 'x', '#D0574B' if stage == 'base' else '#5EF2E2')
    if stage == 'nouvenn':
        # NIC: módulo de comunicação embarcado (círculo azul no medidor)
        s += circ((xf + .001, (my0 + my1) / 2, mz0 + .22), .14, 'x', BLUE[1], '#FFFFFF', 1.2)
        s += circ((xf + .002, (my0 + my1) / 2, mz0 + .22), .05, 'x', '#FFFFFF')
        s += waves((xf + .05, my0 + .05, mz1 + .02), BLUE[1], .8)
    return s


def meter_room(stage, n=5.0, m=1.75):
    s = walls(n, m)
    s += energy_panel(stage, m)
    s += water_line(stage)
    s += gas_meter(stage)
    return s


# ---------- cena 3: torre ----------
def fence(n, m, h=.5):
    """Alambrado baixo nas bordas da frente."""
    col = '#9AAAB2'
    s = ''
    yb, xb = m - .35, n - .35
    s += face([(.35, yb, 0), (xb, yb, 0), (xb, yb, h), (.35, yb, h)], 'rgba(154,170,178,.18)')
    s += face([(xb, .35, 0), (xb, yb, 0), (xb, yb, h), (xb, .35, h)], 'rgba(154,170,178,.18)')
    k = 0
    x = .35
    while x <= xb + .01:
        s += line3((x, yb, 0), (x, yb, h + .05), col, 1.6); x += .7
    y = .35
    while y < yb - .01:
        s += line3((xb, y, 0), (xb, y, h + .05), col, 1.6); y += .7
    s += line3((.35, yb, h), (xb, yb, h), col, 1.5) + line3((xb, .35, h), (xb, yb, h), col, 1.5)
    return s


# ---------- cena 4: plataforma ----------
def monitor(x0, x1, y, z0, z1, case=INK):
    xc = (x0 + x1) / 2
    s = shadow(xc - .35, y - .3, .7, .4, .2)
    s += box(xc - .32, y - .28, 0, .64, .36, .06, ('#5C7480', '#3E5560', '#2E434C'))   # pé
    s += box(xc - .06, y - .16, .06, .12, .1, z0, ('#5C7480', '#3E5560', '#2E434C'))   # haste
    s += box(x0, y - .1, z0, x1 - x0, .1, z1 - z0, ('#2E4A55', '#1A3640', '#132A33'))   # carcaça
    scr, f = screen_y(x0 + .07, x1 - .07, y + .001, z0 + .07, z1 - .07, '#0E2F38', '#0B3F47')
    return s + scr, f


# ---------- cena 5: galeria ----------
def gallery(x0=.4, y0=.4, w=4.3, d=1.5, h=1.62):
    s = shadow(x0, y0, w, d, .16)
    s += box(x0, y0, 0, w, d, h, W)
    s += box(x0 - .04, y0 - .04, h, w + .08, d + .08, .12, G)                 # platibanda
    yf = y0 + d + .001
    awn = [(mix(TEAL[0], '#FFFFFF', .2), TEAL[1]), (mix(AMBER, '#FFFFFF', .25), '#D98E26'),
           (mix(BLUE[0], '#FFFFFF', .25), BLUE[1])]
    sw = w / 3
    for k in range(3):
        a, b = x0 + k * sw + .1, x0 + (k + 1) * sw - .1
        # vitrine + porta (porta ~1 unidade)
        s += rect_y(a, b, yf, 0, 1.05, '#E3ECEF')
        s += rect_y(a + .06, b - .5, yf + .001, .16, .98, GLASS)
        s += rect_y(b - .44, b - .06, yf + .001, 0, .98, '#7FB9CC')
        s += line3((b - .25, yf + .002, 0), (b - .25, yf + .002, .98), '#E3ECEF', 1.0)
        # reflexo
        s += face([(a + .2, yf + .002, .25), (a + .34, yf + .002, .25), (a + .62, yf + .002, .9), (a + .48, yf + .002, .9)], 'rgba(255,255,255,.45)')
        # letreiro (faixa colorida discreta, sem texto)
        s += rect_y(a + .2, b - .2, yf, 1.32, 1.47, mix(awn[k][1], '#FFFFFF', .55))
        # toldo inclinado com listras
        z_top, z_bot, out = 1.22, 1.02, .42
        nst = 6
        for i in range(nst):
            u0, u1 = a + (b - a) * i / nst, a + (b - a) * (i + 1) / nst
            col = awn[k][1] if i % 2 == 0 else awn[k][0]
            s += face([(u0, yf, z_top), (u1, yf, z_top), (u1, yf + out, z_bot), (u0, yf + out, z_bot)], col)
            s += face([(u0, yf + out, z_bot), (u1, yf + out, z_bot), (u1, yf + out, z_bot - .1), (u0, yf + out, z_bot - .1)],
                      mix(col, '#0B2A30', .12))
        s += face([(b, yf, z_top), (b, yf + out, z_bot), (b, yf + out, z_bot - .1), (b, yf, z_top - .02)], mix(awn[k][1], '#0B2A30', .25))
    # lateral: janelas altas
    s += win_right(x0, y0, 0, w, d, h, 1)
    # condensadoras no telhado
    for cx in (x0 + .7, x0 + 1.9):
        s += box(cx, y0 + .35, h + .12, .7, .55, .32, ('#F4F7F8', '#D3DDE1', '#B9C7CC'))
        s += circ((cx + .35, y0 + .62, h + .441), .2, 'z', '#8FA3AB', '#6F848C', .7)
        s += circ((cx + .35, y0 + .62, h + .442), .06, 'z', '#5E727A')
    return s


# ---------- cenas ----------
def scene1():
    return scene([meter_room('base')], n=5.0, m=1.75)


def scene2():
    return scene([meter_room('nouvenn')], n=5.0, m=1.75)


def scene3():
    n, m = 5.6, 4.0
    return scene([tree(.95, 3.25, .95), vivo_tower(2.45, 1.95, 3.9), tree(4.75, 2.85, 1.05), fence(n, m)], n=n, m=m)


def scene4():
    n, m = 6.75, 3.0
    objs = [noumind_dc(.4, .45, 2.4, 2.1, 1.3)]
    mon, f = monitor(4.2, 6.4, 1.72, .5, 1.95)
    objs.append(mon)
    vals = [.28, .34, .3, .38, .33, .36, .31, .78]
    # área sob a curva
    poly = [P(*f(.08 + i * .84 / (len(vals) - 1), .15 + v * .7)) for i, v in enumerate(vals)]
    poly = [P(*f(.08, .12))] + poly + [P(*f(.92, .12))]
    objs.append(f'<polygon points="{pts(*poly)}" fill="rgba(94,242,226,.18)"/>')
    # limite (tracejado âmbar)
    objs.append(line3(f(.06, .62), f(.94, .62), AMBER, 1.2, ' stroke-dasharray="3 2.5" opacity=".9"'))
    objs.append(line_on(f, vals, '#5EF2E2', 2.2))
    tip = f(.92, .15 + .78 * .7)
    objs.append(pulse(tip, AMBER, 9))
    objs.append(dot(tip, 3.6, AMBER))
    return scene(objs, n=n, m=m)


def scene5():
    n, m = 6.6, 2.55
    objs = [gallery(.35, .35, 4.2, 1.4, 1.62)]
    mon, f = monitor(4.85, 6.35, 2.15, .45, 1.55)
    objs.append(mon)
    objs.append(line3(f(.06, .12), f(.94, .12), '#3F6E78', 1.0))
    objs.append(bars_on(f, [.42, .9, .55], '#5EF2E2', hi=1, hi_col=AMBER))
    objs.append(tree(.45, 2.2, .85))
    return scene(objs, n=n, m=m)


SCENES = [scene1(), scene2(), scene3(), scene4(), scene5()]
CARDS = ['white', 'white', 'net', 'plat', 'white']
SIZES = [(255, 230)] * 5
