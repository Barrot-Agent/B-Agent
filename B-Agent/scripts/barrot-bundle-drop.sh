#!/bin/bash
echo "Executing Bundle Drop Rail..."
zip -r barrot-unified.zip ./src ./workflows ./ecosystem ./docs ./config ./scripts ./codex
mkdir -p bundles
mv barrot-unified.zip bundles/
echo "Bundle drop complete. Mutation-sealed."
