"""Build the hub HTML from tools.json. Does not look up other GitHub repos."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "tools.json"

RESERVED = {
    "css",
    "images",
    "tools",
    "docs",
    "scripts",
    "favicon",
    "index",
    "404",
    ".github",
}

ICONS = [
    # calendar, picture, columns, receipt, house
    '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="8" y="12" width="32" height="28" rx="2"/><path d="M8 20h32M16 8v8M32 8v8M18 28h4M26 28h4M18 34h12"/></svg>',
    '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="8" y="12" width="32" height="26" rx="2"/><path d="M8 32l9-9 7 7 5-5 11 11"/><circle cx="18" cy="20" r="2.5"/></svg>',
    '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="7" y="10" width="10" height="28" rx="1.5"/><rect x="19" y="10" width="10" height="28" rx="1.5"/><rect x="31" y="10" width="10" height="28" rx="1.5"/><path d="M10 16h4M22 16h4M34 16h4M10 22h4M22 22h4"/></svg>',
    '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 8h20v32l-4-2-4 2-4-2-4 2-4-2z"/><path d="M18 18h12M18 24h12M18 30h8"/></svg>',
    '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M8 38V20l16-10 16 10v18H8z"/><path d="M20 38V26h8v12"/></svg>',
]

COUNT_WORDS = [
    "Zero",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Eleven",
    "Twelve",
    "Thirteen",
    "Fourteen",
    "Fifteen",
    "Sixteen",
    "Seventeen",
    "Eighteen",
    "Nineteen",
    "Twenty",
]


def e(text: str) -> str:
    return html.escape(text, quote=True)


def load_tools() -> list[dict]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    tools = data["tools"]
    if not isinstance(tools, list) or not tools:
        raise SystemExit("tools.json has no tools")
    return tools


def slug_ok(repo: str) -> str:
    name = (repo or "").strip()
    if not name or name in RESERVED or "/" in name or "\\" in name or name.startswith("."):
        raise SystemExit(f"bad repo name: {repo}")
    if not all(ch.isalnum() or ch in "-._" for ch in name):
        raise SystemExit(f"bad repo name: {repo}")
    return name


def count_line(n: int) -> str:
    word = COUNT_WORDS[n] if n < len(COUNT_WORDS) else str(n)
    noun = "tool" if n == 1 else "tools"
    return f"{word} small {noun}."


def source_url(tool: dict) -> str:
    return tool.get("source") or f"https://github.com/Aaronlb912/{tool['repo']}"


def mini_nav(tools: list[dict], current: str) -> str:
    bits = []
    for tool in tools:
        repo = e(tool["repo"])
        if tool["repo"] == current:
            bits.append(f'<a href="/tools/{repo}/" aria-current="page">{repo}</a>')
        else:
            bits.append(f'<a href="/tools/{repo}/">{repo}</a>')
    return "\n        ".join(bits)


def extra_links(tool: dict) -> str:
    bits = []
    for link in tool.get("extra") or []:
        bits.append(
            f'<a class="quiet" href="{e(link["href"])}">{e(link["label"])}</a>'
        )
    return "\n        ".join(bits)


def facts_of(tool: dict) -> list[dict]:
    facts = tool.get("facts") or []
    if facts:
        return facts
    rows = []
    if tool.get("blurb"):
        rows.append({"label": "What you do", "text": tool["blurb"]})
    if tool.get("about"):
        rows.append({"label": "About", "text": tool["about"]})
    return rows


def facts_block(tool: dict) -> str:
    facts = facts_of(tool)
    if not facts:
        return ""
    rows = []
    for fact in facts:
        rows.append(
            f"""        <div>
          <dt>{e(fact["label"])}</dt>
          <dd>{e(fact["text"])}</dd>
        </div>"""
        )
    inner = "\n".join(rows)
    return f"""      <dl class="facts">
{inner}
      </dl>
"""


def steps_block(tool: dict) -> str:
    steps = tool.get("steps") or []
    if not steps:
        return ""
    items = "\n".join(f"          <li>{e(step)}</li>" for step in steps)
    return f"""      <section class="how">
        <h2>How to poke it</h2>
        <ol>
{items}
        </ol>
      </section>
"""


def shot_block(tool: dict) -> str:
    shots = tool.get("shots") or []
    if not shots:
        return ""
    look = e(tool.get("look") or "Stills")
    grid = " shots-2" if len(shots) > 1 else ""
    figures = []
    for shot in shots:
        figures.append(
            f"""        <figure class="shot">
          <img src="{e(shot["src"])}" alt="{e(shot.get("alt") or "")}">
          <figcaption>{e(shot.get("caption") or "")}</figcaption>
        </figure>"""
        )
    inner = "\n".join(figures)
    return f"""      <section class="stills">
        <h2 class="look">{look}</h2>
        <div class="shots{grid}">
{inner}
        </div>
      </section>
