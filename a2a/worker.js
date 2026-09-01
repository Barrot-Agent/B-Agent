
const MAX_REQUEST_BYTES = 64 * 1024;
const RATE_WINDOW_MS = 60_000;
const RATE_LIMIT = 30;
const clients = new Map();

function clientAllowed(request) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const now = Date.now();
  const entry = clients.get(ip);

  if (!entry || now - entry.started >= RATE_WINDOW_MS) {
    clients.set(ip, { started: now, count: 1 });
    return true;
  }

  entry.count += 1;
  return entry.count <= RATE_LIMIT;
}

async function fetchWithRetry(url, options, attempts = 3) {
  let lastError;

  for (let attempt = 0; attempt < attempts; attempt++) {
    try {
      const response = await fetch(url, options);
      if (response.ok || (response.status >= 400 &&
          response.status < 500 && response.status !== 429)) {
        return response;
      }
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }

    if (attempt < attempts - 1) {
      const delay = 250 * (2 ** attempt) + Math.floor(Math.random() * 150);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError || new Error("Upstream request failed");
}

// Barrot-Ω A2A (Agent-to-Agent) Worker
// Scoped v1 MVP of the A2A protocol (spec v1.0.1):
//   - Agent Card at /.well-known/agent-card.json
//   - JSON-RPC 2.0 endpoint at / for message/send
//   - Shared-secret auth via X-Barrot-Auth header
// Deliberately out of scope for v1 (see project memory):
//   OAuth2/JWT auth, message/stream (SSE), persistent task store
//   (tasks/get below is an intentional stub, not a bug).

const AGENT_CARD = {
  name: "Barrot-\u03a9",
  description: "Autonomous XRP/BTC signal research agent. Real Groq-backed inference, no owned compute.",
  url: "https://barrot-a2a.amazonprostarelite.workers.dev/",
  version: "1.0.0",
  capabilities: {
    streaming: false,
    pushNotifications: false,
    stateTransitionHistory: false
  },
  defaultInputModes: ["text/plain"],
  defaultOutputModes: ["text/plain"],
  authentication: {
    schemes: ["custom-header"],
    credentials: "X-Barrot-Auth header, shared secret"
  },
  skills: [
    {
      id: "riemann-research",
      description: "Retrieve validated structured research metadata. Publications and computational evidence are never represented as mathematical proof.",
      tags: ["research", "mathematics", "number-theory", "riemann", "read-only"],
    },

    {
      id: "general-query",
      name: "General grounded query",
      description: "Ask Barrot a question; answered via Groq openai/gpt-oss-120b.",
      tags: ["research", "qa"],
      examples: ["What is Barrot's current signal accuracy?"]
    }
  ]
};

function jsonRpcError(id, code, message) {
  return new Response(JSON.stringify({ jsonrpc: "2.0", id, error: { code, message } }), {
    status: 200,
    headers: { "content-type": "application/json" }
  });
}

function jsonRpcResult(id, result) {
  return new Response(JSON.stringify({ jsonrpc: "2.0", id, result }), {
    status: 200,
    headers: { "content-type": "application/json" }
  });
}

async function callGroq(env, text) {
  const body = {
    model: "openai/gpt-oss-120b",
    messages: [
      { role: "system", content: "You are Barrot-\u03a9, answering a request from another agent via the A2A protocol. Be concise and factual." },
      { role: "user", content: text }
    ],
    max_tokens: 1024,
    temperature: 0.3
  };
  const resp = await fetchWithRetry("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.GROQ_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(`Groq API error ${resp.status}: ${errText.slice(0, 300)}`);
  }
  const data = await resp.json();
  return data.choices[0].message.content;
}

function extractText(message) {
  if (!message || !Array.isArray(message.parts)) return "";
  return message.parts
    .filter(p => p.type === "text" || p.kind === "text")
    .map(p => p.text || "")
    .join("\n");
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/.well-known/agent-card.json") {
      return new Response(JSON.stringify(AGENT_CARD, null, 2), {
        headers: { "content-type": "application/json" }
      });
    }

    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "POST, GET, OPTIONS",
          "access-control-allow-headers": "content-type, x-barrot-auth"
        }
      });
    }

    if (request.method !== "POST" || url.pathname !== "/") {
      return new Response("Not found", { status: 404 });
    }

    function constantTimeEqual(a, b) {
      if (a.length !== b.length) return false;
      let mismatch = 0;
      for (let i = 0; i < a.length; i++) {
        mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
      }
      return mismatch === 0;
    }

    const auth = request.headers.get("x-barrot-auth") || "";
    if (!env.BRAIN_SHARED_SECRET || !constantTimeEqual(auth, env.BRAIN_SHARED_SECRET)) {
      return jsonRpcError(null, -32001, "Unauthorized: missing or invalid X-Barrot-Auth header");
    }

    if (!clientAllowed(request)) {
      return new Response(JSON.stringify({
        jsonrpc: "2.0",
        id: null,
        error: { code: -32029, message: "Rate limit exceeded" }
      }), { status: 429, headers: { "content-type": "application/json" } });
    }

    const contentLength = Number(request.headers.get("content-length") || 0);
    if (Number.isFinite(contentLength) && contentLength > MAX_REQUEST_BYTES) {
      return new Response("Request too large", { status: 413 });
    }

    let payload;
    try {
      const rawBody = await request.text();
      if (rawBody.length > MAX_REQUEST_BYTES) {
        return new Response("Request too large", { status: 413 });
      }
      payload = JSON.parse(rawBody);
    } catch (e) {
      return jsonRpcError(null, -32700, "Parse error: invalid JSON");
    }

    const { id = null, method, params = {} } = payload || {};

    if (method === "research/riemann") {
      const requestedLimit = Number(params.limit || 25);
      const limit = Math.max(
        1,
        Math.min(Number.isFinite(requestedLimit) ? requestedLimit : 25, 100)
      );

      const allowedClasses = new Set(
        RIEMANN_RESEARCH_CORPUS.evidence_policy.classes || []
      );

      let evidenceClasses = params.evidence_classes || [];
      if (!Array.isArray(evidenceClasses)) {
        evidenceClasses = [evidenceClasses];
      }

      evidenceClasses = evidenceClasses
        .filter(value => typeof value === "string")
        .filter(value => allowedClasses.has(value));

      let records = RIEMANN_RESEARCH_CORPUS.records || [];

      if (evidenceClasses.length) {
        records = records.filter(record =>
          evidenceClasses.includes(record.evidence_class)
        );
      }

      const query = typeof params.query === "string"
        ? params.query.trim().toLowerCase()
        : "";

      if (query) {
        records = records.filter(record => {
          const searchable = [
            record.title,
            record.summary,
            ...(record.authors || []),
            record.source,
          ].join(" ").toLowerCase();

          return searchable.includes(query);
        });
      }

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
        result_statistics: {
          returned_records: records.length,
          by_evidence_class: byEvidenceClass,
        },
        grounding: {
          mathematical_truth_assessment: false,
          rule: "Returned records are research metadata. Publication claims, computational evidence, and corpus summaries do not establish mathematical proof."
        },
        records,
      });
    }

    if (method === "message/send") {
      const text = extractText(params.message);
      if (!text) {
        return jsonRpcError(id, -32602, "Invalid params: message.parts must contain text");
      }
      let reply;
      try {
        reply = await callGroq(env, text);
      } catch (e) {
        console.error("Groq upstream failure:", e?.message || e);
        return jsonRpcError(id, -32000, "Upstream inference temporarily unavailable");
      }
      const taskId = crypto.randomUUID();
      const task = {
        id: taskId,
        status: { state: "completed" },
        artifacts: [
          { name: "response", parts: [{ type: "text", text: reply }] }
        ]
      };
      return jsonRpcResult(id, task);
    }

    if (method === "tasks/get") {
      return jsonRpcError(id, -32601, "tasks/get not implemented in v1 - all tasks are synchronous, use the result from message/send directly");
    }

    if (method === "message/stream") {
      return jsonRpcError(id, -32601, "message/stream (SSE) not implemented in v1");
    }

    return jsonRpcError(id, -32601, `Method not found: ${method}`);
  }
};
