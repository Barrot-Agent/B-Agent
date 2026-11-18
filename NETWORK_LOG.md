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
