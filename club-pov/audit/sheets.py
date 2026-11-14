"""Hojas de auditoría: fotogramas cada PASO s con la zona segura de TikTok/Reels marcada."""
import sys, os
sys.path.insert(0, "/home/claude/club"); os.chdir("/home/claude/club")
import render as R
from PIL import Image, ImageDraw
PASO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
# zona segura (1080x1920): arriba 210, abajo 460 (descripción/botones), izq 60, dcha 150 (iconos)
SZ = (60, 210, 1080 - 150, 1920 - 460)
ts = [round(i * PASO, 2) for i in range(int(R.TOTAL / PASO) + 1)]
th = []
for t in ts:
    im = R.frame(t).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle(SZ, outline=(0, 255, 0), width=6)
    d.rectangle((0, 0, 200, 70), fill=(0, 0, 0)); d.text((10, 10), f"{t:.1f}s", fill=(255, 255, 0), font=R.font(R.F_UI, 48))
    th.append(im.resize((270, 480)))
for k in range(0, len(th), 12):
    sh = Image.new("RGB", (270 * 6, 480 * 2), (40, 40, 40))
    for i, im in enumerate(th[k:k + 12]): sh.paste(im, ((i % 6) * 270, (i // 6) * 480))
    sh.save(f"audit/sheet_{k // 12:02d}.jpg", quality=85)
print(len(th), "frames")
