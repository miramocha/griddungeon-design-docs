# Summons & Guests (Auxiliary slots)

Combat formation extends the core **3+3 guild party** with **one auxiliary slot per row** — front and back — for **summons** or **guest** allies.

## Formation (combat only)

```
[ Navigator — off formation; see navigator.md ]

[ Enemy row ]

[ Core front ×3 ] [ Aux front ×1 ]   ← summon or guest
[ Core back  ×3 ] [ Aux back  ×1 ]   ← summon or guest
```

| Slot type | Count | Who |
|-----------|-------|-----|
| **Navigator** | 1 active | Party lead; Union + passives; **not** in 3+3 ([navigator](navigator.md)) |
| **Core** | 3 front + 3 back | Guild roster; persistent; explore as one party blob |
| **Aux front** | 1 | One **summon** or **guest** (not both) |
| **Aux back** | 1 | One **summon** or **guest** (not both) |

**Max in battle UI:** Navigator + up to 8 (6 core + 2 aux).

Auxiliary units **do not** appear on the exploration grid — only in combat.

## Summons

| Property | Rule |
|----------|------|
| **Source** | **Summoner class only** (deploy skills); rare items / boss mechanics |
| **Placement** | Occupies aux **front** or **back** per skill definition |
| **Duration** | Turns remaining, HP hits zero, or dismissed |
| **Commands (MVP1)** | **Scripted only** — fixed action/skills per turn; **no** player command menu ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| **Commands (later)** | **TBD** — full player control vs stance hybrid vs keep scripted |
| **AGI** | Summon has own AGI; enters turn queue; turn **auto-resolves** in MVP1 |
| **XP** | No XP to summons |
| **Death** | Disappears; no hospital revive |
| **Between fights** | Does not persist unless skill says otherwise (buff before next fight — rare) |

**Stacking:** One summon per aux slot. New summon on occupied aux slot replaces old (or skill fails — tune per skill).

### MVP1 action script (simple)

Each `SummonDefinition` includes a short **`actionScript`** — resolved top to bottom each summon turn (first valid step wins, or by turn index — pick one pattern in data).

**Example — MVP1 test drone (Summoner skill `deploy_test_drone`):**

| Step | Action | Target |
|------|--------|--------|
| 1 | `volt_burst` (skill) | Random enemy |
| 2+ | `attack` | Lowest HP enemy in reach |

```yaml
summon_id: test_drone
duration_turns: 3
action_script:
  - turn: 1
    action: skill
    skill_id: volt_burst
    target: random_enemy
  - turn: default
    action: attack
    target: lowest_hp_enemy
```

**UI on summon turn:** highlight aux portrait → play VFX → combat log line → **presentation lock** releases → next queue entry ([combat UI motion](combat.md#ui-motion--feedback), [tech notes](../04-tech-notes.md#ui-reactivity)).

**Union bar:** Summon actions do **not** charge Union ([union](union.md)).

## Guests

| Property | Rule |
|----------|------|
| **Source** | Quests, story beats, floor scripts ("ally joins this fight") |
| **Placement** | Designer assigns front or back aux for the encounter |
| **Duration** | One battle, one floor, or until script removes guest |
| **Commands** | Player-controlled by default; **NPC guest** flag = AI-controlled (cutscenes, escort) |
| **AGI** | Guest enters turn queue |
| **XP** | No XP to guests (avoid leveling NPCs) |
| **Death** | Guest downed = unavailable for rest of fight; story may fail quest or use "retreat" script |
| **Exploration** | Guest does not walk the grid with party |

## Targeting & row rules

- Aux slots count as **front** or **back** for melee reach and row skills.
- Enemy melee without pierce targets **front row** (core + aux front) before any back slot.
- **Vanguard**-style guard skills affect allies in same row including aux.
- If aux front is empty, behavior matches classic 3+3.

## UI

- Core slots: standard portraits (6).
- Aux slots: distinct frame (e.g. border color) labeled **Summon** / **Guest**; empty aux slot hidden or shown dimmed.
- Turn queue shows aux icons mixed with party by AGI.

## MVP1

| Phase | Scope |
|-------|--------|
| **MVP1** | Aux slots + one test summon — **scripted** actions only ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| **MVP1+** | One scripted **guest** on a quest fight |
| **Later** | Multiple summon skills, enemy summons, guest roster |

## Related docs

- [Party & classes](party-and-classes.md)
- [Combat](combat.md)
- [ADR 004 — Auxiliary slots](../../decisions/004-auxiliary-slots.md)
- [ADR 016 — Summon control MVP1](../../decisions/016-summon-control-mvp1.md)
