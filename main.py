#!/usr/bin/env python3
"""Draw a newspaper-style front page summing up the world news of
Wednesday 25 November 2026 and write it to entry.png.

Pure Python standard library only (the grader runs python:3.13-slim,
which ships no Pillow): a tiny raster canvas, a hand-written 5x7 bitmap
font, and a zlib PNG encoder. No network, no clock, no randomness, no
environment input except the output directory, so two runs write
byte-identical files.

Run:  python3 main.py        (writes entry.png next to this file, or
       into $MAKEFUN_OUTPUT_DIR when that is set, as the grader does)
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)   # newsprint
INK = (20, 20, 20)       # near-black ink
GREY = (110, 105, 92)    # small print
RED = (166, 30, 30)      # kicker red
NAVY = (31, 58, 95)      # markets band
SKY = (207, 222, 234)    # illustration sky
SEA = (31, 78, 121)      # illustration sea
SUN = (242, 193, 78)
FLAME = (232, 114, 42)
FLAME2 = (242, 193, 78)
HULL = (32, 36, 42)
DECK = (58, 63, 71)
SMOKE = (122, 122, 122)
WHITE = (255, 255, 255)
CLOUD = (255, 255, 255)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 cells; '1' is ink, '0' is blank. Uppercase,
# digits and punctuation only: the whole page is set in capitals, as a
# newspaper front page would be. Unknown characters render as a space.
FONT = {
    'A': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'B': ('11110', '10001', '10001', '11110', '10001', '10001', '11110'),
    'C': ('01110', '10001', '10000', '10000', '10000', '10001', '01110'),
    'D': ('11110', '10001', '10001', '10001', '10001', '10001', '11110'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'G': ('01110', '10001', '10000', '10111', '10001', '10001', '01111'),
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'I': ('01110', '00100', '00100', '00100', '00100', '00100', '01110'),
    'J': ('00111', '00010', '00010', '00010', '00010', '10010', '01100'),
    'K': ('10001', '10010', '10100', '11000', '10100', '10010', '10001'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'N': ('10001', '11001', '10101', '10011', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
    'Q': ('01110', '10001', '10001', '10001', '10101', '10010', '01101'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'S': ('01111', '10000', '10000', '01110', '00001', '00001', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'U': ('10001', '10001', '10001', '10001', '10001', '10001', '01110'),
    'V': ('10001', '10001', '10001', '10001', '10001', '01010', '00100'),
    'W': ('10001', '10001', '10001', '10101', '10101', '11011', '10001'),
    'X': ('10001', '10001', '01010', '00100', '01010', '10001', '10001'),
    'Y': ('10001', '10001', '01010', '00100', '00100', '00100', '00100'),
    'Z': ('11111', '00001', '00010', '00100', '01000', '10000', '11111'),
    '0': ('01110', '10001', '10011', '10101', '11001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00110', '01000', '10000', '11111'),
    '3': ('11111', '00010', '00100', '00010', '00001', '10001', '01110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('00110', '01000', '10000', '11110', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00010', '00100', '01000', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00010', '01100'),
    ' ': ('00000', '00000', '00000', '00000', '00000', '00000', '00000'),
    '.': ('00000', '00000', '00000', '00000', '00000', '01100', '01100'),
    ',': ('00000', '00000', '00000', '00000', '01100', '00100', '01000'),
    ':': ('00000', '01100', '01100', '00000', '01100', '01100', '00000'),
    ';': ('00000', '01100', '01100', '00000', '01100', '00100', '01000'),
    '!': ('00100', '00100', '00100', '00100', '00100', '00000', '00100'),
    '?': ('01110', '10001', '00001', '00110', '00100', '00000', '00100'),
    "'": ('00100', '00100', '01000', '00000', '00000', '00000', '00000'),
    '"': ('01010', '01010', '00000', '00000', '00000', '00000', '00000'),
    '-': ('00000', '00000', '00000', '01110', '00000', '00000', '00000'),
    '(': ('00010', '00100', '01000', '01000', '01000', '00100', '00010'),
    ')': ('01000', '00100', '00010', '00010', '00010', '00100', '01000'),
    '/': ('00001', '00010', '00010', '00100', '01000', '01000', '10000'),
    '&': ('01100', '10010', '10100', '01000', '10101', '10010', '01101'),
    '%': ('11001', '11010', '00010', '00100', '01000', '01011', '10011'),
    '$': ('00100', '01111', '10100', '01110', '00101', '11110', '00100'),
    '+': ('00000', '00100', '00100', '11111', '00100', '00100', '00000'),
    '=': ('00000', '00000', '11111', '00000', '11111', '00000', '00000'),
    '*': ('00000', '10101', '01110', '11111', '01110', '10101', '00000'),
    '#': ('01010', '01010', '11111', '01010', '11111', '01010', '01010'),
    '@': ('01110', '10001', '10111', '10101', '10110', '10000', '01110'),
    '_': ('00000', '00000', '00000', '00000', '00000', '00000', '11111'),
    '[': ('01110', '01000', '01000', '01000', '01000', '01000', '01110'),
    ']': ('01110', '00010', '00010', '00010', '00010', '00010', '01110'),
    '<': ('00010', '00100', '01000', '10000', '01000', '00100', '00010'),
    '>': ('01000', '00100', '00010', '00001', '00010', '00100', '01000'),
    '|': ('00100', '00100', '00100', '00100', '00100', '00100', '00100'),
    '\u2022': ('00000', '00000', '01100', '01100', '01100', '00000', '00000'),
    '\u2014': ('00000', '00000', '00000', '11111', '00000', '00000', '00000'),
}

BLANK = ('00000', '00000', '00000', '00000', '00000', '00000', '00000')


def clean(text):
    """Uppercase and fold the few non-ASCII marks the font lacks."""
    return (text.upper()
            .replace('\u2019', "'").replace('\u2018', "'")
            .replace('\u201c', '"').replace('\u201d', '"')
            .replace('\u00b7', '\u2022').replace('\u2013', '-'))


def char_width(scale):
    return 6 * scale


def text_width(text, scale):
    text = clean(text)
    return max(0, len(text) * char_width(scale) - scale)


def wrap(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width px."""
    words = clean(text).split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    """An RGB raster with a few flat-shape primitives."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(background) * (width * height))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o] = color[0]
            self.px[o + 1] = color[1]
            self.px[o + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        """Filled circle."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, cy + dy, 2 * half + 1, 1, color)

    def triangle(self, ax, ay, bx, by, cx, cy, color):
        """Filled triangle by horizontal scanlines."""
        pts = sorted(((ax, ay), (bx, by), (cx, cy)), key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        for y in range(y0, y2 + 1):
            xs = []
            for (px, py), (qx, qy) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x0, y0), (x2, y2))):
                if py == qy:
                    continue
                if min(py, qy) <= y <= max(py, qy):
                    xs.append(px + (qx - px) * (y - py) / (qy - py))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, y, xb - xa + 1, 1, color)

    def poly(self, points, color):
        """Filled convex polygon (fan from the first vertex)."""
        for i in range(1, len(points) - 1):
            self.triangle(points[0][0], points[0][1],
                          points[i][0], points[i][1],
                          points[i + 1][0], points[i + 1][1], color)

    def text(self, s, x, y, scale, color, align='left'):
        """Draw one line of the bitmap font, scaled by an integer."""
        s = clean(s)
        w = text_width(s, scale)
        if align == 'center':
            x -= w // 2
        elif align == 'right':
            x -= w
        for i, ch in enumerate(s):
            glyph = FONT.get(ch, BLANK)
            gx = x + i * char_width(scale)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(gx + col * scale, y + row * scale,
                                  scale, scale, color)

    def para(self, lines, x, y, scale, color, leading=None):
        """Draw wrapped lines; returns the y just below the last line."""
        step = (8 * scale + 2) if leading is None else leading
        for line in lines:
            self.text(line, x, y, scale, color)
            y += step
        return y


