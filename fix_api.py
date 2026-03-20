with open('/data/data/com.termux/files/home/barrot/barrot.py', 'r') as f:
    content = f.read()

content = content.replace('GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")', 'HF_TOKEN = os.environ.get("HF_TOKEN", "")')
content = content.replace('API_URL = "https://models.inference.ai.azure.com/chat/completions"', 'API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"')
content = content.replace('MODEL = "gpt-4o"', 'MODEL = "mistralai/Mistral-7B-Instruct-v0.3"')
content = content.replace('"Authorization": "Bearer " + GITHUB_TOKEN', '"Authorization": "Bearer " + HF_TOKEN')
content = content.replace('"model": MODEL,', '')
content = content.replace('"max_tokens": 500,', '')
content = content.replace('"messages": [{"role": "user", "content": prompt}]', '"inputs": prompt, "parameters": {"max_new_tokens": 500, "temperature": 0.7}')
content = content.replace('if "choices" in data:', 'if isinstance(data, list):')
content = content.replace('return data["choices"][0]["message"]["content"].strip()', 'return data[0].get("generated_text", "").strip()')

with open('/data/data/com.termux/files/home/barrot/barrot.py', 'w') as f:
    f.write(content)

print("Done. barrot.py switched to Hugging Face.")
