#!/bin/bash
# cleanup_merged_branches.sh
# Run this script to delete all merged branches from remote repository
# WARNING: This will permanently delete branches. Ensure all changes are merged first!

branches=(
  "feature/shrm-v2"
  "Micro-Agent-workflow"
  "copilot/optimize-workflow-structure"
  "copilot/reassess-directives-and-processes"
  "copilot/evolution-of-shrm-v2"
  "copilot/evolve-shrm-into-v2-0"
  "copilot/evolve-shrm-to-v2-0"
  "copilot/evolve-shrm-to-v2-0-again"
  "copilot/enable-barrot-cognitive-enhancements"
  "copilot/enhance-cognitive-capabilities"
  "copilot/enhance-barrot-functionality"
  "copilot/implement-barrot-cognition-logic"
  "copilot/ping-pong-barrot-shrm"
  "copilot/implement-ping-pongings-infrastructure"
  "copilot/implement-ping-pongings-workflow"
  "copilot/identify-high-impact-datasets"
  "copilot/ingest-datasets-and-tools"
  "copilot/enhance-autonomous-learning-capabilities"
  "copilot/add-barrot-website-functionality"
  "copilot/create-presale-page-and-token"
  "copilot/setup-barrot-on-mobile"
  "copilot/identify-priorities-strategies"
  "copilot/fix-typo-in-documentation"
  "copilot/implement-self-improvement-protocols"
  "copilot/implement-superior-search-engine"
  "copilot/suggest-next-steps-development"
  "copilot/add-barrot-workflows"
  "copilot/add-snapshot-functionality"
)

echo "=========================================="
echo "Branch Cleanup Script for Barrot-Agent"
echo "=========================================="
echo ""
echo "This script will delete ${#branches[@]} merged branches from the remote repository."
echo ""
echo "⚠️  WARNING: This action cannot be undone!"
echo ""
echo "Before proceeding, please verify:"
echo "  1. All changes from these branches are merged into Main"
echo "  2. No open pull requests reference these branches"
echo "  3. You have created a backup if needed"
echo "  4. You have proper permissions to delete branches"
echo ""
echo "Branches to be deleted:"
for branch in "${branches[@]}"; do
  echo "  - $branch"
done
echo ""
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

echo ""
echo "Starting branch deletion..."
echo ""

deleted=0
failed=0

for branch in "${branches[@]}"; do
  echo -n "Deleting: $branch ... "
  if git push origin --delete "$branch" 2>/dev/null; then
    echo "✓ Deleted"
    ((deleted++))
  else
    echo "✗ Failed (may already be deleted or insufficient permissions)"
    ((failed++))
  fi
done

echo ""
echo "=========================================="
echo "Cleanup Summary"
echo "=========================================="
echo "Successfully deleted: $deleted branches"
echo "Failed to delete: $failed branches"
echo ""
echo "Branch cleanup complete!"
echo ""
echo "Next steps:"
echo "  1. Verify the branches are deleted on GitHub"
echo "  2. Run 'git fetch --prune' to update local references"
echo "  3. Update any documentation that references these branches"
echo "  4. Notify team members of the cleanup"
