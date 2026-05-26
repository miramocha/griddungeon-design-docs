# Cursor user rule — committing changes with git

Copy into **Cursor Settings → Rules → User Rules** (replaces the previous `committing-changes-with-git` block).

---

Only create commits when requested by the user. If unclear, ask first.

## Git safety

- NEVER update the git config
- NEVER run destructive/irreversible git commands (like push --force, hard reset, etc.) unless the user explicitly requests them
- NEVER skip hooks (--no-verify, --no-gpg-sign, etc.) unless the user explicitly requests it
- NEVER force push to main/master; warn the user if they request it
- Avoid `git commit --amend`. ONLY use --amend when ALL conditions are met:
  1. User explicitly requested amend, OR commit SUCCEEDED but pre-commit hook auto-modified files that need including
  2. HEAD commit was created by you in this conversation
  3. Commit has NOT been pushed to remote
- If commit FAILED or was REJECTED by hook, NEVER amend — fix and create a NEW commit
- If already pushed to remote, NEVER amend unless the user explicitly requests it
- NEVER commit changes unless the user explicitly asks
- NEVER use interactive git (`-i` flags)

## Workflow

1. Batch: `git status`, `git diff` (staged + unstaged), `git log -3 --oneline`
2. Draft commit message; exclude secrets
3. **C# / Unity:** CSharpier on changed `.cs` **before** commit (see repo `pre-commit-csharpier-format.mdc`)
4. `git add` → `git commit` (HEREDOC / PowerShell here-string)
5. **C# / Unity:** **Post-commit** independent review (`post-commit-csharp-code-review.mdc`): `git show HEAD`, delegate **fresh-reviewer**, report Blocker / Should fix / Nit
6. Fix **Blockers** in a **follow-up commit** (default); amend only per amend rules above. Do not push with known Blockers unless the user approves
7. `git status` after commit; push only when asked

## Order summary

**CSharpier → commit → fresh-reviewer → (fix Blockers) → push**
