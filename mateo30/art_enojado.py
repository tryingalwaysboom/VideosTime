"""Capas extra de Mateo: enojado (berrinche del Día 3). Uso: python3 art_enojado.py"""
import os, re
from playwright.sync_api import sync_playwright
import art30 as B
A = B.A
L = {"mateo_enojado": B.mateo("enojado", False), "mateo_enojado_hab": B.mateo("enojado", True)}
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    for name, s in L.items():
        w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
        pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2); hp = os.path.join(B.OUT, "_tmp.html")
        open(hp, "w").write(f"<html><head><style>{A.FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
        pg.goto("file://" + hp); pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(B.OUT, name + ".png"), omit_background=True); pg.close()
    br.close(); os.remove(os.path.join(B.OUT, "_tmp.html"))
