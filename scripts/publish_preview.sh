#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BRANCH="resume-evidence-v2-preview"
REPO="https://github.com/xansar1/Ai-resume-screening.git"
if git ls-remote --exit-code --heads "$REPO" "$BRANCH" >/dev/null 2>&1; then
 echo "Branch $BRANCH already exists. Refusing automatic overwrite." >&2
 exit 1
fi
python3 -m py_compile app.py resume_explorer/engine.py api/main.py
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/repo"
cp -R app.py README.md requirements.txt requirements-dev.txt .python-version .gitignore .streamlit .github resume_explorer api scripts tests "$TMP/repo/"
find "$TMP/repo" -type d -name __pycache__ -prune -exec rm -rf '{}' +
cd "$TMP/repo"
git init -b "$BRANCH"
git add .
git -c user.name="Portfolio Project Publisher" -c user.email="publisher@users.noreply.github.com" commit -m "Ship Resume Evidence Explorer V2 ethical text demo"
git remote add origin "$REPO"
git push -u origin "$BRANCH"
printf '\nPublished: https://github.com/xansar1/Ai-resume-screening/tree/%s\n' "$BRANCH"
printf 'Existing main branch left unchanged. Do not upload personal resume files.\n'
