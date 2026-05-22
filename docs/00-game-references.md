# Game references

Curated titles for **future design and tone checks**. **MVP1 authority** stays **Etrian Odyssey–first** ([00 — Vision](00-vision.md)); entries here inform optional systems, UX, and post-MVP1 ideas — they do not override locked ADRs unless we explicitly amend one.

---

## Primary (locked for MVP1)

| Game | Use in Grid Dungeon |
|------|---------------------|
| ***Etrian Odyssey*** (series) | Auto-map (no player drawing), FOEs, strata/floors, guild party, AGI combat, hub between dives, EO Union-style team burst → [Synchro Protocol](02-systems/synchro-protocol.md) |

---

## Secondary references

| Game | Relevant beats | Possible borrow (evaluate later) |
|------|----------------|----------------------------------|
| ***Mary Skelter: Nightmares*** / ***Nightmares 2*** | FPV grid labyrinth; **auto-map**; visible **strong enemies** on the map; hub/base between tower floors; turn-based combat with **ailments / binds** and flashy skill presentation; party of distinct roles | Map + FOE tension validation; reactive combat UI and telegraphing; dungeon **floor themes** and “tower climb” pacing; transformation / rage-style **burst modes** only if we want a parallel to Synchro (do **not** replace Navigator + Synchro bar without ADR) |
| *Wizardry* | Hardcore dungeon crawl, wipe stakes | Death/save tone comparisons only — we follow EO hub model |
| *Shin Megami Tensei* / dungeon crawlers | Weaknesses, buff stacking | Light touch on elemental weaknesses ([combat](02-systems/combat.md)); full press-turn out of scope |

---

## Mary Skelter — design notes (scratchpad)

Use when reviewing exploration, combat UI, or “dungeon feel” features. **Not committed.**

| Topic | MSK angle | Grid Dungeon today |
|-------|-----------|-------------------|
| **Exploration** | FPV steps in a mapped tower | EO grid + auto-reveal ([ADR 002](../decisions/002-mapping-model.md)); floor painter + 2D HUD |
| **Map threats** | Boss / FOE-like map icons, routing matters | FOE step patrol ([ADR 003](../decisions/003-foe-step-patrol.md)) |
| **Combat read** | Strong VFX, clear hit / ailment feedback | Reactive blocking HUD ([04 — Tech notes](04-tech-notes.md#ui-reactivity)); Fixed presentation MVP1 |
| **Hub loop** | Base camp between dives | Hub services ([hub-and-services](02-systems/hub-and-services.md)) |
| **Burst modes** | Transform / blood / rage spikes | **Synchro bar** + Navigator ([ADR 006](../decisions/006-union-team-bar.md), [007](../decisions/007-navigator-role.md)) — compare feel only |
| **Verticality** | Multi-floor tower structure | Strata + `level` bands ([ADR 019](../decisions/019-floor-verticality.md)) |

When a feature proposal cites Mary Skelter, link it here and note **EO compatibility** (grid step events, no action combat, read-only player map).

---

## Related

- [00 — Vision](00-vision.md)
- [00 — Release scope](00-release-scope.md)
- [MVP1 spec](mvp1-spec.md)
