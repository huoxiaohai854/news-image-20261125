"""Clean-room newspaper front page for 25 November 2026.

Draws a 1024x1024 PNG with only the Python standard library.
No external fonts, no network, no clock, no randomness: the same
input always produces the same bytes.

Layout: masthead, one lead story, then eight stories in a 2x4 grid.
All nine topics of 25 November 2026 appear as headlines.
"""

import binascii
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (245, 240, 230)
INK = (18, 18, 18)
GREY = (90, 86, 78)
RED = (140, 30, 25)

# 5x7 bitmap font, uppercase only. Each glyph is 7 rows of 5 cells.
# "#" is ink, "." is empty. Text is upper-cased before drawing.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def new_image():
    buf = bytearray(WIDTH * HEIGHT * 3)
    for i in range(0, len(buf), 3):
        buf[i] = PAPER[0]
        buf[i + 1] = PAPER[1]
        buf[i + 2] = PAPER[2]
    return buf


def set_pixel(buf, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def fill_rect(buf, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_pixel(buf, xx, yy, color)


def hline(buf, x, y, w, color, thick=1):
    fill_rect(buf, x, y, w, thick, color)


def char_width(scale):
    return 5 * scale + scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


def draw_text(buf, x, y, text, scale, color):
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(buf, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += char_width(scale)
    return cx


def draw_centered(buf, y, text, scale, color, cx0=0, cx1=WIDTH):
    w = text_width(text, scale)
    x = cx0 + (cx1 - cx0 - w) // 2
    draw_text(buf, x, y, text, scale, color)


def wrap(text, max_chars):
    words = text.upper().split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(buf, x, y, w, kicker, headline, body, head_scale=3):
    # Kicker line with a small red square.
    fill_rect(buf, x, y + 2, 10, 10, RED)
    draw_text(buf, x + 16, y, kicker, 2, RED)
    # Headline, wrapped to the block width.
    max_chars = w // char_width(head_scale)
    lines = wrap(headline, max_chars)
    hy = y + 22
    for line in lines:
        draw_text(buf, x, hy, line, head_scale, INK)
        hy += 7 * head_scale + 6
    # Body text, scale 2.
    max_body = w // char_width(2)
    blines = wrap(body, max_body)
    by = hy + 6
    for line in blines[:3]:
        draw_text(buf, x, by, line, 2, GREY)
        by += 7 * 2 + 5
    return by


def build():
    buf = new_image()
    # Outer frame.
    fill_rect(buf, 24, 24, WIDTH - 48, 3, INK)
    fill_rect(buf, 24, HEIGHT - 27, WIDTH - 48, 3, INK)
    fill_rect(buf, 24, 24, 3, HEIGHT - 48, INK)
    fill_rect(buf, WIDTH - 27, 24, 3, HEIGHT - 48, INK)

    # Masthead.
    draw_centered(buf, 40, "THE WORLD TODAY", 6, INK)
    draw_centered(buf, 96, "WORLD NEWS - WEDNESDAY, NOVEMBER 25, 2026", 2, GREY)
    hline(buf, 36, 128, WIDTH - 72, INK, 4)
    hline(buf, 36, 138, WIDTH - 72, INK, 1)

    # Lead story (topic 1): Strait of Hormuz, two tankers hit by mines.
    draw_text(buf, 36, 158, "TOP STORY - STRAIT OF HORMUZ", 2, RED)
    draw_text(buf, 36, 186, "STRAIT OF HORMUZ:", 4, INK)
    draw_text(buf, 36, 224, "TWO TANKERS HIT", 4, INK)
    draw_text(buf, 36, 262, "BY MINES, ON FIRE", 4, INK)
    draw_text(buf, 36, 306,
              "TWO TANKERS WERE STRUCK AND CAUGHT FIRE IN THE STRAIT.", 2, GREY)
    hline(buf, 36, 336, WIDTH - 72, INK, 2)

    # Grid: 2 columns x 4 rows, topics 2-9.
    col_w = 466
    col_x = (36, 522)
    row_y = (356, 506, 656, 806)
    stories = [
        ("2 - MIDDLE EAST", "HOUTHIS CLAIM REFINERY ATTACK",
         "THE GROUP SAID IT CARRIED OUT THE STRIKE. OFFICIALS HAVE NOT "
         "CONFIRMED THE CLAIM."),
        ("3 - MIDDLE EAST", "GAZA",
         "FIGHTING AND AID EFFORTS CONTINUED. TALKS ON A CEASEFIRE "
         "REMAIN IN FOCUS."),
        ("4 - EUROPE", "UKRAINE",
         "THE WAR CONTINUED ON MULTIPLE FRONTS. DIPLOMATIC EFFORTS "
         "WENT ON IN PARALLEL."),
        ("5 - TECH", "HUAWEI RULING",
         "A COURT RULED ON THE HUAWEI CASE. THE DECISION DRAWS "
         "WIDE ATTENTION."),
        ("6 - MARKETS", "GLOBAL MARKETS PLUNGE",
         "STOCKS FELL SHARPLY AROUND THE WORLD. INVESTORS MOVED "
         "TO SAFER ASSETS."),
        ("7 - SPACE", "SHENZHOU-24",
         "CHINA'S SHENZHOU-24 MISSION MADE HEADLINES. DETAILS OF "
         "THE FLIGHT WERE FOLLOWED CLOSELY."),
        ("8 - PACIFIC", "AUSTRALIA-SOLOMON ISLANDS PACT",
         "AUSTRALIA AND SOLOMON ISLANDS SIGNED A NEW AGREEMENT. "
         "THE PACT COVERS SECURITY COOPERATION."),
        ("9 - AMERICAS", "CARTAGENA HOSTAGE RESCUE",
         "HOSTAGES WERE FREED IN CARTAGENA. AUTHORITIES CONFIRMED "
         "THE RESCUE OPERATION."),
    ]
    for idx, (kicker, headline, body) in enumerate(stories):
        x = col_x[idx % 2]
        y = row_y[idx // 2]
        draw_block(buf, x, y, col_w, kicker, headline, body)
        if idx % 2 == 0:
            # Vertical divider between the two columns.
            fill_rect(buf, 508, y, 2, 128, GREY)

    # Footer.
    hline(buf, 36, 946, WIDTH - 72, INK, 2)
    draw_centered(buf, 962, "NINE STORIES ON ONE PAGE - NOVEMBER 25, 2026", 2, GREY)
    return buf


def png_chunk(kind, data):
    chunk = struct.pack(">I", len(data)) + kind + data
    crc = binascii.crc32(kind + data) & 0xFFFFFFFF
    return chunk + struct.pack(">I", crc)


def encode_png(buf):
    raw = bytearray()
    stride = WIDTH * 3
    for y in range(HEIGHT):
        raw.append(0)
        start = y * stride
        raw += buf[start:start + stride]
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += png_chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
