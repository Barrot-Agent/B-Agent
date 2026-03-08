#!/bin/bash
echo "Updating Provenance Ledger..."
TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%SZ")
HASH=$(sha256sum bundles/barrot-unified.zip | awk '{print $1}')
echo "Timestamp: $TIMESTAMP" >> config/provenance-ledger.json
echo "Bundle Hash: $HASH" >> config/provenance-ledger.json
echo "Mutation-Seal: ACTIVE" >> config/provenance-ledger.json
echo "Provenance update complete."
