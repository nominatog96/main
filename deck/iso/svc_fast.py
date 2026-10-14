from iso_lib import *
HW = BLUE

def hwbox(x, y, z, w, d, h, wave=True, ant=True):
    s = box(x, y, z, w, d, h, HW)
    s += dot((x + w + .001, y + d * .3, z + h * .7), 1.8, '#8CFFC4', 'led')
    if ant:
        s += line3((x + w * .8, y + d * .3, z + h), (x + w * .8, y + d * .3, z + h + .55), HW[2], 2)
        s += dot((x + w * .8, y + d * .3, z + h + .58), 2.2, HW[2])
    if wave:
        s += waves((x + w * .8, y + d * .3, z + h + .45), HW[1], .85)
    return s

def cabinet(x, y, w=1.2, d=.55, h=1.7, modules=True):
    s = shadow(x, y, w, d) + box(x, y, 0, w, d, h, G)
    # porta aberta mostrando interior na face esquerda (plano y+d)
    s += face([(x + .08, y + d + .001, .1), (x + w - .08, y + d + .001, .1), (x + w - .08, y + d + .001, h - .1), (x + .08, y + d + .001, h - .1)], '#E9EEF0', '#9FB2BA', 1)
    if modules:
        for r, z in enumerate((.35, .85, 1.3)):
            s += face([(x + .15, y + d + .002, z), (x + w - .15, y + d + .002, z), (x + w - .15, y + d + .002, z + .06), (x + .15, y + d + .002, z + .06)], '#B9C6CC')
            for k in range(4):
                c = '#9B5CF6' if (r == 1 and k == 1) else ('#C9D5DA' if k % 2 else '#DCE5E8')
                xx = x + .18 + k * (w - .36) / 4
                s += face([(xx, y + d + .003, z + .06), (xx + (w - .36) / 4 - .04, y + d + .003, z + .06), (xx + (w - .36) / 4 - .04, y + d + .003, z + .34), (xx, y + d + .003, z + .34)], c, '#8EA1A9', .6)
    return s

def pump(x, y):
    s = shadow(x, y, 1.6, .8) + box(x, y, 0, 1.6, .8, .18, STEEL)
    s += cyl(x + .45, y + .4, .18, .32, .55, STEEL)          # corpo bomba
    s += box(x + .8, y + .15, .18, .7, .5, .5, ('#7FB6C9', '#4F8FA6', '#3C7489'))  # motor
    s += pipe((x + .45, y + .4, .55), (x + .45, y - 1.0, .55), .12, '#7FA9B8')
    s += pipe((x + .1, y + .4, .4), (x - .9, y + .4, .4), .12, '#7FA9B8')
    return s

def tank(x, y, r=.55, h=1.0):
    return shadow(x - r, y - r, 2 * r, 2 * r) + cyl(x, y, 0, r, h, ('#EEF4F6', '#C9D6DB', '#A9BAC1'))

def vpn_lock(p3):
    c = P(*p3); extend(c[0], c[1], 22)
    return (f'<g transform="translate({c[0]:.1f},{c[1]:.1f})"><path d="M-9,-4 v-6 a9,9 0 0 1 18,0 v6" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
            f'<rect x="-13" y="-5" width="26" height="20" rx="4" fill="#FFFFFF"/><circle cx="0" cy="4" r="3" fill="{TEAL[2]}"/></g>')

def dish(p3, s=1.0):
    c = P(*p3); extend(c[0], c[1], 16)
    return (f'<g transform="translate({c[0]:.1f},{c[1]:.1f})"><line x1="0" y1="0" x2="0" y2="{-10*s:.1f}" stroke="#7A8992" stroke-width="2"/>'
            f'<ellipse cx="{-2*s:.1f}" cy="{-16*s:.1f}" rx="{10*s:.1f}" ry="{7*s:.1f}" transform="rotate(-25 {-2*s:.1f} {-16*s:.1f})" fill="#F4F7F8" stroke="#8796A0" stroke-width="1.2"/></g>')

def gear(p3, col=TEAL[0], r=13):
    c = P(*p3); extend(c[0], c[1], r + 6)
    teeth = ''.join(f'<rect x="-3" y="{-r-4}" width="6" height="8" rx="1.5" transform="rotate({a})" fill="{col}"/>' for a in range(0, 360, 45))
    return f'<g transform="translate({c[0]:.1f},{c[1]:.1f})">{teeth}<circle r="{r}" fill="{col}"/><circle r="{r*.42:.1f}" fill="#0A5F6B"/></g>'

def alarm_screen(x, y, z):
    s, f = screen_x(y, y + 1.1, x, z, z + .8)
    s += line_on(f, [.3, .45, .35, .6, .5, .8], '#5EF2E2')
    s += dot(f(.82, .75), 4, '#F2A93B', 'led')
    return box(x - .1, y + .45, 0, .1, .2, z, G) + s

