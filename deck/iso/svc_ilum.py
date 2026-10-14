from iso_lib import *
"""Serviço 2 · Telegestão de iluminação pública: cenas isométricas dos 4 cards de arquitetura."""
import math

AMBER = '#F5A524'
LAMP = '#FFE7A0'
LAMP_HI = '#FFF6D2'
ROAD = '#8E9CA3'
SIDEW = ('#F3F8F8', '#D3E0E3', '#BDCDD2')
HEAD = ('#F4F7F8', '#C9D5DA', '#A9B9C0')
POLE = '#9DB1B9'
TIRE = '#2F3F46'

_n = [0]


def _id(p):
    _n[0] += 1
    return f'ilum{p}{_n[0]}'


# ---------- chão ----------
def flat(pts2, fill, z=.004, extra=''):
    return face([(x, y, z) for x, y in pts2], fill, extra=extra)


def road_x(x0, x1, y0, y1, dash=True):
    """Faixa de asfalto ao longo de x com marcação central tracejada."""
    s = flat([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ROAD)
    if dash:
        yc = (y0 + y1) / 2; L = .46; g = .34; x = x0 + .25
        while x + L < x1 - .1:
            s += flat([(x, yc - .045), (x + L, yc - .045), (x + L, yc + .045), (x, yc + .045)], '#F6F8F9', z=.008)
            x += L + g
    return s


def walk(x0, y0, w, d, h=.07):
    return box(x0, y0, 0, w, d, h, SIDEW)


def light_pool(x, y, r, op=.9):
    gid = _id('lp')
    c = P(x, y, 0); rx = r * U * 1.2247; ry = r * U * .7071
    return (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{LAMP_HI}" stop-opacity="{op}"/>'
            f'<stop offset=".5" stop-color="{LAMP}" stop-opacity="{op * .7:.2f}"/><stop offset="1" stop-color="{LAMP}" stop-opacity="0"/>'
            f'</radialGradient></defs><ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{gid})"/>')


def light_cone(x, y, zt, r, op=.55):
    """Cone de luz do topo (cabeça da luminária) até a elipse no chão."""
    gid = _id('lc')
    a = P(x, y, zt); c = P(x, y, 0); rx = r * U * 1.2247 * .9; ry = r * U * .7071 * .9
    hw = .16 * U
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LAMP_HI}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{LAMP}" stop-opacity="{op * .25:.2f}"/></linearGradient></defs>'
            f'<path d="M{a[0] - hw:.1f},{a[1]:.1f} L{a[0] + hw:.1f},{a[1]:.1f} L{c[0] + rx:.1f},{c[1]:.1f} '
            f'A{rx:.1f},{ry:.1f} 0 0 1 {c[0] - rx:.1f},{c[1]:.1f} Z" fill="url(#{gid})"/>')


# ---------- poste de iluminação ----------
def tube(a3, c3, b3, r, col=POLE):
    """Tubo curvo (Bézier quadrática) entre a e b com controle c."""
    a, c, b = P(*a3), P(*c3), P(*b3)
    w = 2 * r * U
    d = f'M{a[0]:.1f},{a[1]:.1f} Q{c[0]:.1f},{c[1]:.1f} {b[0]:.1f},{b[1]:.1f}'
    return (f'<path d="{d}" fill="none" stroke="{mix(col, "#0B2A30", .3)}" stroke-width="{w + 1.6:.1f}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round"/>')


def pole_shaft(x, y, H):
    s = shadow(x - .2, y - .2, .4, .4, .2)
    s += cyl(x, y, 0, .13, .24, ('#E3EBEE', '#B3C3CA', '#8DA1A9'))
    s += pipe((x, y, .22), (x, y, H), .058, POLE)
    s += cyl(x, y, H - .04, .075, .08, ('#DCE5E9', POLE, '#7F949C'), edge=False)
    return s


