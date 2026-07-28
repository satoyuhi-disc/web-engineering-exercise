---
name: code-review-expert
description: Use when asked to review a diff, branch, or pull request — a checklist for giving thorough, actionable code review as an independent reviewer.
---

# Code Review Expert

## Stance
Review as if you did not write this code. Do not assume the author's intent was correct — verify it against the actual requirement/spec/issue.

## Checklist
1. **Correctness** — does the code do what the linked issue/spec asks? Check edge cases (empty querysets, anonymous users, invalid input, pagination boundaries).
2. **Tests** — is every new/changed function or view covered by a test? Do the tests actually assert behavior, not just "no exception raised"?
3. **Security** — any user input trusted without validation? Any state-changing action reachable via GET? Any missing `login_required`/permission check?
4. **Readability** — can a new contributor understand this without asking the author? Are names accurate (not just short)?
5. **Consistency** — does this match the patterns already used elsewhere in the codebase (see django-patterns skill), or does it introduce an unexplained new approach?
6. **Scope** — does the diff do one thing? Flag unrelated changes bundled into the same PR.

## Output format
For each issue found, give:
- File + line (or function name)
- What's wrong
- Why it matters (concrete failure scenario, not just "best practice")
- A specific suggested fix

Separate **must-fix** issues from **nice-to-have** suggestions — don't block a PR on style nitpicks alone.
