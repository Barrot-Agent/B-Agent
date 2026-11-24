import test from "node:test";
import assert from "node:assert/strict";
import worker, { BarrotTaskQueue } from "./worker.js";
import { createHash } from "node:crypto";

class FakeStorage {
  constructor() { this.values = new Map(); }
  async get(key) { return this.values.get(key); }
  async put(key, value) { this.values.set(key, structuredClone(value)); }
  async list({ prefix = "" } = {}) {
    return new Map([...this.values.entries()]
      .filter(([key]) => key.startsWith(prefix))
      .map(([key, value]) => [key, structuredClone(value)]));
  }
  async transaction(callback) { return callback(this); }
}

function makeQueue() {
  const storage = new FakeStorage();
  return { queue: new BarrotTaskQueue({ storage }), storage };
}

async function jsonRequest(queue, path, body, method = "POST") {
  return queue.fetch(new Request("https://queue.test" + path, {
    method,
    headers: { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  }));
}

test("task submission is durable and idempotent", async () => {
  const { queue, storage } = makeQueue();
  const body = { task_id: "task-12345678", title: "Build", instructions: "Implement bridge." };
  const first = await (await jsonRequest(queue, "/submit", body)).json();
  const replay = await (await jsonRequest(queue, "/submit", body)).json();
  assert.equal(first.status, "queued");
  assert.equal(replay.idempotent_replay, true);
  assert.equal((await storage.get("task:task-12345678")).instructions, "Implement bridge.");
});

test("only one worker claims a queued task and the lease owner completes it", async () => {
  const { queue } = makeQueue();
  await jsonRequest(queue, "/submit", {
    task_id: "task-12345678", title: "Build", instructions: "Implement bridge."
  });
  const claimed = await (await jsonRequest(queue, "/claim", { worker_id: "worker-a" })).json();
  assert.equal(claimed.task.status, "running");
  assert.equal(claimed.task.assigned_worker, "worker-a");
  const empty = await (await jsonRequest(queue, "/claim", { worker_id: "worker-b" })).json();
  assert.equal(empty.task, null);
  const denied = await jsonRequest(queue, "/complete/task-12345678", {
    worker_id: "worker-b", success: true, result: { output: "wrong worker" }
  });
  assert.equal(denied.status, 409);
  const completed = await (await jsonRequest(queue, "/complete/task-12345678", {
    worker_id: "worker-a", success: true, result: { output: "verified" }
  })).json();
  assert.equal(completed.status, "completed");
  const stored = await (await jsonRequest(queue, "/get/task-12345678", undefined, "GET")).json();
  assert.equal(stored.result.output, "verified");
});

test("expired lease is reclaimable and attempts are bounded", async () => {
  const { queue, storage } = makeQueue();
  await jsonRequest(queue, "/submit", {
    task_id: "task-12345678", title: "Build", instructions: "Implement bridge."
  });
  await jsonRequest(queue, "/claim", { worker_id: "worker-a", lease_seconds: 60 });
  const task = await storage.get("task:task-12345678");
  task.lease_until = 0;
  task.attempts = 2;
  await storage.put("task:task-12345678", task);
  const reclaimed = await (await jsonRequest(queue, "/claim", { worker_id: "worker-b" })).json();
  assert.equal(reclaimed.task.assigned_worker, "worker-b");
  assert.equal(reclaimed.task.attempts, 3);
  const stored = await storage.get("task:task-12345678");
  stored.lease_until = 0;
  await storage.put("task:task-12345678", stored);
  await jsonRequest(queue, "/claim", { worker_id: "worker-c" });
  const failed = await storage.get("task:task-12345678");
  assert.equal(failed.status, "failed");
  assert.equal(failed.error, "worker_lease_expired_max_attempts");
});

test("HTTP task gateway authenticates submit and returns task status", async () => {
  const { queue } = makeQueue();
  const namespace = {
    idFromName: () => "primary",
    get: () => ({ fetch: (input, init) => queue.fetch(new Request(input, init)) }),
  };
  const env = { BRAIN_SHARED_SECRET: "shared-test-secret", BARROT_TASKS: namespace };
  const denied = await worker.fetch(new Request("https://worker.test/v1/tasks", {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ title: "Denied", instructions: "No auth" }),
  }), env);
  assert.equal(denied.status, 401);

  const submitted = await worker.fetch(new Request("https://worker.test/v1/tasks", {
    method: "POST",
    headers: { "content-type": "application/json", "X-Barrot-Auth": "shared-test-secret" },
    body: JSON.stringify({ title: "Build", instructions: "Run the task." }),
  }), env);
  assert.equal(submitted.status, 202);
  const task = await submitted.json();
  assert.ok(task.task_id);

  const status = await worker.fetch(new Request(
    "https://worker.test/v1/tasks/" + task.task_id,
    { headers: { "X-Barrot-Auth": "shared-test-secret" } },
  ), env);
  assert.equal(status.status, 200);
  assert.equal((await status.json()).status, "queued");
});

