# Session note — 2026-11-19 — local fix-SHA hunt for a Chrome/V8 patch diff

Self-contained record. Written so a reader (human or model) can summarise it
without access to the conversation it came from.

## The question asked

> Find the fix SHA for a Chrome/V8 security fix using **local git history only —
> no search**. Run `git log --oneline -30`, list candidates, pick the one that
> brackets the fix, run `git show <SHA> --stat`, and proceed with the static /
> V8 / report analysis. If no SHA brackets it, name the 3 closest SHAs and why
> each fails.

Context: the Chrome reverse-engineering track needed a patch diff for one of
three verified CVEs (CVE-2020-6418, CVE-2024-2887, CVE-2023-7024). A patch diff
needs a commit SHA. Remote commit search had already failed: the Chromium
Gitiles endpoint ignores the `?q=` search parameter (two different queries
returned byte-identical responses), and the nearest pair of V8 release tags
(`8.0.426.15` vs `8.0.426.16`) diffed to 0 lines on both
`src/compiler/operation-typer.cc` and `src/compiler/typer.cc`.

## What was run

```
git log --oneline -30
git rev-list --all --count
git ls-tree -r --name-only HEAD | grep -E '^(v8|third_party/blink|...)'
git log --all --oneline -- v8 third_party/blink
git rev-list --all --objects | grep -cE '(^| )(v8/src|third_party/blink/renderer|third_party/webrtc/)'
git show <SHA> --stat    # on the 3 candidates
```

## The finding

The repository is **Barrot-Agent**, not a Chromium checkout.

- 25,022 commits, 162,532 objects in the full object database.
- **0 objects** matching `v8/src`, `third_party/blink/renderer`, or
  `third_party/webrtc/` — searched across all history, not just HEAD.
- No git submodules, no Chromium checkout anywhere on disk, no `.mojom` files.
- The 72 paths that looked Chromium-like are `content/*.md`, the repo's own
  content pipeline.

A fix SHA is a commit object in **Chromium's** object database. This clone does
not have that object database. No `git log` flag can produce an object that was
never fetched. This is not a search limitation; it is a different repository.

The three nearest-looking SHAs are all Barrot-Agent commits, and none contains a
line of V8 or Blink code.

## The 3 closest SHAs and why each fails

| SHA | What `git show --stat` shows | Why it fails |
|---|---|---|
| `9a8c3d7d0` | `CHROME_MASTERY_85.md`, 3 CVE JSON records, `tests/test_chrome_cves.py`, 584 insertions | CVE **metadata** only — advisory text, no engine source, no diff |
| `35862c8a1` | `REVERSE_ENGINEERED_BUGS.md` (421 lines), `sandbox/chrome/` exercises and fuzzer | The author's own C and Python models; no upstream Chromium commit |
| `1fc4f9310` | `network_guard.py`, `MODEL_REVERSE_ENGINEERING.md`, rotating XRP loop | Added the capability to fetch V8 source; the fetched files went to `/tmp` and were never committed |

## Three routes that would actually unblock it

| Option | Cost | Status |
|---|---|---|
| Paste one fix commit SHA | 30 seconds | Works now — the two revisions can be fetched at `<SHA>^` and `<SHA>` and diffed locally; both URLs are already on the guard's allowlist |
| Fetch GitHub's commit list for one file (`github.com/v8/v8/commits/main/src/compiler/typer.cc`) | one guarded GET, no new permission | works, but was excluded by the "no search" instruction |
| Shallow `git clone` of V8 (`--filter=blob:none`) | ~300-600 MB against 5.3 GB free | needs explicit approval, because `git clone` bypasses `network_guard.py` and breaks the single-egress rule |

No static/V8/report analysis was performed, because there was no diff to
analyse. Producing one anyway would have meant inventing the artefact the whole
track exists to verify.

## Secondary item: Polymarket multi-agent desk spec

A spec for a six-agent trading terminal (SCANNER → RUG CHECK → SIZER → EXECUTOR
→ LOGGER → EQUITY) was supplied, with a research → rules → backtest → execution
workflow. Two blockers were identified before any code:

- The network allowlist covers kaggle, coingecko, coinmarketcap, chromium,
  github, wikipedia. It does **not** cover `polymarket.com`, `gamma-api`, or
  `clob.polymarket.com`, so a live scanner cannot be built under current rules.
- `py-clob-client` requires authenticated network access and keys, which
  violates the read-only, no-secrets and single-guard rules.

Buildable immediately, paper-only on fixtures: research analyzer over a supplied
trade export, explicit signal rules, a backtester, six agents with structured
reason strings, and a dashboard. No live path and no keys.

The unverified "$68 → $750k" claim circulating with screenshots of this UI was
treated as illustration of the interface pattern only, not as evidence of
returns.

## Status

- Patch diff: still blocked, waiting on one SHA or one approval.
- Verified CVE citations: 3, hashed, in `sandbox/chrome/cves/`.
- Chrome mastery: 16.1 average across 7 sub-skills, 0 of 3 full REs.
- Paper trading only. Real XRP at risk: $0.
