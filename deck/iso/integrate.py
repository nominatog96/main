"""Encaixa as cenas isométricas (svc_*.json) nos cards dos 5 slides de serviço do deck."""
import json, re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_lib
P = '/home/user/main/deck/index.html'
s = open(P).read()

# slide -> (módulo, índices dos cards .sg que recebem cena, na ordem do HTML)
MAP = {
    'svc-util': ('svc_util', [0, 1, 2, 3, 4]),
    'svc-ilum': ('svc_ilum', [0, 1, 2, 3]),
    'ativos-arq': ('svc_ativos', [0, 1, 2, 3]),
    'svc-agro': ('svc_agro', [0, 1, 2, 3]),
    'svc-esp': ('svc_esp', [2, 3, 4, 5]),
}


def div_end(t, i):
    """índice logo após o </div> que fecha o <div ...> que começa em t[i]."""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', t[i:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return i + m.end()
    raise ValueError('div sem fechamento')


def strip_old(sec):
    # remove cenas anteriores (protótipo)
    while '<div class="isoin">' in sec:
        i = sec.index('<div class="isoin">')
        sec = sec[:i] + sec[div_end(sec, i):]
    return sec


for sid, (mod, idxs) in MAP.items():
    data = json.load(open(os.path.join(HERE, f'{mod}.json')))
    scenes = data['scenes']
    assert len(scenes) == len(idxs), (sid, len(scenes), len(idxs))
    a = s.index(f'id="{sid}"'); a = s.rindex('<section', 0, a); b = s.index('</section>', a)
    sec = strip_old(s[a:b])
    starts = [m.start() for m in re.finditer(r'<div class="sg[ "]', sec)]
    # processa de trás para frente para não invalidar índices
    for k in sorted(range(len(idxs)), key=lambda k: -idxs[k]):
        st = starts[idxs[k]]
        en = div_end(sec, st)
        card = sec[st:en]
        card = re.sub(r'<svg class="ai".*?</svg>', '', card, count=1, flags=re.S)
        svg = scenes[k].replace('<svg class="isoS"', '<svg class="isoS" preserveAspectRatio="xMidYMax meet"', 1)
        card = card[:-len('</div>')] + f'<div class="isoin">{svg}</div></div>'
        sec = sec[:st] + card + sec[en:]
    s = s[:a] + sec + s[b:]

# defs: troca o filtro do protótipo pelo da biblioteca
s = re.sub(r'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><filter id="blur".*?</svg>\n?', '', s, flags=re.S)
if 'id="isoBlur"' not in s:
    s = s.replace('<div id="stage">', '<div id="stage">\n' + iso_lib.DEFS, 1)

# CSS: substitui o bloco do protótipo
i = s.index('/* cenas isométricas dentro dos cards */')
j = s.index('.svaf .af:has(.isoin) .cn{align-self:start;margin-top:110px}') + len('.svaf .af:has(.isoin) .cn{align-self:start;margin-top:110px}')
s = s[:i] + '''/* cenas isométricas no pé dos cards: ocupam só o espaço que sobra abaixo do texto */
.af .sg:has(>.isoin){min-height:0}
.isoin{flex:1 1 0;min-height:0;max-height:270px;margin:auto -10px -6px;container-type:size;display:flex;align-items:flex-end;justify-content:center}
.isoin .isoS{width:100%;height:100%;overflow:visible;display:block}
@container (max-height:70px){.isoin .isoS{display:none}}
.sg.net .isoin .isoS,.sg.plat .isoin .isoS{filter:drop-shadow(0 12px 14px rgba(0,0,0,.16))}
.isoS .pulse circle{transform-box:fill-box;transform-origin:center;animation:ipulse 1.8s ease-out infinite}
@keyframes ipulse{from{transform:scale(.4);opacity:.9}to{transform:scale(1.8);opacity:0}}
.isoS .led{animation:iled 1.4s ease-in-out infinite}
@keyframes iled{50%{opacity:.25}}
.isoS .wv,.isoS .glow{animation:iled 1.6s ease-in-out infinite}''' + s[j:]
s = s.replace('.svaf .af .sg:has(.isoin){padding-top:14px}\n', '')
s = s.replace('.svaf .af .sg:has(.isoin){padding-top:14px}', '')
open(P, 'w').write(s)
print('ok', s.count('class="isoin"'), 'cenas')
