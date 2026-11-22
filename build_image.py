#!/usr/bin/env python3
"""Render entry.png for news-image-20261121 from stories_20261121.json.

Original renderer written for the v11 entry: a warm broadsheet front page
(navy masthead, lead cards with fact banners, a big-numbers strip, a pin
map, an ALSO ON SATURDAY digest and a DATE CHECK footer) drawn with PIL.
Deterministic: same JSON + same fonts -> identical PNG bytes.
"""

import hashlib
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "stories_20261121.json")
OUT_PATH = os.path.join(HERE, "entry.png")

# --- palette ---------------------------------------------------------------
PAPER = (247, 242, 231)
CARD_BG = (255, 253, 246)
NAVY = (22, 40, 63)
INK = (22, 24, 29)
RED = (176, 42, 33)
GOLD = (201, 162, 39)
GOLD_PALE = (232, 213, 150)
GREY = (96, 92, 82)
RULE = (196, 184, 152)
PANEL = (238, 231, 210)
LAND = (216, 203, 168)
LAND_EDGE = (168, 152, 112)
GRID_LINE = (206, 194, 158)

W = H = 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968 content width

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, maxw):
    """Greedy word wrap; returns list of lines that fit maxw."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(draw, trial, fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_size(draw, text, path, start, maxw, minimum=10):
    """Largest font size <= start whose text fits maxw."""
    size = start
    while size > minimum and tw(draw, text, font(path, size)) > maxw:
        size -= 1
    return size


def tracked(draw, cx, y, text, fnt, fill, tracking=3):
    """Draw letter-spaced text centred on cx; returns total width."""
    widths = [tw(draw, ch, fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += wch + tracking
    return total


def number_disc(draw, cx, cy, r, n, fill=RED):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    fnt = font(SANS_B, 13 if n < 10 else 11)
    label = str(n)
    wch = tw(draw, label, fnt)
    draw.text((cx - wch / 2, cy - 8 if n < 10 else -7 + cy), label, font=fnt,
              fill=(255, 255, 255))


# --- masthead ---------------------------------------------------------------

def masthead(draw, data):
    draw.rectangle([0, 0, W, 142], fill=NAVY)
    draw.rectangle([0, 142, W, 145], fill=GOLD)
    tracked(draw, W / 2, 13, "THE DAY IN WORLD NEWS", font(SANS_B, 23),
            GOLD_PALE, tracking=6)
    title = data["title"]
    size = fit_size(draw, title, SERIF_B, 70, CW - 40)
    fnt = font(SERIF_B, size)
    wch = tw(draw, title, fnt)
    draw.text(((W - wch) / 2, 40), title, font=fnt, fill=(255, 255, 255))
    n_stories = len(data["cards"]) + len(data["digest"])
    stats = "%d STORIES · 7 REGIONS · ONE PAGE" % n_stories
    tracked(draw, W / 2, 118, stats, font(SANS_B, 14), GOLD_PALE, tracking=3)


# --- big numbers strip ------------------------------------------------------

def numbers_strip(draw, data, y0=154):
    items = data["numbers_strip"]
    n = len(items)
    cell = CW / n
    big_f = font(SERIF_B, 26)
    cap_f = font(SANS_R, 9)
    for i, item in enumerate(items):
        x = MARGIN + i * cell
        if i:
            draw.line([x, y0 + 2, x, y0 + 48], fill=RULE, width=1)
        draw.text((x + 8, y0), item["big"], font=big_f, fill=RED)
        lines = wrap(draw, item["cap"], cap_f, cell - 16)[:2]
        for j, line in enumerate(lines):
            draw.text((x + 8, y0 + 30 + j * 10), line, font=cap_f, fill=INK)
    draw.line([MARGIN, y0 + 53, MARGIN + CW, y0 + 53], fill=RULE, width=1)


# --- cards ------------------------------------------------------------------

def chip_box(draw, x, y, text, fnt, fg, bg):
    wch = tw(draw, text, fnt)
    draw.rectangle([x, y, x + wch + 10, y + 15], fill=bg)
    draw.text((x + 5, y + 2), text, font=fnt, fill=fg)
    return wch + 10


def hero_card(draw, card, y0):
    h = 108
    draw.rectangle([MARGIN, y0, MARGIN + CW, y0 + h], fill=CARD_BG,
                   outline=RULE, width=1)
    # left banner panel
    pw = 292
    draw.rectangle([MARGIN, y0, MARGIN + pw, y0 + h], fill=NAVY)
    bf = font(SANS_B, fit_size(draw, card["banner"], SANS_B, 30, pw - 52))
    parts = card["banner"].split(": ", 1)
    if len(parts) == 2:
        draw.text((MARGIN + 40, y0 + 14), parts[0] + ":", font=bf,
                  fill=GOLD_PALE)
        draw.text((MARGIN + 40, y0 + 14 + bf.size + 4), parts[1], font=bf,
                  fill=(255, 255, 255))
    else:
        draw.text((MARGIN + 40, y0 + 14), card["banner"], font=bf,
                  fill=(255, 255, 255))
    if card.get("chip"):
        chip_box(draw, MARGIN + 16, y0 + h - 26, card["chip"],
                 font(SANS_B, 11), NAVY, GOLD_PALE)
    # right content
    x = MARGIN + pw + 18
    maxw = MARGIN + CW - x - 14
    cat = "%s · %s" % (card["region"], card["topic"])
    draw.text((x, y0 + 10), cat, font=font(SANS_B, 12), fill=RED)
    meta = "%s · %s" % (card["source"], card["status"])
    mf = font(SANS_B, 11)
    draw.text((MARGIN + CW - 14 - tw(draw, meta, mf), y0 + 10), meta,
              font=mf, fill=GREY)
    hf = font(SERIF_B, 23)
    lines = wrap(draw, card["headline"], hf, maxw)[:2]
    for j, line in enumerate(lines):
        draw.text((x, y0 + 28 + j * 27), line, font=hf, fill=INK)
    bf2 = font(SANS_R, 13)
    body_y = y0 + 28 + len(lines) * 27 + 3
    for j, line in enumerate(wrap(draw, card["body"], bf2, maxw)[:2]):
        draw.text((x, body_y + j * 17), line, font=bf2, fill=INK)
    number_disc(draw, MARGIN + 17, y0 + 17, 13, card["n"])


def grid_card(draw, card, x, y, w, h, body_size):
    draw.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=RULE, width=1)
    # banner strip (number disc sits on the strip, banner text indented)
    draw.rectangle([x, y, x + w, y + 21], fill=NAVY)
    has_chip = bool(card.get("chip"))
    bf = font(SANS_B, fit_size(draw, card["banner"], SANS_B, 13,
                               w - 124 if has_chip else w - 44))
    draw.text((x + 28, y + 4), card["banner"], font=bf, fill=(255, 255, 255))
    if has_chip:
        cf = font(SANS_B, 9)
        chw = tw(draw, card["chip"], cf)
        draw.rectangle([x + w - chw - 12, y + 3, x + w - 4, y + 18], fill=GOLD)
        draw.text((x + w - chw - 8, y + 5), card["chip"], font=cf, fill=NAVY)
    # category + meta
    cat = "%s · %s" % (card["region"], card["topic"])
    draw.text((x + 8, y + 26), cat, font=font(SANS_B, 10), fill=RED)
    meta = "%s · %s" % (card["source"], card["status"])
    mf = font(SANS_R, 9)
    draw.text((x + w - 8 - tw(draw, meta, mf), y + 26), meta, font=mf,
              fill=GREY)
    # headline
    hf = font(SERIF_B, 13)
    lines = wrap(draw, card["headline"], hf, w - 16)[:2]
    for j, line in enumerate(lines):
        draw.text((x + 8, y + 40 + j * 16), line, font=hf, fill=INK)
    # body
    bf2 = font(SANS_R, body_size)
    body_y = y + 40 + len(lines) * 16 + 2
    max_lines = max(1, int((y + h - 5 - body_y) // (body_size + 2)))
    for j, line in enumerate(wrap(draw, card["body"], bf2, w - 16)[:max_lines]):
        draw.text((x + 8, body_y + j * (body_size + 2)), line, font=bf2,
                  fill=INK)
    number_disc(draw, x + 13, y + 11, 10, card["n"])


# --- map --------------------------------------------------------------------

LAND_POLYS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-108, 73), (-95, 80), (-85, 70),
     (-80, 73), (-76, 62), (-65, 60), (-56, 52), (-60, 46), (-70, 44),
     (-74, 40), (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-89, 30),
     (-94, 29), (-97, 26), (-97, 16), (-92, 15), (-87, 13), (-83, 9),
     (-79, 9), (-85, 11), (-90, 14), (-95, 17), (-102, 18), (-105, 20),
     (-110, 24), (-114, 29), (-120, 34), (-124, 40), (-124, 47),
     (-130, 55), (-148, 60), (-162, 61)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-40, -22), (-48, -27), (-52, -33), (-58, -39),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -47),
     (-73, -38), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-80, -4),
     (-77, 1), (-77, 5)],
    # Africa
    [(-17, 15), (-10, 29), (-6, 35), (3, 37), (10, 37), (20, 32), (30, 31),
     (33, 27), (35, 24), (38, 21), (40, 15), (43, 12), (48, 11), (51, 12),
     (48, 5), (42, -2), (40, -10), (38, -18), (36, -22), (33, -26),
     (28, -33), (20, -35), (17, -32), (15, -27), (13, -18), (12, -10),
     (9, -1), (9, 4), (-8, 4), (-13, 7), (-17, 12)],
    # Europe
    [(-10, 36), (-6, 36), (-2, 37), (-9, 43), (-2, 44), (-1, 46), (-5, 48),
     (0, 50), (3, 53), (7, 54), (8, 57), (5, 59), (10, 59), (12, 56),
     (18, 55), (21, 54), (24, 59), (28, 60), (25, 65), (30, 70), (40, 67),
     (45, 64), (42, 58), (48, 52), (40, 48), (33, 46), (28, 41), (23, 40),
     (19, 42), (15, 44), (12, 44), (8, 44), (3, 43), (3, 39)],
    # Asia
    [(30, 70), (45, 68), (60, 69), (80, 73), (100, 77), (120, 73),
     (140, 72), (160, 70), (178, 66), (173, 62), (162, 60), (155, 58),
     (142, 54), (140, 47), (135, 41), (129, 38), (122, 38), (121, 31),
     (118, 26), (110, 20), (108, 15), (106, 9), (103, 6), (100, 9),
     (98, 13), (94, 17), (90, 22), (86, 20), (80, 15), (77, 8), (75, 13),
     (72, 20), (66, 25), (57, 26), (51, 28), (48, 30), (44, 29), (42, 34),
     (36, 36), (30, 41), (27, 42), (28, 48), (31, 55), (29, 62)],
    # Indonesia / SE Asia islands (stylised blobs)
    [(95, 5), (105, -6), (112, -7), (108, 1), (100, 0)],
    [(110, -7), (120, -8), (125, -9), (115, -8)],
    [(119, -1), (125, 1), (131, -1), (136, -2), (141, -3), (146, -6),
     (141, -8), (132, -4), (124, -2)],
    # Japan
    [(130, 31), (134, 34), (138, 35), (140, 37), (141, 40), (142, 44),
     (140, 42), (138, 38), (135, 34), (131, 32)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-7, 58), (-5, 58), (-2, 55),
     (-1, 52), (1, 51)],
    # Australia
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -36), (140, -38), (145, -38), (150, -37),
     (153, -31), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -11), (129, -13), (126, -14), (122, -17),
     (118, -20)],
    # New Zealand
    [(167, -46), (172, -41), (176, -38), (174, -37), (171, -42),
     (168, -47)],
]


def pin_map(draw, cards, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=PANEL, outline=RULE,
                   width=1)

    def px(lon, lat):
        return (x0 + (lon + 180) / 360.0 * w, y0 + (90 - lat) / 180.0 * h)

    for glon in range(-150, 180, 30):
        gx, _ = px(glon, 0)
        draw.line([gx, y0 + 1, gx, y0 + h - 1], fill=GRID_LINE, width=1)
    for glat in range(-60, 90, 30):
        _, gy = px(0, glat)
        draw.line([x0 + 1, gy, x0 + w - 1, gy], fill=GRID_LINE, width=1)
    for poly in LAND_POLYS:
        pts = [px(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for card in cards:
        if "pin" not in card:
            continue
        cx, cy = px(card["pin"][0], card["pin"][1])
        r = 9
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(255, 255, 255), width=2)
        fnt = font(SANS_B, 10 if card["n"] >= 10 else 11)
        label = str(card["n"])
        wch = tw(draw, label, fnt)
        draw.text((cx - wch / 2, cy - 6), label, font=fnt,
                  fill=(255, 255, 255))


# --- bottom section ---------------------------------------------------------

def bottom(draw, data, y0=758):
    # map block
    draw.text((MARGIN, y0), "WHERE IT HAPPENED", font=font(SANS_B, 15),
              fill=RED)
    draw.line([MARGIN, y0 + 22, MARGIN + 456, y0 + 22], fill=NAVY, width=2)
    pin_map(draw, data["cards"], MARGIN, y0 + 28, 456, 148)
    # digest block
    x0 = 508
    draw.text((x0, y0), "ALSO ON SATURDAY", font=font(SANS_B, 15), fill=RED)
    draw.line([x0, y0 + 22, MARGIN + CW, y0 + 22], fill=NAVY, width=2)
    items = data["digest"]
    half = (len(items) + 1) // 2
    cols = [items[:half], items[half:]]
    col_w = (MARGIN + CW - x0 - 12) // 2
    size = 10.5
    while size >= 8.5:
        fnt = font(SANS_R, int(size))
        fnt_b = font(SANS_B, int(size))
        lh = size + 2.5
        worst = 0
        for col in cols:
            total = 0.0
            for it in col:
                lead = "%d · %s — " % (it["n"], it["place"])
                lines = wrap(draw, lead + it["text"], fnt, col_w)
                total += len(lines) * lh + 2.5
            worst = max(worst, total)
        if worst <= 150:
            break
        size -= 0.5
    fnt = font(SANS_R, int(size))
    fnt_b = font(SANS_B, int(size))
    lh = size + 2.5
    for ci, col in enumerate(cols):
        cx = x0 + ci * (col_w + 12)
        cy = y0 + 30
        for it in col:
            lead = "%d · %s — " % (it["n"], it["place"])
            full = lead + it["text"]
            lines = wrap(draw, full, fnt, col_w)
            for j, line in enumerate(lines):
                if j == 0:
                    # bold the "n · place —" lead-in on the first line
                    lead_part = lead if len(lead) <= len(line) else line
                    draw.text((cx, cy), lead_part, font=fnt_b, fill=INK)
                    rest = line[len(lead_part):]
                    if rest:
                        draw.text((cx + tw(draw, lead_part, fnt_b), cy),
                                  rest, font=fnt, fill=INK)
                else:
                    draw.text((cx, cy), line, font=fnt, fill=INK)
                cy += lh
            cy += 2.5


# --- footer -----------------------------------------------------------------

def footer(draw, data, y0=950):
    sources = []
    for c in data["cards"] + data["digest"]:
        if c["source"] not in sources:
            sources.append(c["source"])
    src_line = "WIRES & SOURCES: " + " · ".join(sources)
    fnt = font(SANS_R, 9)
    lines = wrap(draw, src_line, fnt, CW)[:2]
    for j, line in enumerate(lines):
        draw.text((MARGIN, y0 + j * 11), line, font=fnt, fill=GREY)
    box_y = y0 + len(lines) * 11 + 4
    draw.rectangle([MARGIN, box_y, MARGIN + CW, 1018], outline=NAVY, width=1)
    text = "DATE CHECK — " + data["date_check"]
    tf = font(SANS_R, 10)
    tlines = wrap(draw, text, tf, CW - 20)
    for j, line in enumerate(tlines[:3]):
        f = font(SANS_B, 10) if j == 0 and line.startswith("DATE CHECK") else tf
        if j == 0:
            draw.text((MARGIN + 10, box_y + 6), "DATE CHECK — ", font=f,
                      fill=RED)
            rest = line[len("DATE CHECK — "):]
            draw.text((MARGIN + 10 + tw(draw, "DATE CHECK — ", f),
                       box_y + 6), rest, font=tf, fill=INK)
        else:
            draw.text((MARGIN + 10, box_y + 6 + j * 13), line, font=tf,
                      fill=INK)


# --- main -------------------------------------------------------------------

def choose_body_size(draw, cards, w):
    """Largest shared grid-body size (9.5/9/8.5) keeping every body <=3 lines."""
    for size in (10, 9, 8):
        fnt = font(SANS_R, size)
        if all(len(wrap(draw, c["body"], fnt, w - 16)) <= 3 for c in cards):
            return size
    return 8


def main():
    with open(DATA_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    masthead(draw, data)
    numbers_strip(draw, data)
    cards = sorted(data["cards"], key=lambda c: c["n"])
    hero_card(draw, cards[0], 218)
    rest = cards[1:]
    body_size = choose_body_size(draw, rest, 314)
    gx, gy = MARGIN, 334
    col_w, row_h, gap_x, gap_y = 314, 98, 13, 6
    for i, card in enumerate(rest):
        x = gx + (i % 3) * (col_w + gap_x)
        y = gy + (i // 3) * (row_h + gap_y)
        grid_card(draw, card, x, y, col_w, row_h, body_size)
    bottom(draw, data)
    footer(draw, data)
    img.save(OUT_PATH, format="PNG", optimize=True)
    raw = open(OUT_PATH, "rb").read()
    print("entry.png bytes:", len(raw))
    print("entry.png sha256:", hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
