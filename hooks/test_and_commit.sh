#!/bin/bash
echo "Running lint and tests..."
black src/ --check
pytest -q

if [ $? -ne 0 ]; then
    echo "❌ Lint or tests failed. Fix before commit."
    exit 1
fi

echo "✅ All checks passed."
git add .
git commit -m "Auto: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
echo "✅ Code pushed successfully."