def weather_station(x, y):
    s = shadow(x - .3, y - .3, .6, .6)
    s += line3((x, y, 0), (x, y, 3.0), '#8796A0', 3)
    s += line3((x, y, 2.9), (x - .6, y, 2.9), '#8796A0', 2)
    c = P(x - .6, y, 3.05)
    for dx in (-6, 0, 6):
        s += f'<circle cx="{c[0]+dx:.1f}" cy="{c[1] - (2 if dx == 0 else 0):.1f}" r="3.2" fill="#FFFFFF" stroke="#8796A0" stroke-width="1"/>'
    s += line3((x, y, 2.9), (x + .55, y + .1, 2.9), '#8796A0', 2) + face([(x + .55, y + .1, 2.75), (x + .85, y + .1, 2.9), (x + .55, y + .1, 3.05)], '#F2A93B')
    # painel solar
    s += face([(x - .1, y + .2, 1.6), (x + .7, y + .2, 1.6), (x + .7, y + .9, 2.1), (x - .1, y + .9, 2.1)], '#2C4A7A', '#9FB2BA', 1)
    for k in (1, 2, 3):
        s += line3((x - .1 + k * .2, y + .2, 1.6), (x - .1 + k * .2, y + .9, 2.1), '#5E7FB0', .8)
    s += hwbox(x - .32, y - .05, 1.0, .42, .3, .5, wave=True, ant=False)
    s += cyl(x + .9, y + .9, 0, .15, .7, STEEL)  # pluviômetro
    return s

def crops(x0, y0, rows=4, L=2.6):
    s = ''
    for i in range(rows):
        y = y0 + i * .45
        s += face([(x0, y, .01), (x0 + L, y, .01), (x0 + L, y + .28, .01), (x0, y + .28, .01)], '#C8E6B3')
        for k in range(6):
            s += dot((x0 + .2 + k * L / 6, y + .14, .12), 3, GREEN[1])
    return s

def weather_screen(x, y):
    s, f = screen_y(x, x + 1.8, y, 1.0, 2.3)
    s = box(x + .8, y - .2, 0, .2, .2, 1.0, G) + s
    sun = P(*f(.2, .72)); s += f'<circle cx="{sun[0]:.1f}" cy="{sun[1]:.1f}" r="7" fill="#F2C27A"/>'
    s += bars_on(f, [.25, .45, .3, .55], '#5EF2E2', hi=3)
    return s

def barn(x, y):
    s = shadow(x, y, 1.4, 1.0) + box(x, y, 0, 1.4, 1.0, .8, ('#F4E0D6', '#D9725F', '#B85C4A'))
    s += face([(x, y, .8), (x + 1.4, y, .8), (x + 1.4, y + .5, 1.3), (x, y + .5, 1.3)], '#E9EEF0', '#9FB2BA', .8)
    s += face([(x, y + .5, 1.3), (x + 1.4, y + .5, 1.3), (x + 1.4, y + 1.0, .8), (x, y + 1.0, .8)], '#CFDCE1', '#9FB2BA', .8)
    return s

def siren_building(x, y):
    s = shadow(x, y, 1.2, 1.0) + building(x, y, 1.2, 1.0, 1.4, 2)
    s += cyl(x + .6, y + .5, 1.48, .16, .22, ('#FFB0A0', '#E25B45', '#B8432F')) + dot((x + .6, y + .5, 1.8), 3, '#E25B45', 'led')
    return s

def road_seg(x, y, L=2.4):
    s = face([(x, y, .01), (x + L, y, .01), (x + L, y + .8, .01), (x, y + .8, .01)], ASPH[1])
    for k in range(4):
        s += face([(x + .2 + k * .6, y + .38, .02), (x + .5 + k * .6, y + .38, .02), (x + .5 + k * .6, y + .44, .02), (x + .2 + k * .6, y + .44, .02)], '#FFFFFF')
    return s

def car(x, y, col):
    return shadow(x, y, .9, .5) + box(x, y, .08, .9, .5, .3, col) + box(x + .2, y + .05, .38, .5, .4, .22, ('#E8F4FA', '#A8DAEB', '#8CC4D8'))