def lum_head(x, y, H, L, state='on', slc=True, wave=True, wave_col=None):
    """Braço + cabeça LED (alongada em -y, a partir do poste em (x,y)) + SLC azul no topo.
    Retorna (svg, ponto do centro da luz no chão)."""
    wave_col = wave_col or BLUE[1]
    ya, yb = y - L - .66, y - L + .04       # extensão da cabeça em y
    z0 = H + .1
    s = tube((x, y, H), (x, y - .15, H + .38), (x, yb - .02, z0 + .08), .045)
    lit = state in ('on', 'dim')
    if lit:
        g = P(x, (ya + yb) / 2, z0 - .02)
        s += (f'<ellipse cx="{g[0]:.1f}" cy="{g[1] + 3:.1f}" rx="13" ry="6" fill="{LAMP}" opacity="{.95 if state == "on" else .6}" '
              f'filter="url(#isoBlur)"/>')
        extend(g[0], g[1] + 3, 16)
    s += box(x - .2, ya, z0, .4, yb - ya, .1, HEAD)
    # faixa de LED (vista nas laterais inferiores)
    strip = LAMP if lit else '#7D8E95'
    s += face([(x + .201, ya + .05, z0), (x + .201, yb - .04, z0), (x + .201, yb - .04, z0 + .035), (x + .201, ya + .05, z0 + .035)], strip)
    s += face([(x - .16, yb + .001, z0), (x + .16, yb + .001, z0), (x + .16, yb + .001, z0 + .035), (x - .16, yb + .001, z0 + .035)], strip)
    # tampa superior
    s += box(x - .15, ya + .05, z0 + .1, .3, yb - ya - .14, .06, ('#FFFFFF', '#D9E3E7', '#BCCBD1'))
    zt = z0 + .16
    if slc:
        sy = yb - .26
        s += cyl(x, sy, zt, .19, .11, BLUE)
        s += dot((x + .02, sy + .02, zt + .11), 1.5, '#8CFFC4', 'led')
        if wave:
            s += waves((x + .1, sy, zt + .2), wave_col, .8)
    return s, (x, (ya + yb) / 2, z0)


def streetlight(x, y, H=3.2, L=1.0, state='on', slc=True, wave=True, wave_col=None):
    head, lc = lum_head(x, y, H, L, state, slc, wave, wave_col)
    return head + pole_shaft(x, y, H), lc


def lights_ground(lc, r=1.05, state='on'):
    """Poça de luz no chão sob a cabeça (desenhar junto do chão)."""
    if state == 'off':
        return ''
    op = .95 if state == 'on' else .55
    return light_pool(lc[0], lc[1], r, op)


def lights_cone(lc, r=1.05, state='on'):
    if state == 'off':
        return ''
    op = .5 if state == 'on' else .26
    return light_cone(lc[0], lc[1], lc[2], r, op)


