# Gathering & Fishing (MVP2)

**Scope:** MVP2 — not required for first playable ([release scope](../00-release-scope.md)).

Dungeon **interact nodes** where the party plays a short **minigame** to earn **materials** for [synthesis](character-progression.md) and [gather quests](../03-content/dungeons-and-encounters.md). EO parallel: chop/mining points; fishing adds a pacing break and stratum-flavored loot.

## Design goals

| Goal | How |
|------|-----|
| **Optional route** | Nodes on side paths — not mandatory for floor clear |
| **Risk/time trade** | Minigame takes wall-clock seconds; party **frozen** (no steps); no FOE step tick during minigame |
| **Hub payoff** | Materials only matter when **synthesis** ships in MVP2 |
| **Map literacy** | Used nodes appear on auto-map; respawn rules clear |

---

## Node types

| Type | Tile / marker | Tool (fiction) | Minigame |
|------|---------------|----------------|----------|
| **Chop** | Tree stump, dead tree | Axe | **Gather** — rhythm / timing bar |
| **Mine** | Ore vein, crystal | Pick | **Gather** — same core UI, different art/SFX |
| **Forage** | Bush, mushroom patch | Hands / kit | **Gather** — shorter timing window |
| **Fish** | Pond, stream (floor water tile) | Rod | **Fishing** — cast → bite → react prompt |

All types share: `Space` **Interact** while facing node ([input bindings](input-bindings.md)).

---

## Exploration flow

```
Party on adjacent cell, facing node
  → Interact
  → If node depleted (same dive) → message, exit
  → If missing tool item (optional MVP2) → shop hint
  → Enter MinigameMode (exploration input locked)
  → Play minigame → result tier
  → Grant materials to party inventory
  → Mark node state; map icon update
  → Resume exploration
```

- **No random encounter** roll while in minigame (safe activity).
- **FOE patrol** does not advance during minigame ([ADR 003](../../decisions/003-foe-step-patrol.md) — frozen like combat).

---

## Gather minigame (chop / mine / forage)

Single reusable **GatherMinigame** controller; skin per node type.

### Loop (draft)

1. **Ready** — prompt “Press Space on beat” (or hold/release).
2. **3–5 beats** — shrinking timing window; hit = Good, miss = Bad.
3. **Score** → tier: Fail / OK / Great.
4. **Loot table** roll by tier + node `lootTableId` + floor depth.

| Tier | Typical yield |
|------|----------------|
| Fail | 0–1 low material (or junk) |
| OK | 1–2 standard materials |
| Great | 2–3 + rare roll on table |

**Optional class hook:** Marksman passive +1 tier step (MVP2 nice-to-have).

### UX

- Overlay on FPV or simple full-screen panel (keep dungeon visible dimmed).
- `Esc` cancels → no materials, no node depletion (or half-depletion — **MVP2: cancel = no spend**).
- Duration target: **5–15 seconds** per node.

---

## Fishing minigame

Separate **FishingMinigame** — slower, one big timing check.

### Loop (draft)

1. **Cast** — `Space` to cast line (animation stub).
2. **Wait** — 1–3s random “bite” window (bobber icon).
3. **Hook** — `Space` within **0.4–0.6s** react window when bite flashes.
4. **Reel** — optional second tap for Great tier (MVP2 simple: single hook timing only).
5. **Result tier** → fish/material loot table (stratum-specific fish).

| Tier | Yield |
|------|--------|
| Miss hook | Nothing or “seaweed” junk |
| OK | Common fish / material |
| Great | Rare fish + bonus material |

**Fish nodes** only on authored water-adjacent tiles; max **1–2 per floor** early strata to avoid fishing grind meta.

---

## Node state & respawn

| State | Behavior |
|-------|----------|
| **Fresh** | Can interact |
| **Depleted (same dive)** | Interact shows “Already harvested” until hub return |
| **After hub return** | Nodes **respawn** ([ADR 008](../../decisions/008-campaign-defaults.md) floor reset — same as existing gather note in [dungeons & encounters](../03-content/dungeons-and-encounters.md)) |

**Chests** stay looted; **gather/fish nodes** reset on hub return + re-enter (EO-style resource refresh).

Map: icon for node type; **depleted** icon variant or greyed ([mapping](mapping.md)).

---

## Materials & synthesis

Materials are **stackable inventory items** (not gear). Bag model: [items & inventory](items-and-inventory.md) · [ADR 036](../../decisions/036-party-inventory-model.md) (Materials tab MVP2).

```
MaterialId, quantity → PartyInventory
  → Hub synthesis recipes consume quantities
  → Quest “Bring 3 Cedar” checks inventory
```

Example material IDs (content):

| Material | Source |
|----------|--------|
| `wood_cedar` | Chop (stratum 1) |
| `ore_copper` | Mine (stratum 1) |
| `herb_medicinal` | Forage |
| `fish_trout` | Fish (stratum 1 stream) |

Synthesis unlock: quests + hospital/stratum progress — see [character progression](character-progression.md).

---

## Content authoring

Per floor in `StratumFloor`:

```yaml
gather_nodes:
  - id: s1_b3_mine_01
    type: mine
    cell: [12, 8]
    facingRequired: south
    lootTable: mine_stratum1
    oncePerDive: true   # default

fish_nodes:
  - id: s1_b4_pond_01
    type: fish
    cell: [4, 15]
    lootTable: fish_stratum1
```

**Stratum 1 teaching:** B2F first forage (1 node), B3F mine, B4F chop + **first fish** on B4F stream ([dungeons & encounters](../03-content/dungeons-and-encounters.md)).

---

## UI & input (MVP2)

| Context | Input |
|---------|--------|
| Interact node | `Space` (exploration map) |
| Gather beats | `Space` on timing |
| Fishing hook | `Space` on bite flash |
| Cancel | `Esc` |

Combat map not used during minigame.

---

## Tech (Unity 6)

- `GatherNodeInstance` / `FishNodeInstance` on floor data
- `MinigameController` state machine: `None | Gather | Fish`
- `IGatherMinigame` / `IFishingMinigame` for UI + pure score logic (testable)
- Loot: `LootTable` ScriptableObject keyed by tier
- Save: node depleted flags per floor in dive save; clear on hub respawn trigger

---

## Scope checklist

| Item | MVP1 | MVP2 |
|------|-----|------|
| Placeholder gather tiles on map | Optional stub | Active nodes |
| Interact → loot | Instant or disabled | Minigame required |
| Fishing | — | Pond/stream nodes |
| Synthesis hub | — | Enabled |
| Gather quests | — | Quest counter |
| Marksman gather bonus | — | Optional |

---

## Related docs

- [Release scope](../00-release-scope.md)
- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
- [Hub & services](hub-and-services.md)
- [Mapping](mapping.md)
- [Character progression](character-progression.md)
