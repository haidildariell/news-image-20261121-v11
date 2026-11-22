# Saturday 21 November 2026 — The Day in World News

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/haidildariell/news-image-20261121-v11/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/haidildariell/news-image-20261121-v11/reward.svg)](https://make.fun/bounty/news-image-20261121)

Bounty: https://make.fun/bounty/news-image-20261121

One page that sums up Saturday 21 November 2026 in world news: a warm
broadsheet front page, 1024×1024, carrying 35 stories from 7 regions.

## What is on the page

- **Masthead** — "THE DAY IN WORLD NEWS", the giant date line, and the
  count line: 35 stories · 7 regions · one page.
- **Big-numbers strip** — Day 13 of COP31, 5 missiles down over Riyadh
  and Jizan, the 6.7 Junín quake, 146 people safe in Davao, bitcoin at
  $58,983, and Rahul's 124\*.
- **13 lead cards**, each with a banner that states the core fact in one
  big line ("COP31: OVERTIME", "PERU: QUAKE 6.7", "DAVAO: 146 SAFE"),
  a source chip, a status chip (CONFIRMED / OFFICIAL / REPORTED), a
  serif headline and a two-line brief with a bold place lead-in. The
  story set is the consensus of the day's coverage: COP31 running into
  overtime in Antalya, the five Houthi missiles, the Peru quake, Kyiv,
  the Hormuz drone claim, Iran's uranium stock, Trump's data-centre tax
  vow, the China–Japan Taiwan exchange, the Davao emergency landing,
  Canberra's AI talks, bitcoin, Russell's P1 and Rahul's century.
- **WHERE IT HAPPENED** — a pin map with the 13 lead stories plotted by
  number.
- **ALSO ON SATURDAY** — 22 numbered one-liners in two columns, each
  with a bold place lead-in and its wire source.
- **DATE CHECK footer** — every story on the page happened on Saturday
  21 November 2026. Friday's news (Wall Street's fall into correction,
  the barrage on Kyiv's bridges, the missile in Poland, the UK–EU deal,
  Cyclone Akvan's landfall) is named and deliberately left out, as are
  items not confirmed when the page was drawn.

## How it is built

- `stories_20261121.json` — the story data (cards, digest, numbers
  strip, date check).
- `build_image.py` — the renderer (Python + PIL). It draws the whole
  page from the JSON and writes `entry.png`. Rendering is
  deterministic: the same JSON and fonts produce byte-identical PNGs.
- `entry.png` — the pre-rendered front page (1024×1024, under 1 MiB).
- `main.py` — the harness entrypoint. It is stdlib-only on purpose:
  the sandbox has no PIL, so it simply copies the pre-rendered
  `entry.png` to `/output/entry.png`.
- `SOURCES.md` — the wire source behind every story on the page.

## License

MIT — see `LICENSE`.
