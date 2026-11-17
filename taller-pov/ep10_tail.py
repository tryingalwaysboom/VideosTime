# ======================================================================= ESCENAS NUEVAS (Ep.10 "Cara a cara")
def silf(c, name, cx, base, h, flip=False, col=(4, 4, 8)):
    im = R.layer(name); im = im.crop(im.getbbox()); w = int(im.width * h / im.height); sp = im.resize((w, h), Image.LANCZOS)
    if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    blk = Image.new("RGBA", sp.size, col + (255,)); blk.putalpha(sp.getchannel("A")); c.alpha_composite(blk, (cx - w // 2, base - h))

def fachada(T, t0, dur, ab=0.0, z0=1.1, z1=1.3):
    c = bg("bg_fachada", T, t0, z0, z1, dur, .5, .6); dark(c, 90); tinte(c, (10, 20, 70), 55)
    glow(c, (300, 960, 760, 1240), (255, 215, 140), int(90 + 70 * ab), 50)
    ov = blank(); ImageDraw.Draw(ov).rectangle((540 - 20 - int(110 * ab), 1000, 540 + 20 + int(110 * ab), 1260), fill=(255, 235, 180, 210)); c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(4)))
    return c

def sombrero(c, cx, cy, w, ang=0):
    lay = Image.new("RGBA", (int(w * 2.4), int(w * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); m, n = lay.width // 2, lay.height // 2
    d.ellipse((m - w, n - w * .13, m + w, n + w * .13), fill=(24, 22, 28, 255), outline=(8, 8, 12, 255), width=3)
    d.rounded_rectangle((m - w * .62, n - w * .6, m + w * .62, n), int(w * .2), fill=(34, 32, 40, 255), outline=(8, 8, 12, 255), width=3)
    d.rectangle((m - w * .61, n - w * .18, m + w * .61, n - w * .02), fill=(120, 38, 38, 255))
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC); c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def padre(c, pr, T, x, z, alto, lid=None, hat=True, flip=False):
    return pj(c, pr, "padre_full" if hat else "padre_sin_sombrero", x, z, alto, T, lid, flip)

def mensaje(c, T, t0, t1, user, txt):
    if not (t0 <= T < t1): return
    k = popscale(T, t0, .35)
    if T > t1 - .3: k *= clamp((t1 - T) / .3)
    if k <= 0: return
    lay = blank(); d = ImageDraw.Draw(lay); x0, y0, x1, y1 = 90, 690, 990, 930
    d.rounded_rectangle((x0, y0, x1, y1), 38, fill=(255, 255, 255, 245), outline=OL, width=6)
    d.ellipse((x0 + 28, y0 + 30, x0 + 108, y0 + 110), fill=(60, 120, 230), outline=OL, width=4)
    d.text((x0 + 68, y0 + 70), user[0].upper(), font=R.font(F_ANTON, 44), fill=WHITE, anchor="mm")
    d.text((x0 + 130, y0 + 48), "@" + user, font=R.font(F_ANTON, 38), fill=OL, anchor="lm")
    d.text((x0 + 130, y0 + 90), "MENSAJE NUEVO", font=R.font(F_UI, 24), fill=(200, 50, 50), anchor="lm")
    f = R.font(F_UI, 36); words = txt.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > x1 - x0 - 70: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    for i, l in enumerate(lines): d.text((x0 + 35, y0 + 140 + i * 44), l, font=f, fill=OL, anchor="lm")
    if abs(k - 1) > .01:
        cx, cy = 540, (y0 + y1) // 2
        big = lay.resize((max(1, int(W * k)), max(1, int(H * k))), Image.BILINEAR); ox, oy = int(cx - cx * k), int(cy - cy * k)
        lay = blank(); lay.alpha_composite(big, (max(0, ox), max(0, oy)), (max(0, -ox), max(0, -oy)))
    c.alpha_composite(lay)

# ---- 1. la patada (frame 0 ya es acción)
def s_patada(T, t0, dur):
    tp = WT("G01", "patada.")
    ab = ease(clamp((T - t0 + .4) / .5)) if T < tp else 1.0
    c = fachada(T, t0, dur, max(.55, ab), 1.15, 1.7)
    k = zoom(T, t0, dur, .95, 1.1)
    silf(c, "nitro_full", int(300), 1650, int(900 * k)); silf(c, "lucia_full", 800, 1650, int(840 * k), flip=True)
    if T >= tp:
        u = clamp((T - tp) / .35); fl = Image.new("RGBA", (W, H), (255, 240, 200, int(170 * (1 - u)))); c.alpha_composite(fl)
    lluvia(c, T, 110, 120, 1400); vineta(c, 220); c = shake(c, T, 3 + 6 * (T >= tp and T < tp + .4), 44)
    if T < tp + .8: et(c, T, .12, "ELEGISTEIS LA A", 440, YEL, 46)
    mensaje(c, T, .5, tp - .35, "danineos100", "Toca plantarle cara y enterarse de toda la historia")
    tx(c, T, tp, "¡A PATADA!", 600, RED, -5, 128)
    return c

# ---- 2. grito
def s_grito(T, t0, dur):
    c, pr = nave_c(830, 6); dark(c, 120); tinte(c, (60, 20, 10), 45)
    glow(c, (60, 700, 1020, 1700), (255, 190, 90), 70 + 20 * math.sin(T * 9), 90)
    ix, iy, w, h = sil(c, pr, "padre_sin_sombrero", .45, 6.6, 2.0, (4, 4, 8)); hat(c, ix, iy + int(h * .02), int(w * .42))
    pj(c, pr, "nitro_full", -.5, 3.0, 2.1, T, "G02")
    c = shake(c, T, 3, 44); c = cam(c, T, t0, dur, 1.0, 1.18, .45, .4); vineta(c, 210)
    tx(c, T, S("G02") + .12, "¡SUELTE ESE CAJÓN!", 400, RED, -4, 84)
    return c

def hat(c, cx, cy, w):
    d = ImageDraw.Draw(c); d.ellipse((cx - w, cy - 14, cx + w, cy + 14), fill=(4, 4, 8)); d.rounded_rectangle((cx - w * .55, cy - 70, cx + w * .55, cy), 14, fill=(4, 4, 8))

# ---- 3. se quita el sombrero
def s_sombrero(T, t0, dur):
    ts = WT("G03", "sombrero")
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (70, 10, 10), 45)
    glow(c, (120, 500, 960, 1800), (255, 200, 120), 110, 110)
    k = ease(clamp((T - t0) / dur))
    info = padre(c, pr, T, .15, 4.9 - .9 * k, 2.1, None, hat=T < ts + .05)
    f = info["f"]
    if T >= ts + .05:
        u = ease(clamp((T - ts - .05) / .5)); hx = info["x0"] + (799 - info["ox"]) * f; hy = info["y0"] + (700 - info["oy"]) * f
        sombrero(c, hx - 430 * u * f, hy + 1330 * u * f, 330 * f, -20 * u)
    c = cam(c, T, t0, dur, 1.0, 1.22, .5, .35); c = shake(c, T, 2, 40); vineta(c, 215)
    tx(c, T, WT("G03", "inmuta."), "NI SE INMUTA", 400, YEL, -5, 100)
    return c