test("transmutation packets preserve source lineage and reject altered originals", async () => {
  const { queue } = makeQueue();
  const namespace = {
    idFromName: () => "primary",
    get: () => ({ fetch: (input, init) => queue.fetch(new Request(input, init)) }),
  };
  const env = { BRAIN_SHARED_SECRET: "gateway-secret", BARROT_TASKS: namespace };
  const original = "Inspect the existing Barrot/OpenCode transmutation path.";
  const packet = {
    protocol_version: "barrot.chatgpt.transmutation.v1",
    packet_id: "packet-0000001",
    parent_packet_id: null,
    sender: "chatgpt",
    recipient: "barrot",
    round: 0,
    phase: "interpret",
    requested_action: "analyze",
    original_request: original,
    original_request_sha256: createHash("sha256").update(original, "utf8").digest("hex"),
    intent: "Map the existing execution and evidence flow.",
    invariants: ["Preserve the original request.", "Use the existing MMI evidence path."],
    constraints: ["Read-only inspection."],
    source_refs: [
      { ref: "BARROT_SYNC.md@main", source_kind: "governing", relationship: "governs" },
      { ref: "Barrot-Agent/B-Agent@main", source_kind: "repository", relationship: "implements" },
    ],
    evidence_refs: ["github:main:7d7aba841cb849e461376a8fcdd4cc4fa10c9af6"],
    acceptance_criteria: ["Return exact paths and evidence."],
    stop_conditions: ["Stop if the source cannot be verified."],
    budget: { max_rounds: 4, max_execution_seconds: 600 },
  };
  const submitted = await worker.fetch(new Request("https://worker.test/v1/tasks", {
    method: "POST",
    headers: { "content-type": "application/json", "X-Barrot-Auth": "gateway-secret" },
    body: JSON.stringify({
      title: "Transmutation packet",
      instructions: "Analyze the supplied packet.",
      context: { transmutation: packet },
    }),
  }), env);
  assert.equal(submitted.status, 202);
  const accepted = await submitted.json();
  const stored = await (await queue.fetch(new Request(
    "https://queue.test/get/" + accepted.task_id,
    { method: "GET" },
  ))).json();
  assert.deepEqual(stored.context.transmutation, packet);

  const tampered = { ...packet, original_request: "A changed original request." };
  const rejected = await worker.fetch(new Request("https://worker.test/v1/tasks", {
    method: "POST",
    headers: { "content-type": "application/json", "X-Barrot-Auth": "gateway-secret" },
    body: JSON.stringify({
      title: "Tampered packet",
      instructions: "Analyze.",
      context: { transmutation: tampered },
    }),
  }), env);
  assert.equal(rejected.status, 400);
  assert.equal((await rejected.json()).error, "original_request_hash_mismatch");
});

test("Agent Card and OpenAPI are public metadata only", async () => {
  const env = {};
  const card = await worker.fetch(new Request("https://worker.test/.well-known/agent-card.json"), env);
  assert.equal(card.status, 200);
  assert.equal((await card.json()).version, "2.0.0");
  const schema = await worker.fetch(new Request("https://worker.test/openapi.json"), env);
  assert.equal(schema.status, 200);
  assert.ok((await schema.json()).paths["/v1/tasks"]);
});



