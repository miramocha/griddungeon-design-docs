# Cursor rules (design-docs repo)

Unity implementation rules are **shared with** [`griddungeon-game`](../../griddungeon-game) so architecture work in this repo follows the same principles as codegen.

## How files are linked (local)

On Windows, rule files here are **hard links** to `griddungeon-game/.cursor/rules/*.mdc` (same file data on disk). Edit either path — both repos see the change immediately.

Symbolic links require elevated PowerShell; use hard links or the setup script below.

## Fresh clone / link broken

From repo root, with sibling `griddungeon-game` at `../griddungeon-game`:

```powershell
./scripts/link-cursor-rules.ps1
```

The script recreates hard links when possible; otherwise **copies** from the game repo.

## Canonical source

| Rule | Purpose |
|------|---------|
| `unity-clean-code-principles.mdc` | SRP, DRY, KISS, YAGNI (always apply) |
| `unity-csharp-naming.mdc` | Names for C# sketches in class design docs |
| `unity-csharp-formatting.mdc` | Layout / class organization |
| `unity-csharp-comments.mdc` | Comment style |
| `unity-common-pitfalls.mdc` | Unity gotchas |
| `unity-ui-toolkit.mdc` | UI Toolkit bindings |
| `architecture-design-principles.mdc` | **Design-docs only** — maps principles → MVP1 architecture types |
| `ticket-test-documentation.mdc` | **Shared** — record test plans on GitHub issues/PRs when closing work |

## Architecture mapping

See [architecture-design-principles.mdc](architecture-design-principles.mdc) and [game phase](../docs/02-systems/game-phase.md#design-goals-mvp1).
