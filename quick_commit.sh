#!/bin/bash
# Quick commit helper with auto-sync
# Usage: ./quick_commit.sh "your message"

if [ -z "$1" ]; then
    echo "❌ Error: Please provide a commit message"
    echo "Usage: ./quick_commit.sh \"your message\""
    exit 1
fi

echo "📝 Committing changes..."
git add -A
git commit -m "$1"

# The post-commit hook will automatically sync to GitHub
