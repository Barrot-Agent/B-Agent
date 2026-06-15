#!/usr/bin/env bash
# ==============================================================================
# BARROT-Ω REPOSITORY AUTOMATION RELAY
# Architect: Sean | Node: Brooklyn Core
# Objective: Phase 1 & 2 Automated Ledger Synchronization
# ==============================================================================

set -e

echo "[BARROT-Ω] Running live telemetry matrix..."
python3 xrp_telemetry_matrix.py

if [ -f "COUNCIL_REVIEW.md" ]; then
    echo "[BARROT-Ω] Telemetry captured. Initializing Phase 1 GitHub sync..."
    
    # Staging historical matrix update
    git add xrp_telemetry_matrix.py COUNCIL_REVIEW.md
    
    # Committing state to the ledger with unique timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    git commit -m "Council Matrix Sync: $TIMESTAMP [Anchor: 0.707]"
    
    echo "[BARROT-Ω] Pushing physical asset state to repository..."
    git push origin main
    
    echo "[BARROT-Ω] Phase 1 Sync Complete."
    echo "=============================================================================="
    echo "[BARROT-Ω] Executing Phase 2: Relay Payload Prepared for Local Orchestration Nodes."
    echo "=============================================================================="
else
    echo "[CRITICAL] COUNCIL_REVIEW.md not generated. Halting automation relay."
    exit 1
fi

# Triggering Ingestion Engine
python3 council_ingest_node.py
