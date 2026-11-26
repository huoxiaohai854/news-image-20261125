# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/huoxiaohai854/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/huoxiaohai854/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A deterministic Python program that draws one newspaper-style front page summing up the world's news of Wednesday, 25 November 2026 — lead story on two tankers ablaze after mine strikes in the Strait of Hormuz, plus the Houthi refinery claim, Gaza, Ukraine, the Huawei verdict, tumbling markets, Shenzhou-24, the Australia–Solomon Islands pact and the Cartagena hostage rescue. No network at runtime; the news is embedded as static data, so two runs write byte-identical PNGs.

The program uses only the Python standard library (the grader runs `python:3.13-slim`, which ships no Pillow): a tiny raster canvas, a hand-written 5x7 bitmap font, and a zlib PNG encoder.

## Run it

```sh
python3 main.py
```

This writes `entry.png` (1024×1024, under 1 MiB) next to `main.py`, or into `$MAKEFUN_OUTPUT_DIR` when that is set, as the grader does.

---

<sub>Entered on [make.fun](https://make.fun/?ref=7gnjrf7y&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
