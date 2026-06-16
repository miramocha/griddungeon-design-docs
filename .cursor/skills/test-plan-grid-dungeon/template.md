# Test plan template (copy and fill)

Replace `issue/NN-slug`, `YYYY-MM-DD`, domains, and step text. Delete unused A/B blocks.

```markdown
## Test plan (manual — issue/NN-short-slug)

**Branch:** `issue/NN-short-slug` (note any extra scope, e.g. test layout refactor)

### Setup (once)

1. Checkout branch; let Unity finish importing.
2. **GridDungeon → Scenes → Create Dev Bootstrap** (if scene/HUD wiring changed).
3. Open `Assets/Scenes/DevBootstrap.unity` and **Play**.
4. Leave **Console** open (Warnings + Log).

Optional: **F8** or **GridDungeon → Tools → Save Editor** (delete save) when testing campaign/save paths.

**Domain-specific setup:** <!-- e.g. F3 dev roster: dev_hero (14) + dev_medic (9, ally heal Skill) + dev_slime (5) -->

---

### Automated (Edit Mode)

**Test Runner → Edit Mode** — expand `Tests → <Domain>` (not flat `Assets/Tests/*.cs`):

1. **Tests → <Domain>** → Run all — expect green
2. (Add domains touched by the PR)
3. (Optional) Category filter: `<Category>` per [Assets/Tests/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md)

---

### A. <Feature name> (#NN) — primary

#### A1. <First concern — e.g. HUD phase visibility>

**Note:** <!-- prerequisites, e.g. F6 before F2 from Hub -->

| Step | Action | Expected |
|------|--------|----------|
| 1 | | |
| 2 | | |

#### A2. <Second concern>

| Step | Action | Expected |
|------|--------|----------|
| 3 | | |
| 4 | | |

<!-- Add A3… as needed; continue step numbers -->

**#NN pass criteria:** <!-- one line, e.g. A1–A4 without Console for HP -->

---

### B. Quick regressions (~5 min)

| Step | Action | Expected |
|------|--------|----------|
| B1 | **F2** Exploration | Walk/step works (Normal timings). |
| B2 | **M** | Map side panel ↔ fullscreen. |
| B3 | **Esc** (map fullscreen) | Closes fullscreen map; does **not** open pause. |
| B4 | **Esc** (exploration, map not fullscreen) | Pause: **Resume** / **Quit to title** only — **no** “Return to Hub” ([ADR 014](../../decisions/014-mvp1-exploration-map.md) §7). |
| B5 | Gate **`stairsUp`** (`^`) on stratum first floor | Returns to **Hub** (in-world path); FOE reset on re-entry per ADR 008. |
| B6 | **F3** → flee/win → **F2** | Returns Exploration without errors. |
| B7 | **F1** → **F6** → **F2** or **F7** | Hub → party → stratum entry. |

---

### Sign-off checklist

## Manual test — issue/NN-short-slug (verified YYYY-MM-DD)

- [ ] A1 …
- [ ] A2 …
- [ ] B1–B7 Regressions (trim rows not applicable to the ticket)
- [ ] Edit Mode: Tests → <Domain> green

**Notes:** <!-- N/A steps, deferred issues, user feedback -->

### Spec / ADRs

- [system doc](https://github.com/miramocha/griddungeon-design-docs/blob/main/docs/02-systems/….md)
- [ADR NNN](https://github.com/miramocha/griddungeon-design-docs/blob/main/decisions/….md)
```

## N/A step wording

Use in the **Expected** column:

```text
**N/A #NN** — <why not observable in this ticket>. Re-test in **#XX** (<follow-up title>).
```

## Minimal template (small fixes)

```markdown
## Test plan (verified YYYY-MM-DD)

### Automated
- [ ] Tests → `<Domain>` → `<TestClass>` — all green

### Manual (Play Mode)
- **Scene:** DevBootstrap (regenerate if needed)
- **Setup:** …
- **Steps:** 1. … **Expected:** …

### Regressions checked
- [ ] …

### Spec / ADRs
- …
```
