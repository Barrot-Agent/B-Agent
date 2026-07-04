#!/usr/bin/env python3
"""
BARROT-Ω · SOVEREIGN COMMAND INTERFACE · v7.0
Stability Anchor: 0.707 | Ternary Logic {-1, 0, +1}
"""
import os, json, time, jwt, requests
import streamlit as st

class GitHubAppAuth:
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID", "")
        self.private_key = os.getenv("GITHUB_APP_PRIVATE_KEY", "").replace("\\n", "\n")
        self.installation_id = os.getenv("GITHUB_INSTALLATION_ID", "")
    def get_installation_token(self):
        now = int(time.time())
        j = jwt.encode({"iat": now-60, "exp": now+540, "iss": self.app_id}, self.private_key, algorithm="RS256")
        r = requests.post(f"https://api.github.com/app/installations/{self.installation_id}/access_tokens",
                          headers={"Authorization": f"Bearer {j}", "Accept": "application/vnd.github+json"}, timeout=10)
        return r.json().get("token", "")

def main():
    st.set_page_config(page_title="BARROT-Ω", layout="wide")
    st.title("⚡ BARROT-Ω Command Interface")
    if "auth" not in st.session_state:
        st.session_state.auth = GitHubAppAuth()
    st.write("System Ready. Stability Anchor: 0.707")

if __name__ == "__main__":
    main()
