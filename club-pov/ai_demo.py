"""Prueba: plano de Paco con imagen IA (estilo Pixar) animada por código — parallax, luz, polvo, subtítulos y barra de la serie."""
import os, sys, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageEnhance
import render as R, look

W, H, FPS = 1080, 1920, 30
AI = os.path.join(R.HERE, "ai")

# ---------------------------------------------------------------- capas
src = Image.open(os.path.join(AI, "paco_vestuario.png")).convert("RGB")
cut = Image.open(os.path.join(AI, "paco_cut.png")).convert("RGBA")
a = np.asarray(cut.getchannel("A")).copy()
n, lab, st, _ = cv2.connectedComponentsWithStats((a > 128).astype(np.uint8))
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
a[lab != big] = 0                                  # quita restos sueltos
a = cv2.GaussianBlur(a, (3, 3), 0)
cut.putalpha(Image.fromarray(a))

plate_p = os.path.join(AI, "vestuario_sin_paco.png")
if not os.path.exists(plate_p):                    # fondo sin Paco (relleno)
    img = np.asarray(src)[..., ::-1]
    m = cv2.dilate((a > 20).astype(np.uint8) * 255, np.ones((25, 25), np.uint8))
    sm = cv2.resize(img, None, fx=.5, fy=.5); mm = cv2.resize(m, None, fx=.5, fy=.5)
    fill = cv2.inpaint(sm, mm, 9, cv2.INPAINT_TELEA)
    fill = cv2.resize(fill, (img.shape[1], img.shape[0]))
    out = np.where(m[..., None] > 0, fill, img)
    cv2.imwrite(plate_p, out)
plate = Image.open(plate_p).convert("RGB")

# fondo: escalado a 1.12 x alto del vídeo, desenfocado (profundidad de campo)
BS = H * 1.12 / plate.height
BG = plate.resize((int(plate.width * BS), int(plate.height * BS)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(7))
BG = ImageEnhance.Brightness(BG).enhance(.92)
# Paco: recorte nítido y escalado
bx = cut.getbbox()
P = cut.crop(bx)
PS = 1.72
P = P.resize((int(P.width * PS), int(P.height * PS)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))

# fotogramas con labios sincronizados (SadTalker, generado en GitHub Actions)
def _frames(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, src.height, src.width, 3)
LIPS = {"N09": _frames(os.path.join(AI, "paco_N09.mp4"))}
ALPHA = cut.getchannel("A")
_pc = {}
def paco_layer(T):
    """Paco recortado; si está hablando, con la boca del vídeo de lipsync."""
    for lid, fr in LIPS.items():
        i = int((T - R.S(lid)) * 25)
        if 0 <= i < len(fr):
            if ("L", lid, i) not in _pc:
                im = Image.fromarray(fr[i]).convert("RGBA"); im.putalpha(ALPHA)
                im = im.crop(bx); im = im.resize((int(im.width * PS), int(im.height * PS)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
                _pc.clear(); _pc[("L", lid, i)] = im
            return _pc[("L", lid, i)]
    return P

# ---------------------------------------------------------------- tiempo
T0 = R.S("N08") - .4
T1 = R.E("N09") + .9
D = T1 - T0
t_paco = R.WT("N08", "Paco.")

def frame(t):
    T = T0 + t
    u = t / D
    # cámara: avance lento + paneo; el fondo se mueve menos que Paco (parallax)
    z = 1.0 + .06 * u + .05 * R.ease((T - t_paco) / .5) * (T >= t_paco)
    bg = BG.resize((int(BG.width * z), int(BG.height * z)), Image.BILINEAR)
    cx = bg.width * .62 - 140 * u * z
    cy = bg.height * .5
    c = bg.crop((int(cx - W / 2), int(cy - H / 2), int(cx + W / 2), int(cy + H / 2))).convert("RGBA")
    R.rays(c, T, -60, 330, 28, 34, 1900, (255, 222, 170), 62)       # luz de la ventana
    # Paco: respira y, cuando habla, se mueve un poco
    habla = R.S("N09") <= T < R.E("N09")
    br = 1 + .006 * math.sin(t * 2.4)
    sz = z * (1 + .02 * u)
    P_ = paco_layer(T)
    p = P_.resize((int(P_.width * sz), int(P_.height * sz * br)), Image.BILINEAR)
    px = W / 2 + 40 * u - p.width / 2 + 30
    py = H - p.height + 40
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))                       # sombra de contacto
    c.alpha_composite(p, (int(px), int(py)))
    R.dust(c, T, 60)
    R.ficha(c, T, t_paco + .1, 50, 310, "PACO", "UTILLERO DESDE 1985", "9 MESES SIN COBRAR")
    c = look.cine(c, T, 0)
    if int(T * 30) % 97 in (0, 1):                                    # parpadeo del fluorescente
        c = ImageEnhance.Brightness(c.convert("RGB")).enhance(.86).convert("RGBA")
    c.alpha_composite(R.VIG)
    c.alpha_composite(R.grains()[int(T * 24) % 4])
    R.draw_hud(c, T)
    R.draw_caption(c, T)
    return c.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(R.TMP, f"ai_{t}.jpg"), quality=90)
        sys.exit()
    vid = os.path.join(R.TMP, "ai_v.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for f in range(int(D * FPS)): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-ss", str(T0), "-t", str(D), "-i", os.path.join(R.TMP, "voz_prev.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", os.path.join(R.HERE, "prueba_paco_pixar_animado.mp4")])
    print("ok", D)
