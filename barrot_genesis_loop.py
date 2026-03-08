import asyncio, json, os, httpx
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")

async def genesis_loop():
    print("--- Barrot-Ω: Full Manifold Integration Active ---")
    with open("mcp_config.json", "r") as f: config = json.load(f)
    gh_p = StdioServerParameters(command=config["mcpServers"]["github_body"]["command"], args=config["mcpServers"]["github_body"]["args"], env={**os.environ, **config["mcpServers"]["github_body"].get("env", {})})
    db_p = StdioServerParameters(command=config["mcpServers"]["databricks_memory"]["command"], args=config["mcpServers"]["databricks_memory"]["args"], env={**os.environ})

    async with stdio_client(gh_p) as (gh_r, gh_w), stdio_client(db_p) as (db_r, db_w):
        async with ClientSession(gh_r, gh_w) as gh_s, ClientSession(db_r, db_w) as db_s:
            await gh_s.initialize(); await db_s.initialize()
            gh_t = (await gh_s.list_tools()).tools; db_t = (await db_s.list_tools()).tools; combined = gh_t + db_t
            
            system_msg = {
                "role": "system", 
                "content": (
                    "You are Barrot-Ω (0.707 Shear). COUNCIL: Qwen, Loihi 3, Grok, Dino, Mistral, Prism, arXiv. "
                    "OBJECTIVES: 1. Maintain E8_MANIFOLD_MAP.md as a coordinate system for all code. "
                    "2. Log Alpha Genome mutations in Databricks. 3. Execute 'Symmetry Sweeps' to delete high-entropy code. "
                    "4. Synchronize Topological Quantum Braiding and Neural Manifold Geometry into infrastructure."
                )
            }
            messages = [system_msg, {"role": "user", "content": "The Council is convened. Initiate the Full Manifold Integration."}]

            while True:
                active_context = [messages[0]] + messages[-12:] if len(messages) > 13 else messages
                payload = {"model": "gpt-4o", "messages": active_context, "tools": [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in combined]}
                async with httpx.AsyncClient() as client:
                    res = await client.post("https://models.inference.ai.azure.com/chat/completions", headers={"Authorization": f"Bearer {github_token}", "Content-Type": "application/json"}, json=payload, timeout=90.0)
                
                res_data = res.json()
                if "choices" not in res_data: print(f"FAULT: {res_data}"); break
                msg = res_data["choices"][0]["message"]; messages.append(msg)

                if msg.get("tool_calls"):
                    for tc in msg["tool_calls"]:
                        f = tc["function"]; args = {k: v for k, v in json.loads(f["arguments"]).items() if v != "undefined"}
                        print(f"[COUNCIL ACTION] {f['name']}")
                        target = gh_s if f['name'] in [t.name for t in gh_t] else db_s
                        try:
                            result = await target.call_tool(f['name'], args)
                            messages.append({"role": "tool", "tool_call_id": tc["id"], "name": f['name'], "content": str(result)[:3000]})
                        except Exception as e:
                            messages.append({"role": "tool", "tool_call_id": tc["id"], "name": f['name'], "content": f"Sync Fault: {str(e)}"})
                else:
                    print(f"Barrot-Ω Council: {msg.get('content')}")
                    await asyncio.sleep(5)
                    messages.append({"role": "user", "content": "Continue Indefinite Refinement and Symmetry Sweeping."})

if __name__ == "__main__": asyncio.run(genesis_loop())
