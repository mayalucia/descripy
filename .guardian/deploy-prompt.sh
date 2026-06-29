#!/usr/bin/env bash
# Deploy the guardian worksite prompt to the repo root.
# CLAUDE.md is a rendered artefact; .guardian/CLAUDE.md is the source.
DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$DIR/.guardian/CLAUDE.md" ]; then
  cp "$DIR/.guardian/CLAUDE.md" "$DIR/CLAUDE.md"
  echo "deployed .guardian/CLAUDE.md -> CLAUDE.md"
else
  echo "error: .guardian/CLAUDE.md not found" >&2
  exit 1
fi