# --------------------------------------------------------------------- PNG
def png_bytes(canvas):
    """Encode the canvas as a PNG. No ancillary chunks, no timestamps:
    the same canvas always encodes to the same bytes."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', compressed) + chunk(b'IEND', b''))


# ------------------------------------------------------------------ layout
MARGIN = 28
RIGHT = WIDTH - MARGIN


def outline(canvas, x, y, w, h, color, thick=1):
    canvas.rect(x, y, w, thick, color)
    canvas.rect(x, y + h - thick, w, thick, color)
    canvas.rect(x, y, thick, h, color)
    canvas.rect(x + w - thick, y, thick, h, color)


def story(canvas, x, y, w, kicker, headline, body):
    """One middle-column story: red kicker, two-line headline, body."""
    canvas.text(kicker, x, y, 1, RED)
    lines = wrap(headline, w, 3)
    yy = canvas.para(lines, x, y + 13, 3, INK, leading=24)
    canvas.para(wrap(body, w, 2), x, yy + 4, 2, INK, leading=18)


def brief(canvas, x, y, w, h, kicker, headline, body):
    """One bottom-row boxed brief."""
    outline(canvas, x, y, w, h, INK, 1)
    canvas.text(kicker, x + 12, y + 12, 1, RED)
    lines = wrap(headline, w - 24, 2)
    yy = canvas.para(lines, x + 12, y + 28, 2, INK, leading=17)
    canvas.para(wrap(body, w - 24, 2), x + 12, yy + 6, 2, INK, leading=18)


def draw_hormuz_scene(canvas, x, y, w, h):
    """Two tankers on a blue sea under a pale sky, one burning."""
    outline(canvas, x, y, w, h, INK, 2)
    ix, iy = x + 2, y + 2
    iw, ih = w - 4, h - 4
    canvas.rect(ix, iy, iw, 136, SKY)              # sky
    canvas.disc(ix + iw - 46, iy + 32, 20, SUN)    # sun
    for cx, cy, r in ((56, 28, 12), (76, 22, 15), (96, 29, 11),
                      (216, 56, 11), (234, 50, 14), (252, 57, 10)):
        canvas.disc(ix + cx, iy + cy, r, CLOUD)    # clouds
    canvas.rect(ix, iy + 136, iw, ih - 136 - 28, SEA)  # sea
    for row, off in ((150, 0), (166, 40), (182, 12), (198, 52)):
        for wx in (8, 120, 232):
            canvas.hline(ix + wx + off % 60, iy + row, 52, WHITE, 2)
    # far tanker, right
    canvas.poly([(ix + 186, iy + 154), (ix + 316, iy + 154),
                 (ix + 308, iy + 176), (ix + 194, iy + 176)], HULL)
    canvas.rect(ix + 206, iy + 140, 44, 14, DECK)
    canvas.rect(ix + 252, iy + 128, 14, 12, RED)
    # near tanker, left, burning
    canvas.poly([(ix + 20, iy + 168), (ix + 142, iy + 168),
                 (ix + 134, iy + 192), (ix + 28, iy + 192)], HULL)
    canvas.rect(ix + 42, iy + 150, 58, 18, DECK)
    canvas.rect(ix + 86, iy + 134, 18, 16, RED)
    canvas.rect(ix + 86, iy + 140, 18, 4, WHITE)
    canvas.rect(ix + 48, iy + 154, 16, 12, SUN)
    canvas.rect(ix + 68, iy + 154, 16, 12, WHITE)
    canvas.vline(ix + 32, iy + 142, 26, INK, 2)
    canvas.triangle(ix + 58, iy + 150, ix + 70, iy + 120,
                    ix + 82, iy + 150, FLAME)
    canvas.triangle(ix + 76, iy + 150, ix + 86, iy + 128,
                    ix + 96, iy + 150, FLAME2)
    canvas.triangle(ix + 92, iy + 150, ix + 102, iy + 132,
                    ix + 112, iy + 150, FLAME)
    for cx, cy, r in ((72, 108, 9), (82, 90, 12), (96, 72, 15)):
        canvas.disc(ix + cx, iy + cy, r, SMOKE)
    # naval mine in the water
    mx, my = ix + 172, iy + 204
    canvas.disc(mx, my, 6, INK)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, -1), (1, -1), (-1, 1)):
        canvas.line(mx, my, mx + dx * 11, my + dy * 11, INK)
    # caption strip
    canvas.rect(ix, iy + ih - 28, iw, 28, PAPER)
    canvas.hline(ix, iy + ih - 28, iw, INK, 1)
    canvas.text("THE STRAIT OF HORMUZ, THE WORLD'S BUSIEST OIL LANE",
                ix + iw // 2, iy + ih - 19, 1, INK, align='center')


def build():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    # outer double border
    outline(c, 16, 16, WIDTH - 32, HEIGHT - 32, INK, 2)
    outline(c, 22, 22, WIDTH - 44, HEIGHT - 44, INK, 1)

    # masthead
    c.text("THE WORLD TODAY", WIDTH // 2, 34, 7, INK, align='center')
    c.hline(MARGIN, 94, RIGHT - MARGIN, INK, 2)
    c.text("WEDNESDAY, 25 NOVEMBER 2026", WIDTH // 2, 104, 3, RED,
           align='center')
    c.text("EVERY STORY BELOW HAPPENED OR WAS FIRST REPORTED ON "
           "WEDNESDAY 25 NOVEMBER 2026",
           WIDTH // 2, 132, 1, INK, align='center')
    c.hline(MARGIN, 146, RIGHT - MARGIN, INK, 4)
    c.hline(MARGIN, 154, RIGHT - MARGIN, INK, 1)

    # lead story
    c.text("LEAD STORY \u2022 STRAIT OF HORMUZ", MARGIN, 168, 2, RED)
    c.text("TWO TANKERS ABLAZE", MARGIN, 196, 5, INK)
    c.text("AFTER MINE STRIKES", MARGIN, 238, 5, INK)
    c.hline(MARGIN, 284, 576, INK, 1)
    c.para(wrap("IRAN SAID TWO OIL TANKERS STRUCK NAVAL MINES IN THE "
                "STRAIT OF HORMUZ AND CAUGHT FIRE. TEHRAN SAID THE "
                "SHIPS HAD TAKEN AN UNAUTHORIZED ROUTE THROUGH THE "
                "BUSY OIL LANE.", 576, 2),
           MARGIN, 294, 2, INK, leading=18)
    outline(c, MARGIN, 378, 576, 34, INK, 1)
    c.text("BRENT CRUDE: $89.73, UP 1.1% ON THE DAY.",
           MARGIN + 12, 388, 2, RED)
    draw_hormuz_scene(c, 620, 162, 376, 250)

    # middle stories
    c.hline(MARGIN, 440, RIGHT - MARGIN, INK, 2)
    c.vline(512, 452, 248, INK, 1)
    story(c, MARGIN, 452, 470, "YEMEN \u2022 SAUDI ARABIA",
          "HOUTHIS STRIKE SAUDI REFINERY",
          "YEMEN'S HOUTHIS SAID THEY ATTACKED THE RAS TANURA OIL "
          "REFINERY, A DAY AFTER A DRONE ATTACK ON A RIYADH TOWER "
          "HURT 11.")
    c.hline(MARGIN, 572, 470, INK, 1)
    story(c, MARGIN, 584, 470, "GAZA",
          "HAMAS SECURITY CHIEF KILLED IN GAZA",
          "ISRAEL KILLED HAMAS COLONEL MOHAMMAD ABUELOUF, ITS "
          "INTERIOR SECURITY CHIEF. HIS WIFE AND TWO CHILDREN ALSO "
          "DIED.")
    story(c, 526, 452, 470, "UKRAINE \u2022 RUSSIA",
          "UKRAINE DRONES HIT TWO REFINERIES",
          "UKRAINIAN DRONES SET TWO ROSNEFT REFINERIES IN SAMARA "
          "ABLAZE. ONE PERSON WAS KILLED. RUSSIA HIT ODESA AND "
          "KYIV.")
    c.hline(526, 572, 470, INK, 1)
    story(c, 526, 584, 470, "TECH \u2022 UNITED STATES",
          "HUAWEI GUILTY IN U.S. FRAUD TRIAL",
          "A U.S. JURY FOUND HUAWEI GUILTY OF BANK FRAUD AND "
          "TRADE-SECRET THEFT ON 10 OF 12 COUNTS. RACKETEERING: "
          "NOT GUILTY.")

    # markets band
    c.rect(MARGIN, 712, RIGHT - MARGIN, 80, NAVY)
    c.text("WALL STREET AND ASIA TUMBLE ON AI DOUBTS",
           WIDTH // 2, 726, 3, WHITE, align='center')
    c.text("KOSPI -6.2%   NIKKEI -2.8%   S&P 500 -2.2%   GOLD -3.2%   "
           "BRENT $89.73 +1.1%",
           WIDTH // 2, 758, 2, WHITE, align='center')

    # bottom briefs
    brief(c, 28, 804, 304, 144, "SPACE",
          "FIRST PAKISTANI ASTRONAUT IN ORBIT",
          "CHINA'S SHENZHOU-24 DOCKED WITH TIANGONG HOURS AFTER "
          "LAUNCH.")
    brief(c, 360, 804, 304, 144, "THE PACIFIC",
          "PACIFIC PACT BARS FOREIGN BASES",
          "AUSTRALIA AND SOLOMON ISLANDS SIGNED A TREATY BARRING "
          "FOREIGN BASES.")
    brief(c, 692, 804, 304, 144, "COLOMBIA",
          "ALL HOSTAGES FREED IN CARTAGENA",
          "COLOMBIAN FORCES FREED EVERY HOSTAGE AFTER A 17-HOUR "
          "SIEGE.")

    # footer round-up
    c.text("ALSO ON 25 NOVEMBER: SPAIN HEADS FOR A SNAP ELECTION "
           "\u2022 POLAND PLANS A NO-FLY ZONE \u2022 SUDAN STRIKES "
           "KILL 19",
           WIDTH // 2, 958, 1, GREY, align='center')
    c.text("SPACEX CLEARED FOR 1M SATELLITES \u2022 U.S. TARIFFS "
           "LOOM FOR 16 ECONOMIES \u2022 COP31 TALKS FAIL",
           WIDTH // 2, 972, 1, GREY, align='center')
    c.text("DRAWN FROM THE DAY'S REPORTS \u2022 THE WORLD TODAY "
           "\u2022 WEDNESDAY 25 NOVEMBER 2026",
           WIDTH // 2, 986, 1, GREY, align='center')
    return c


def main():
    canvas = build()
    data = png_bytes(canvas)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or ""
    if not outdir or not os.path.isdir(outdir):
        if os.path.isdir("/output"):
            outdir = "/output"
        else:
            outdir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