def s_sonrie(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (70, 0, 10), 55)
    glow(c, (120, 500, 960, 1800), (255, 200, 120), 130, 110)
    info = padre(c, pr, T, .1, 4.0, 2.2, None, hat=False)
    f = info["f"]; mx = info["x0"] + (799 - info["ox"]) * f; my = info["y0"] + (1128 - info["oy"]) * f
    d = ImageDraw.Draw(c); u = ease(clamp((T - t0) / .35))
    d.arc((mx - 60 * f * 1.4, my - 40 * f, mx + 60 * f * 1.4, my + 30 * f * (1 + u)), 20, 160, fill=(40, 14, 14), width=max(3, int(10 * f)))
    c = cam(c, T, t0, dur, 1.35, 1.75, .5, .17); vineta(c, 235)
    tx(c, T, t0 + .1, "SONRÍE…", 1420, RED, -4, 110)
    return c

# ---- 4. "Llegáis tarde"
def s_tarde(T, t0, dur):
    c, pr = nave_c(830, -6); dark(c, 110); tinte(c, (20, 30, 90), 30)
    glow(c, (60, 600, 1020, 1700), (255, 200, 120), 80, 90)
    sil(c, pr, "nitro_full", -.9, 2.8, 2.0, (4, 4, 8)); sil(c, pr, "lucia_full", -.2, 3.2, 1.9, (4, 4, 8), True)
    padre(c, pr, T, .7, 4.6 - .5 * ease(clamp((T - t0) / dur)), 2.1, "G04", hat=False, flip=True)
    c = cam(c, T, t0, dur, 1.0, 1.2, .6, .4); vineta(c, 215)
    tx(c, T, S("G04") + .15, "LLEGÁIS TARDE", 400, YEL, -4, 98)
    return c

