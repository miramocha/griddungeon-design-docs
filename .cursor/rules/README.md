# Cursor rules (design-docs repo)

Unity implementation rules are **shared with** [griddungeon-game](https://github.com/miramocha/griddungeon-game) so architecture work in this repo follows the same principles as codegen.

## How files are linked (local)

On Windows, rule files here are **hard links** to `griddungeon-game/.cursor/rules/*.mdc` (same file data on disk). Edit either path — both repos see the change immediately.

Symbolic links require elevated PowerShell; use hard links or the setup script below.

## Fresh clone / sync both repos

From **design-docs** repo root, with sibling `griddungeon-game` at `../griddungeon-game`:

```powershell
./scripts/sync-cursor-config.ps1
```

This runs, in order:

1. `link-cursor-rules.ps1` — hard links (or copies) **shared** rules from game → design-docs
2. `sync-cursor-skills.ps1` — mirrors skill folders per canonical repo
3. Copies `fresh-reviewer.md` to design-docs `.cursor/agents/`
4. Clears `.cursor/local/` drafts in **both** repos

Rules-only repair: `./scripts/link-cursor-rules.ps1`

## Canonical source

| Rule | Purpose |
|------|---------|
| `unity-clean-code-principles.mdc` | SRP, DRY, KISS, YAGNI (always apply) |
| `unity-csharp-naming.mdc` | Names for C# sketches in class design docs |
| `unity-csharp-language.mdc` | C# 9 subset — no `init`, `record`, etc. |
| `unity-csharp-formatting.mdc` | Layout / class organization |
| `unity-csharp-comments.mdc` | Comment style |
| `unity-common-pitfalls.mdc` | Unity gotchas |
| `unity-ui-toolkit.mdc` | UI Toolkit bindings |
| `architecture-design-principles.mdc` | **Design-docs only** — maps principles → MVP1 architecture types |
| `ticket-test-documentation.mdc` | **Shared** — record test plans on GitHub issues/PRs when closing work |
| `post-commit-csharp-code-review.mdc` | **Shared** — independent C# review after agent-created commits (skipped in docs-only repos) |
| `pre-commit-csharpier-format.mdc` | **Shared** — CSharpier (extension/CLI) on changed `.cs` before commit |
| `git-commit-agent-workflow.mdc` | **Shared** — agent git commit order (format → commit → post-commit review → push) |
| `unity-meta-files.mdc` | **Game** — `.meta` GUID policy (link from game repo via `scripts/link-cursor-rules.ps1`) |

## Agent skills (design-docs repo)

| Skill | Purpose |
|-------|---------|
| [test-plan-grid-dungeon](../skills/test-plan-grid-dungeon/SKILL.md) | Consistent GitHub/PR test plans (tables, sign-off, N/A deferrals) |
| [validate-unity-meta](../skills/validate-unity-meta/SKILL.md) | Unity `.meta` validation — runs in **griddungeon-game** |
| [blender-bone-remap](../skills/blender-bone-remap/SKILL.md) | VRoid/VRM bone rename + mirror pairs (Blender MCP) |
| [vroid-shapekey-remap](../skills/vroid-shapekey-remap/SKILL.md) | VRoid `Fcl_*` shape key → `vroid*` naming (Blender MCP) |

**Mirrored skills** — identical copies in both repos (`test-plan-grid-dungeon`, `validate-unity-meta`, `pull-next-backlog-ticket`, `stratum-floor-*`, `blender-bone-remap`, `vroid-shapekey-remap`, …). Run `./scripts/sync-cursor-skills.ps1` after edits (canonical source per skill is in that script).

## Agents

| Agent | Notes |
|-------|--------|
| [fresh-reviewer](../agents/fresh-reviewer.md) | Copied from game repo by `sync-cursor-config.ps1` |

## Architecture mapping

See [architecture-design-principles.mdc](architecture-design-principles.mdc) and [game phase](../../docs/02-systems/game-phase.md#design-goals-mvp1).
