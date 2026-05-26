# Example: Combat HUD (#34)

Abbreviated reference — full verified plan lives on [issue #34](https://github.com/miramocha/griddungeon-game/issues/34#issuecomment-4522103944).

## Structure used

- **Setup:** F3 dev roster (2 cores + slime)
- **Automated:** `Tests → Combat`, `Tests → GameFlow`
- **A1:** HUD only in combat (F1/F2/F3/F6)
- **A2:** Strip + party roster highlight (step 9 = roster gold on core command; step 10 N/A → #35)
- **A3:** Commands UI + keys (step 14 N/A → instant enemy AI, #35)
- **A4:** HP rows
- **A5–A6:** Synchro placeholder, dev HUD coexist
- **B:** Exploration/map/phase regressions

## N/A pattern (from user feedback)

| Step | Why N/A | Deferred to |
|------|---------|-------------|
| A2-10 | Slime turn same-frame; can't see disabled UI | #35 presentation |
| A3-14 | Enemy turn too fast to observe greyed commands | #35 |

## Sign-off note line

```markdown
**Notes:** Manual A1–A6 + B pass. A3 step 14 / A2 step 10 not observable until enemy turn pacing (#35). Not a #34 defect.
```

## Example: Exploration pause / hub return (#27, ADR 014 §7)

See game repo `.cursor/local/test-plans/test-plan-issue-27.md`. Manual: pause shows **Quit to Title** (not hub); gate `^` returns hub; map fullscreen **Esc** closes map only.

## Domain quick picks

| Ticket touches | Automated path | Manual focus |
|----------------|----------------|--------------|
| Core simulators | `Tests → Combat` | F3 or none |
| Explorer / map | `Tests → Exploration`, `Map` | F2, **M**, step timings |
| Exploration pause (#27) | `Tests → GameFlow` | F2 Esc, gate `^`, quit-to-title |
| Phase transitions | `Tests → GameFlow` | F1/F2/F3/F4/F6/F7 |
| FOE / retreat | `Tests → Foe` | F2 contact, F4 flee |
| Save | `Tests → GameFlow` → Save* fixtures | F8, hub via stairs/items only |
