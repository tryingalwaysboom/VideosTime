"""3 stories de engagement (sentimiento del público). Genera versión limpia (para poner el sticker en la app) y vista previa."""
import os, ep3
import portada as P
from luces import coche_faros
R = ep3.R
from render import Image, ImageDraw, ImageFilter, W, H, bg, put, text, dark, YEL, RED, WHITE, OL, CYAN, F_UI, F_ANTON

OUT = os.path.join(R.HERE, "stories_eng"); os.makedirs(OUT, exist_ok=True)

def base(name, fx=.5, fy=.55, z=1.15, d=120):
    c = bg(name, 0, 0, z, z, 1, fx, fy); dark(c, d); return c

def titulo(c, y=330):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); P._neon_titulo(lay, 400)
    lay = lay.resize((int(W * .62), int(H * .62)), Image.BILINEAR)
    c.alpha_composite(lay, (int(540 - 540 * .62), int(y - 400 * .62)))

def pregunta(c, s1, s2, y=540, col=YEL):
    d = ImageDraw.Draw(c); text(d, (540, y), s1, 92, col, stroke=9)
    if s2: text(d, (540, y + 105), s2, 92, col, stroke=9)

def mock_poll(c, y, a, b):
    d = ImageDraw.Draw(c); d.rounded_rectangle((190, y, 890, y + 250), 30, fill=(255, 255, 255))
    for i, s in enumerate((a, b)):
        yy = y + 30 + i * 110; d.rounded_rectangle((220, yy, 860, yy + 90), 45, fill=(240, 240, 245))
        d.text((540, yy + 45), s, font=R.font(F_ANTON, 44), fill=(40, 40, 50), anchor="mm")

def mock_slider(c, y):
    d = ImageDraw.Draw(c); d.rounded_rectangle((190, y, 890, y + 200), 30, fill=(255, 255, 255))
    d.text((540, y + 55), "¿Cuánto te fías?", font=R.font(F_ANTON, 42), fill=(40, 40, 50), anchor="mm")
    d.rounded_rectangle((250, y + 125, 830, y + 145), 10, fill=(225, 225, 232)); d.rounded_rectangle((250, y + 125, 560, y + 145), 10, fill=(250, 180, 60))
    d.ellipse((520, y + 95, 600, y + 175), fill=(255, 205, 80), outline=(40, 40, 50), width=4)

def mock_question(c, y):
    d = ImageDraw.Draw(c); d.rounded_rectangle((190, y, 890, y + 260), 30, fill=(255, 255, 255))
    d.rounded_rectangle((190, y, 890, y + 110), 30, fill=(150, 70, 220)); d.rectangle((190, y + 80, 890, y + 110), fill=(150, 70, 220))
    d.text((540, y + 55), "Tu teoría...", font=R.font(F_ANTON, 44), fill=WHITE, anchor="mm")
    d.rounded_rectangle((230, y + 140, 850, y + 225), 20, fill=(240, 240, 245))
    d.text((540, y + 182), "Escribe algo...", font=R.font(F_UI, 34), fill=(150, 150, 160), anchor="mm")

def story1():   # encuesta: Nitro villano o víctima
    c = base("bg_poligono", .5, .95, 1.35, 90)
    put(c, "nitro", 830, 1230, .6)
    coche_faros(c, 680, 1530, .8, 1.0)
    titulo(c); pregunta(c, "NITRO:", "¿VILLANO O VÍCTIMA?")
    return c, lambda c: mock_poll(c, 800, "VILLANO", "VÍCTIMA")

def story2():   # deslizador: confianza en Lucía
    c = base("bg_fachada", .5, .72, 1.15, 90)
    put(c, "seat_rally", 470, 1470, .85); put(c, "lucia", 840, 1330, .64)
    titulo(c); pregunta(c, "¿TE FÍAS", "DE LUCÍA?", col=CYAN)
    return c, lambda c: mock_slider(c, 800)

def story3():   # caja de preguntas: qué esconde el depósito
    c = base("bg_noche", .5, .55, 1.0, 40)
    put(c, "deportivo", 540, 1380, 1.05)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((640, 1360, 900, 1540), outline=RED + (255,), width=10); od.ellipse((620, 1340, 920, 1560), outline=RED + (120,), width=6)
    c.alpha_composite(ov); text(ImageDraw.Draw(c), (780, 1640), "DEPÓSITO", 44, RED, stroke=5)
    titulo(c); pregunta(c, "¿QUÉ ESCONDE", "EL COCHE DEL TÍO?")
    return c, lambda c: mock_question(c, 795)

if __name__ == "__main__":
    for i, f in enumerate((story1, story2, story3), 1):
        c, mock = f()
        clean = c.copy(); clean.alpha_composite(R.VIG); clean.convert("RGB").save(os.path.join(OUT, f"story_eng_{i}.jpg"), quality=93)
        pv = c.copy(); mock(pv); pv.alpha_composite(R.VIG); pv.convert("RGB").save(os.path.join(OUT, f"story_eng_{i}_vista_previa.jpg"), quality=90)
    print("ok")
