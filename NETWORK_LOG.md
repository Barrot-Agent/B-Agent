# NETWORK LOG

Append-only. Every attempt is recorded, including blocked ones. No secret is
ever written here: only the host, the status, the byte count, and the purpose.

| time (UTC) | method | host | status | bytes | verdict | purpose / reason |
|---|---|---|---|---|---|---|
| 2026-11-18T19:36:44Z | POST | api.coingecko.com | - | 0 | BLOCKED | method not GET: post test |
| 2026-11-18T19:36:44Z | GET | api.coingecko.com | - | 0 | ABORT | LIVE KEY DETECTED — ABORT: LUNAROUTE_API_KEY |
| 2026-11-18T19:36:55Z | GET | www.kaggle.com | 200 | 4208 | ALLOW | kaggle models list (5.31s) |
| 2026-11-18T19:36:58Z | GET | api.coingecko.com | 200 | 570 | ALLOW | coingecko spot prices (0.34s) |
| 2026-11-18T19:37:05Z | GET | chromium.googlesource.com | 200 | 8430 | ALLOW | chromium src log (5.08s) |
| 2026-11-18T19:38:00Z | GET | api.coingecko.com | 200 | 5654 | ALLOW | coingecko markets (5.64s) |
| 2026-11-18T19:38:03Z | GET | api.coingecko.com | 200 | 3742 | ALLOW | coingecko global (0.37s) |
| 2026-11-18T19:42:29Z | GET | chromium.googlesource.com | 503 | 0 | HTTP_ERROR | chromium commit diff probe: Service Unavailable |
| 2026-11-18T19:43:00Z | GET | chromium.googlesource.com | - | 0 | ERROR | chromium diff ^!: TimeoutError |
| 2026-11-18T19:43:13Z | GET | chromium.googlesource.com | - | 0 | ERROR | chromium log sha: TimeoutError |
| 2026-11-18T19:50:09Z | POST | api.coingecko.com | - | 0 | BLOCKED | method not GET: post test |
| 2026-11-18T19:50:09Z | GET | api.coingecko.com | - | 0 | ABORT | LIVE KEY DETECTED — ABORT: LUNAROUTE_API_KEY |
| 2026-11-19T06:08:22Z | GET | raw.githubusercontent.com | 200 | 15910 | ALLOW | cvelistV5 verify CVE-2020-6418 (0.41s) |
| 2026-11-19T06:08:25Z | GET | raw.githubusercontent.com | 200 | 8121 | ALLOW | cvelistV5 verify CVE-2024-2887 (0.33s) |
| 2026-11-19T06:08:27Z | GET | raw.githubusercontent.com | 200 | 8200 | ALLOW | cvelistV5 verify CVE-2023-7024 (0.36s) |
| 2026-11-19T06:09:07Z | GET | chromium.googlesource.com | 200 | 10832 | ALLOW | chromium gitiles search (11.98s) |
| 2026-11-19T06:09:16Z | GET | chromium.googlesource.com | 200 | 10832 | ALLOW | chromium gitiles search 2 (6.45s) |
| 2026-11-19T06:09:35Z | GET | raw.githubusercontent.com | 404 | 0 | HTTP_ERROR | chromium file v8/src/compiler/operation-typer.cc @ 80.0.3987.121: Not Found |
| 2026-11-19T06:09:43Z | GET | raw.githubusercontent.com | 404 | 0 | HTTP_ERROR | chromium file v8/src/compiler/operation-typer.cc @ 80.0.3987.122: Not Found |
| 2026-11-19T06:09:57Z | GET | raw.githubusercontent.com | 404 | 0 | HTTP_ERROR | chromium probe main path: Not Found |
| 2026-11-19T06:09:59Z | GET | raw.githubusercontent.com | 404 | 0 | HTTP_ERROR | chromium probe refs/tags: Not Found |
| 2026-11-19T06:10:18Z | GET | raw.githubusercontent.com | 200 | 48421 | ALLOW | v8 mirror probe v8 main (5.49s) |
| 2026-11-19T06:10:21Z | GET | raw.githubusercontent.com | 200 | 770 | ALLOW | v8 mirror probe v8 version (0.33s) |
| 2026-11-19T06:10:35Z | GET | raw.githubusercontent.com | 200 | 45144 | ALLOW | v8 src/compiler/operation-typer.cc @ 8.0.426.15 (0.35s) |
| 2026-11-19T06:10:43Z | GET | raw.githubusercontent.com | 200 | 45144 | ALLOW | v8 src/compiler/operation-typer.cc @ 8.0.426.16 (5.42s) |
| 2026-11-19T06:11:00Z | GET | raw.githubusercontent.com | 200 | 76926 | ALLOW | v8 typer.cc @ 8.0.426.15 (0.42s) |
| 2026-11-19T06:11:03Z | GET | raw.githubusercontent.com | 200 | 76926 | ALLOW | v8 typer.cc @ 8.0.426.16 (0.42s) |
| 2026-11-19T06:11:42Z | GET | raw.githubusercontent.com | 200 | 15910 | ALLOW | cvelistV5 persist CVE-2020-6418 (0.22s) |
| 2026-11-19T06:11:44Z | GET | raw.githubusercontent.com | 200 | 8121 | ALLOW | cvelistV5 persist CVE-2024-2887 (0.23s) |
| 2026-11-19T06:11:47Z | GET | raw.githubusercontent.com | 200 | 8200 | ALLOW | cvelistV5 persist CVE-2023-7024 (0.20s) |
| 2026-11-19T06:14:26Z | GET | raw.githubusercontent.com | 200 | 71105 | ALLOW | chromium mirror probe blink mojom (5.50s) |
| 2026-11-19T06:14:29Z | GET | raw.githubusercontent.com | 200 | 146571 | ALLOW | chromium mirror probe blink cpp (0.48s) |
| 2026-11-19T19:04:24Z | GET | raw.githubusercontent.com | 200 | 4990 | ALLOW | verify session note is publicly readable (0.35s) |