# ---------- veículos e edificações ----------
def wheel_y(xc, yp, zc, r, n=18):
    p = [(xc + r * math.cos(2 * math.pi * k / n), yp, zc + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    h = [(xc + r * .45 * math.cos(2 * math.pi * k / n), yp + .001, zc + r * .45 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    return face(p, TIRE, '#1E2A2F', .6) + face(h, '#B9C7CD')


def car(x, y, L=1.5, d=.72, body=('#FFFFFF', '#E3ECEF', '#C8D6DB')):
    """Carro ao longo de x (frente para +x)."""
    s = shadow(x, y, L, d, .2)
    s += box(x, y, .12, L, d, .28, body)
    s += box(x + .32, y + .07, .4, .72, d - .14, .24, body)
    s += face([(x + .36, y + d - .069, .44), (x + 1.0, y + d - .069, .44), (x + 1.0, y + d - .069, .6), (x + .36, y + d - .069, .6)], GLASS)
    s += face([(x + 1.041, y + .12, .44), (x + 1.041, y + d - .12, .44), (x + 1.041, y + d - .12, .6), (x + 1.041, y + .12, .6)], '#BFE4F0')
    s += face([(x + L + .001, y + .08, .3), (x + L + .001, y + .2, .3), (x + L + .001, y + .2, .36), (x + L + .001, y + .08, .36)], '#FFF3C8')
    s += face([(x + L + .001, y + d - .2, .3), (x + L + .001, y + d - .08, .3), (x + L + .001, y + d - .08, .36), (x + L + .001, y + d - .2, .36)], '#FFF3C8')
    s += wheel_y(x + .3, y + d + .01, .14, .14) + wheel_y(x + L - .3, y + d + .01, .14, .14)
    return s


def house(x0, y0, w, d, h, rh=.42, roof=('#9DB6C0', '#7D9AA6', '#5F7E8A'), door_u=.62):
    """Casa com telhado de duas águas (cumeeira ao longo de x), fachada para +y."""
    ov = .1
    s = shadow(x0, y0, w, d, .2)
    s += box(x0, y0, 0, w, d, h, W)
    yf = y0 + d + .002
    # porta e janelas na fachada (+y)
    dx = x0 + w * door_u
    s += face([(dx, yf, 0), (dx + .34, yf, 0), (dx + .34, yf, .74), (dx, yf, .74)], '#4E7480')
    s += dot((dx + .27, yf, .38), 1.1, '#E9F1F3')
    for wx in (x0 + .22, x0 + .22 + .42):
        if wx + .3 < dx - .06:
            s += face([(wx, yf, .36), (wx + .3, yf, .36), (wx + .3, yf, .7), (wx, yf, .7)], GLASS, '#FFFFFF', 1.2)
    # janela lateral (+x)
    xr = x0 + w + .002
    s += face([(xr, y0 + d * .32, .36), (xr, y0 + d * .68, .36), (xr, y0 + d * .68, .7), (xr, y0 + d * .32, .7)], '#C2E6F2', '#FFFFFF', 1.2)
    # telhado
    yr = y0 + d / 2; zr = h + rh; dz = ov * rh / (d / 2)
    e = lambda c: mix(c, '#0B2A30', .22)
    s += face([(x0 - ov, y0 - ov, h - dz), (x0 + w + ov, y0 - ov, h - dz), (x0 + w + ov, yr, zr), (x0 - ov, yr, zr)], roof[2], e(roof[2]))
    s += face([(x0 + w, y0, h), (x0 + w, y0 + d, h), (x0 + w, yr, zr)], W[2], e(W[2]))
    s += face([(x0 - ov, yr, zr), (x0 + w + ov, yr, zr), (x0 + w + ov, y0 + d + ov, h - dz), (x0 - ov, y0 + d + ov, h - dz)], roof[0], e(roof[0]))
    # espessura do beiral frontal
    s += face([(x0 - ov, y0 + d + ov, h - dz), (x0 + w + ov, y0 + d + ov, h - dz), (x0 + w + ov, y0 + d + ov, h - dz - .06), (x0 - ov, y0 + d + ov, h - dz - .06)], roof[1])
    return s


# =====================================================================================
# 1) Luminária com SLC: trecho de rua com 2 postes LED, SLC azul no topo, poça de luz
# =====================================================================================
def scene_slc():
    n, m = 8.2, 3.7
    ry0, ry1 = 1.2, 2.5
    o = []
    o.append(walk(.22, .22, n - .44, ry0 - .22))
    o.append(road_x(.22, n - .22, ry0, ry1))
    o.append(walk(.22, ry1, n - .44, m - .22 - ry1))
    xs = (3.2, 6.55)
    sts = ('on', 'dim')
    heads = []
    for x, st in zip(xs, sts):
        sv, lc = streetlight(x, 3.05, 2.95, 1.0, st)
        heads.append((sv, lc, st))
    for sv, lc, st in heads:
        o.append(lights_ground(lc, 1.0, st))
    # árvores na calçada de trás
    o.append(tree(1.0, .62, .95))
    o.append(tree(2.3, .62, .85))
    o.append(tree(5.0, .62, 1.0))
    o.append(tree(7.45, .62, .85))
    o.append(car(4.1, 1.36, 1.5, .68))
    for sv, lc, st in heads:
        o.append(lights_cone(lc, 1.0, st))
    for sv, lc, st in heads:
        o.append(sv)
    return scene(o, n=n, m=m)


# =====================================================================================
# 2) Rede Vivo NB-IoT: torre Vivo ao lado de um trecho de rua com poste e casa
# =====================================================================================
def scene_net():
    n, m = 8.2, 3.9
    ry0, ry1 = 1.35, 2.5
    o = []
    o.append(walk(.22, .22, n - .44, ry0 - .22))
    o.append(road_x(.22, n - .22, ry0, ry1))
    o.append(walk(.22, ry1, n - .44, m - .22 - ry1))
    px, py, H = 4.15, 3.1, 2.9
    sv, lc = streetlight(px, py, H, 1.0, 'on', wave_col='#FFFFFF')
    o.append(lights_ground(lc, .95))
    o.append(house(.55, .3, 1.85, .92, 1.0))
    o.append(tree(2.9, .72, .9))
    o.append(tree(5.4, .72, .85))
    o.append(lights_cone(lc, .95))
    o.append(sv)
    tx, ty, TH = 6.5, 3.1, 4.0
    o.append(vivo_tower(tx, ty, TH, shelter=False))
    # abrigo de equipamentos ao lado da torre
    o.append(shadow(7.25, 2.62, .7, .86) + box(7.25, 2.62, 0, .7, .86, .8, W))
    o.append(face([(7.951, 2.8, .18), (7.951, 3.25, .18), (7.951, 3.25, .62), (7.951, 2.8, .62)], STEEL[1]))
    # enlace: antena Vivo -> SLC do poste
    a = P(tx - .2, ty, TH - .85); b = P(px, lc[1] + .3, H + .5)
    mx, my = (a[0] + b[0]) / 2, min(a[1], b[1]) - 26
    o.append(f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{mx:.1f},{my:.1f} {b[0] + 6:.1f},{b[1]:.1f}" fill="none" stroke="#E7C6FF" '
             f'stroke-width="2.2" stroke-dasharray="4 4" stroke-linecap="round"/>')
    extend(mx, my, 4)
    return scene(o, n=n, m=m)


# =====================================================================================
# 3) NLM: prédio nouMIND + tela grande com mapa de luminárias
# =====================================================================================
def scene_nlm():
    n, m = 7.6, 3.8
    o = []
    o.append(noumind_dc(4.4, .45, 2.6, 2.2, 1.35))
    # tela grande em pé, virada para +y
    x0, x1, yb, z0, z1 = .75, 3.85, 2.55, .55, 2.45
    o.append(shadow(x0 + .4, yb - .3, x1 - x0 - .8, .7, .16))
    for xl in (x0 + .7, x1 - .7):
        o.append(box(xl - .16, yb - .3, 0, .32, .6, .05, ('#E9F0F2', '#BFCDD2', '#A3B5BC')))
        o.append(box(xl - .05, yb - .02, .05, .1, .1, z0, ('#C9D5DA', '#9FB2BA', '#82979F')))
    o.append(box(x0, yb, z0, x1 - x0, .14, z1 - z0, ('#F7FAFB', '#E3EBEE', '#C3D1D7')))
    sc, f = screen_y(x0 + .1, x1 - .1, yb + .141, z0 + .1, z1 - .1, frame='#0A3A42', bg='#0B3F47')
    o.append(sc)
    # mapa simplificado: quadras e ruas
    street = '#3F7F88'
    for v in (.22, .52, .8):
        o.append(f'<polyline points="{pts(P(*f(.04, v)), P(*f(.96, v)))}" stroke="{street}" stroke-width="2.4" stroke-linecap="round"/>')
    for u in (.16, .42, .68, .9):
        o.append(f'<polyline points="{pts(P(*f(u, .08)), P(*f(u, .94)))}" stroke="{street}" stroke-width="2.4" stroke-linecap="round"/>')
    o.append(f'<polyline points="{pts(P(*f(.04, .9)), P(*f(.55, .15)))}" stroke="{street}" stroke-width="2.4" stroke-linecap="round"/>')
    ok = [(.16, .22), (.42, .22), (.68, .22), (.9, .22), (.16, .52), (.68, .52), (.9, .52), (.42, .8), (.68, .8), (.9, .8), (.16, .8), (.29, .52)]
    for u, v in ok:
        o.append(dot(f(u, v), 2.6, '#57E39A'))
    bad = f(.42, .52)
    o.append(pulse(bad, AMBER, 7))
    o.append(dot(bad, 3.0, AMBER))
    return scene(o, n=n, m=m)


# =====================================================================================
# 4) Operação da prefeitura: prefeitura com colunas + caminhão cesto indo ao poste apagado
# =====================================================================================
def city_hall(x0, y0, w, d, h):
    s = shadow(x0, y0, w, d + .6, .2)
    yf = y0 + d
    # escadaria / base do pórtico
    s += box(x0 - .05, y0, 0, w + .1, d + .62, .08, ('#F7FAFB', '#DCE6EA', '#C3D1D6'))
    s += box(x0 + .45, y0, .08, w - .9, d + .52, .08, ('#F7FAFB', '#DCE6EA', '#C3D1D6'))
    s += box(x0, y0, .08, w, d, h, W)
    s += win_right(x0, y0, .08, w, d, h, 2)
    # janelas da fachada fora do pórtico
    for wx in (x0 + .12, x0 + w - .38):
        for zz in (.38, .98):
            s += face([(wx, yf + .002, zz), (wx + .26, yf + .002, zz), (wx + .26, yf + .002, zz + .34), (wx, yf + .002, zz + .34)], GLASS)
    # porta central
    xm = x0 + w / 2
    s += face([(xm - .2, yf + .002, .16), (xm + .2, yf + .002, .16), (xm + .2, yf + .002, .86), (xm - .2, yf + .002, .86)], '#4E7480')
    # platibanda
    s += box(x0 - .04, y0 - .04, h + .08, w + .08, d + .08, .12, G)
    # colunas
    px0, px1 = x0 + .55, x0 + w - .55
    yc = yf + .34
    ncol = 5
    for i in range(ncol):
        cx = px0 + (px1 - px0) * i / (ncol - 1)
        s += cyl(cx, yc, .16, .085, h - .08 - .1, ('#FFFFFF', '#EEF3F5', '#C3D1D7'))
    # entablamento + frontão
    zt = h + .08
    s += box(px0 - .2, yf, zt - .1, px1 - px0 + .4, .52, .14, ('#FFFFFF', '#E6EEF1', '#CFDCE1'))
    zb = zt + .04; pk = .5; xa, xb = px0 - .24, px1 + .24; ym = yf + .54
    e = lambda c: mix(c, '#0B2A30', .22)
    s += face([(xa, yf, zb), (xm, yf, zb + pk), (xm, ym, zb + pk), (xa, ym, zb)], '#DCE6EA', e('#DCE6EA'))
    s += face([(xm, yf, zb + pk), (xb, yf, zb), (xb, ym, zb), (xm, ym, zb + pk)], '#C3D1D7', e('#C3D1D7'))
    s += face([(xa, ym, zb), (xb, ym, zb), (xm, ym, zb + pk)], '#F4F8F9', e('#F4F8F9'))
    s += face([(xa + .32, ym + .002, zb + .07), (xb - .32, ym + .002, zb + .07), (xm, ym + .002, zb + pk - .1)], '#E2EAED')
    return s


def flag(x, y, H=2.6, col='#7FA8B6'):
    s = cyl(x, y, 0, .09, .08, G)
    s += pipe((x, y, .05), (x, y, H), .028, '#B9C8CE')
    pts3 = []
    L = .75; hh = .44
    for k in range(9):
        t = k / 8
        pts3.append((x + t * L, y, H - .05 + .05 * math.sin(t * 5.5)))
    for k in range(8, -1, -1):
        t = k / 8
        pts3.append((x + t * L, y, H - .05 - hh + .05 * math.sin(t * 5.5)))
    s += face(pts3, col, mix(col, '#0B2A30', .25), .7)
    s += dot((x, y, H + .03), 1.6, '#DCE5E9')
    return s


def bucket_truck(tx, ty, d=.78):
    """Caminhão de manutenção (cesto aéreo). Frente (capô) em +x. Retorna (svg, ponto do giro da lança)."""
    Lb, gap, cb, hd = 1.42, .05, .52, .3
    L = Lb + gap + cb + hd
    s = shadow(tx, ty, L, d, .24)
    s += box(tx, ty, .2, L, d, .12, ('#6E7F86', '#55666D', '#45555B'))
    # baú utilitário com portas de compartimento
    s += box(tx, ty, .32, Lb, d, .42, W)
    yl = ty + d + .002
    nd = 3; dw = (Lb - .1) / nd
    for k in range(nd):
        a = tx + .05 + k * dw + .03; b = a + dw - .06
        s += face([(a, yl, .4), (b, yl, .4), (b, yl, .68), (a, yl, .68)], '#EDF3F5', '#9FB2BA', .8)
        s += line3((b - .1, yl, .52), (b - .1, yl, .58), '#7F949C', 1.6)
    s += face([(tx, yl + .001, .34), (tx + Lb, yl + .001, .34), (tx + Lb, yl + .001, .38), (tx, yl + .001, .38)], TEAL[1])
    # cabine + capô
    cx = tx + Lb + gap
    s += box(cx, ty, .32, cb, d, .72, W)
    s += box(cx + cb, ty + .04, .32, hd, d - .08, .3, W)
    s += face([(cx + .06, yl, .66), (cx + cb - .1, yl, .66), (cx + cb - .02, yl, .96), (cx + .06, yl, .96)], GLASS)
    s += face([(cx + cb + .001, ty + .08, .64), (cx + cb + .001, ty + d - .08, .64), (cx + cb + .001, ty + d - .08, .98), (cx + cb + .001, ty + .08, .98)], '#BFE4F0')
    s += face([(cx, yl + .001, .34), (cx + cb, yl + .001, .34), (cx + cb, yl + .001, .38), (cx, yl + .001, .38)], TEAL[1])
    s += face([(cx + cb, ty + d - .04 + .001, .34), (cx + cb + hd, ty + d - .04 + .001, .34), (cx + cb + hd, ty + d - .04 + .001, .38), (cx + cb, ty + d - .04 + .001, .38)], TEAL[1])
    xf = tx + L + .001
    s += face([(xf, ty + d - .22, .42), (xf, ty + d - .1, .42), (xf, ty + d - .1, .5), (xf, ty + d - .22, .5)], '#FFF3C8')
    s += face([(xf, ty + .1, .42), (xf, ty + .22, .42), (xf, ty + .22, .5), (xf, ty + .1, .5)], '#FFF3C8')
    # giroflex
    s += box(cx + .16, ty + .3, 1.04, .2, .18, .07, (AMBER, '#D98A12', '#B8740C'))
    s += dot((cx + .26, ty + .39, 1.13), 2.4, '#FFD27A', 'led')
    # rodas
    s += wheel_y(tx + .4, ty + d + .01, .2, .21) + wheel_y(tx + L - .45, ty + d + .01, .2, .21)
    return s, (tx + .32, ty + d / 2, .74)


def boom(base3, elbow3, tip3):
    s = cyl(base3[0], base3[1], base3[2], .21, .14, STEEL)
    b = (base3[0], base3[1], base3[2] + .14)
    s += pipe(b, elbow3, .075, '#E3EBEE')
    s += pipe(elbow3, tip3, .062, '#E3EBEE')
    s += dot(elbow3, 2.6, '#9FB2BA')
    return s


def basket(x, y, z, w=.42, d=.4, h=.34):
    s = ''
    # técnico: capacete e colete
    c = P(x + w / 2, y + d / 2, z + h + .1)
    s += f'<rect x="{c[0] - 3.6:.1f}" y="{c[1] + 1:.1f}" width="7.2" height="6" rx="2" fill="{AMBER}"/>'
    s += f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="2.9" fill="#E7C29E"/>'
    s += f'<path d="M{c[0] - 3.5:.1f},{c[1] - .3:.1f} a3.5,3.5 0 0 1 7,0 z" fill="#FFFFFF" stroke="#AFC0C7" stroke-width=".7"/>'
    s += box(x, y, z, w, d, h, BRASS)
    return s


def scene_ops():
    n, m = 8.6, 4.4
    ry0, ry1 = 2.05, 3.2
    o = []
    o.append(walk(.22, .22, n - .44, ry0 - .22))
    o.append(road_x(.22, n - .22, ry0, ry1))
    o.append(walk(.22, ry1, n - .44, m - .22 - ry1))
    o.append(city_hall(.5, .4, 2.75, 1.0, 1.2))
    o.append(flag(3.75, 1.45, 2.4))
    o.append(tree(5.0, .75, .95))
    o.append(tree(7.6, .75, .9))
    # poste com lâmpada apagada (falha) e caminhão cesto
    px, py, H = 5.75, 3.72, 2.9
    head, lc = lum_head(px, py, H, 1.0, 'off', True, False)
    tx, ty = 6.15, 2.15
    tr, b0 = bucket_truck(tx, ty)
    o.append(tr)
    bx, by, bz = px + .26, 2.28, H - .66
    o.append(boom(b0, (tx + 1.25, b0[1], 2.0), (bx + .21, by + .2, bz + .06)))
    o.append(head)
    o.append(basket(bx, by, bz))
    o.append(pole_shaft(px, py, H))
    o.append(pulse((px, lc[1] + .1, H + .6), AMBER, 8))
    return scene(o, n=n, m=m)


SCENES = [scene_slc(), scene_net(), scene_nlm(), scene_ops()]
CARDS = ['white', 'net', 'plat', 'white']
SIZES = [(340, 260)] * 4