"""


def pager(tools: list[dict], index: int) -> str:
    prev_html = '<a href="/">All tools</a>'
    next_html = '<a href="/">All tools</a>'
    if index > 0:
        prev = tools[index - 1]["repo"]
        prev_html = f'<a href="/tools/{e(prev)}/">Back: {e(prev)}</a>'
    if index < len(tools) - 1:
        nxt = tools[index + 1]["repo"]
        next_html = f'<a href="/tools/{e(nxt)}/">Next: {e(nxt)}</a>'
    return f"""      <p class="pager">
        {prev_html}
        {next_html}
      </p>"""


def card(tool: dict, index: int) -> str:
    repo = e(tool["repo"])
    n = f"{index + 1:02d}"
    tone = index % 5
    icon = ICONS[tone]
    return f"""        <a class="tool tone-{tone}" href="/tools/{repo}/">
          <div class="mark" aria-hidden="true">
            {icon}
          </div>
          <div class="body">
            <p class="num">{n} / {e(tool["label"])}</p>
            <h2>{repo}</h2>
            <p class="blurb">{e(tool["blurb"])}</p>
            <p class="hint">{e(tool.get("hint") or "")}</p>
            <p class="tool-links"><span class="open">See the page</span></p>
          </div>
        </a>"""


def index_html(tools: list[dict]) -> str:
    n = len(tools)
    last = tools[-1]
    cards = "\n\n".join(card(t, i) for i, t in enumerate(tools))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Aaron's tools</title>
  <meta name="description" content="Small tools. Open a page, look around, try the live demo.">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/css/site.css">
</head>
<body>
  <a class="skip" href="#main">Skip to tools</a>
  <header class="site-header">
    <div class="wrap-wide">
      <a class="brand" href="/">Aaron's tools</a>
    </div>
  </header>

  <main id="main">
    <div class="wrap-wide">
      <div class="hero">
        <h1>{e(count_line(n))}<br>Click around.</h1>
        <p class="lede">Each card opens a page with a live demo in a box. The real app still lives in its own repo.</p>
        <p class="tour"><a href="/tools/{e(last["repo"])}/">Start with {e(last["label"])}.</a></p>
      </div>
    </div>

    <div class="wrap-wide">
      <div class="tools">
{cards}
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="wrap-wide">
      <p>A directory of tools. Not a portfolio, not a store.</p>
      <p>
        <a href="https://github.com/Aaronlb912">GitHub</a>
        ·
        <a href="https://www.aaronbryantdev.com/">Portfolio</a>
      </p>
    </div>
  </footer>
</body>
</html>
"""


def tool_page(tools: list[dict], index: int) -> str:
    tool = tools[index]
    repo = slug_ok(tool["repo"])
    n = f"{index + 1:02d}"
    tone = index % 5
    demo = tool.get("demo") or f"https://aaronlb912.github.io/{repo}/"
    iframe = tool.get("iframe") or demo
    launch = tool.get("launch") or "Launch the demo"
    extras = extra_links(tool)
    extra_html = ("\n        " + extras) if extras else ""
    blurb = tool.get("blurb") or tool.get("about") or ""
    try_lede = tool.get("try") or "Same page, sitting in a box."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(repo)} - Aaron's tools</title>
  <meta name="description" content="{e(blurb)}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/css/site.css">
</head>
<body class="page-tone-{tone}">
  <header class="site-header">
    <div class="wrap-wide">
      <a class="brand" href="/">Aaron's tools</a>
      <nav class="mini-nav" aria-label="Tools">
        {mini_nav(tools, repo)}
      </nav>
    </div>
  </header>

  <div class="banner">
    <div class="wrap-wide">
      <p class="num">{n} / {e(tool["label"])}</p>
      <h1>{e(repo)}</h1>
      <p>{e(blurb)}</p>
      <p class="tool-links">
        <a class="open" href="{e(demo)}">{e(launch)}</a>{extra_html}
        <a class="quiet" href="{e(source_url(tool))}">Source</a>
      </p>
    </div>
  </div>

  <main>
    <div class="wrap">
{facts_block(tool)}
{steps_block(tool)}
    </div>
    <div class="wrap-wide">
      <section class="try">
        <h2>Live demo</h2>
        <p class="lede">{e(try_lede)}</p>
        <div class="frame-wrap">
          <iframe title="Live {e(repo)} demo" src="{e(iframe)}" loading="lazy"></iframe>
        </div>
      </section>
{shot_block(tool)}
{pager(tools, index)}
    </div>
  </main>
</body>
</html>
"""


def build() -> None:
    tools = load_tools()
    for tool in tools:
        slug_ok(tool["repo"])
    (ROOT / "index.html").write_text(index_html(tools), encoding="utf-8", newline="\n")
    for i, tool in enumerate(tools):
        folder = ROOT / "tools" / tool["repo"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(tool_page(tools, i), encoding="utf-8", newline="\n")
    print(f"built {len(tools)} tools")


if __name__ == "__main__":
    build()
