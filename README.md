# Aaron's tools

The GitHub user site at https://aaronlb912.github.io

This repo owns `/` and `/tools/...`. Home is a card per tool. Each card opens a page with an iframe of the live demo.

The apps stay in their own repos. Those still publish at `https://aaronlb912.github.io/<repo>/`. Do not put a folder named after a tool at the root of this repo. That would hide the real demo.

## Who it is for

Anyone who wants to click through the tools. Aaron, mostly.

## Run it locally

From this folder, on this Windows machine:

```bash
py -3 -m http.server 8080
```

`python` is not on PATH. Then open http://127.0.0.1:8080

## Add a tool (daily ships)

Do not scan old repos. When a new daily tool already has Pages loading, register it.

```bash
py -3 scripts/register_tool.py --repo the-repo --label "short label" --blurb "one sentence" --about "two sentences for the tool page" --demo https://aaronlb912.github.io/the-repo/
```

That writes `tools.json`, rebuilds the HTML, and puts a page at `/tools/the-repo/`. Then commit and push this repo so Pages updates.

Or, after this workflow is on GitHub:

```bash
gh workflow run register-tool.yml --repo Aaronlb912/aaronlb912.github.io -f repo=the-repo -f label="short label" -f blurb="one sentence" -f about="two sentences" -f demo=https://aaronlb912.github.io/the-repo/
```

The four daily-tool prompts tell the agent to do this when Pages is live.

## Still unfinished

- `who-to-call` and `minutes` have no Pages site yet. Do not add them until they do.
- Screenshots on tool pages go stale when a tool's UI changes.