# ---- 5. Lucía
def s_lucia10(T, t0, dur):
    c, pr = nave_c(830, 12); dark(c, 100); tinte(c, (60, 0, 20), 50)
    silf(c, "padre_sin_sombrero", 800, 1500, 1500, True, (10, 8, 14))
    pj(c, pr, "lucia_full", -.2, 2.5, 2.2, T, "G05")
    c = cam(c, T, t0, dur, 1.1, 1.4, .45, .3); c = shake(c, T, 2, 40); vineta(c, 230)
    tx(c, T, S("G05") + .1, "¡PAPÁ!", 380, RED, -4, 140)
    return c

# ---- 6. el pacto
def s_pacto(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (70, 10, 10), 40)
    glow(c, (120, 500, 960, 1800), (255, 200, 120), 110, 110)
    padre(c, pr, T, .1, 4.3 - .6 * ease(clamp((T - t0) / dur)), 2.1, "G06", hat=False)
    tp = WT("G06", "pacto")
    if T >= tp - .1:
        k = popscale(T, tp - .1, .35)
        if k > 0: papel(c, 800, 1350, .62 * k, rot=8, firmas=3, resalta=True, T=T)
    c = cam(c, T, t0, dur, 1.0, 1.15, .5, .4); vineta(c, 215)
    tx(c, T, tp, "FIRMÓ EL PACTO", 400, YEL, -4, 92)
    return c

# ---- 7. la deuda
def s_deuda(T, t0, dur):
    c, pr = nave_c(830, 8); dark(c, 110); tinte(c, (60, 0, 20), 50)
    glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
    sil(c, pr, "padre_sin_sombrero", 1.0, 6.0, 2.0, (4, 4, 8), True)
    pj(c, pr, "nitro_full", -.3, 3.1, 2.1, T, "G07")
    c = cam(c, T, t0, dur, 1.0, 1.18, .45, .4); vineta(c, 215)
    tx(c, T, WT("G07", "deuda"), "-64.300 €", 400, RED, -5, 140)
    return c

