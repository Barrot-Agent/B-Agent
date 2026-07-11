#!/bin/bash

# Script to complete the Main branch deletion from remote
# This script should be executed by someone with push permissions to the repository

set -e

echo "Checking current branch status..."
git fetch --all

echo ""
echo "Verifying Main and main branches..."
git ls-remote --heads origin | grep -E "(Main|main)" || true

echo ""
echo "Deleting remote Main branch..."
if git ls-remote --heads origin | grep -q "refs/heads/Main"; then
    git push origin --delete Main
    echo "✅ Remote Main branch deleted successfully"
else
    echo "ℹ️  Remote Main branch not found (may already be deleted)"
fi

echo ""
echo "Verifying deletion..."
if git ls-remote --heads origin | grep -q "refs/heads/Main"; then
    echo "❌ Main branch still exists"
    exit 1
else
    echo "✅ Main branch successfully removed from remote"
fi

echo ""
echo "Current remote branches with 'main' in name:"
git ls-remote --heads origin | grep -i main || echo "No branches found"
