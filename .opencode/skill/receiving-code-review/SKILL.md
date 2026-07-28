---
name: receiving-code-review
description: Use when processing code review feedback on your own PR — how to triage comments and decide what to change.
---

# Receiving Code Review

## Triage every comment into one of three buckets
1. **Must fix** — correctness bug, security issue, missing test for changed behavior.
2. **Worth doing** — genuine improvement, but not blocking; do it now if cheap, otherwise note it.
3. **Disagree / out of scope** — respond with reasoning instead of silently ignoring or silently complying.

## Rules
- Never apply a suggested fix you don't understand — ask for clarification instead of guessing.
- If a reviewer flags a missing test, add the test before addressing anything else in that comment thread.
- If two reviewers (or two review passes from different models) disagree, don't average their suggestions — pick one deliberately and note why.
- Re-run the full test suite + lint after applying review fixes, not just the changed file.
- Summarize what changed vs. the review at the top of your response/commit, so the human doesn't have to re-derive it.

## When the AI reviewer is wrong
It's expected that an independent review model will sometimes flag something safe as risky (or vice versa). The developer, not the agent, makes the final call on what to change — record that decision briefly (e.g. in the PR description) rather than blindly accepting every comment.
