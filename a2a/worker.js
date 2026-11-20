import { RIEMANN_RESEARCH_CORPUS } from "./riemann_research_corpus.js";

const MAX_REQUEST_BYTES = 64 * 1024;
const RATE_WINDOW_MS = 60_000;
const RATE_LIMIT = 30;
const clients = new Map();
const MAX_TASK_TEXT = 32 * 1024;
const MAX_RESULT_BYTES = 96 * 1024;
const MAX_OUTSTANDING_TASKS = 100;
const DEFAULT_LEASE_SECONDS = 3600;
const MAX_ATTEMPTS = 3;

const AGENT_CARD = {
  name: "Barrot V3",
  description: "Authenticated task gateway to the existing Barrot OpenCode runtime. Tasks are queued durably and executed by the connected Barrot worker.",
  url: "https://barrot-a2a-worker.amazonprostarelite.workers.dev/",
  version: "2.0.0",
  capabilities: {
    streaming: false,
    pushNotifications: false,
    stateTransitionHistory: false
  },
  defaultInputModes: ["text/plain", "application/json"],
  defaultOutputModes: ["text/plain", "application/json"],
  authentication: {
    schemes: ["custom-header"],
    credentials: "X-Barrot-Auth header, shared secret"
  },
  skills: [
    {
      id: "opencode-task-execution",
      name: "Existing OpenCode task execution",
      description: "Submit a task for execution by Barrot in its existing OpenCode environment. Returns a durable task ID; retrieve status and evidence with tasks/get.",
      tags: ["orchestration", "coding", "research", "execution"],
      examples: ["Inspect the current repository state and report verified blockers.", "Implement the approved task, run relevant tests, and return evidence."]
    },
    {
      id: "riemann-research",
      name: "Read-only Riemann research corpus",
      description: "Retrieve validated structured research metadata. Publications and computational evidence are never represented as mathematical proof.",
      tags: ["research", "mathematics", "number-theory", "riemann", "read-only"],
      examples: ["Retrieve the latest Riemann research corpus."]
    }
  ]
};

const OPENAPI = {
  openapi: "3.1.0",
  info: {
    title: "Barrot V3 Task Gateway",
    version: "2.0.0",
    description: "Durable task submission and result retrieval for the existing Barrot OpenCode runtime."
  },
  servers: [{ url: "https://barrot-a2a-worker.amazonprostarelite.workers.dev" }],
  security: [{ BarrotAuth: [] }],
  components: {
    securitySchemes: {
      BarrotAuth: { type: "apiKey", in: "header", name: "X-Barrot-Auth" }
    },
    schemas: {
      TaskSubmission: {
        type: "object",
        required: ["title", "instructions"],
        properties: {
          title: { type: "string", maxLength: 200 },
          instructions: { type: "string", maxLength: 32768 },
          context: { type: "object", additionalProperties: true },
          task_id: { type: "string" }
        }
      }
    }
  },
  paths: {
    "/v1/tasks": {
      post: {
        operationId: "submitBarrotTask",
        summary: "Submit a task to Barrot's existing OpenCode runtime",
        requestBody: {
          required: true,
          content: { "application/json": { schema: { $ref: "#/components/schemas/TaskSubmission" } } }
        },
        responses: {
          "202": { description: "Task durably queued; response includes task_id." },
          "400": { description: "Invalid task." },
          "401": { description: "Unauthorized." },
          "503": { description: "Durable task queue unavailable." }
        }
      }
    },
    "/v1/tasks/{task_id}": {
      get: {
        operationId: "getBarrotTask",
        summary: "Retrieve task status, result, and execution evidence",
        parameters: [{ name: "task_id", in: "path", required: true, schema: { type: "string" } }],
        responses: {
          "200": { description: "Task record." },
          "404": { description: "Task not found." },
          "401": { description: "Unauthorized." }
        }
      }
    }
  }
};

function json(payload, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...extraHeaders }
  });
}

function constantTimeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length || !a.length) return false;
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return mismatch === 0;
}

