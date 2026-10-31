#!/usr/bin/env python3
"""
BARROT-Omega | HRM WIRE-IN PATCHER | v1.0
Surgically swaps bare Ternary.resolve() call sites for hrm_resolve()
in core/xrp_liquidity_bridge.py and hf_space/app.py.
Every replacement is verified; the script fails loudly and changes
NOTHING on partial match. Run from repo root: python3 scripts/wire_in_hrm.py
"""

import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch(path: Path, replacements: list):
    src = path.read_text()
    for old, new in replacements:
        if src.count(old) != 1:
            print(f"FAIL: expected exactly 1 match in {path.name} for:\n{old[:90]}...")
            print("Nothing was modified. Aborting.")
            sys.exit(1)
    shutil.copy(path, path.with_suffix(path.suffix + ".bak"))
    for old, new in replacements:
        src = src.replace(old, new)
    path.write_text(src)
    print(f"OK: {path.name} patched ({len(replacements)} sites), backup at {path.name}.bak")


BRIDGE = ROOT / "core" / "xrp_liquidity_bridge.py"
bridge_reps = [
    (
        'HF_TOKEN           = os.getenv("HF_TOKEN", "")',
        'HF_TOKEN           = os.getenv("HF_TOKEN", "")\n\n'
        "# -- HRM hierarchical resolver (core/hrm_ternary.py) --------------\n"
        "try:\n"
        "    from hrm_ternary import hrm_resolve          # run from core/\n"
        "except ImportError:\n"
        "    from core.hrm_ternary import hrm_resolve     # run from repo root",
    ),
    (
        "    mrp = Ternary.resolve(ob_sig, oc_sig, sent_sig)\n"
        "\n"
        "    # ── Sovereign Absolution: unanimous SELL triggers override NULL ──\n"
        "    if ob_sig == oc_sig == sent_sig == Ternary.SELL:\n"
        '        print("[SOVEREIGN ABSOLUTION] All signals SELL. Override engaged → NULL output.")\n'
        "        mrp = Ternary.NULL",
        "    # -- HRM hierarchical resolution (gate + confidence + absolution) --\n"
        '    hrm = hrm_resolve({"orderbook": ob_sig, "onchain": oc_sig, "sentiment": sent_sig})\n'
        "    mrp = hrm.state\n"
        "    if hrm.absolution_fired:\n"
        '        print("[SOVEREIGN ABSOLUTION] Unanimous SELL. Override engaged -> NULL output.")\n'
        "    elif hrm.raw_state != hrm.state:\n"
        '        print(f"[HRM GATE] {hrm.basis}")',
    ),
    (
        "        mrp_output  = mrp,\n" "        mrp_label   = Ternary.label(mrp)\n" "    )",
        "        mrp_output  = mrp,\n"
        "        mrp_label   = Ternary.label(mrp),\n"
        "        confidence  = hrm.confidence\n"
        "    )",
    ),
    (
        "    mrp_output:  int\n" "    mrp_label:   str",
        "    mrp_output:  int\n" "    mrp_label:   str\n" "    confidence:  float = 0.0",
    ),
    (
        "        # Confidence from signal convergence\n"
        "        signals = [state.ob_signal, state.oc_signal, state.sent_signal]\n"
        "        agree   = sum(1 for s in signals if s == state.mrp_output)\n"
        "        conf    = agree / 3.0",
        "        # Measured confidence: HRM agreement x convergence\n"
        "        conf = state.confidence",
    ),
]

APP = ROOT / "hf_space" / "app.py"
app_reps = [
    (
        "from typing import Optional",
        "from typing import Optional\n\n"
        "# -- HRM hierarchical resolver (ships alongside app.py on the Space) --\n"
        "try:\n"
        "    from hrm_ternary import hrm_resolve\n"
        "    HRM_AVAILABLE = True\n"
        "except ImportError:\n"
        "    HRM_AVAILABLE = False",
    ),
    (
        "                mrp             = Ternary.resolve(ob_sig, oc_sig, sent_sig)\n"
        "\n"
        "                # Sovereign Absolution\n"
        "                absolved = False\n"
        "                if ob_sig == oc_sig == sent_sig == Ternary.SELL:\n"
        "                    mrp      = Ternary.NULL\n"
        "                    absolved = True",
        "                if HRM_AVAILABLE:\n"
        '                    hrm      = hrm_resolve({"orderbook": ob_sig, "onchain": oc_sig, "sentiment": sent_sig})\n'
        "                    mrp      = hrm.state\n"
        "                    conf     = hrm.confidence\n"
        "                    absolved = hrm.absolution_fired\n"
        "                else:\n"
        "                    mrp      = Ternary.resolve(ob_sig, oc_sig, sent_sig)\n"
        "                    conf     = None\n"
        "                    absolved = False\n"
        "                    if ob_sig == oc_sig == sent_sig == Ternary.SELL:\n"
        "                        mrp, absolved = Ternary.NULL, True",
    ),
    (
        "st.markdown(f\"<div class='metric-card'><div style='color:#00ffcc88'>MRP OUTPUT</div><div class='signal-{'buy' if mrp==1 else 'sell' if mrp==-1 else 'null'}'>{ico} {lbl}</div></div>\", unsafe_allow_html=True)",
        "st.markdown(f\"<div class='metric-card'><div style='color:#00ffcc88'>MRP OUTPUT</div><div class='signal-{'buy' if mrp==1 else 'sell' if mrp==-1 else 'null'}'>{ico} {lbl}</div><div style='font-size:0.8em'>conf={conf if conf is not None else 'n/a'}</div></div>\", unsafe_allow_html=True)",
    ),
]

patch(BRIDGE, bridge_reps)
patch(APP, app_reps)
shutil.copy(ROOT / "core" / "hrm_ternary.py", ROOT / "hf_space" / "hrm_ternary.py")
print("OK: core/hrm_ternary.py mirrored to hf_space/hrm_ternary.py")
print("\nWIRE-IN COMPLETE")
