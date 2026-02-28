import json, os
class AethelMemory:
    def __init__(self, s="project_barrot_state.json"): self.s=s; self.state=self.load()
    def load(self):
        if os.path.exists(self.s): return json.load(open(self.s))
        return {"status": "INITIALIZED", "pieces": 56}
    def report(self): print(f"🏛️ Aethel-Core: {self.state}")
if __name__ == "__main__": AethelMemory().report()
