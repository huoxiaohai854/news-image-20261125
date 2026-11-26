# News Image — 25 November 2026 (clean rebuild)

A clean-room rebuild: a 1024x1024 newspaper front page summarising world
news for Wednesday, 25 November 2026. Written from scratch in this
directory only, using the Python standard library alone (no PIL, no
network, no clock, no randomness). The 5x7 bitmap font is embedded in
`main.py`; the PNG encoder is hand-written with `struct` + `zlib`.

## Run

```sh
python3 main.py
# writes entry.png to /output, or to $MAKEFUN_OUTPUT_DIR if set:
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

Two runs produce byte-identical output.

## The nine topics on the page

1. 头条：霍尔木兹海峡两艘油轮遭水雷袭击起火 — lead story:
   "Strait of Hormuz: Two Tankers Hit by Mines, on Fire"
2. 胡塞武装炼油厂袭击宣称 — "Houthis Claim Refinery Attack"
3. 加沙 — "Gaza"
4. 乌克兰 — "Ukraine"
5. 华为裁决 — "Huawei Ruling"
6. 全球市场大跌 — "Global Markets Plunge"
7. 神舟二十四号 — "Shenzhou-24"
8. 澳大利亚—所罗门群岛协议 — "Australia-Solomon Islands Pact"
9. 卡塔赫纳人质解救 — "Cartagena Hostage Rescue"

Layout: masthead + date line, lead story across the top, then the
remaining eight stories in a 2-column x 4-row grid, footer line.
