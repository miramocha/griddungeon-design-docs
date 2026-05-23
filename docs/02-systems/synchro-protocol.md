# Synchro Protocol (Team Bar)

**Locked name** ([ADR 020](../../decisions/020-team-burst-naming.md)). Replaces working name **Union**.

Party-wide **Synchro Charge** (team resource) for coordinated **Protocol** actions, executed by the active **[Navigator](navigator.md)**. Inspired by *Etrian Odyssey V* Union skills; shown as a **single shared meter** in combat UI.

### Resource vs action (parallel to core combat)

| | **Core six** | **Party / Navigator** |
|---|--------------|-------------------------|
| **Resource** | MP | **Synchro Charge** (0–100%, one pool) |
| **Action** | Skill (attack, guard, skill, item) | **Protocol** (`CombatCommand.Protocol`) |
| **Spend** | MP cost per skill | Full charge (100%) → **0%** on Protocol use |

C# uses `SynchroBar` / `SynchroBarDelta` for this pool ([ADR 020](../../decisions/020-team-burst-naming.md)); player-facing meter label stays **Synchro**.

## Synchro Charge

| Property | Rule |
|----------|------|
| **Range** | 0–100% (one pool for the whole party) |
| **UI** | Prominent combat meter (label: **Synchro** — not “Charge”) |
| **Gain** | **Core six** combat actions only |
| **Spend** | **Navigator** executes a Protocol when charge is **100%** |

## Gaining Synchro Charge

### When leaving hub

