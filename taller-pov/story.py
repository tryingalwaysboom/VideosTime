"""Story 1080x1920 con CTA: comentar A o B en la Parte 1 y seguir la página. Zona segura: 250..1580."""
import os
from PIL import Image, ImageDraw, ImageFilter
import render as r
import portada as P

def story(out):
    c = r.bg("bg_taller", 0, 0, 1.2, 1.2, 1, .5, .62); r.dark(c, 140)
    gl = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.ellipse((-100, 1000, 1180, 1400), fill=r.MAG + (90,))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))
    P._neon_titulo(c, 400)
    d = ImageDraw.Draw(c)
    r.text(d, (540, 600), "¿QUÉ HARÍAS TÚ?", 96, r.YEL, stroke=9)
    # las dos opciones de la Parte 1
    for y, L_, t1, t2, col in ((730, "A", "VENDER A NITRO", "+25.700 € · pierdes el coche", (46, 160, 90)),
                               (900, "B", "CERRARLE LA PERSIANA", "410 € · te quedas el coche", r.MAG)):
        r.panel(c, (90, y - 70, 990, y + 70), fill=(16, 14, 30), alpha=235, rad=28, outline=col, ow=6); d = ImageDraw.Draw(c)
        d.rounded_rectangle((112, y - 50, 212, y + 50), 22, fill=col)
        r.text(d, (162, y), L_, 76, r.WHITE)
        r.text(d, (240, y - 20), t1, 52, r.WHITE, "lm")
        r.text(d, (240, y + 34), t2, 30, r.YEL, "lm", r.F_UI)
    P._suelo_reflejo(c, "deportivo", 540, 1130, .78)
    d = ImageDraw.Draw(c)
    # CTA comentar
    d.rounded_rectangle((120, 1330, 960, 1440), 55, fill=r.WHITE, outline=r.OL, width=6)
    r.text(d, (540, 1385), "COMENTA A o B EN LA PARTE 1", 54, r.OL)
    # CTA seguir
    d.rounded_rectangle((150, 1475, 930, 1565), 45, fill=r.RED, outline=r.WHITE, width=6)
    r.text(d, (540, 1520), "SÍGUENOS · TÚ DECIDES CÓMO SIGUE", 46, r.WHITE)
    c.alpha_composite(r.VIG); c.convert("RGB").save(out, quality=94)

if __name__ == "__main__":
    story(os.path.join(r.HERE, "story_parte1.jpg"))
