# Barrot A2A → OpenCode Task Bridge

> **Status: QUARANTINED / NOT ACTIVATED.** The 2026-11-20 main-branch deployment attempt failed at Cloudflare authentication (API error 10000 / token error 9109) before Worker deployment; the secret-upload step was skipped. No Worker deployment or secret rotation is verified. The consolidated integration keeps the deploy workflow manual-only, removes the A2A URL/secret from the default OpenCode configuration, and requires explicit `BARROT_A2A_AUTO_RUNNER=YES` before the local consumer can start. Do not enable the runner until OS sandboxing, environment/credential isolation, network-egress restrictions, per-task authorization, and least-privilege GitHub access are implemented and independently reviewed.


## Purpose

The Cloudflare Worker is a durable ingress and task-status gateway. It is not a second Barrot brain and does not call Groq to answer assignments.

The existing OpenCode environment runs the outbound runner in `scripts/barrot_a2a_runner.py`. The runner claims queued tasks over HTTPS and invokes `opencode run --agent barrot --format json` from the same host and OS account as the existing OpenCode shared service. It does not start a second OpenCode server and does not expose a local port to the internet.

## Flow

1. GPT Actions submits `POST /v1/tasks` with `X-Barrot-Auth`.
2. The Worker stores the task in the `BarrotTaskQueue` Durable Object and returns a stable `task_id`.
3. The outbound runner claims the task using `POST /v1/agent/claim`.
4. The runner invokes the existing OpenCode shared service through the OpenCode CLI, selecting the `barrot` agent.
5. The runner posts the execution result to `POST /v1/agent/tasks/{task_id}/complete`.
6. GPT Actions retrieves the task and result using `GET /v1/tasks/{task_id}`.

A2A JSON-RPC compatibility is retained at `POST /`: `message/send` queues work and `tasks/get` retrieves it. `GET /.well-known/agent-card.json` publishes the Agent Card. `GET /openapi.json` publishes the GPT Actions schema.

## Cloudflare configuration

`a2a/wrangler.toml` binds a SQLite-backed Durable Object named `BARROT_TASKS`. The deployment workflow is manual-only. It requires explicit `YES` for deployment and secret rotation, the exact current 40-character main SHA, and verification that main has not advanced. It uploads only `BRAIN_SHARED_SECRET` after the Worker script exists. Existing Cloudflare account/token and GitHub secret values must never be copied into source or logs.

The same `BRAIN_SHARED_SECRET` authenticates the OpenCode runner by default. A separate `BARROT_AGENT_SECRET` may be configured as a Cloudflare Worker secret for the runner; when present, it overrides the shared secret for agent-only claim/completion routes. Do not put either secret in repository files.

## Existing OpenCode host configuration

Run the queue consumer as the same OS user and from the repository checkout used by the existing OpenCode service. The `barrot` MCP server launches the outbound consumer only when `BARROT_A2A_AUTO_RUNNER=YES` is explicitly set and both the gateway URL and runner credential are present. The default OpenCode configuration intentionally provides neither the A2A URL nor runner secrets; no endpoint or credential is injected automatically. A file lock ensures only one consumer runs, even when multiple OpenCode sessions load the MCP server. The consumer logs to `~/.barrot/a2a-runner.log`.

Environment contract:

- `BARROT_A2A_AUTO_RUNNER` — must be set to `YES` as a separate explicit opt-in; absent by default.
- `BARROT_A2A_URL` — `https://barrot-a2a-worker.amazonprostarelite.workers.dev` after the Worker is deployed.
- `BARROT_AGENT_SECRET` — optional dedicated runner credential, supplied through the host's secret/environment manager.
- `BRAIN_SHARED_SECRET` — fallback runner credential when `BARROT_AGENT_SECRET` is not set.
- `BARROT_WORKDIR` — absolute path to the existing B-Agent checkout.
- `BARROT_OPENCODE_AGENT` — optional; defaults to `barrot`.
- `BARROT_TASK_TIMEOUT_SECONDS` — optional; defaults to 1800 seconds, maximum 1800.
- `BARROT_A2A_POLL_SECONDS` — optional; defaults to 5 seconds.

The runner is a queue consumer, not an HTTP server. It does not expose the host or OpenCode API publicly, and it does not start another OpenCode server. The existing OpenCode MCP lifecycle starts it; a singleton lock prevents duplicate consumers. For a manual diagnostic or one-task smoke test, use `python3 scripts/barrot_a2a_runner.py --once`. The runner's 3600-second task lease exceeds its 1800-second execution timeout; an abandoned lease is recoverable and claims are bounded to three attempts.

## Safety and execution semantics

- Every task receives a durable ID and is stored before acknowledgement.
- Submission is idempotent when a caller supplies the same `task_id`.
- The queue limits outstanding tasks to 100.
- A claim has a worker identity and lease. Only that worker may complete the task.
- Expired leases can be reclaimed, with a three-attempt ceiling.
- Task input and result sizes are bounded.
- The consolidated OpenCode configuration uses ask-before-action permissions; the runner remains disabled by default.
- The current runner still executes in the host environment and is not OS-sandboxed. Do not activate it until credentials are isolated and task-level actions are technically constrained.
- The task prompt requires inspection before modification and prohibits commit, push, merge, deployment, credential changes, and external side effects unless that specific action is explicitly authorized in the task.
- No live trading is enabled by this bridge.
- Model output is not proof. The runner returns raw execution evidence and exit status; ChatGPT must independently evaluate it.

## Verification

Worker tests:

```bash
cd a2a
node --test worker.test.js
```

Runner tests:

```bash
python -m pytest tests/test_barrot_a2a_runner.py -q
```

Live acceptance is separate from unit tests. It requires:
1. Successful Worker deployment to the intended Cloudflare account.
2. `GET /.well-known/agent-card.json` returns the Barrot V3 card.
3. Authenticated task submission returns a task ID and persists as `queued`.
4. The existing OpenCode host claims the task and executes it using agent `barrot`.
5. The task transitions to `completed` or `failed` with the actual process result and evidence.
6. GPT Actions can retrieve that exact task result.
7. Unauthorized submit, claim, and completion requests are rejected.

A passing unit test or a successful Cloudflare deployment alone does not establish end-to-end connectivity.
