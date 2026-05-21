# Summons & Guests (Auxiliary slots)

Combat formation extends the core **3+3 guild party** with **one auxiliary slot per row** — front and back — for **summons** or **guest** allies.

## Formation (combat only)

```
[ Enemy row ]

[ Core front ×3 ] [ Aux front ×1 ]   ← summon or guest
[ Core back  ×3 ] [ Aux back  ×1 ]   ← summon or guest
```

| Slot type | Count | Who |
|-----------|-------|-----|
| **Core** | 3 front + 3 back | Guild roster; persistent; explore as one party blob |
| **Aux front** | 1 | One **summon** or **guest** (not both) |
| **Aux back** | 1 | One **summon** or **guest** (not both) |

**Max fighters in battle:** 8 (6 core + 2 aux), if both aux slots are filled.

Auxiliary units **do not** appear on the exploration grid — only in combat.

## Summons

| Property | Rule |
|----------|------|
| **Source** | Class skills (e.g. Alchemist, future summoner), items, boss mechanics |
| **Placement** | Occupies aux **front** or **back** per skill definition |
| **Duration** | Turns remaining, HP hits zero, or dismissed |
| **Commands** | Player-issued each turn while alive (same command set as party, skill list per summon) |
| **AGI** | Summon has own AGI; enters turn queue |
| **XP** | No XP to summons |
| **Death** | Disappears; no hospital revive |
| **Between fights** | Does not persist unless skill says otherwise (buff before next fight — rare) |

**Stacking:** One summon per aux slot. New summon on occupied aux slot replaces old (or skill fails — tune per skill).

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
- **Protector**-style guard skills affect allies in same row including aux.
- If aux front is empty, behavior matches classic 3+3.

## UI

- Core slots: standard portraits (6).
- Aux slots: distinct frame (e.g. border color) labeled **Summon** / **Guest**; empty aux slot hidden or shown dimmed.
- Turn queue shows aux icons mixed with party by AGI.

## MVP

| Phase | Scope |
|-------|--------|
| **MVP** | Combat layout reserves aux slots; one test **summon** skill (aux back, 3 turns) |
| **MVP+** | One scripted **guest** on a quest fight |
| **Later** | Multiple summon skills, enemy summons, guest roster |

## Related docs

- [Party & classes](party-and-classes.md)
- [Combat](combat.md)
- [ADR 004 — Auxiliary slots](../../decisions/004-auxiliary-slots.md)
