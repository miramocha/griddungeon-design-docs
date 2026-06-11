---
name: pull-next-backlog-ticket
description: >-
  Selects the next highest-priority open item from a GitHub Project backlog (Ready
  then Backlog, P0→P1→P2), claims it, and starts implementation. Use when the user
  asks to pull the next ticket, pick up backlog work, start the top priority issue,
  or work from a GitHub Project board (e.g. users/OWNER/projects/N).
---

# Pull next backlog ticket

End-to-end: **discover** → **rank** → **claim** → **implement**. Works with any GitHub Project (classic fields: Status, Priority, Size, etc.).

## Prerequisites

1. **`gh` authenticated** with `project` scope:
   ```bash
   gh auth status
   gh auth refresh -s project
   ```
2. **Project identity** — resolve before querying (see [Configuration](#configuration)).
3. **GitHub CLI for all GitHub ops** (`gh issue view`, `gh project item-edit`, …). Use MCP only if `gh` fails.

## Configuration

**Step 0 — always:** read `.cursor/backlog-project.json` at the root of any open workspace repo (`griddungeon-game`, `griddungeon-design-docs`). Grid Dungeon ships this file pre-filled for [project 3](https://github.com/users/miramocha/projects/3). Do **not** search the repo or ask the user for the project URL when this file exists.

Resolve overrides in this order (first match wins after Step 0):

| Setting | Sources |
|---------|---------|
| `.cursor/backlog-project.json` | **Default** — `owner`, `number`, `projectUrl`, status columns, priorities |
| User message | Explicit project URL or `owner` + `number` override |
| Parse URL | `/users/{owner}/projects/{n}` or `/orgs/{owner}/projects/{n}` |

If no config file exists in any open workspace root, **ask once** for project URL or `owner` + `number`.

### Typical overrides (optional JSON)

| Key | Default | Purpose |
|-----|---------|---------|
| `owner` | — | Project owner login (`@me` allowed) |
| `number` | — | Project number |
| `readyStatus` | `Ready` | Column searched first |
| `backlogStatus` | `Backlog` | Column searched second |
| `inProgressStatus` | `In progress` | Claim target + resume check |
| `doneStatuses` | `["Done"]` | Excluded from selection |
| `priorityOrder` | `["P0","P1","P2"]` | Tie-break order |
| `sizeOrder` | `["XS","S","M","L","XL"]` | Prefer smaller when priorities tie |
| `repoPrefer` | auto | `game`, `docs`, or `null` — boost issues whose repo matches open workspace |
| `excludeLabels` | `["blocked","wontfix"]` | Skip items with any of these |
| `preferLabels` | `["required"]` | Tie-break: prefer `required` over `optional`; legacy `mvp1` label counts as required |
| `limit` | `50` | Max items per `item-list` call |

## Workflow overview

```
Task Progress:
- [ ] 1. Resolve project + discover fields
- [ ] 2. Gather candidates (Ready → Backlog × priorities)
- [ ] 3. Rank and pick one issue
- [ ] 4. Claim on the board (+ optional gh issue assign)
- [ ] 5. Load full issue context and plan
- [ ] 6. Branch + implement
- [ ] 7. Handoff (PR / test plan) per repo rules
```

---

## Step 1 — Resolve project and fields

```bash
gh project view <number> --owner <owner> --format json
gh project field-list <number> --owner <owner> --format json
```

From `field-list`, note **IDs** (not just names) for:

- **Status** (`ProjectV2SingleSelectField`) — map option names → `single-select-option-id`
- **Priority** — same
- **Size** — optional tie-break

If the board uses different labels (e.g. `Todo` instead of `Backlog`), update queries and `backlog-project.json` to match **actual** option names from `field-list`.

---

## Step 2 — Gather candidates

Use [Projects filter syntax](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/filtering-projects) with `gh project item-list`.

**Base filter** (always):

```
is:open is:issue -status:Done
```

Add exclusions from config, e.g. `-label:blocked -label:wontfix`.

### Tier A — Ready column (highest intent to start)

For each priority in `priorityOrder` (or once without priority if the board has no Priority field):

```bash
gh project item-list <number> --owner <owner> --format json --limit <limit> \
  --query 'status:Ready priority:P0 is:open is:issue -status:Done'
```

Repeat for `P1`, `P2`, or omit `priority:` if the field does not exist.

### Tier B — Backlog column

Same queries with `status:Backlog` (or configured `backlogStatus`).

### Tier C — Resume (optional, ask user if ambiguous)

If the user said "continue" or has WIP:

```bash
gh project item-list <number> --owner <owner> --format json --limit 10 \
  --query 'status:"In progress" assignee:@me is:open is:issue'
```

If exactly one match, prefer it over pulling new work unless the user asked for a **new** ticket.

### De-duplicate

Merge Tier A + B JSON `items` arrays; dedupe by `content.url` or `id`.

---

## Step 3 — Rank and select one ticket

Apply in order until one winner remains:

1. **Tier** — Ready before Backlog.
2. **Priority** — `P0` > `P1` > `P2` > unset (config order).
3. **Repo relevance** — If workspace has `origin` remotes, prefer issues where `repository` or `content.repository` matches an open folder’s repo (e.g. `griddungeon-game` vs `griddungeon-design-docs`). Use `repoPrefer` when set.
4. **Feature scope** — Prefer issues labeled `required` (or legacy `mvp1`) over `optional` when `preferLabels` is set in config.
5. **Unblocked** — Skip if body contains `Depends on` / `Blocked by` referencing open issues:
   ```bash
   gh issue view <owner>/<repo>#<n> --json state -q .state
   ```
   Skip when dependency `state != CLOSED`. (Heuristic; not all teams use this format.)
6. **Size** — Prefer smaller `sizeOrder` when still tied (quick wins).
7. **Board order** — If still tied, keep first item returned by `item-list` (approximates view order).

**Announce the pick** before coding:

```markdown
## Next ticket
- **Issue:** <title> — <url>
- **Repo:** <owner/repo> #<number>
- **Project:** status <X>, priority <Y>, size <Z>
- **Why:** <one line: tier + priority + repo match + unblocked>
```

If no candidates: report empty tiers, suggest checking filters, adding Ready items, or lowering priority bar. **Do not** invent work.

---

## Step 4 — Claim on the project board

1. Set Status → **In progress** (use discovered field + option IDs):

   ```bash
   gh project item-edit \
     --id <project-item-id> \
     --project-id <PVT_... from project view> \
     --field-id <status-field-id> \
     --single-select-option-id <in-progress-option-id>
   ```

2. Optionally assign on the issue:

   ```bash
   gh issue edit <url> --add-assignee @me
   ```

3. Optional comment:

   ```bash
   gh issue comment <url> --body "Picked up from project backlog — starting implementation."
   ```

Do not mark **Done** until the user confirms completion.

---

## Step 5 — Load full issue context

```bash
gh issue view <url> --comments
```

Extract: Summary, Acceptance / checklist, Spec links, Related issues, Test plan, Out of scope.

**Read linked design docs** when the issue points to them (especially `docs/` acceptance criteria).

Post a short implementation plan in chat (files to touch, repos, tests) before large edits.

---

## Step 6 — Branch and implement

1. **cd** to the issue’s repo root (multi-root workspace: match `repository` from the item).
2. **Branch** from default branch:
   ```bash
   git fetch origin
   git checkout main && git pull   # or master
   git checkout -b issue-<number>-<short-slug>
   ```
3. Implement against **Acceptance** checkboxes; keep scope minimal (YAGNI).
4. Follow repo **Cursor rules** (format/review on commit, Unity test runner not CLI batch, etc.).

---

## Step 7 — Handoff

| Repo type | On completion |
|-----------|----------------|
| Unity / game code | Ask user for Edit Mode tests; use **test-plan-grid-dungeon** skill for issue comment |
| Docs-only | PR or direct commit per user request |
| Any | `gh pr create` when user asks; link `Fixes #<n>` |

Update project Status → **In review** when a PR is open (if that column exists).

---

## Grid Dungeon defaults

Project board: [Codename: GridDungeon](https://github.com/users/miramocha/projects/3). Defaults live in each repo’s `.cursor/backlog-project.json` (`repoPrefer` differs for game vs design-docs).

---

## Failure modes

| Symptom | Action |
|---------|--------|
| `project` scope missing | `gh auth refresh -s project` |
| Unknown status name | Re-run `field-list`; align config |
| Empty Ready/Backlog | Widen query (drop `priority:`), check `-label:` exclusions |
| Item is draft / no `content.number` | Skip; not a linked issue |
| Wrong repo checked out | `cd` to correct workspace root before branching |

---

## What not to do

- Do not run Unity batch tests while Editor may be open (see repo rules).
- Do not commit or push unless the user asks.
- Do not close issues without verification + test plan when required.
- Do not pull multiple tickets unless the user explicitly requests a batch.
