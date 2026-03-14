#!/data/data/com.termux/files/usr/bin/bash
# BARROT-Ω VAULT REFINEMENT — 0.707 STABILITY AUDIT
# Converted to use GITHUB_TOKEN + existing memory structure

VAULT_DIR="$HOME/barrot"
REFINE_LOG="$VAULT_DIR/refinement_$(date +%Y%m%d).log"

echo "[vΩ] Initiating Refinement Audit: Testing for 0.707 Stability..."

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "[!] CRITICAL: GITHUB_TOKEN missing. Run: source ~/.bashrc"
    exit 1
fi

# Audit all JSON context files for 0.707 anchor presence
for entry in "$VAULT_DIR"/*.json; do
    [[ -f "$entry" ]] || continue
    ENTRY_ID=$(basename "$entry")
    
    # Check if anchor is present
    if grep -q "0.7071" "$entry"; then
        echo "[STABLE] $ENTRY_ID — 0.707 anchor confirmed" | tee -a "$REFINE_LOG"
    else
        echo "[UNSTABLE] $ENTRY_ID — missing anchor, needs refinement" | tee -a "$REFINE_LOG"
    fi
done

echo "[vΩ] Refinement Complete. Log: $REFINE_LOG"