def videowall(x, y):
    s = box(x, y, 0, 2.6, .25, .4, G)
    for r in range(2):
        for c in range(3):
            x0 = x + .1 + c * .82; z0 = .55 + r * .72
            sc, f = screen_y(x0, x0 + .76, y + .26, z0, z0 + .66)
            s += sc
            if (r, c) == (0, 0): s += bars_on(f, [.4, .7, .5, .9], '#5EF2E2')
            elif (r, c) == (0, 1): s += line_on(f, [.2, .5, .4, .7, .6], '#5EF2E2')
            elif (r, c) == (0, 2): s += ''.join(dot(f(.2 + i * .2, .5), 2.4, '#8CFFC4' if i != 2 else '#E25B45') for i in range(4))
            elif (r, c) == (1, 0): s += dot(f(.5, .5), 6, '#F2A93B', 'led')
            elif (r, c) == (1, 1): s += bars_on(f, [.6, .3, .8], '#F2C27A')
            else: s += line_on(f, [.6, .4, .5, .3, .45], '#B98CF5')
    s += box(x + .6, y + 1.0, 0, 1.4, .6, .45, W)  # mesa
    return s

def rooftop_tower(bx=.8, by=.8, bh=2.2):
    s = shadow(bx, by, 2.4, 2.0) + building(bx, by, 2.4, 2.0, bh, 3)
    cx, cy = bx + 1.2, by + 1.0; b = .3; H = 2.0
    for dx, dy in ((-b, -b), (b, -b), (b, b), (-b, b)):
        s += line3((cx + dx, cy + dy, bh), (cx, cy, bh + H), '#7A8992', 2)
    for ox, oy in ((-.2, .02), (.04, -.22)):
        s += box(cx + ox, cy + oy, bh + H - .9, .14, .18, .6, VIVO)
    s += pulse((cx, cy, bh + H + .25), VIVO[1], 13)
    s += vpn_lock((bx + 2.2, by + .2, bh + 1.4))
    return s

# ---- ATIVOS: [fldc white 305x130, quadro white 245x115, net 200x240, plat 260x240]
ATIVOS = [
    scene([tank(1.0, .9, .5, .9), pump(2.0, 1.4), dot((2.0, 1.0, .9), 3, '#F2A93B'), hwbox(4.0, .5, 0, .35, .3, .55, wave=True, ant=False)], n=5.4, m=2.4),
    scene([cabinet(.6, .5, 1.4, .5, 1.5), hwbox(2.4, .6, 0, .7, .5, .55), box(3.4, .6, 0, .6, .5, .4, ('#9DB4BD', '#6F8790', '#5A7079'))], n=4.6, m=1.8),
    scene([vivo_tower(1.4, 1.6, 4.2, shelter=False), dish((2.6, 2.6, .3)), vpn_lock((2.9, .9, 2.6))], n=3.4, m=3.4),
    scene([noumind_dc(.5, .7, 2.6, 2.2, 1.4), gear((3.2, .4, 2.2)), alarm_screen(3.6, 2.0, .9)], n=4.0, m=3.6),
]
AGRO = [
    scene([crops(.4, 2.2, 3, 3.6), weather_station(1.3, 1.0), tree(3.9, .6, .9)], n=4.4, m=3.8),
    scene([crops(.3, 2.6, 3, 3.6), vivo_tower(1.6, 1.4, 4.4)], n=4.2, m=4.0),
    scene([noumind_dc(.4, .4, 2.4, 2.0, 1.3), weather_screen(1.0, 3.2)], n=4.0, m=3.6),
    scene([road_seg(.3, 3.0, 4.2), siren_building(.5, .5), barn(2.6, .4), cyl(2.1, 2.2, 0, .45, .8, TEAL)], n=4.8, m=4.0),
]
ESP = [
    scene([box(.4, .4, 0, 3.4, .3, 2.2, G), hwbox(.9, .75, .9, .7, .45, .6), cabinet(2.0, .75, 1.1, .45, 1.6, False),
           pipe((1.6, .95, 1.2), (3.6, 2.6, .2), .04, '#9B5CF6'), dot((3.6, 2.6, .3), 4, '#8CFFC4', 'led')], n=4.2, m=3.2),
    scene([rooftop_tower()], n=4.0, m=3.6),
    scene([videowall(.5, .6)], n=3.6, m=2.4),
    scene([box(.6, .5, 0, .8, .7, .9, W), box(1.5, .75, .5, 1.6, .08, .08, ('#F2A93B', '#E08A1E', '#C0761A')),
           car(.6, 2.2, ('#F6F7F8', '#C9D5DA', '#A9BAC1')), car(1.8, 2.2, ('#E7B7A8', '#D9725F', '#B85C4A')), car(3.0, 2.2, ('#C7D9F2', '#7FA6D9', '#5F86BA')),
           dot((1.5, 3.3, .02), 4, '#8CFFC4', 'led'), dot((2.7, 3.3, .02), 4, '#E25B45'), dot((3.9, 3.3, .02), 4, '#8CFFC4', 'led'), hwbox(.75, .2, .9, .4, .3, .35, wave=True, ant=False)], n=4.6, m=3.8),
]