test("gateway and agent routes require separate credentials", async () => {
  const { queue } = makeQueue();
  const namespace = {
    idFromName: () => "primary",
    get: () => ({ fetch: (input, init) => queue.fetch(new Request(input, init)) }),
  };
  const env = {
    BRAIN_SHARED_SECRET: "gateway-only-secret",
    BARROT_AGENT_SECRET: "agent-only-secret",
    BARROT_TASKS: namespace,
  };
  const submitted = await worker.fetch(new Request("https://worker.test/v1/tasks", {
    method: "POST",
    headers: { "content-type": "application/json", "X-Barrot-Auth": "gateway-only-secret" },
    body: JSON.stringify({ title: "Separate auth", instructions: "Verify route separation." }),
  }), env);
  assert.equal(submitted.status, 202);
  const task = await submitted.json();

  const gatewayCannotClaim = await worker.fetch(new Request("https://worker.test/v1/agent/claim", {
    method: "POST",
    headers: { "content-type": "application/json", "X-Barrot-Auth": "gateway-only-secret" },
    body: JSON.stringify({ worker_id: "worker-a" }),
  }), env);
  assert.equal(gatewayCannotClaim.status, 401);

  const claimed = await worker.fetch(new Request("https://worker.test/v1/agent/claim", {
    method: "POST",
    headers: { "content-type": "application/json", "X-Barrot-Auth": "agent-only-secret" },
    body: JSON.stringify({ worker_id: "worker-a" }),
  }), env);
  assert.equal(claimed.status, 200);
  assert.equal((await claimed.json()).task.task_id, task.task_id);

  const gatewayCannotComplete = await worker.fetch(new Request(
    "https://worker.test/v1/agent/tasks/" + task.task_id + "/complete", {
      method: "POST",
      headers: { "content-type": "application/json", "X-Barrot-Auth": "gateway-only-secret" },
      body: JSON.stringify({ worker_id: "worker-a", success: true, result: { output: "forged" } }),
    }), env);
  assert.equal(gatewayCannotComplete.status, 401);

  const completed = await worker.fetch(new Request(
    "https://worker.test/v1/agent/tasks/" + task.task_id + "/complete", {
      method: "POST",
      headers: { "content-type": "application/json", "X-Barrot-Auth": "agent-only-secret" },
      body: JSON.stringify({ worker_id: "worker-a", success: true, result: { output: "verified" } }),
    }), env);
  assert.equal(completed.status, 200);
  assert.equal((await completed.json()).status, "completed");
});

test("agent routes fail closed when the dedicated agent secret is absent", async () => {
  const { queue } = makeQueue();
  const namespace = {
    idFromName: () => "primary",
    get: () => ({ fetch: (input, init) => queue.fetch(new Request(input, init)) }),
  };
  const env = { BRAIN_SHARED_SECRET: "gateway-only-secret", BARROT_TASKS: namespace };
  const response = await worker.fetch(new Request("https://worker.test/v1/agent/claim", {
    method: "POST",
    headers: { "content-type": "application/json", "X-Barrot-Auth": "gateway-only-secret" },
    body: JSON.stringify({ worker_id: "worker-a" }),
  }), env);
  assert.equal(response.status, 401);
});

test("task submission enforces the per-client rate limit", async () => {
  const { queue } = makeQueue();
  const namespace = {
    idFromName: () => "primary",
    get: () => ({ fetch: (input, init) => queue.fetch(new Request(input, init)) }),
  };
  const env = { BRAIN_SHARED_SECRET: "rate-limit-secret", BARROT_TASKS: namespace };
  const statuses = [];
  for (let index = 0; index < 31; index++) {
    const response = await worker.fetch(new Request("https://worker.test/v1/tasks", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "X-Barrot-Auth": "rate-limit-secret",
        "CF-Connecting-IP": "198.51.100.77",
      },
      body: JSON.stringify({ title: "Task " + index, instructions: "Run task " + index }),
    }), env);
    statuses.push(response.status);
  }
  assert.equal(statuses.filter(status => status === 202).length, 30);
  assert.equal(statuses[30], 429);
});
