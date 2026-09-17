"""Add or update one tool in tools.json, then rebuild the hub.

Does not scan GitHub. Call this when a daily tool's Pages URL already loads.
"""

from __future__ import annotations

import argparse
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

from build_hub import CATALOG, ROOT, build, slug_ok

DEFAULT_PAGES = "https://aaronlb912.github.io/{repo}/"


def pages_ok(url: str) -> None:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "aaron-tools-hub"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            code = res.getcode()
    except urllib.error.HTTPError as err:
        raise SystemExit(f"Pages is not live yet ({err.code}): {url}") from err
    except urllib.error.URLError as err:
        raise SystemExit(f"could not reach Pages: {url} ({err.reason})") from err
    if code >= 400:
        raise SystemExit(f"Pages is not live yet ({code}): {url}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--blurb", required=True)
    parser.add_argument("--about", required=True)
    parser.add_argument("--hint", default="")
    parser.add_argument("--demo", default="")
    parser.add_argument("--iframe", default="")
    parser.add_argument("--look", default="Look")
    parser.add_argument("--try", dest="try_lede", default="Same page, sitting in a box.")
    parser.add_argument("--launch", default="Launch the demo")
    parser.add_argument("--extra", default="")
    parser.add_argument("--extra-label", default="")
    parser.add_argument("--shot", default="")
    parser.add_argument("--skip-check", action="store_true")
    args = parser.parse_args()

    repo = slug_ok(args.repo)
    demo = args.demo.strip() or DEFAULT_PAGES.format(repo=repo)
    iframe = args.iframe.strip() or demo

    if not args.skip_check:
        pages_ok(demo)

    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    tools = data["tools"]
    entry = None
    for item in tools:
        if item.get("repo") == repo:
            entry = item
            break
    if entry is None:
        entry = {"repo": repo}
        tools.append(entry)

    entry["label"] = args.label.strip()
    entry["blurb"] = args.blurb.strip()
    entry["about"] = args.about.strip()
    entry["hint"] = args.hint.strip()
    entry["demo"] = demo
    entry["iframe"] = iframe
    entry["look"] = args.look.strip() or "Look"
    entry["try"] = args.try_lede.strip()
    entry["launch"] = args.launch.strip() or "Launch the demo"

    extra_href = args.extra.strip()
    extra_label = args.extra_label.strip()
    if extra_href and extra_label:
        entry["extra"] = [{"href": extra_href, "label": extra_label}]
    elif extra_href or extra_label:
        raise SystemExit("need both --extra and --extra-label")

    shot_src = args.shot.strip()
    if shot_src:
        src = Path(shot_src)
        if not src.is_file():
            raise SystemExit(f"shot not found: {src}")
        dest = ROOT / "images" / f"{repo}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        entry["shots"] = [
            {
                "src": f"/images/{repo}.png",
                "alt": args.label.strip(),
                "caption": args.blurb.strip(),
            }
        ]
    elif "shots" not in entry:
        entry["shots"] = []

    CATALOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    build()


if __name__ == "__main__":
    main()