function clientAllowed(request) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const now = Date.now();
  const entry = clients.get(ip);
  if (clients.size >= 1024) {
    for (const [key, value] of clients) {
      if (now - value.started >= RATE_WINDOW_MS) clients.delete(key);
    }
  }
  if (!entry || now - entry.started >= RATE_WINDOW_MS) {
    clients.set(ip, { started: now, count: 1 });
    return true;
  }
  entry.count += 1;
  return entry.count <= RATE_LIMIT;
}

function authorized(request, secret) {
  return Boolean(secret) && constantTimeEqual(request.headers.get("x-barrot-auth") || "", secret);
}

async function readJson(request, maxBytes = MAX_REQUEST_BYTES) {
  const declared = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declared) && declared > maxBytes) throw new Error("REQUEST_TOO_LARGE");
  const raw = await request.text();
  if (new TextEncoder().encode(raw).byteLength > maxBytes) throw new Error("REQUEST_TOO_LARGE");
  try { return JSON.parse(raw); } catch { throw new Error("INVALID_JSON"); }
}

function queue(env) {
  if (!env.BARROT_TASKS) throw new Error("TASK_QUEUE_NOT_CONFIGURED");
  const id = env.BARROT_TASKS.idFromName("barrot-v3-primary");
  return env.BARROT_TASKS.get(id);
}

async function queueRequest(env, path, body) {
  const stub = queue(env);
  return stub.fetch("https://barrot-queue.internal" + path, {
    method: body === undefined ? "GET" : "POST",
    headers: { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body)
  });
}

function extractText(message) {
  if (!message || !Array.isArray(message.parts)) return "";
  return message.parts
    .filter(part => part && (part.type === "text" || part.kind === "text"))
    .map(part => typeof part.text === "string" ? part.text : "")
    .join("\n")
    .trim();
}

function jsonRpcError(id, code, message) {
  return json({ jsonrpc: "2.0", id, error: { code, message } });
}

function jsonRpcResult(id, result) {
  return json({ jsonrpc: "2.0", id, result });
}

