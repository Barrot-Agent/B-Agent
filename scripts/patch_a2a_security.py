from pathlib import Path

path = Path("a2a/worker.js")
text = path.read_text()


security_code = r'''

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
'''.strip()

if "MAX_REQUEST_BYTES" not in text:
    if anchor not in text:
        raise SystemExit("ERROR: Expected import anchor not found. Nothing changed.")
    text = text.replace(anchor, security_code, 1)

text = text.replace(
    'const resp = await fetch("https://api.groq.com/openai/v1/chat/completions", {',
    'const resp = await fetchWithRetry("https://api.groq.com/openai/v1/chat/completions", {'
)

old_parse = '''    let payload;
    try {
      payload = await request.json();'''

new_parse = '''    if (!clientAllowed(request)) {
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
      payload = JSON.parse(rawBody);'''

if old_parse in text:
    text = text.replace(old_parse, new_parse, 1)
elif "clientAllowed(request)" not in text:
    raise SystemExit("ERROR: Expected JSON parsing block not found. Nothing changed.")

text = text.replace(
    'return jsonRpcError(id, -32000, `Upstream error: ${e.message}`);',
    'console.error("Groq upstream failure:", e?.message || e);\\n        return jsonRpcError(id, -32000, "Upstream inference temporarily unavailable");'
)

path.write_text(text)
print("A2A hardening patch applied successfully.")