- Charge set to **100%** when party enters the labyrinth from hub — **except** before Stratum 1 Synchro tutorial ([§ S1 tutorial gating](#s1-tutorial-gating-first-foe)).
- Navigator auras may modify gain rate (e.g. `guild_handler` +5%) — only while Synchro is **unlocked**.

### S1 tutorial gating (first FOE)

**Campaign:** [S1 intro — flags & beats](../03-content/campaign/s1-intro.md) · **Implementation:** [game #10](https://github.com/miramocha/griddungeon-game/issues/10) (combat rules / `TutorialCombatKind`) · [game #19](https://github.com/miramocha/griddungeon-game/issues/19) UI epic → [#35](https://github.com/miramocha/griddungeon-game/issues/35) (Synchro meter + tutorial prompts)

**Campaign flags:** `s1_synchro_unlocked` (mid-fight), `s1_synchro_protocol_tutorial_done`, `s1_first_foe_tutorial_complete` (see table below).

| State | Synchro Charge | Gain in combat | Protocol (`U` / core turn) | Hub → labyrinth |
|-------|----------------|--------------|----------------------------|-----------------|
| **Before first FOE contact** | Hidden / locked | **No gain** | **Disabled** | **0%** |
| **First FOE phase A** (start) | Locked | No gain | Disabled | — |
| **Crisis → guided Protocol** | **100%** after unlock VN | No gain until unlock | **Guided** `protocol_strike` only | — |
| **After tutorial complete** | Normal | Normal | Normal | **100%** on hub exit |

**First FOE (locked):** `foe_alley_stalker` on `s1_B2F` — mandatory tutorial fight ([campaign S1](../03-content/campaign/s1-intro.md) · [dungeons — B2F](../03-content/dungeons-and-encounters.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe)).

1. **Act 3 path** — block B3F until `s1_first_foe_tutorial_complete`.
2. **`noFlee: true`** — cannot skip the lesson.
3. **Unbeatable FOE** — until Protocol resolve, enemies **cannot be killed** (HP floor at 1 / `tutorialUnbeatable`); normal damage does not end the fight.
4. **Scripted beat order (locked)** — full sequence in [story events § S1 tutorial flow](story-events.md#s1-tutorial-flow-foe_alley_stalker); summary:

| Step | What happens |
|------|----------------|
| **A — Opening** | Synchro locked; normal tutorial combat (FOE on HP floor if player focuses it). |
| **B — Crisis trigger** | When **2 completed core turns** OR **FOE at HP floor** (first): scripted **FOE crisis AOE** — party-wide hit reduces **all living core HP to 1** (fake wipe; **no** game over, cores stay up). |
| **C — Unlock VN** | After crisis UI beat: **`s1_synchro_protocol_unlock`** — Navigator briefing; set `s1_synchro_unlocked`, Synchro **100%**. |
| **D — Guided Protocol** | [Guided tutorial](guided-tutorial.md#combat-guided-tutorial-s1--protocol) — HUD highlights **Protocol**; player must confirm **`protocol_strike`** (only allowed command). |
| **E — Protocol finisher** | `protocol_strike` resolves; FOE **dies** (tutorial unbeatable lifted for this hit); set `s1_synchro_protocol_tutorial_done`. |
| **F — Exit VN + hub** | **`s1_tutorial_hub_return`** — short outro; **scripted warp to hub** (not normal combat → exploration on B2F); set `s1_first_foe_tutorial_complete`. |

5. **Crisis AOE** — authored scripted enemy action (display-only or minimal rules damage); must not KO cores — clamp living core HP to **1**. FOE HP may stay at floor through crisis.
6. **Hub return** — exceptional `Combat → Hub` transition ([game phase](game-phase.md)); player re-enters stratum from hub when ready (mouth spawn per [S1 intro](../03-content/campaign/s1-intro.md)).

Random fights before this FOE contact: Synchro **locked**. `CombatEntryContext.tutorialKind = SynchroFirstFoe` in implementation ([combat](combat.md)).

### During combat

While charge is below 100%, **core formation members** add to the shared pool:

| Event | Synchro gain (MVP1 baseline — tune in data) |
|-------|-------------------|
| Normal attack | +4% |
| Skill used | +6% |
| Guard | +3% |
| Item use | +2% |
| Core member takes HP damage | +2% (once per hit) |
| Enemy killed (participating in kill) | +5% |
| Core member downed | −25% charge |
| Combat ends (victory) | +10% if charge below 100% (optional catch-up) |

- **Navigator** does not act in AGI queue — does not directly add charge.
- **No gain** from aux summons/guests or enemy actions.
- Charge cannot exceed 100%.
- **Between battles** on the same floor: charge **persists** (if unlocked).
- **Return to hub:** charge reset to **100%** when unlocked; **0%** and locked when `s1_synchro_unlocked` false.

Exploration steps do **not** charge Synchro.

## Spending — Protocol skills (Navigator)

| Rule | Detail |
|------|--------|
| **Invoker** | **Core** on their AGI turn when charge is 100% ([Timing](#timing--core-turn-action-mvp1)) |
| **Executor** | Active **Navigator** off-formation ([navigator.md](navigator.md)) — no Navigator AGI turn |
| **Cost** | Charge → **0%** after use |
| **Threshold** | Charge must be **100%** |
| **Participants** | Living **core six** per skill min/max; downed excluded |
| **Aux** | Do not participate (MVP1) |
| **Skill list** | Navigator kit + guild-unlocked common Protocols |

### Timing — core turn action (MVP1)

When **Synchro Charge** is **100%**, a **core member** on their AGI turn may use **Protocol** (`CombatCommand.Protocol`) instead of attack/guard/skill/item:

1. Player picks a Protocol from the **Navigator’s** available list (Navigator executes; living core join per skill rules).
2. Resolve effects; charge → **0%**; that character’s turn ends (normal queue advance).
3. Other core/enemy/summon turns continue in AGI order.

Each time charge is **100%**, the party may invoke **one** Protocol on a core turn (spend resets charge to **0%**). The same fight may use **multiple** Protocols if Synchro **recharges** during combat ([ADR 006](../../decisions/006-union-team-bar.md)). **Blocked** only while a Deploy **sortie is alive** or a **Transform** is active ([ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md), [ADR 024](../../decisions/024-protocol-transform.md)).

```
Combat round:
  AGI turn phase (core may choose Protocol when Synchro = 100%)
  → End of round
```

## Protocol skill list (draft)

**Common** (guild unlock) + **Navigator-specific** extras:

| Skill | Participants | Effect |
|-------|----------------|--------|
| **Protocol Strike** | 2+ | Damage all enemies (MVP1: `protocol_strike`) |
| **Protocol Guard** | 3+ | Party damage reduction 1 turn |
| **Protocol Mend** | 2+ | Heal all living core (MVP1: `protocol_mend`) |
| **Protocol Retreat** | 4+ | High chance flee to floor entrance |
| **Protocol Scan** | 1+ | Register enemy in codex |

### Skill ideas (post-MVP1)

Not MVP1. [ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md) (Deploy) and [ADR 024](../../decisions/024-protocol-transform.md) (Transform). Navigator stays off-formation ([ADR 007](../../decisions/007-navigator-role.md)). **Recharge loop:** multiple Protocols per battle when Synchro hits **100%** again; **not** while sortie or transform is active.

| Skill | Participants | Effect |
|-------|----------------|--------|
| **Protocol Deploy** (`protocol_deploy`) | 3+ | **Core** spends AGI turn; Navigator spawns **sortie summon** in empty aux slot ([ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)). Scripted sortie turns. No Protocol while sortie lives; may **Deploy again** later if aux empty + Synchro full. Aux label: **Navigator display name**. |
| **Protocol Transform** (`protocol_transform`) | 3+ | **Core** spends AGI turn; **any living core** target; **slot-replace** with transform profile ([ADR 024](../../decisions/024-protocol-transform.md)). **Hybrid** + **Revert** / duration / HP→0 revert safe. No Protocol while transform active; may **Transform again** after revert + recharge. UI: profile name + **“via [CoreName]”**. |

**Locked:** aura on during Deploy/Transform; core six (and transform profile) charge Synchro; no overlapping sortie + transform.

### Kit + hub lock (practical)

Protocols come from the **active Navigator’s fixed kit** only ([navigator.md](navigator.md)). **No mid-dungeon Navigator swap** ([ADR 007](../../decisions/007-navigator-role.md)) — the party cannot switch to another Navigator’s Protocol list during exploration or combat.

| Implication | Detail |
|-------------|--------|
| **Deploy → Transform in one fight** | Only if **that** Navigator’s kit includes **both** `protocol_deploy` and `protocol_transform` — a **content** choice, not a hub swap |
| **Typical dive** | Most Navigators expected to offer **one** post-MVP1 mode skill (Deploy **or** Transform) plus common Protocols (Strike, Mend, …); repeated Protocols in a fight are usually **Strike/Mend** recharges |
| **Overlap rule** | Engine still blocks sortie + transform **at once**; sequential Deploy then Transform is rare but valid when kit allows |

**Content guidance:** prefer **one mode Protocol per Navigator** so players pick Navigators at hub for identity, not to combo Deploy and Transform in a single battle.

## Presentation

- Navigator portrait leads Protocol command ([combat presentation](combat-presentation.md)).
- Highlight participating core portraits.

## MVP1

**Design (locked — this doc):**

- [x] Synchro Charge + Protocol on core turn at 100%
- [x] Default Navigator kit: `protocol_strike`, `protocol_mend` ([Navigator](navigator.md) · [class design § MVP1 IDs](../05-class-design-mvp1.md#mvp1-content-ids-locked))
- [x] Core actions gain Synchro Charge; Navigator off-formation
- [x] S1 tutorial gating specified (flags, phases, [campaign S1](../03-content/campaign/s1-intro.md))

**Implementation (game — open):**

- [ ] S1 gate: crisis AOE → VN unlock → guided `protocol_strike` → FOE kill → hub warp ([#10](https://github.com/miramocha/griddungeon-game/issues/10), [#35](https://github.com/miramocha/griddungeon-game/issues/35), [story events § S1 flow](story-events.md#s1-tutorial-flow-foe_alley_stalker))

## Not in scope (MVP1)

- Per-character Synchro gauges
- Aux in Protocol skills
- **Boost/Break**

## Related docs

- [Navigator](navigator.md)
- [Combat](combat.md)
- [ADR 006 — Team bar mechanics](../../decisions/006-union-team-bar.md)
- [ADR 020 — Naming](../../decisions/020-team-burst-naming.md)
- [ADR 007 — Navigator role](../../decisions/007-navigator-role.md)
- [ADR 023 — Protocol Deploy sortie summon](../../decisions/023-protocol-deploy-sortie-summon.md)
- [ADR 024 — Protocol Transform](../../decisions/024-protocol-transform.md)
