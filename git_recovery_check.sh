#!/bin/bash

echo "=========================================="
echo "GIT HISTORY RECOVERY DIAGNOSTIC"
echo "=========================================="

echo ""
echo "1. Checking for dangling commits..."
git fsck --full 2>&1 | grep -i "dangling commit" | head -5 || echo "   No dangling commits found"

echo ""
echo "2. Checking git log with all references..."
git log --all --graph --oneline --decorate -20

echo ""
echo "3. Checking reflog (all reference changes)..."
git reflog --all -20

echo ""
echo "4. Checking for backup references..."
git show-ref -a | head -20 || echo "   No backup refs"

echo ""
echo "5. Checking git notes..."
git notes list || echo "   No git notes found"

echo ""
echo "6. Checking GitHub URL..."
echo "   Repository: $(git config --get remote.origin.url)"

echo ""
echo "=========================================="
echo "CONCLUSION:"
echo "=========================================="
echo "If no dangling commits appear above,"
echo "the force-push has cleaned up old references."
echo ""
echo "RECOVERY OPTIONS:"
echo "1. GitHub Support (90-day retention)"
echo "2. Check GitHub Insights → Network graph"
echo "3. Look for PR/Issue references to old commits"
echo "=========================================="
