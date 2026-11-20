import test from "node:test";
import assert from "node:assert/strict";
import worker, { BarrotTaskQueue } from "./worker.js";

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

test("Agent Card and OpenAPI are public metadata only", async () => {
  const env = {};
  const card = await worker.fetch(new Request("https://worker.test/.well-known/agent-card.json"), env);
  assert.equal(card.status, 200);
  assert.equal((await card.json()).version, "2.0.0");
  const schema = await worker.fetch(new Request("https://worker.test/openapi.json"), env);
  assert.equal(schema.status, 200);
  assert.ok((await schema.json()).paths["/v1/tasks"]);
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
