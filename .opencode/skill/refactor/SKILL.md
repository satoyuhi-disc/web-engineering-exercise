---
name: refactor
description: Use before opening a PR, once a feature works — a checklist for cleaning up code without changing behavior.
---

# Refactor

## Precondition
Only refactor code that is already covered by passing tests. If it isn't, write the test first — a refactor without a safety net is just a rewrite.

## What to look for
- Duplicated logic across views/templates → extract to a shared function, manager method, or template partial.
- Long view functions doing fetch + validate + transform + render → split into named steps.
- Magic numbers/strings repeated more than once → named constant.
- Overly broad `try/except` → narrow to the specific exception expected.
- Dead code (unused imports, unreachable branches, commented-out code) → delete, don't comment out.

## Process
1. Run the full test suite — confirm green before touching anything.
2. Make one category of change at a time (e.g. "extract queryset methods" as one commit, "rename variables" as another).
3. Run tests + ruff + black after each step, not just at the end.
4. Never refactor and add new behavior in the same commit — separate them so review is easy.