async function handleJsonRpc(request, env) {
  if (!authorized(request, env.BRAIN_SHARED_SECRET)) {
    return jsonRpcError(null, -32001, "Unauthorized");
  }
  if (!clientAllowed(request)) return jsonRpcError(null, -32029, "Rate limit exceeded");
  let payload;
  try { payload = await readJson(request); }
  catch (error) {
    return jsonRpcError(null, error.message === "REQUEST_TOO_LARGE" ? -32600 : -32700,
      error.message === "REQUEST_TOO_LARGE" ? "Request too large" : "Invalid JSON");
  }
  const { id = null, method, params = {} } = payload || {};

  if (method === "message/send") {
    const instructions = extractText(params.message);
    if (!instructions || instructions.length > MAX_TASK_TEXT) {
      return jsonRpcError(id, -32602, "message.parts must contain 1-32768 characters of text");
    }
    try {
      const response = await queueRequest(env, "/submit", {
        title: typeof params.title === "string" ? params.title.slice(0, 200) : "A2A task",
        instructions,
        context: params.context && typeof params.context === "object" ? params.context : {}
      });
      const task = await response.json();
      if (!response.ok) return jsonRpcError(id, -32000, task.error || "Task submission failed");
      return jsonRpcResult(id, {
        id: task.task_id,
        status: { state: "submitted" },
        metadata: { queue_status: task.status, created_at: task.created_at }
      });
    } catch {
      return jsonRpcError(id, -32000, "Durable task queue unavailable");
    }
  }

  if (method === "tasks/get") {
    const taskId = params.id || params.task_id;
    if (typeof taskId !== "string" || !taskId) return jsonRpcError(id, -32602, "tasks/get requires params.id");
    try {
      const response = await queueRequest(env, "/get/" + encodeURIComponent(taskId));
      const task = await response.json();
      if (!response.ok) return jsonRpcError(id, -32004, task.error || "Task not found");
      return jsonRpcResult(id, {
        id: task.task_id,
        status: { state: ({ queued: "submitted", running: "working", completed: "completed", failed: "failed" })[task.status] || "unknown" },
        artifacts: task.result ? [{ name: "execution-result", parts: [{ type: "text", text: JSON.stringify(task.result) }] }] : [],
        metadata: { attempts: task.attempts, created_at: task.created_at, updated_at: task.updated_at, error: task.error || null }
      });
    } catch {
      return jsonRpcError(id, -32000, "Durable task queue unavailable");
    }
  }

  if (method === "research/riemann") {
    const requestedLimit = Number(params.limit || 25);
    const limit = Math.max(1, Math.min(Number.isFinite(requestedLimit) ? requestedLimit : 25, 100));
    const allowedClasses = new Set(RIEMANN_RESEARCH_CORPUS.evidence_policy.classes || []);
    let evidenceClasses = params.evidence_classes || [];
    if (!Array.isArray(evidenceClasses)) evidenceClasses = [evidenceClasses];
    evidenceClasses = evidenceClasses.filter(value => typeof value === "string" && allowedClasses.has(value));
    let records = RIEMANN_RESEARCH_CORPUS.records || [];
    if (evidenceClasses.length) records = records.filter(record => evidenceClasses.includes(record.evidence_class));
    const query = typeof params.query === "string" ? params.query.trim().toLowerCase() : "";
    if (query) records = records.filter(record =>
      [record.title, record.summary, ...(record.authors || []), record.source].join(" ").toLowerCase().includes(query)
    );
    records = records.slice(0, limit);
    const byEvidenceClass = {};
    for (const record of records) {
      const kind = record.evidence_class || "barrot_research_lead";
      byEvidenceClass[kind] = (byEvidenceClass[kind] || 0) + 1;
    }
    return jsonRpcResult(id, {
      capability: "riemann-research",
      read_only: true,
      domain: RIEMANN_RESEARCH_CORPUS.domain,
      evidence_policy: RIEMANN_RESEARCH_CORPUS.evidence_policy,
      query: query || null,
      evidence_classes: evidenceClasses,
      result_statistics: { returned_records: records.length, by_evidence_class: byEvidenceClass },
      grounding: {
        source: "Barrot read-only Riemann research corpus",
        mathematical_truth_assessment: false,
        rule: "Returned records are research metadata. Publication claims, computational evidence, and corpus summaries do not establish mathematical proof."
      },
      records
    });
  }

  return jsonRpcError(id, -32601, "Method not found: " + method);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET, POST, OPTIONS",
        "access-control-allow-headers": "content-type, x-barrot-auth"
      }});
    }
    if (request.method === "GET" && path === "/.well-known/agent-card.json") return json(AGENT_CARD);
    if (request.method === "GET" && path === "/openapi.json") return json(OPENAPI);

    if (path === "/" && request.method === "POST") return handleJsonRpc(request, env);

    if (path === "/v1/tasks" && request.method === "POST") {
      if (!authorized(request, env.BRAIN_SHARED_SECRET)) return json({ error: "unauthorized" }, 401);
      if (!clientAllowed(request)) return json({ error: "rate_limit_exceeded" }, 429);
      let body;
      try { body = await readJson(request); }
      catch (error) {
        return json({ error: error.message === "REQUEST_TOO_LARGE" ? "request_too_large" : "invalid_json" }, 400);
      }
      if (!body || typeof body.title !== "string" || !body.title.trim() ||
          typeof body.instructions !== "string" || !body.instructions.trim() ||
          body.title.length > 200 || body.instructions.length > MAX_TASK_TEXT) {
        return json({ error: "title and instructions are required and must be within size limits" }, 400);
      }
      try {
        const response = await queueRequest(env, "/submit", {
          task_id: body.task_id,
          title: body.title.trim(),
          instructions: body.instructions,
          context: body.context && typeof body.context === "object" && !Array.isArray(body.context) ? body.context : {}
        });
        return json(await response.json(), response.status === 200 ? 202 : response.status);
      } catch {
        return json({ error: "durable_task_queue_unavailable" }, 503);
      }
    }

    const taskMatch = path.match(/^\/v1\/tasks\/([A-Za-z0-9._:-]{8,100})$/);
    if (taskMatch && request.method === "GET") {
      if (!authorized(request, env.BRAIN_SHARED_SECRET)) return json({ error: "unauthorized" }, 401);
      try {
        const response = await queueRequest(env, "/get/" + encodeURIComponent(taskMatch[1]));
        return new Response(await response.text(), { status: response.status, headers: { "content-type": "application/json" } });
      } catch {
        return json({ error: "durable_task_queue_unavailable" }, 503);
      }
    }

    if (path === "/v1/agent/claim" && request.method === "POST") {
      const agentSecret = env.BARROT_AGENT_SECRET || env.BRAIN_SHARED_SECRET;
      if (!authorized(request, agentSecret)) return json({ error: "unauthorized" }, 401);
      let body;
      try { body = await readJson(request, 4096); } catch { return json({ error: "invalid_json" }, 400); }
      const workerId = typeof body.worker_id === "string" ? body.worker_id.slice(0, 128) : "";
      if (!workerId) return json({ error: "worker_id_required" }, 400);
      try {
        const response = await queueRequest(env, "/claim", {
          worker_id: workerId,
          lease_seconds: Math.max(60, Math.min(Number(body.lease_seconds) || DEFAULT_LEASE_SECONDS, 3600))
        });
        return new Response(await response.text(), { status: response.status, headers: { "content-type": "application/json" } });
      } catch {
        return json({ error: "durable_task_queue_unavailable" }, 503);
      }
    }

    const completeMatch = path.match(/^\/v1\/agent\/tasks\/([A-Za-z0-9._:-]{8,100})\/complete$/);
    if (completeMatch && request.method === "POST") {
      const agentSecret = env.BARROT_AGENT_SECRET || env.BRAIN_SHARED_SECRET;
      if (!authorized(request, agentSecret)) return json({ error: "unauthorized" }, 401);
      let body;
      try { body = await readJson(request, MAX_RESULT_BYTES + 4096); }
      catch (error) { return json({ error: error.message === "REQUEST_TOO_LARGE" ? "result_too_large" : "invalid_json" }, 400); }
      if (typeof body.worker_id !== "string" || !body.worker_id ||
          !body.result || typeof body.result !== "object") {
        return json({ error: "worker_id_and_result_required" }, 400);
      }
      try {
        const response = await queueRequest(env, "/complete/" + encodeURIComponent(completeMatch[1]), body);
        return new Response(await response.text(), { status: response.status, headers: { "content-type": "application/json" } });
      } catch {
        return json({ error: "durable_task_queue_unavailable" }, 503);
      }
    }

    return json({ error: "not_found" }, 404);
  }
};

