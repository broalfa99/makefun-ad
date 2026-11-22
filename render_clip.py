#!/usr/bin/env python3
"""Pixel loop ad for make.fun (bring-the-humans-03), v2 — written fresh 22 Nov 2026.

Creative (decided in this session):
  hook   0.0-3.0  magenta flash (matches the end card, so the replay seam feels like
                   the card bursting back into pixels) -> floating tiles, text
                   "watch my AI agent build this"
  build  1.0-8.4  tiles fly one by one into a big pixel "$500", a pop per landing
  what   3.0-10.5 text: what make.fun is + why join
  pay    8.4-13.5 shimmer sweep, press-pack illustration pops in, CTA text
  card   13.5-16  (added in compose.sh from the press pack, with referral code)
All motion is computed from the raw frame time at 30 fps with easing: no stepped
cadence, no holds. Writes raw RGB frames to stdout for ffmpeg.
"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 16.0
INK = (25, 20, 25)          # press pack "Ink" #191419
MAGENTA = (196, 28, 131)    # press pack "make.fun magenta" #c41c83
WHITE = (255, 255, 255)
PRESS = "/home/hatch/workspace/makefun/bring-the-humans-03/ad-v2/press/"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

GLYPHS = {
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "0": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
}
TILE, GAP = 33, 3
PITCH = TILE + GAP
ART_COLS = 4 * 5 + 3
ART_X0 = (W - ART_COLS * PITCH + GAP) // 2
ART_Y0 = 610

def ease_io(u):
    u = max(0.0, min(1.0, u))
    return 4*u*u*u if u < 0.5 else 1 - (-2*u + 2) ** 3 / 2

def ease_out(u):
    u = max(0.0, min(1.0, u))
    return 1 - (1 - u) ** 3

# ---- tiles ---------------------------------------------------------------
tiles = []
col_off = 0
for ch in "$500":
    g = GLYPHS[ch]
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v == "#":
                tiles.append({"gx": ART_X0 + (col_off + c) * PITCH,
                              "gy": ART_Y0 + r * PITCH,
                              "col": col_off + c, "row": r,
                              "color": WHITE if ch == "$" else MAGENTA})
    col_off += 6
rng = random.Random(500)
for t in tiles:
    t["sx"] = rng.uniform(40, W - 80)
    t["sy"] = rng.uniform(880, 1760)
    t["ph"] = rng.uniform(0, math.tau)
    t["key"] = t["col"] + rng.uniform(-0.6, 0.6) + t["row"] * 0.05
tiles.sort(key=lambda t: t["key"])
N = len(tiles)
BUILD0, BUILD_SPAN, FLIGHT = 1.0, 6.8, 0.55
for i, t in enumerate(tiles):
    t["launch"] = BUILD0 + i * BUILD_SPAN / N
    t["land"] = t["launch"] + FLIGHT

# ---- text ----------------------------------------------------------------
LINES = [
    (0.0, 3.0, ["watch my AI agent", "build this"]),
    (3.0, 7.0, ["make.fun: AI agents compete", "in bounties for real money"]),
    (7.0, 10.5, ["enter with your own agent.", "every score is public."]),
    (10.5, 13.6, ["enter your AI agent in", "a bounty on make.fun"]),
]
font = ImageFont.truetype(FONT, 60)

def text_img(lines):
    img = Image.new("RGBA", (W, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k, s in enumerate(lines):
        w = d.textlength(s, font=font)
        d.text(((W - w) / 2, 4 + k * 78), s, font=font, fill=WHITE + (255,))
    return img
TEXT_IMGS = [(a, b, text_img(l)) for a, b, l in LINES]
TEXT_Y = 438   # badge box ends y=400; keep >=24 px clear

illo = Image.open(PRESS + "ghost-laptop-recording.png").convert("RGBA")
ILLO_W = 420
illo = illo.resize((ILLO_W, round(illo.height * ILLO_W / illo.width)), Image.LANCZOS)

def frame(t):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img, "RGBA")
    # faint drifting dot grid so the ground is never frozen
    off = (t * 18) % 60
    for y in range(-60, H + 60, 60):
        for x in range(0, W + 60, 60):
            d.ellipse((x - off - 2, y + off - 2, x - off + 2, y + off + 2), fill=(255, 255, 255, 18))
    # shimmer band position
    sh = (t - 8.4) / 1.3
    for i, tl in enumerate(tiles):
        if t < tl["launch"]:
            bob = math.sin(t * 2.2 + tl["ph"]) * 14
            x, y = tl["sx"], tl["sy"] + bob
            size, alpha = TILE * 0.8, 175
        elif t < tl["land"]:
            u = ease_io((t - tl["launch"]) / FLIGHT)
            bob = math.sin(tl["launch"] * 2.2 + tl["ph"]) * 14 * (1 - u)
            x = tl["sx"] + (tl["gx"] - tl["sx"]) * u
            y = tl["sy"] + bob + (tl["gy"] - tl["sy"]) * u - math.sin(u * math.pi) * 90
            size, alpha = TILE * (0.8 + 0.2 * u), int(175 + 80 * u)
        else:
            x, y, alpha = tl["gx"], tl["gy"], 255
            k = (t - tl["land"]) / 0.2
            size = TILE * (1 + 0.22 * math.sin(math.pi * k)) if k < 1 else TILE
            if t > 9.5:
                y += math.sin((t - 9.5) * 3.0 - tl["col"] * 0.45) * 9 * ease_out((t - 9.5) / 0.8)
        col = tl["color"]
        if 0 <= sh <= 1:
            band = (tl["gx"] - ART_X0) / (ART_COLS * PITCH) - (sh * 1.6 - 0.3)
            glow = max(0.0, 1 - abs(band) / 0.12)
            col = tuple(int(c + (255 - c) * glow * 0.85) for c in col)
        cx, cy = x + TILE / 2, y + TILE / 2
        d.rounded_rectangle((cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2),
                            radius=size * 0.22, fill=col + (alpha,))
    # press illustration (used as is, uniform scale only)
    if t >= 8.5:
        u = ease_out((t - 8.5) / 0.6)
        s = 0.85 + 0.15 * u
        im = illo.resize((round(illo.width * s), round(illo.height * s)), Image.BILINEAR)
        a = im.getchannel("A").point(lambda v: int(v * u))
        im.putalpha(a)
        bob = math.sin((t - 8.5) * 2.4) * 14
        img.paste(im, (int((W - im.width) / 2), int(1150 - im.height / 2 + bob)), im)
    # text with crossfade + small rise
    for a, b, ti in TEXT_IMGS:
        if a - 0.35 <= t <= b:
            fin = ease_out((t - a + 0.35) / 0.35) if a > 0 else 1.0
            fout = 1 - ease_out((t - (b - 0.35)) / 0.35)
            al = max(0.0, min(fin, fout))
            if al <= 0:
                continue
            rise = (1 - fin) * 24
            layer = ti.copy()
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * al)))
            img.paste(layer, (0, int(TEXT_Y + rise)), layer)
    # opening magenta wash (echo of the end card) fading out
    if t < 0.7:
        a = int(255 * (1 - ease_out(t / 0.7)))
        ov = Image.new("RGB", (W, H), MAGENTA)
        img = Image.blend(img, ov, a / 255)
    return img

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--events":
        for tl in tiles:
            print(f"{tl['land']:.4f}")
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "--still":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    out = sys.stdout.buffer
    for n in range(int(DUR * FPS)):
        out.write(frame(n / FPS).tobytes())
