
# Fix torch import error
try:
    import torch
    print("✅ torch imported")
except ImportError as e:
    print(f"❌ torch import failed: {e}")
    print("Installing torch...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "torch"])
    import torch
    print("✅ torch installed and imported")