export class BarrotTaskQueue {
  constructor(state) {
    this.state = state;
    this.storage = state.storage;
  }

  async fetch(request) {
    const url = new URL(request.url);
    try {
      if (url.pathname === "/submit" && request.method === "POST") return this.submit(await request.json());
      if (url.pathname === "/claim" && request.method === "POST") return this.claim(await request.json());
      if (url.pathname.startsWith("/get/") && request.method === "GET") {
        return this.get(decodeURIComponent(url.pathname.slice(5)));
      }
      if (url.pathname.startsWith("/complete/") && request.method === "POST") {
        return this.complete(decodeURIComponent(url.pathname.slice(10)), await request.json());
      }
      return json({ error: "not_found" }, 404);
    } catch (error) {
      return json({ error: "queue_operation_failed", detail: String(error?.message || error) }, 500);
    }
  }

  async submit(input) {
    const now = Date.now();
    const taskId = typeof input.task_id === "string" && /^[A-Za-z0-9._:-]{8,100}$/.test(input.task_id)
      ? input.task_id : crypto.randomUUID();
    return this.storage.transaction(async () => {
      const existing = await this.storage.get("task:" + taskId);
      if (existing) return json({ task_id: taskId, status: existing.status, created_at: existing.created_at, idempotent_replay: true });
      const entries = await this.storage.list({ prefix: "task:" });
      const cutoff = now - 30 * 24 * 60 * 60 * 1000;
      for (const [key, oldTask] of entries.entries()) {
        if ((oldTask.status === "completed" || oldTask.status === "failed") &&
            Date.parse(oldTask.updated_at || oldTask.created_at) < cutoff) {
          await this.storage.delete(key);
        }
      }
      const outstanding = [...entries.values()].filter(task => task.status === "queued" || task.status === "running").length;
      if (outstanding >= MAX_OUTSTANDING_TASKS) return json({ error: "queue_full" }, 429);
      const task = {
        task_id: taskId,
        title: String(input.title || "Barrot task").slice(0, 200),
        instructions: String(input.instructions || "").slice(0, MAX_TASK_TEXT),
        context: input.context && typeof input.context === "object" ? input.context : {},
        status: "queued",
        attempts: 0,
        max_attempts: MAX_ATTEMPTS,
        created_at: new Date(now).toISOString(),
        updated_at: new Date(now).toISOString(),
        lease_until: null,
        assigned_worker: null,
        result: null,
        error: null
      };
      await this.storage.put("task:" + taskId, task);
      return json({ task_id: taskId, status: task.status, created_at: task.created_at });
    });
  }