# ---- 8. la llave
def llave(c, x, y, s, ang):
    lay = Image.new("RGBA", (520, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); o = (60, 30, 10, 255); m = (176, 120, 60, 255)
    d.ellipse((10, 50, 130, 170), fill=m, outline=o, width=8); d.ellipse((46, 86, 94, 134), fill=(0, 0, 0, 0), outline=o, width=8)
    d.rectangle((126, 96, 430, 124), fill=m, outline=o, width=8)
    for xx in (360, 400): d.rectangle((xx, 120, xx + 24, 170), fill=m, outline=o, width=6)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def s_llave(T, t0, dur):
    tl = WT("G08", "llave")
    c = bg("bg_mesa", T, t0, 1.3, 1.6, dur, .5, .5); dark(c, 100); tinte(c, (60, 20, 10), 35)
    glow(c, (60, 500, 1020, 1500), (255, 200, 130), 110, 90)
    u = ease(clamp((T - tl + .25) / .3)); y = -200 + 1480 * u
    if T > tl + .05: y = 1480 - 22 * abs(math.sin((T - tl - .05) * 18)) * math.exp(-(T - tl) * 4)
    llave(c, 540, y, 1.5 + .2 * math.sin(T * 3) * (T > tl + .2), -22)
    if T >= tl + .05:
        k = clamp((T - tl - .05) / .5); d = ImageDraw.Draw(c)
        for i in range(8): d.ellipse((540 + (i - 4) * 70 * k - 8, 1520 - 40 * k * ((i * 7) % 5) / 4 - 8, 540 + (i - 4) * 70 * k + 8, 1520 - 40 * k * ((i * 7) % 5) / 4 + 8), fill=(255, 220, 160, 200))
    c = shake(c, T, 6 * (tl <= T < tl + .25), 40); vineta(c, 200)
    tx(c, T, WT("G08", "oxidada"), "UNA LLAVE VIEJA", 520, YEL, -4, 96)
    return c

# ---- 9. la deuda del 96
def s_del96(T, t0, dur):
    c, pr = nave_c(830, -4); dark(c, 130); tinte(c, (80, 0, 10), 70)
    glow(c, (120, 500, 960, 1800), (255, 120, 80), 110, 110)
    sil(c, pr, "nitro_full", -.9, 2.7, 2.0, (4, 4, 8)); sil(c, pr, "lucia_full", -.25, 3.2, 1.9, (4, 4, 8), True)
    padre(c, pr, T, .5, 4.4 - .5 * ease(clamp((T - t0) / dur)), 2.1, "G09", hat=False, flip=True)
    c = cam(c, T, t0, dur, 1.0, 1.2, .6, .4); vineta(c, 225)
    tx(c, T, WT("G09", "noventa"), "DESDE EL 96", 400, RED, -4, 110)
    return c

# ---- 10. faros fuera
def s_faros(T, t0, dur):
    c = fachada(T, t0, dur, 1.0, 1.1, 1.25); dark(c, 40); tn = WT("G10", "coches")
    for i, (cx, d0) in enumerate(((220, 0), (540, .35), (860, .7))):
        k = ease(clamp((T - t0 - d0) / 1.6)); r = 18 + 90 * k; yy = 1330 - 30 * k
        for dx in (-1, 1):
            xx = cx + dx * (60 + 120 * k)
            glow(c, (xx - r * 3, yy - r * 2, xx + r * 3, yy + r * 2), (255, 240, 200), int(110 + 90 * k), 40)
            ImageDraw.Draw(c).ellipse((xx - r * .5, yy - r * .35, xx + r * .5, yy + r * .35), fill=(255, 252, 235))
    silf(c, "nitro_full", 250, 1900, 820); silf(c, "lucia_full", 840, 1900, 770, flip=True)
    lluvia(c, T, 120, 130, 1400); vineta(c, 215); c = shake(c, T, 2 + 3 * (T > tn), 44)
    tx(c, T, tn, "TRES COCHES", 560, RED, -5, 110)
    return c

# ---- 11. vienen por el contrato
def s_vienen(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (90, 0, 10), 70)
    glow(c, (120, 500, 960, 1800), (255, 90, 70), 100 + 40 * math.sin(T * 12), 110)
    padre(c, pr, T, .1, 4.3 - .7 * ease(clamp((T - t0) / dur)), 2.1, "G11", hat=False)
    c = shake(c, T, 5, 46); c = cam(c, T, t0, dur, 1.0, 1.22, .5, .35); vineta(c, 225)
    tx(c, T, WT("G11", "contrato."), "¡VIENEN POR EL CONTRATO!", 400, YEL, -4, 74)
    return c

# ---- 12. lo tengo yo
def s_loteng(T, t0, dur):
    c, pr = nave_c(830, 8); dark(c, 110); tinte(c, (20, 30, 90), 35); glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
    pj(c, pr, "nitro_full", -.2, 2.8, 2.2, T, "G12")
    k = popscale(T, S("G12") + .3, .3)
    if k > 0: papel(c, 760, 1380, .5 * k, rot=-10, firmas=3, T=T)
    c = cam(c, T, t0, dur, 1.0, 1.18, .45, .4); vineta(c, 215)
    tx(c, T, WT("G12", "tengo"), "LO TENGO YO", 400, YEL, -5, 108)
    return c

# ---- 13. la mano
def s_mano(T, t0, dur):
    k = ease(clamp((T - t0) / dur)); te = WT("G13", "extiende")
    c, pr = nave_c(830, 0); dark(c, 110); tinte(c, (60, 10, 30), 45); glow(c, (60, 700, 1020, 1600), (255, 200, 120), 80, 90)
    pj(c, pr, "nitro_full", -.7, 3.4, 2.1, T, None)
    padre(c, pr, T, .7, 3.6, 2.1, None, hat=False, flip=True)
    pp = popscale(T, S("G13") + .2, .3)
    if pp > 0:
        glow(c, (380, 1000, 700, 1300), (255, 235, 170), 140, 60); papel(c, 540, 1160, .42 * pp, rot=-6, firmas=3, T=T)
    c = cam(c, T, t0, dur, 1.0, 1.15, .5, .5); vineta(c, 215)
    tx(c, T, te, "¿SE LO DAS?", 400, YEL, -4, 108)
    return c

# ---- final partido
T_SPLIT = WT("G15", "Confiar.") - .1
def lado10(name):
    key = "L10" + name
    if key in _LC: return _LC[key]
    if name == "A":
        A, pr = nave_c(830, 0); A = A.convert("RGBA"); dark(A, 110); A.alpha_composite(Image.new("RGBA", (W, H), (60, 20, 40, 50)))
        glow(A, (120, 500, 960, 1800), (255, 200, 120), 90, 110)
        pj(A, pr, "nitro_full", -.8, 3.4, 2.1, 0, None); padre(A, pr, 0, .9, 3.6, 2.1, None, hat=False, flip=True)
    else:
        A = fachada(0, 0, 1, 1.0, 1.15, 1.15).convert("RGBA"); dark(A, 40)
        for cx in (200, 540, 880):
            for dx in (-1, 1):
                xx = cx + dx * 140; glow(A, (xx - 150, 1180, xx + 150, 1420), (255, 240, 200), 150, 40); ImageDraw.Draw(A).ellipse((xx - 40, 1270, xx + 40, 1330), fill=(255, 252, 235))
        silf(A, "nitro_full", 300, 1900, 840); silf(A, "lucia_full", 760, 1900, 790, flip=True)
    _LC[key] = A; return A

def s_split10(T, t0, dur):
    s0 = T_SPLIT
    A, B = lado10("A"), lado10("B")
    u = ease((T - s0 + .25) / .45); tb = WT("G15", "huir.") - .05; tn = S("G16") - .05
    hiA = T < tb; neutro = T >= tn
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if (neutro or not hiA) else Image.blend(B, blk, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if (neutro or hiA) else Image.blend(A, blk, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (int(255 * v),), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    for cx, t1, t2, t3, col in ((270, "CONFIAR", "+ Sabrás la verdad", "- Puede mentir", AZ), (790, "HUIR", "+ Te lo quedas", "- Os perseguirán", MAG)):
        k = popscale(T, s0 + .2, .35)
        if k > 0: opcion8(d, cx, 420, t1, t2, t3, col, k)
    tc = WT("G16", "Comenta") - .05
    if T >= tc:
        k = popscale(T, tc, .3)
        if k > 0:
            lay = blank(); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle((120, 1100, 960, 1210), 55, fill=(255, 255, 255, 245), outline=OL, width=6)
            text(ld, (540, 1155), "COMENTA CONFIAR O HUIR", 50, OL, stroke=0)
            if abs(k - 1) > .01:
                big = lay.resize((int(W * k), int(H * k)), Image.BILINEAR); ox, oy = int(540 - 540 * k), int(1155 - 1155 * k)
                lay = blank(); lay.alpha_composite(big, (max(0, ox), max(0, oy)), (max(0, -ox), max(0, -oy)))
            c.alpha_composite(lay)
    return c

AV6[:] = [S("G09") + .2]
def aviso6(c, T):
    for t0 in AV6:
        if not (t0 <= T < t0 + 5.0): continue
        u = ease((T - t0) / .35) if T < t0 + 4.6 else 1 - ease((T - t0 - 4.6) / .35)
        y = 300 + 20 * (1 - u); a = int(255 * u)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        w2 = 330 * (1 + .03 * math.sin((T - t0) * 8))
        d.rounded_rectangle((540 - w2, y, 540 + w2, y + 74), 37, fill=(255, 255, 255, a), outline=OL + (a,), width=5)
        d.text((540, y + 24), "¿TÚ QUÉ HARÍAS? CUÉNTALO", font=R.font(F_ANTON, 29), fill=OL + (a,), anchor="mm")
        d.text((540, y + 54), "tu comentario decide la parte 11", font=R.font(F_UI, 23), fill=(200, 50, 50, a), anchor="mm")
        c.alpha_composite(lay)

FASES = [(0, "Entrar al taller"), (S("G03"), "Plantar cara al intruso"), (S("G09"), "Proteger el contrato"), (S("G13"), "Tú eliges")]
def draw_hud10(canvas, T):
    if T >= T_SPLIT: return
    canvas.alpha_composite(R.barra_base())
    d = ImageDraw.Draw(canvas); x0, y0, x1 = 36, 168, 1044
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    for k, v, x in (("coch", "1", x0 + 300), ("caja", euros(1010), x0 + 420), ("deuda", "-" + euros(64300), x0 + 600), ("rep", "2", x0 + 880)):
        cy = y0 + 34
        if k == "coch": R.carito(d, x, cy, CYAN)
        if k == "caja": R.coin(d, x, cy, 15)
        if k == "deuda": R.flecha(d, x, cy, 1.0)
        if k == "rep": R.estrella(d, x, cy, 17, (242, 190, 60))
        d.text((x + 24, y0 + 35), v, font=R.font(F_ANTON, 34), fill=(255, 120, 110) if k == "deuda" else WHITE, anchor="lm")
    idx = max(i for i, (t, _) in enumerate(FASES) if T >= t); t_fase, obj = FASES[idx]
    d.text((x0 + 132, y0 + 87), obj, font=R.font(F_UI, 24 * pop(t_fase)), fill=(255, 140, 120) if idx else WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "REPUTACIÓN", font=R.font(F_UI, 18), fill=GRIS, anchor="rm")
    p = clamp(T / (T_SPLIT - .1)); xb0, xb1 = x0 + 24, x1 - 24
    d.rounded_rectangle((xb0, y0 + 102, xb1, y0 + 107), 3, fill=(255, 255, 255, 40))
    d.rounded_rectangle((xb0, y0 + 102, xb0 + (xb1 - xb0) * p, y0 + 107), 3, fill=CYAN)
    d.ellipse((xb0 + (xb1 - xb0) * p - 7, y0 + 99, xb0 + (xb1 - xb0) * p + 7, y0 + 110), fill=WHITE)
    aviso6(canvas, T)

# ======================================================================= guion de planos
PLANOS = []
def add(t0, fn): PLANOS.append((t0, fn))
def A_(lid, fn, off=-.12): add(S(lid) + off, fn)
def W_(lid, w, fn, off=-.1): add(WT(lid, w) + off, fn)
add(0, s_patada)
A_("G02", s_grito)
A_("G03", s_sombrero); W_("G03", "sonríe", s_sonrie, -.05)
A_("G04", s_tarde); A_("G05", s_lucia10); A_("G06", s_pacto); A_("G07", s_deuda); A_("G08", s_llave)
A_("G09", s_del96); A_("G10", s_faros); A_("G11", s_vienen); A_("G12", s_loteng); A_("G13", s_mano)
add(T_SPLIT, s_split10)
PLANOS.sort(key=lambda p: p[0])
R.SCENES = []
for i, (t, f) in enumerate(PLANOS):
    dur = ((PLANOS[i + 1][0] if i + 1 < len(PLANOS) else R.TOTAL) - t)
    R.SCENES.append((t, (lambda f, t, dur: (lambda T: (bruma_luz(f(T, t, dur), T) if f is not s_split10 else f(T, t, dur))))(f, t, dur)))

R.IMPACTS = [WT("G01", "patada.") - .05, S("G02"), WT("G03", "sombrero"), S("G05"), WT("G08", "llave"), WT("G10", "coches"), S("G11"), T_SPLIT]
R.draw_hud = draw_hud10
R.HIDE_LAST_CAPTION = False

def lecho(nombre, src, dur, fade=.4, loop=False):
    import numpy as np, wave
    out = os.path.join(R.HERE, "sfx", nombre + ".wav"); sr = 44100
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(R.HERE, "sfx", src + ".wav"), "-ac", "2", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, 2) / 32768
    n = int(dur * sr)
    if loop: y = np.tile(x, (n // len(x) + 1, 1))[:n]
    else:
        y = np.zeros((n, 2), np.float32); m = min(n, len(x)); y[:m] = x[:m]
    f = int(fade * sr); y[-f:] *= np.linspace(1, 0, f)[:, None]
    w = wave.open(out, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: R.frame(float(t)).save(os.path.join(R.TMP, f"e10_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "info":
        print({k: [round(a, 2), round(b, 2)] for k, (a, b) in R.TL.items()}, round(R.TOTAL, 2))
        print(len(R.SCENES), [round(t, 1) for t, f in R.SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(R.SCENES)))
        with Pool(2) as pool:
            pool.starmap(R.render_scene, [(i, os.path.join(R.TMP, f"e10s{i:02d}.mp4")) for i in ids])
    elif cmd == "mix":
        import mix
        F = lambda n: os.path.join(R.HERE, "sfx", n + ".wav")
        tf = S("G10"); tfr = WT("G10", "frenan")
        idle0 = lecho("e10_idle_nitro", "nitro_ralenti", 4.6, .6, True)
        llega = lecho("e10_llegan", "nitro_motor", tfr - tf + .4, .15)
        idle1 = lecho("e10_idle_coches", "v8_ralenti", WT("G13", "extiende") - tfr + 2.5, 1.0, True)
        huye = lecho("e10_huye", "seat_acelera", 3.0, .5)
        efectos = [
            (F("impacto"), WT("G01", "patada.") - .08, -3), (F("puerta_nave"), WT("G01", "patada.") - .45, -5), (F("movil"), .5, -2), (F("brillo"), .3, -8),
            (F("seat_derrape"), .05, 1), (idle0, .3, -1), (F("petardeo"), 2.4, 0),
            (F("tension"), S("G03") - .1, -9), (F("impacto"), S("G02") + .05, -9),
            (F("brillo"), WT("G03", "sombrero") - .05, -8), (F("impacto"), S("G05") - .05, -8),
            (F("tension"), S("G06") - .1, -10), (F("impacto"), WT("G07", "deuda") - .05, -8),
            (F("caja"), WT("G08", "llave") - .05, -7), (F("tension"), S("G09") - .1, -10),
            (llega, tf - .1, 3), (F("nitro_ruge"), tf + .5, 1), (F("petardeo"), tf + 1.3, 0),
            (F("seat_derrape"), tfr - .15, 4), (F("seat_derrape"), tfr + .25, 3), (idle1, tfr + .1, -2),
            (F("petardeo"), S("G11") + 1.0, 0), (F("tension"), S("G12") - .1, -10),
            (F("impacto"), S("G11") - .05, -6),
            (F("brillo"), WT("G13", "extiende") - .05, -7), (F("impacto"), T_SPLIT, -6),
            (huye, WT("G15", "huir.") - .15, 3), (F("petardeo"), WT("G15", "huir.") + .9, 0),
            (F("brillo"), WT("G16", "Comenta") - .05, -4),
        ]
        mix.main(os.path.join(R.HERE, "el_taller_de_ruben_ep10_corto.mp4"), "e10s", efectos)
