#!/usr/bin/env python3
"""Build entry.png for news-image-20261124.

Draws a newspaper front page, "The World in One Day - 24 November 2026",
with PIL (available in this VM). Stories, all verified from reporting on
Tuesday 24 November 2026:
  LEAD: Iran says three oil tankers hit naval mines and caught fire in the
        Strait of Hormuz (IRGC statement, reported overnight into 24 Nov).
  KOREA: South Korea scrambles jets; evacuation warning for Ulleung island
         after Russian military planes enter the air-defence zone (24 Nov).
  BRIEFS: Seoul names a new foreign minister and intelligence chief (24 Nov);
          the US naval blockade of Iran and Tehran's vow to break it.
  LIGHTER: The full Beaver Supermoon peaks 9:53 a.m. EST and passes within
           0.9 degrees of the Pleiades (Seven Sisters) before dawn (24 Nov).
Output: 1024x1024 PNG, under 1 MiB.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 234)
INK = (20, 20, 20)
RED = (178, 34, 34)
NAVY = (15, 42, 74)
GREY = (90, 90, 90)
RULE = (60, 60, 60)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, spacing=4, align="left"):
    lines = wrap(draw, text, fnt, max_w)
    for line in lines:
        if align == "center":
            lx = x + (max_w - draw.textlength(line, font=fnt)) / 2
        else:
            lx = x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, y1 - y0)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, yy), (x1, yy)], fill=c)


def flame(draw, cx, base, w, h):
    """A stylised flame: layered teardrops in red, orange, yellow."""
    for scale, col in ((1.0, (200, 40, 20)), (0.72, (240, 120, 20)),
                       (0.45, (250, 200, 60))):
        fw, fh = w * scale, h * scale
        pts = [(cx - fw / 2, base), (cx - fw * 0.32, base - fh * 0.55),
               (cx + fw * 0.10, base - fh * 0.85), (cx + fw * 0.28, base - fh),
               (cx + fw * 0.42, base - fh * 0.55), (cx + fw / 2, base),
               (cx, base - fh * 0.12)]
        draw.polygon(pts, fill=col)


def draw_lead_scene(img, box):
    """Dusk over the Strait of Hormuz: burning tankers on dark water.

    Drawn on its own layer so smoke and flames can never spill past
    the scene's frame onto the date line above it.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    horizon = int(h * 0.52)
    vgrad(draw, (0, 0, w, horizon), (64, 28, 66), (214, 110, 48))
    # low sun
    draw.ellipse([w - 190, 26, w - 110, 106], fill=(255, 214, 130))
    vgrad(draw, (0, horizon, w, h), (28, 66, 84), (10, 32, 48))
    # sun glint on water
    for i in range(6):
        yy = horizon + 14 + i * 16
        wdt = 130 - i * 14
        draw.line([(w - 150 - wdt // 2, yy), (w - 150 + wdt // 2, yy)],
                  fill=(255, 190, 90), width=3)
    # distant headland
    draw.polygon([(0, horizon), (150, horizon - 42), (320, horizon),
                  (0, horizon)], fill=(40, 24, 44))
    # three tankers
    tankers = [(60, 150, 1.0), (330, 210, 1.25), (660, 150, 1.0)]
    for tx, tw, sc in tankers:
        th = int(34 * sc)
        deck = horizon + 26
        draw.rectangle([tx, deck - th, tx + tw, deck], fill=(18, 18, 22))
        draw.rectangle([tx + tw * 0.62, deck - th - 22 * sc, tx + tw * 0.78,
                        deck - th], fill=(30, 30, 34))
        draw.rectangle([tx + 6, deck, tx + tw - 6, deck + 8], fill=(12, 12, 16))
        # flames on deck
        flame(draw, tx + tw * 0.25, deck - th + 6, 34 * sc, 66 * sc)
        flame(draw, tx + tw * 0.55, deck - th + 4, 26 * sc, 52 * sc)
        # smoke
        for k in range(3):
            sx = tx + tw * 0.3 + k * 14
            sy = deck - th - 46 - k * 30
            r = 26 + k * 8
            draw.ellipse([sx - r, sy - r * 0.7, sx + r, sy + r * 0.7],
                         fill=(70, 66, 64))
    img.paste(layer, (x0, y0), layer)
    d = ImageDraw.Draw(img, "RGBA")
    # frame
    d.rectangle(box, outline=(20, 20, 20), width=3)


def draw_jet(draw, cx, cy, s, col):
    """Simple fighter-jet silhouette, nose to the right."""
    # slim fuselage: long thin triangle
    draw.polygon([(cx - 54 * s, cy), (cx + 58 * s, cy - 4 * s),
                  (cx + 58 * s, cy + 4 * s)], fill=col)
    # main swept wing
    draw.polygon([(cx - 8 * s, cy - 4 * s), (cx + 16 * s, cy - 26 * s),
                  (cx + 26 * s, cy - 4 * s)], fill=col)
    # tail wing
    draw.polygon([(cx - 30 * s, cy + 3 * s), (cx - 10 * s, cy + 20 * s),
                  (cx - 2 * s, cy + 3 * s)], fill=col)
    # tail fin
    draw.polygon([(cx - 46 * s, cy - 3 * s), (cx - 34 * s, cy - 18 * s),
                  (cx - 28 * s, cy - 3 * s)], fill=col)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    M = 36  # margin
    CW = W - 2 * M  # content width

    # ---- Masthead ----
    y = 26
    f_kick = font(SANS_B, 15)
    kick = "ONE DAY  ·  ONE PAGE  ·  THE WORLD"
    d.text(((W - d.textlength(kick, font=f_kick)) / 2, y), kick,
           font=f_kick, fill=GREY)
    y += 30
    f_title = font(SERIF_B, 60)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(title, font=f_title)) / 2, y), title,
           font=f_title, fill=INK)
    y += 78
    d.line([(M, y), (W - M, y)], fill=RULE, width=3)
    y += 6
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
    y += 12
    f_date = font(SANS_B, 24)
    date = "TUESDAY, 24 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, y), date,
           font=f_date, fill=RED)
    y += 40

    # ---- Lead illustration ----
    scene = (M, y, W - M, y + 218)
    draw_lead_scene(img, scene)
    y = scene[3] + 10
    f_cap = font(SANS, 14)
    cap = ("The Strait of Hormuz at dusk — the world's busiest oil chokepoint, "
           "where three tankers burned after hitting mines, Iran's Revolutionary Guard says.")
    y = draw_wrapped(d, M, y, cap, f_cap, CW, GREY, spacing=2)
    y += 8

    # ---- Lead headline ----
    f_head = font(SERIF_B, 44)
    y = draw_wrapped(d, M, y, "THREE TANKERS ABLAZE IN THE STRAIT OF HORMUZ",
                     f_head, CW, INK, spacing=2, align="center")
    y += 6
    f_stand = font(SERIF, 19)
    stand = ("Iran says the ships struck naval mines in the world's busiest oil "
             "chokepoint — as attacks on shipping reach their highest level "
             "since the war began.")
    y = draw_wrapped(d, M + 30, y, stand, f_stand, CW - 60, INK, spacing=3,
                     align="center")
    y += 12
    d.line([(M, y), (W - M, y)], fill=RULE, width=2)
    y += 16

    # ---- Middle: two columns ----
    col_w = (CW - 28) // 2
    left_x, right_x = M, M + col_w + 28
    mid_top = y

    # Left: Korea
    f_k = font(SANS_B, 16)
    d.text((left_x, y), "KOREA", font=f_k, fill=RED)
    y2 = y + 26
    f_h2 = font(SERIF_B, 27)
    y2 = draw_wrapped(d, left_x, y2,
                      "Seoul scrambles jets as Russian planes near",
                      f_h2, col_w, INK, spacing=2)
    y2 += 4
    # small jet + island sketch
    sketch = (left_x, y2, left_x + col_w, y2 + 58)
    d.rectangle(sketch, fill=(232, 238, 244), outline=RULE)
    draw_jet(d, left_x + 170, y2 + 30, 1.0, NAVY)
    draw_jet(d, left_x + 350, y2 + 20, 0.7, (90, 110, 140))
    d.polygon([(left_x + 30, y2 + 58), (left_x + 90, y2 + 34),
               (left_x + 150, y2 + 58)], fill=(60, 90, 70))
    d.text((left_x + 8, y2 + 6), "ULLEUNG ISLAND", font=font(SANS_B, 11),
           fill=(60, 90, 70))
    y2 = sketch[3] + 10
    f_body = font(SANS, 16)
    y2 = draw_wrapped(d, left_x, y2,
                      "South Korea scrambled fighter jets on Tuesday after "
                      "Russian military planes entered its air-defence zone. "
                      "An evacuation warning for Ulleung island was lifted "
                      "after three minutes; no airspace was breached.",
                      f_body, col_w, INK, spacing=3)
    left_bottom = y2

    # Right: Also today
    y3 = mid_top
    d.text((right_x, y3), "ALSO TODAY", font=f_k, fill=RED)
    y3 += 26
    d.line([(right_x, y3), (right_x + col_w, y3)], fill=RULE, width=1)
    y3 += 10
    f_h3 = font(SERIF_B, 21)
    y3 = draw_wrapped(d, right_x, y3, "Seoul names new envoys",
                      f_h3, col_w, INK, spacing=2)
    y3 += 2
    y3 = draw_wrapped(d, right_x, y3,
                      "South Korea's president nominates a new foreign "
                      "minister and a new intelligence chief, amid US "
                      "worries over the region.", f_body, col_w, INK,
                      spacing=3)
    y3 += 12
    d.line([(right_x, y3), (right_x + col_w, y3)], fill=RULE, width=1)
    y3 += 10
    y3 = draw_wrapped(d, right_x, y3, "Gulf on edge", f_h3, col_w, INK,
                      spacing=2)
    y3 += 2
    y3 = draw_wrapped(d, right_x, y3,
                      "The US naval blockade has brought Iranian oil "
                      "exports to a near standstill. Tehran vows to break "
                      "it; Washington warns any ship that tries will end "
                      "up at the bottom of the sea.", f_body, col_w, INK,
                      spacing=3)
    right_bottom = y3

    y = max(left_bottom, right_bottom) + 16
    d.line([(M, y), (W - M, y)], fill=RULE, width=2)
    y += 14

    # ---- Bottom strip: supermoon ----
    band = (M, y, W - M, 990)
    d.rectangle(band, fill=NAVY)
    # moon + stars
    mx, my = M + 58, band[1] + 52
    d.ellipse([mx - 38, my - 38, mx + 38, my + 38], fill=(245, 230, 170))
    d.ellipse([mx - 22, my - 26, mx - 6, my - 10], fill=(228, 210, 150))
    d.ellipse([mx + 8, my + 6, mx + 22, my + 20], fill=(228, 210, 150))
    for sx, sy, r in ((M + 150, band[1] + 18, 3), (M + 178, band[1] + 44, 2),
                      (M + 138, band[1] + 78, 2), (M + 196, band[1] + 84, 3),
                      (M + 160, band[1] + 62, 2)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    tx = M + 205
    tw = W - M - tx - 16
    f_moon = font(SERIF_B, 24)
    yy = band[1] + 12
    yy = draw_wrapped(d, tx, yy,
                      "BEAVER SUPERMOON MEETS THE SEVEN SISTERS",
                      f_moon, tw, (255, 255, 255), spacing=2)
    yy += 4
    f_moon2 = font(SANS, 15)
    draw_wrapped(d, tx, yy,
                 "November's full moon peaks at 9:53 a.m. EST and slides "
                 "within 0.9° of the Pleiades before dawn — the first of "
                 "three supermoons in a row.",
                 f_moon2, tw, (220, 228, 240), spacing=3)

    # ---- Footer ----
    f_foot = font(SANS, 13)
    foot = "The World in One Day — 24 November 2026  ·  Drawn from the day's reporting"
    d.text(((W - d.textlength(foot, font=f_foot)) / 2, 997), foot,
           font=f_foot, fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
