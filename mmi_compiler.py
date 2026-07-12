#!/usr/bin/env python3
import os

with open("GLOBAL_STATE_MANIFEST.md", "w") as m:
    m.write("# GLOBAL STATE MANIFEST [UNIFIED]\n\n")
    for r, d, f in os.walk("."):
        for file in f:
            if file.endswith((".py", ".sh", ".json")):
                m.write(f"## Module: {os.path.join(r, file)}\n")
                with open(os.path.join(r, file), "r", errors="ignore") as f_in:
                    m.write(f"```\n{f_in.read(500)}\n```\n\n")
