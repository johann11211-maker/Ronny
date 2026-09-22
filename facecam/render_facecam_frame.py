#!/usr/bin/env python3
"""Erzeugt einen 16:9-Facecam-Rahmen mit schwarz-grauem Rand, eingraviertem
Schriftzug in der unteren Leiste und einem Glueh-Zyklus, der sich nahtlos
wiederholen laesst.

Der Rahmen ist statisch, animiert wird nur der Schriftzug: er wird langsam
hell-orange eingeblendet und wieder ausgeblendet. Die Gravur selbst bleibt
immer sichtbar, auch wenn das Leuchten ganz aus ist.

Der Zyklus beginnt und endet in der dunklen Phase, deshalb ist der letzte
Frame pixelgleich mit dem ersten -- das Video laeuft als Schleife ohne Sprung.
"""

import argparse
import hashlib
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SS = 2  # Supersampling-Faktor fuer Kanten und Schrift

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------

def smootherstep(x):
    """Weiche 0->1-Blende, an beiden Enden mit Steigung und Kruemmung null."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0)


def sd_round_rect(px, py, cx, cy, hw, hh, r):
    """Vorzeichenbehaftete Distanz zu einem abgerundeten Rechteck.

    Negativ innerhalb, positiv ausserhalb, in Ausgabe-Pixeln gemessen.
    """
    r = min(r, hw, hh)
    qx = np.abs(px - cx) - (hw - r)
    qy = np.abs(py - cy) - (hh - r)
    outside = np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0))
    inside = np.minimum(np.maximum(qx, qy), 0.0)
    return outside + inside - r


def downsample(a):
    """Supersampling-Raster auf Ausgabeaufloesung mitteln."""
    h, w = a.shape[:2]
    if a.ndim == 2:
        return a.reshape(h // SS, SS, w // SS, SS).mean(axis=(1, 3))
    c = a.shape[2]
    return a.reshape(h // SS, SS, w // SS, SS, c).mean(axis=(1, 3))


def value_noise(h, w, cell, rng):
    """Weiches Rauschen: grobes Zufallsgitter, bikubisch hochskaliert."""
    gh = int(np.ceil(h / cell)) + 2
    gw = int(np.ceil(w / cell)) + 2
    grid = (rng.random((gh, gw)) * 255).astype(np.uint8)
    img = Image.fromarray(grid, "L").resize((gw * cell, gh * cell), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32)[:h, :w] / 255.0


def fbm(h, w, rng, cells=(38, 19, 10, 5, 3), weights=(0.36, 0.26, 0.19, 0.12, 0.07)):
    """Mehrere Rausch-Oktaven uebereinander -- ergibt die Materialstruktur."""
    out = np.zeros((h, w), dtype=np.float32)
    for cell, weight in zip(cells, weights):
        out += weight * value_noise(h, w, cell, rng)
    out -= out.min()
    if out.max() > 0:
        out /= out.max()
    return out


def _gauss_exact(a, sigma, axis):
    """Separable Gauss-Faltung -- genau, aber nur fuer kleine Radien sinnvoll."""
    r = int(np.ceil(3.0 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1, dtype=np.float32) / sigma) ** 2)
    k /= k.sum()
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r, r)
    p = np.pad(a, pad, mode="edge")
    n = a.shape[axis]
    out = np.zeros_like(a)
    for j, w in enumerate(k):
        out += w * np.take(p, np.arange(j, j + n), axis=axis)
    return out


def _box(a, r, axis):
    """Kastenfilter ueber 2r+1 Pixel, per Praefixsumme in linearer Zeit."""
    if r < 1:
        return a
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r, r)
    p = np.pad(a, pad, mode="edge")
    cs = np.cumsum(p, axis=axis, dtype=np.float64)
    zeros = np.zeros_like(np.take(cs, [0], axis=axis))
    cs = np.concatenate([zeros, cs], axis=axis)
    hi = np.take(cs, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(cs, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a, sigma):
    """Weichzeichner auf einem float-Array.

    Kleine Radien werden exakt gefaltet, damit die Gravurkanten sauber
    bleiben. Groessere Radien nutzen drei Kastenfilter -- vom Gauss optisch
    nicht zu unterscheiden und deutlich schneller.
    """
    a = np.ascontiguousarray(a, dtype=np.float32)
    if sigma <= 0:
        return a
    if sigma <= 3.0:
        return _gauss_exact(_gauss_exact(a, sigma, 0), sigma, 1)
    # Boxbreite, die drei Durchgaenge auf das gewuenschte Sigma bringt.
    w = np.sqrt(12.0 * sigma * sigma / 3.0 + 1.0)
    r = max(1, int(round((w - 1.0) / 2.0)))
    for axis in (0, 1):
        for _ in range(3):
            a = _box(a, r, axis)
    return a


def shift(a, dx, dy):
    """Array um ganze Pixel verschieben, Rand mit Null aufgefuellt."""
    out = np.zeros_like(a)
    h, w = a.shape
    xs_src = slice(max(0, -dx), w - max(0, dx))
    xs_dst = slice(max(0, dx), w - max(0, -dx))
    ys_src = slice(max(0, -dy), h - max(0, dy))
    ys_dst = slice(max(0, dy), h - max(0, -dy))
    out[ys_dst, xs_dst] = a[ys_src, xs_src]
    return out


def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise SystemExit("Keine passende Schriftart gefunden: " + ", ".join(FONT_CANDIDATES))


def fit_font(text, target_cap_height):
    """Schriftgroesse suchen, bei der die Versalhoehe des Texts passt."""
    lo, hi = 8, 600
    while lo < hi:
        mid = (lo + hi + 1) // 2
        font = load_font(mid)
        bbox = font.getbbox(text)
        if (bbox[3] - bbox[1]) <= target_cap_height:
            lo = mid
        else:
            hi = mid - 1
    return load_font(lo)


def draw_tracked_text(size, text, font, tracking, center_x, baseline_mid_y):
    """Text zeichenweise mit Sperrung zeichnen, zentriert um einen Punkt."""
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    img = Image.new("L", size, 0)
    drw = ImageDraw.Draw(img)
    bbox = font.getbbox(text)
    x = center_x - total / 2.0
    y = baseline_mid_y - (bbox[1] + bbox[3]) / 2.0
    for ch, adv in zip(text, widths):
        drw.text((x, y), ch, font=font, fill=255)
        x += adv + tracking
    return np.asarray(img, dtype=np.float32) / 255.0


# --------------------------------------------------------------------------
# Rahmen aufbauen
# --------------------------------------------------------------------------

def build_frame(cfg):
    """Baut den statischen Rahmen und alle Glueh-Ebenen des Schriftzugs."""
    W, H = cfg.width, cfg.height
    sw, sh = W * SS, H * SS

    # --- Geometrie -------------------------------------------------------
    # Aussenkontur und Kamerafenster als abgerundete Rechtecke.
    inner_left = cfg.side
    inner_right = W - cfg.side
    inner_top = cfg.top
    inner_bottom = H - cfg.bar
    bar_top = H - cfg.bar

    x = (np.arange(sw, dtype=np.float32) + 0.5) / SS
    y = (np.arange(sh, dtype=np.float32) + 0.5) / SS
    px = x[None, :]
    py = y[:, None]

    d_out = sd_round_rect(px, py, W / 2.0, H / 2.0,
                          W / 2.0, H / 2.0, cfg.radius_outer)
    d_in = sd_round_rect(px, py,
                         (inner_left + inner_right) / 2.0,
                         (inner_top + inner_bottom) / 2.0,
                         (inner_right - inner_left) / 2.0,
                         (inner_bottom - inner_top) / 2.0,
                         cfg.radius_inner)

    # Deckkraft: innerhalb der Aussenkontur, ausserhalb des Kamerafensters.
    a_out = np.clip(0.5 - d_out * SS, 0.0, 1.0)
    a_in = np.clip(0.5 + d_in * SS, 0.0, 1.0)
    alpha_ss = a_out * a_in

    # --- Abschraegung ----------------------------------------------------
    # Hoehenprofil: an beiden Kanten null, in der Mitte der Randflaeche eins.
    edge_dist = np.minimum(-d_out, d_in)
    height = smootherstep(edge_dist / cfg.bevel)
    zx = np.gradient(height * cfg.bevel_depth, axis=1) * SS
    zy = np.gradient(height * cfg.bevel_depth, axis=0) * SS
    norm = np.sqrt(zx * zx + zy * zy + 1.0)
    # Licht von oben links.
    lx, ly, lz = -0.48, -0.62, 0.62
    llen = np.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / llen, ly / llen, lz / llen
    lambert = (-zx * lx - zy * ly + lz) / norm
    light_ss = 1.0 + cfg.bevel_gain * (lambert - lz)
    del d_out, d_in, a_out, a_in, edge_dist, zx, zy, norm, lambert

    alpha = downsample(alpha_ss).astype(np.float32)
    light = downsample(light_ss).astype(np.float32)
    height_ds = downsample(height).astype(np.float32)
    del alpha_ss, light_ss, height

    # --- Material: schwarz-graue Mischung --------------------------------
    rng = np.random.default_rng(cfg.seed)
    tex = fbm(H, W, rng)
    grain = value_noise(H, W, 2, rng)  # feines Korn gegen Banding

    yy = (np.arange(H, dtype=np.float32) / (H - 1))[:, None]
    xx = (np.arange(W, dtype=np.float32) / (W - 1))[None, :]
    # Diagonaler Verlauf, damit der Rand nicht flach wirkt.
    sweep = 0.62 * (1.0 - yy) + 0.38 * (1.0 - xx)

    # Schwarz und Grau sollen sich deutlich mischen: die Flecken werden im
    # Kontrast angehoben und ueber den ruhigen Verlauf gelegt.
    mottle = smootherstep((tex - 0.40) / 0.55)
    mix = np.clip(0.40 * mottle + 0.32 * tex + 0.28 * sweep, 0.0, 1.0)
    mix = np.clip(mix + 0.040 * (grain - 0.5), 0.0, 1.0)

    # Randflaeche oben/seitlich: schwarz bis mittelgrau.
    lum_frame = cfg.frame_dark + (cfg.frame_light - cfg.frame_dark) * mix
    # Untere Leiste: deutlich schwaerzer, nur leicht graue Sprengsel.
    lum_bar = cfg.bar_dark + (cfg.bar_light - cfg.bar_dark) * mix

    bar_w = np.clip((np.arange(H, dtype=np.float32)[:, None] - bar_top) + 0.5, 0.0, 1.0)
    bar_w = np.repeat(bar_w, W, axis=1)
    lum = lum_frame * (1.0 - bar_w) + lum_bar * bar_w

    # Feine Fuge zwischen Randflaeche und Leiste.
    seam = np.exp(-0.5 * ((np.arange(H, dtype=np.float32) - bar_top) / 1.1) ** 2)
    lum += (0.055 * seam)[:, None]

    lum *= light
    # Aussen- und Innenkante leicht abdunkeln, damit der Rahmen fasst.
    lum *= 0.70 + 0.30 * smootherstep(height_ds * 1.30)
    lum = np.clip(lum, 0.0, 1.0)

    base_rgb = np.repeat(lum[:, :, None], 3, axis=2)
    # Der Rand bleibt neutral, bekommt aber eine Spur kuehle Tiefe.
    base_rgb[:, :, 2] *= 1.035
    base_rgb[:, :, 0] *= 0.99
    base_rgb = np.clip(base_rgb, 0.0, 1.0)

    # --- Schriftzug gravieren --------------------------------------------
    cap = cfg.bar * cfg.text_height
    font = fit_font(cfg.text, cap * SS)
    text_mask = downsample(draw_tracked_text(
        (sw, sh), cfg.text, font,
        cfg.tracking * cap * SS,
        (W / 2.0) * SS,
        (bar_top + cfg.bar / 2.0) * SS,
    )).astype(np.float32)

    # Gravur: obere Kante im Schatten, untere Kante im Licht -- der Abdruck
    # bleibt dauerhaft sichtbar, auch wenn das Leuchten ganz aus ist.
    step = max(1, int(round(cap / 26.0)))
    soft = blur(text_mask, 0.6 * step)
    relief = (blur(shift(soft, -step, -step), 1.0 * step)
              - blur(shift(soft, step, step), 1.0 * step))
    engrave = np.clip(relief, 0.0, None)   # oben links: Schatten
    catch = np.clip(-relief, 0.0, None)    # unten rechts: Lichtkante

    base_rgb -= (cfg.engrave_depth * engrave + 0.030 * text_mask)[:, :, None]
    base_rgb += (cfg.engrave_catch * catch)[:, :, None]
    base_rgb = np.clip(base_rgb, 0.0, 1.0)

    # --- Glueh-Ebenen -----------------------------------------------------
    # Zwei Ebenen: warmes Orange (linear) und heller Kern (quadratisch).
    # Beide werden auf die Rahmenflaeche maskiert, damit nichts ins
    # Kamerafenster blutet.
    bloom = (0.78 * blur(text_mask, 4.0)
             + 0.58 * blur(text_mask, 12.0)
             + 0.42 * blur(text_mask, 30.0)
             + 0.30 * blur(text_mask, 70.0))
    warm = np.clip(1.00 * text_mask + 1.35 * bloom, 0.0, 1.8) * alpha
    hot = np.clip(0.62 * text_mask + 0.28 * blur(text_mask, 3.0), 0.0, 1.5) * alpha

    warm_rgb = warm[:, :, None] * np.asarray(cfg.glow_rgb, dtype=np.float32)
    hot_rgb = hot[:, :, None] * np.asarray(cfg.core_rgb, dtype=np.float32)

    return {
        "base_rgb": base_rgb.astype(np.float32),
        "alpha": alpha,
        "warm_rgb": warm_rgb.astype(np.float32),
        "hot_rgb": hot_rgb.astype(np.float32),
        "bar_top": bar_top,
        "font_size": font.size,
    }


def glow_level(t, cfg):
    """Intensitaet des Schriftzugs zum Zeitpunkt t innerhalb eines Zyklus.

    Der Zyklus startet und endet dunkel, damit die Schleife nahtlos ist.
    """
    t = t % cfg.cycle
    start = cfg.dark_lead
    rise_end = start + cfg.fade_in
    hold_end = rise_end + cfg.hold
    fall_end = hold_end + cfg.fade_out
    if t < start or t >= fall_end:
        return 0.0
    if t < rise_end:
        return float(smootherstep((t - start) / cfg.fade_in))
    if t < hold_end:
        return 1.0
    return float(smootherstep(1.0 - (t - hold_end) / cfg.fade_out))


def compose(layers, level, cfg):
    """Einen Frame als RGBA-uint8 zusammensetzen."""
    rgb = layers["base_rgb"]
    if level > 0.0:
        add = level * layers["warm_rgb"] + (level ** 2.0) * layers["hot_rgb"]
        # Screen-artig addieren: dunkler Untergrund nimmt das Licht voll auf,
        # helle Stellen laufen weich in die Saettigung.
        rgb = rgb + add * (1.0 - 0.45 * rgb)
    out = np.empty((cfg.height, cfg.width, 4), dtype=np.uint8)
    out[:, :, :3] = np.clip(rgb * 255.0 + 0.5, 0, 255).astype(np.uint8)
    out[:, :, 3] = np.clip(layers["alpha"] * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return out


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------

def ffmpeg_exe():
    for env in ("FFMPEG_BINARY", "IMAGEIO_FFMPEG_EXE"):
        if os.environ.get(env):
            return os.environ[env]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def encode_all(cfg, layers, levels, jobs):
    """Alle Ausgabeformate in einem Durchgang bedienen.

    jobs: Liste aus (pfad, ffmpeg-Argumente, Hintergrund oder None).
    Frames mit Leuchtstaerke null sind untereinander identisch und werden
    nur einmal berechnet -- das ist knapp die Haelfte des Zyklus.
    Rueckgabe: Pruefsummen des ersten und des letzten Frames.
    """
    procs = []
    for path, args_out, _bg in jobs:
        cmd = [ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgba",
               "-s", f"{cfg.width}x{cfg.height}", "-r", str(cfg.fps),
               "-i", "pipe:0"] + args_out + [path]
        procs.append(subprocess.Popen(cmd, stdin=subprocess.PIPE))

    dark = None
    first = last = None
    try:
        for i, level in enumerate(levels):
            if level == 0.0 and dark is not None:
                payloads = dark
            else:
                frame = compose(layers, level, cfg)
                payloads = [
                    (flatten(frame, bg) if bg is not None else frame).tobytes()
                    for _path, _args, bg in jobs
                ]
                if level == 0.0:
                    dark = payloads
            for proc, payload in zip(procs, payloads):
                proc.stdin.write(payload)
            if i == 0:
                first = hashlib.sha256(payloads[0]).hexdigest()
            if i == len(levels) - 1:
                last = hashlib.sha256(payloads[0]).hexdigest()
    except BrokenPipeError:
        raise SystemExit("ffmpeg hat die Verbindung abgebrochen.")

    for proc, (path, _args, _bg) in zip(procs, jobs):
        proc.stdin.close()
        if proc.wait() != 0:
            raise SystemExit(f"ffmpeg ist fehlgeschlagen: {path}")
    return first, last


def flatten(rgba, background):
    """RGBA ueber einen undurchsichtigen Hintergrund legen (fuer die Vorschau)."""
    a = rgba[:, :, 3:4].astype(np.float32) / 255.0
    rgb = rgba[:, :, :3].astype(np.float32)
    out = np.empty_like(rgba)
    out[:, :, :3] = np.clip(rgb * a + background * (1.0 - a) + 0.5, 0, 255).astype(np.uint8)
    out[:, :, 3] = 255
    return out


def preview_background(cfg):
    """Ruhiger Verlauf als Platzhalter fuer das Kamerabild."""
    yy = (np.arange(cfg.height, dtype=np.float32) / (cfg.height - 1))[:, None]
    xx = (np.arange(cfg.width, dtype=np.float32) / (cfg.width - 1))[None, :]
    r = 26 + 40 * (1 - yy) + 14 * xx
    g = 34 + 46 * (1 - yy) + 10 * xx
    b = 46 + 58 * (1 - yy) + 6 * xx
    return np.clip(np.stack([r, g, b], axis=2), 0, 255).astype(np.float32)


# --------------------------------------------------------------------------

def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--text", default="AwenHD", help="Schriftzug in der Leiste")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--cycle", type=float, default=20.0,
                   help="Sekunden pro Durchlauf (Standard 20)")
    p.add_argument("--out-dir", default="out")
    p.add_argument("--name", default="awenhd-facecam-frame")
    p.add_argument("--still-only", action="store_true",
                   help="nur Standbilder schreiben, keine Videos")
    p.add_argument("--webm-crf", type=int, default=None,
                   help="WebM verlustbehaftet mit dieser Qualitaetsstufe "
                        "kodieren (z. B. 20); ohne Angabe verlustfrei")
    p.add_argument("--mov", action="store_true",
                   help="zusaetzlich ProRes 4444 schreiben (verlustarm, "
                        "rund 400 MB fuer 10 Sekunden)")
    p.add_argument("--seed", type=int, default=7)

    # Geometrie
    p.add_argument("--side", type=int, default=34, help="Randbreite links/rechts")
    p.add_argument("--top", type=int, default=34, help="Randbreite oben")
    p.add_argument("--bar", type=int, default=104, help="Hoehe der schwarzen Leiste")
    p.add_argument("--radius-outer", type=float, default=22.0)
    p.add_argument("--radius-inner", type=float, default=9.0)

    # Material
    p.add_argument("--bevel", type=float, default=7.5, help="Breite der Abschraegung")
    p.add_argument("--bevel-depth", type=float, default=2.6)
    p.add_argument("--bevel-gain", type=float, default=2.3)
    p.add_argument("--frame-dark", type=float, default=0.040)
    p.add_argument("--frame-light", type=float, default=0.345)
    p.add_argument("--bar-dark", type=float, default=0.016)
    p.add_argument("--bar-light", type=float, default=0.098)

    # Schrift
    p.add_argument("--text-height", type=float, default=0.50,
                   help="Versalhoehe als Anteil der Leistenhoehe")
    p.add_argument("--tracking", type=float, default=0.30,
                   help="Sperrung, als Anteil der Versalhoehe")
    p.add_argument("--engrave-depth", type=float, default=0.100)
    p.add_argument("--engrave-catch", type=float, default=0.080)

    # Animation
    p.add_argument("--dark-lead", type=float, default=2.0,
                   help="dunkle Phase am Zyklusanfang")
    p.add_argument("--fade-in", type=float, default=2.8)
    p.add_argument("--hold", type=float, default=9.0)
    p.add_argument("--fade-out", type=float, default=3.4)

    cfg = p.parse_args(argv)
    cfg.glow_rgb = (1.00, 0.640, 0.290)   # helles Orange
    cfg.core_rgb = (1.00, 0.760, 0.420)   # heisser Kern, bleibt orange
    tail = cfg.cycle - (cfg.dark_lead + cfg.fade_in + cfg.hold + cfg.fade_out)
    if tail < 0:
        raise SystemExit(
            f"Die Blendphasen sind zusammen laenger als der Zyklus "
            f"({cfg.cycle - tail:.2f}s > {cfg.cycle:.2f}s).")
    cfg.dark_tail = tail
    return cfg


def main(argv=None):
    cfg = parse_args(argv or sys.argv[1:])
    if cfg.bar <= 8:
        raise SystemExit("--bar muss groesser als 8 sein.")

    os.makedirs(cfg.out_dir, exist_ok=True)
    print(f"Rahmen {cfg.width}x{cfg.height}, Leiste {cfg.bar}px, "
          f"Schriftzug '{cfg.text}'")
    layers = build_frame(cfg)
    print(f"  Schriftgrad {layers['font_size']}px, Leiste ab y={layers['bar_top']}")

    base = os.path.join(cfg.out_dir, cfg.name)

    # Standbilder: Gravur dunkel und Schriftzug voll ausgeleuchtet.
    Image.fromarray(compose(layers, 0.0, cfg), "RGBA").save(base + "-aus.png")
    Image.fromarray(compose(layers, 1.0, cfg), "RGBA").save(base + "-an.png")
    bg = preview_background(cfg)
    Image.fromarray(flatten(compose(layers, 0.0, cfg), bg), "RGBA").convert("RGB").save(
        base + "-vorschau-aus.png")
    Image.fromarray(flatten(compose(layers, 1.0, cfg), bg), "RGBA").convert("RGB").save(
        base + "-vorschau-an.png")
    print(f"  Standbilder: {base}-aus.png / -an.png (+ Vorschau)")
    if cfg.still_only:
        return 0

    n = int(round(cfg.cycle * cfg.fps))
    levels = [glow_level(i / cfg.fps, cfg) for i in range(n)]
    print(f"  {n} Frames bei {cfg.fps} fps = {n / cfg.fps:.3f}s pro Schleife")
    print(f"  Zyklus: {cfg.dark_lead:g}s dunkel, {cfg.fade_in:g}s ein, "
          f"{cfg.hold:g}s halten, {cfg.fade_out:g}s aus, {cfg.dark_tail:g}s dunkel "
          f"-- um den Schleifenpunkt bleiben "
          f"{cfg.dark_tail + cfg.dark_lead:g}s dunkel")

    jobs = [
        # VP9 mit Alphakanal -- fuer OBS, Browser, Streamlabs.
        # Verlustfrei, damit die Schleife wirklich Frame fuer Frame schliesst
        # und die Randtextur keine Kompressionsartefakte bekommt.
        (base + ".webm", [
            "-an", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
        ] + (["-lossless", "1"] if cfg.webm_crf is None
             else ["-b:v", "0", "-crf", str(cfg.webm_crf)]) + [
            "-row-mt", "1", "-auto-alt-ref", "0", "-lag-in-frames", "0",
            "-metadata:s:v:0", "alpha_mode=1",
        ], None),
        # Vorschau ohne Alpha, Rahmen ueber einem Platzhalter-Hintergrund.
        (base + "-vorschau.mp4", [
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "18", "-preset", "slow", "-movflags", "+faststart",
        ], bg),
    ]
    if cfg.mov:
        # ProRes 4444 -- fuer Schnittprogramme, mit Alphakanal.
        jobs.append((base + ".mov", [
            "-an", "-c:v", "prores_ks", "-profile:v", "4444",
            "-pix_fmt", "yuva444p10le", "-alpha_bits", "8", "-vendor", "apl0",
        ], None))
    first, last = encode_all(cfg, layers, levels, jobs)
    for path, _args, _bg in jobs:
        size = os.path.getsize(path) / 1024.0
        print(f"  {path} ({size:.0f} KiB)")

    if first == last:
        print(f"  Schleife geprueft: erster und letzter Frame identisch ({first[:16]})")
    else:
        print(f"  WARNUNG: erster ({first[:16]}) und letzter Frame ({last[:16]}) "
              f"unterscheiden sich")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
