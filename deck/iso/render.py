"""Renderiza as cenas de um módulo de serviço sobre mock-ups dos cards reais do deck.

Uso: python3 render.py svc_util            -> gera svc_util.png (e svc_util.json com as cenas)
O módulo precisa definir SCENES (lista de SVGs) e CARDS (lista com 'white' | 'net' | 'plat' por cena, mesma ordem).
Opcional: SIZES (lista de (largura_px, altura_px) da área de ilustração de cada card; padrão (300, 230)).
"""
import importlib, json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_lib

name = sys.argv[1]
mod = importlib.import_module(name)
scenes, cards = mod.SCENES, mod.CARDS
sizes = getattr(mod, 'SIZES', [(300, 230)] * len(scenes))
assert len(scenes) == len(cards) == len(sizes)
BG = {'white': 'background:rgba(255,255,255,.88);border:1px solid #fff',
      'net': 'background:linear-gradient(160deg,#0098CC,#00A9A0)',
      'plat': 'background:#0A5F6B'}
cells = ''.join(
    f'<div class="card" style="{BG[c]};width:{w + 40}px"><div class="ill" style="height:{h}px">{s}</div>'
    f'<div class="txt {c}"><span>RÓTULO</span><b>Título do card</b><i>• item de texto do card</i></div></div>'
    for s, c, (w, h) in zip(scenes, cards, sizes))
html = f'''<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Lato:wght@400;700&display=swap" rel="stylesheet">
<style>body{{margin:0;padding:28px;background:linear-gradient(160deg,#F2FAFD,#D3EEED);display:flex;gap:22px;align-items:flex-start;font-family:Lato,sans-serif}}
.card{{border-radius:14px;padding:16px 20px;box-shadow:0 18px 36px -26px rgba(6,54,61,.55)}}
.ill{{display:flex;justify-content:center;align-items:flex-end}}.ill .isoS{{height:100%;width:auto;max-width:100%;overflow:visible}}
.txt{{display:flex;flex-direction:column;gap:6px;margin-top:10px}}.txt span{{font-size:14px;font-weight:700;letter-spacing:.08em;color:#00756D}}
.txt b{{font-family:Poppins;font-size:22px;color:#0E2F38}}.txt i{{font-style:normal;font-size:17px;color:#2B4750}}
.txt.net span,.txt.net b,.txt.net i,.txt.plat span,.txt.plat b,.txt.plat i{{color:#fff}}
.isoS .pulse circle{{transform-box:fill-box;transform-origin:center;animation:ipulse 1.8s ease-out infinite}}
@keyframes ipulse{{from{{transform:scale(.4);opacity:.9}}to{{transform:scale(1.8);opacity:0}}}}
</style><body>{iso_lib.DEFS}{cells}</body>'''
out_html = os.path.join(HERE, f'_{name}.html')
open(out_html, 'w').write(html)
json.dump({'scenes': scenes, 'cards': cards}, open(os.path.join(HERE, f'{name}.json'), 'w'))
total_w = sum(w + 40 + 22 for w, _ in sizes) + 56
shot = os.path.join(HERE, 'shot.js')
subprocess.run(['node', shot, out_html, os.path.join(HERE, f'{name}.png'), str(total_w), '420'], check=True)
print('ok', os.path.join(HERE, f'{name}.png'))
