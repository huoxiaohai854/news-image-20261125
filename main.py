#!/usr/bin/env python3
"""news-image-20261125: a newspaper front page for Wednesday 25 November 2026.

Draws one 1024x1024 PNG with only the Python standard library: a small
raster canvas, a hand-made 5x7 bitmap font, and a zlib PNG encoder.
No network, no clock, no dice, no files read while running, so two
runs write byte-identical output.

Run:  python3 main.py
  Writes entry.png next to this file, or into $MAKEFUN_OUTPUT_DIR when set.
"""

import os
import struct
import zlib
from binascii import crc32

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 241, 222)
INK = (22, 22, 22)
RED = (164, 31, 31)
NAVY = (29, 74, 122)
SEA = (36, 88, 128)
SKY_TOP = (176, 208, 230)
SKY_LOW = (226, 232, 226)
FLAME = (232, 122, 26)
FLAME_HOT = (246, 196, 66)
SMOKE = (120, 118, 112)
HULL = (94, 38, 30)
DECK = (52, 52, 52)

# ---------------------------------------------------------------- font
# A 5-wide, 7-tall bitmap alphabet, drawn row by row.  '#' is ink, '.'
# is empty.  Only the characters the page uses are defined; anything
# else renders blank.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
}

CHAR_W = 6   # 5 pixels of glyph + 1 of spacing
CHAR_H = 7


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    per_line = max(1, max_width // (CHAR_W * scale))
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if len(trial) <= per_line:
                current = trial
            else:
                if current:
                    lines.append(current)
                # A single over-long word is split by characters.
                while len(word) > per_line:
                    lines.append(word[:per_line])
                    word = word[per_line:]
                current = word
        if current:
            lines.append(current)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def hline(self, x, y, w, colour, thickness=1):
        self.fill_rect(x, y, w, thickness, colour)

    def vline(self, x, y, h, colour, thickness=1):
        self.fill_rect(x, y, thickness, h, colour)

    def fill_circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, colour)

    def fill_poly(self, points, colour):
        """Scanline fill for a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.height, max(ys) + 1)):
            crossings = []
            n = len(points)
            for i in range(n):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    crossings.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            crossings.sort()
            for j in range(0, len(crossings) - 1, 2):
                xa = int(crossings[j])
                xb = int(crossings[j + 1])
                self.fill_rect(xa, y, xb - xa + 1, 1, colour)

    def draw_char(self, x, y, char, scale, colour):
        glyph = FONT.get(char, FONT[' '])
        for row_i, row in enumerate(glyph):
            for col_i, cell in enumerate(row):
                if cell == '#':
                    self.fill_rect(x + col_i * scale, y + row_i * scale,
                                   scale, scale, colour)

    def draw_text(self, x, y, text, scale, colour):
        for i, char in enumerate(text):
            self.draw_char(x + i * CHAR_W * scale, y, char, scale, colour)
        return CHAR_H * scale

    def draw_lines(self, x, y, lines, scale, colour, leading=3):
        for line in lines:
            self.draw_text(x, y, line, scale, colour)
            y += CHAR_H * scale + leading
        return y

    def draw_centered(self, y, text, scale, colour, cx=WIDTH // 2):
        w = text_width(text, scale)
        self.draw_text(cx - w // 2, y, text, scale, colour)

    def draw_wrapped_centered(self, y, text, scale, colour, max_width,
                              cx=WIDTH // 2, leading=3):
        lines = wrap_text(text, scale, max_width)
        for line in lines:
            self.draw_centered(y, line, scale, colour, cx)
            y += CHAR_H * scale + leading
        return y


# ---------------------------------------------------------------- png
def png_bytes(canvas):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", crc32(kind + data) & 0xFFFFFFFF)
        return out

    header = struct.pack(">IIBBBBB", canvas.width, canvas.height,
                         8, 2, 0, 0, 0)  # 8-bit RGB, no interlace
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        raw += canvas.pixels[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- page
def draw_tanker(canvas, x, hull_bottom, scale_w, on_fire):
    """A stricken tanker: dark hull on the water, deck blocks, flames."""
    hull_h = 30
    hull_y = hull_bottom - hull_h
    # Hull with a raked bow.
    canvas.fill_poly([(x, hull_y), (x + scale_w, hull_y),
                      (x + scale_w - 16, hull_y + hull_h),
                      (x + 8, hull_y + hull_h)], HULL)
    canvas.fill_rect(x + 6, hull_y - 14, scale_w - 60, 14, DECK)
    canvas.fill_rect(x + scale_w - 58, hull_y - 26, 26, 26, DECK)
    canvas.fill_rect(x + scale_w - 52, hull_y - 38, 14, 12, (210, 210, 200))
    # Portholes.
    for i in range(6):
        canvas.fill_circle(x + 26 + i * 26, hull_y + 16, 3, (246, 236, 200))
    if on_fire:
        base_y = hull_y - 12
        for cx, r, col in ((x + 70, 22, FLAME), (x + 108, 28, FLAME_HOT),
                           (x + 146, 20, FLAME), (x + 88, 15, FLAME_HOT)):
            canvas.fill_circle(cx, base_y - 6, r, col)
        canvas.fill_poly([(x + 58, base_y), (x + 96, base_y - 54),
                          (x + 126, base_y)], FLAME)
        canvas.fill_poly([(x + 116, base_y), (x + 148, base_y - 46),
                          (x + 178, base_y)], FLAME_HOT)
        # Smoke rising, kept inside the picture frame.
        for cx, cy, r in ((x + 96, base_y - 58, 17), (x + 116, base_y - 80, 21),
                          (x + 94, base_y - 98, 19), (x + 122, base_y - 112, 16)):
            canvas.fill_circle(cx, cy, r, SMOKE)


def draw_lead_picture(canvas, x, y, w, h):
    canvas.fill_rect(x, y, w, h, SKY_LOW)
    horizon = y + int(h * 0.52)
    # Sky bands, pale at the horizon.
    bands = 5
    for i in range(bands):
        top = y + i * (horizon - y) // bands
        bot = y + (i + 1) * (horizon - y) // bands
        r = SKY_TOP[0] + (SKY_LOW[0] - SKY_TOP[0]) * i // (bands - 1)
        g = SKY_TOP[1] + (SKY_LOW[1] - SKY_TOP[1]) * i // (bands - 1)
        b = SKY_TOP[2] + (SKY_LOW[2] - SKY_TOP[2]) * i // (bands - 1)
        canvas.fill_rect(x, top, w, bot - top, (r, g, b))
    # Low sun behind the smoke.
    canvas.fill_circle(x + w - 150, y + 52, 30, (244, 214, 140))
    # Sea.
    canvas.fill_rect(x, horizon, w, y + h - horizon, SEA)
    canvas.fill_rect(x, horizon, w, 3, (120, 170, 200))
    # Wake lines.
    for i, wy in enumerate((horizon + 26, horizon + 58, horizon + 92)):
        canvas.hline(x + 40 + i * 30, wy, w - 160 - i * 40,
                     (150, 190, 215), 2)
    # Two tankers, the nearer one burning hardest; hull bottoms stay
    # inside the frame with a strip of sea below them.
    draw_tanker(canvas, x + 48, y + h - 14, 330, True)
    draw_tanker(canvas, x + w - 400, y + h - 30, 300, True)
    # Frame.
    canvas.fill_rect(x, y, w, 3, INK)
    canvas.fill_rect(x, y + h - 3, w, 3, INK)
    canvas.fill_rect(x, y, 3, h, INK)
    canvas.fill_rect(x + w - 3, y, 3, h, INK)


def draw_story(canvas, x, y, w, kicker, headline, body):
    canvas.draw_text(x, y, kicker, 2, RED)
    y += CHAR_H * 2 + 6
    head_lines = wrap_text(headline, 3, w)
    y = canvas.draw_lines(x, y, head_lines, 3, INK, leading=2)
    y += 5
    body_lines = wrap_text(body, 2, w)
    y = canvas.draw_lines(x, y, body_lines, 2, INK, leading=2)
    y += 6
    canvas.hline(x, y, w, (150, 140, 115), 1)
    return y + 10


def build_page():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    margin = 36
    inner = WIDTH - 2 * margin

    # Top line.
    canvas.draw_text(margin, 22, "WEDNESDAY, 25 NOVEMBER 2026", 2, INK)
    right = "WORLD EDITION - NO. 329"
    canvas.draw_text(WIDTH - margin - text_width(right, 2), 22, right, 2, INK)
    canvas.hline(margin, 44, inner, INK, 2)

    # Masthead.
    canvas.draw_centered(52, "THE WORLD TODAY", 8, INK)
    canvas.draw_centered(116, "THE DAY'S WORLD NEWS IN ONE PAGE", 2, RED)
    canvas.hline(margin, 138, inner, INK, 3)
    canvas.hline(margin, 144, inner, INK, 1)

    # Lead headline, three lines.
    y = 158
    for line in ("TWO TANKERS ABLAZE", "AFTER MINE STRIKES",
                 "IN THE STRAIT OF HORMUZ"):
        canvas.draw_centered(y, line, 5, INK)
        y += CHAR_H * 5 + 7
    y += 2
    y = canvas.draw_wrapped_centered(
        y,
        "MINES HIT THE SHIPS IN THE WORLD'S BUSIEST OIL WATERWAY AS FIRE "
        "AND SMOKE ROSE OVER THE GULF",
        2, NAVY, inner - 120)
    y += 10

    # Lead picture.
    pic_h = 190
    draw_lead_picture(canvas, margin, y, inner, pic_h)
    y += pic_h + 8
    canvas.draw_centered(
        y, "SMOKE RISES FROM A STRICKEN TANKER IN THE STRAIT OF HORMUZ.",
        2, INK)
    y += 24
    canvas.hline(margin, y, inner, INK, 2)
    y += 12

    # Three columns of shorter stories.
    col_w = (inner - 48) // 3
    col_x = [margin, margin + col_w + 24, margin + 2 * (col_w + 24)]
    stories = [
        [("MIDDLE EAST", "HOUTHIS CLAIM REFINERY STRIKE",
          "THE GROUP SAID IT HIT A REFINERY, ADDING TO FEARS OF A WIDER "
          "REGIONAL CONFLICT."),
         ("GAZA", "GAZA: A WAR THAT WILL NOT END",
          "FIGHTING AND HARDSHIP DRAG ON FOR CIVILIANS AS DIPLOMACY "
          "STRUGGLES TO FIND A WAY OUT.")],
        [("EUROPE", "UKRAINE: ANOTHER HARD WINTER",
          "THE WAR GRINDS ON INTO THE COLD MONTHS, WITH CITIES BRACING "
          "FOR MORE STRIKES ON POWER AND HEAT."),
         ("TECH", "HUAWEI VERDICT LANDS",
          "A COURT RULING ON THE CHINESE TECH GIANT DRAWS A LINE UNDER A "
          "LONG-RUNNING LEGAL FIGHT.")],
        [("SPACE", "SHENZHOU-24",
          "CHINA'S NEW CREW HEADS FOR ITS SPACE STATION AS THE COUNTRY "
          "PRESSES ON IN ORBIT."),
         ("PACIFIC", "PACIFIC PACT",
          "AUSTRALIA AND THE SOLOMON ISLANDS SIGN A NEW SECURITY PACT, "
          "RESHAPING THE BALANCE IN THE PACIFIC."),
         ("COLOMBIA", "CARTAGENA RESCUE",
          "HOSTAGES ARE FREED IN CARTAGENA AS A TENSE STANDOFF ENDS.")],
    ]
    top = y
    for i, column in enumerate(stories):
        yy = top
        for kicker, headline, body in column:
            yy = draw_story(canvas, col_x[i], yy, col_w,
                            kicker, headline, body)
        if i < 2:
            canvas.vline(col_x[i] + col_w + 12, top, 350, (150, 140, 115), 1)

    # Markets ticker.
    tick_y = 932
    canvas.fill_rect(margin, tick_y, inner, 40, RED)
    canvas.draw_text(
        margin + 14, tick_y + 13,
        "MARKETS TUMBLE AS OIL SPIKES AND INVESTORS FLEE RISK", 2,
        (255, 246, 230))
    # Footer.
    canvas.draw_centered(986, "THE WORLD TODAY - 25 NOVEMBER 2026", 2, INK)
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as handle:
        handle.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