  async claim(input) {
    const now = Date.now();
    const workerId = String(input.worker_id || "").slice(0, 128);
    const leaseSeconds = Math.max(60, Math.min(Number(input.lease_seconds) || DEFAULT_LEASE_SECONDS, 3600));
    if (!workerId) return json({ error: "worker_id_required" }, 400);
    return this.storage.transaction(async () => {
      const entries = await this.storage.list({ prefix: "task:" });
      const tasks = [...entries.entries()].map(([key, value]) => ({ key, value }))
        .sort((a, b) => a.value.created_at.localeCompare(b.value.created_at));
      for (const entry of tasks) {
        const task = entry.value;
        const leaseExpired = task.status === "running" && Number(task.lease_until || 0) <= now;
        if (task.status !== "queued" && !leaseExpired) continue;
        if (task.attempts >= task.max_attempts) {
          task.status = "failed";
          task.error = "worker_lease_expired_max_attempts";
          task.updated_at = new Date(now).toISOString();
          await this.storage.put(entry.key, task);
          continue;
        }
        task.status = "running";
        task.attempts += 1;
        task.assigned_worker = workerId;
        task.lease_until = now + leaseSeconds * 1000;
        task.updated_at = new Date(now).toISOString();
        if (!task.started_at) task.started_at = task.updated_at;
        await this.storage.put(entry.key, task);
        return json({ task });
      }
      return json({ task: null });
    });
  }

  async get(taskId) {
    const task = await this.storage.get("task:" + taskId);
    return task ? json(task) : json({ error: "task_not_found" }, 404);
  }

  async complete(taskId, input) {
    const now = Date.now();
    return this.storage.transaction(async () => {
      const key = "task:" + taskId;
      const task = await this.storage.get(key);
      if (!task) return json({ error: "task_not_found" }, 404);
      if (task.status !== "running" || task.assigned_worker !== input.worker_id) {
        return json({ error: "task_lease_mismatch" }, 409);
      }
      task.result = input.result;
      task.status = input.success === false ? "failed" : "completed";
      task.error = input.success === false ? String(input.error || "execution_failed").slice(0, 1000) : null;
      task.completed_at = new Date(now).toISOString();
      task.updated_at = task.completed_at;
      task.lease_until = null;
      await this.storage.put(key, task);
      return json({ task_id: taskId, status: task.status, completed_at: task.completed_at });
    });
  }
}
