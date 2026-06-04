#!/usr/bin/env bash
# KB bootstrap verifier.
# Checks every spec acceptance criterion for the day-1 scaffold.
# Exit 0 = clean baseline; nonzero = something is missing or wrong.

set -u
cd "$(dirname "$0")/.."   # cd into kb/ root

fail=0

check_file() {
  if [ ! -f "$1" ]; then
    echo "MISSING FILE: $1"
    fail=1
  fi
}

check_dir() {
  if [ ! -d "$1" ]; then
    echo "MISSING DIR:  $1"
    fail=1
  fi
}

check_grep() {
  # check_grep <pattern> <file>
  if ! grep -q "$1" "$2" 2>/dev/null; then
    echo "MISSING CONTENT: '$1' not found in $2"
    fail=1
  fi
}

# 1. git repo present
check_dir .git
if ! git log --oneline >/dev/null 2>&1; then
  echo "GIT REPO INVALID or has no commits"
  fail=1
fi

# 2. Root files
check_file README.md
check_file CLAUDE.md
check_file .gitignore
check_grep "_PRIVATE_\*" .gitignore

# 3. Operation prompts
for op in ingest query file-answer lint; do
  check_file "scripts/${op}.md"
  check_grep "Triggered by" "scripts/${op}.md"
done

# 4. Domain scaffolds
for domain in finance education runstrict-sales; do
  check_dir "${domain}"
  check_file "${domain}/CLAUDE.md"
  check_file "${domain}/index.md"
  check_file "${domain}/log.md"
  check_file "${domain}/raw/_README.md"
  for sub in sources entities concepts; do
    check_dir "${domain}/wiki/${sub}"
  done
done

# 5. Domain-specific seed folders
check_dir finance/wiki/theses
check_dir education/wiki/cases
check_dir runstrict-sales/wiki/plays

# 6. Root invariants present in root CLAUDE.md
check_grep "Hard invariants" CLAUDE.md
check_grep "Cross-domain isolation" CLAUDE.md
check_grep "Source ID convention" CLAUDE.md
check_grep "Page frontmatter" CLAUDE.md

# 7. Domain CLAUDE.md mentions its taxonomy
check_grep "Page types" finance/CLAUDE.md
check_grep "Page types" education/CLAUDE.md
check_grep "Page types" runstrict-sales/CLAUDE.md
check_grep "PII rule" education/CLAUDE.md

# 8. Each index.md and log.md is non-empty
for domain in finance education runstrict-sales; do
  if [ ! -s "${domain}/index.md" ]; then
    echo "EMPTY: ${domain}/index.md"
    fail=1
  fi
  if [ ! -s "${domain}/log.md" ]; then
    echo "EMPTY: ${domain}/log.md"
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "OK — bootstrap clean. Day-1 baseline verified."
  exit 0
else
  echo ""
  echo "FAILED — see issues above."
  exit 1
fi
