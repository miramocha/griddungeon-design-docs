# Game references

Curated titles for **future design and tone checks**. **(launch) authority** stays **Etrian Odyssey–first** ([00 — Vision](00-vision.md)); entries here inform optional systems, UX, and later ideas — they do not override locked ADRs unless we explicitly amend one.

**Naming:** Reference games inform **mechanics**, not **proper nouns**. Do not lift iconic item/skill/enemy names (e.g. EO `medica`, `amrita`, `nectar`). Use original IDs and display names per [tone brief](00-vision.md#tone--setting) — see Cursor rule `content-original-naming.mdc`.

---

## Primary (locked at launch)

| Game | Use in Grid Dungeon |
|------|---------------------|
| ***Etrian Odyssey*** (series) | Auto-map (no player drawing), FOEs, strata/floors, guild party, AGI combat, hub between dives, EO Union-style team burst → [Synchro Protocol](02-systems/synchro-protocol.md) |

### Etrian Odyssey IV+ — enemy formation (locked at launch)

From **Etrian Odyssey IV** onward, enemy lines use the same **front + back row** grid as the player party layout (not a single enemy row). Grid Dungeon adopts this cap at launch ([ADR 015](../decisions/015-mvp1-combat.md)).

| | Etrian Odyssey IV+ | Grid Dungeon (launch) |
|---|-------------------|-------------------|
| **Party on field** | Up to **5** members (front/back rows) | **6** core + **0–2** aux; Navigator off-formation |
| **Enemy formation** | Up to **3** front + **3** back (**6** occupied max) | Same **3+3** cap ([combat scene](02-systems/combat-scene.md#enemy-slots)) |
| **Arena presentation** | 2D/3D enemy lineup on battle stage | Slot rig `EnemySlot_0..5` on backdrop ([ADR 013](../decisions/013-combat-scene-rendering.md)) |

---

## Etrian Odyssey — hub & town loop

**Authority at launch hub rules** ([hub-and-services](02-systems/hub-and-services.md), [release scope](00-release-scope.md)). EO is the model for *what* the hub does; presentation can add MSK-style place-making **after** (launch) without changing service logic.

| EO beat | What EO does | Grid Dungeon |
|---------|--------------|--------------|
| **Camp / guild at the gate** | Town or camp **fixed** at the labyrinth entrance — not an open overworld | Single **guild town** scene from first hub visit (S1 Act 2); same layout throughout |
| **Service loop** | Guild, shop, hospital, inn/save, then **re-enter** stratum | (launch) menu tree: Explorers Guild, Navigator Office, shop, hospital, inn ([hub table](02-systems/hub-and-services.md#hub-locations-mvp1)) |
| **No marathon in the maze** | Heal, equip, save at hub; push depth deliberately | Inn primary save; no labyrinth save (launch); Return thread / gate stairs up |
| **Item bag** | Fixed slots; categorized browse in EO Nexus–style titles | Fixed **party bag** (default 30 slots), **category tabs** (All / Consumables / Equipment) — [items & inventory](02-systems/items-and-inventory.md) · [ADR 036](../decisions/036-party-inventory-model.md) |
| **Stratum entry** | Pick stratum / floor from hub or gate rules | **Enter Stratum** from hub; S1 gate spawn; S2+ warp gates ([dungeons § entry](../03-content/dungeons-and-encounters.md#stratum-entry--warp-gates-locked)) |
| **Hub navigation (EO titles vary)** | Older: **menu / icon** hubs; newer (e.g. Nexus): **walkable** 3D districts | **Menu-first** (EO classic) — **no** avatar walk; later **camera pan** on root-menu focus ([hub environment](02-systems/hub-and-services.md#hub-environment-presentation)) |
| **Presentation** | Often **static** illustration or simple 3D with direct facility pick | Full-screen 3D backdrop + UI overlay; pans **later** |

**Borrow from EO (locked):** service set, save-at-inn, return-before-overextending loop, guild party prep, strata as progression bands.

**Do not copy blindly:** EO2-style exploration TP; player-drawn maps; walk-only hub at launch (scope).

---

## Mary Skelter — hub & base (secondary)

MSK informs **feel** and **presentation bar**, not (launch) mechanics. Compare proposals to EO compatibility ([scratchpad](#mary-skelter--design-notes-scratchpad) below).

| MSK beat | What MSK does | Grid Dungeon |
|----------|---------------|--------------|
| **Base between tower floors** | **Hub / jail base** after nightmare dives — facilities, story, breathing room | Same macro loop as EO hub ([hub macro loop](02-systems/hub-and-services.md#macro-loop-eo-aligned)) |
| **Dungeon vs base contrast** | FPV **nightmare** labyrinth vs safer **base** with readable spaces | Exploration FPV grid + **non-walkable** guild town (menu + backdrop) |
| **Place readability** | Distinct **zones** in base (shop, clinic, etc.) even when navigation is not full open-world | Later: root-menu focus **pans** camera to shop / hospital / guild anchors — **one** shared gate for all **Enter Stratum** rows |
| **Combat / UI read** | Strong hit feedback, ailments, flashy skills | Reactive blocking HUD ([tech notes § UI reactivity](04-tech-notes.md#ui-reactivity)); sparse cinematics ([combat presentation](02-systems/combat-presentation.md)) |
| **Burst fantasy** | Transform / blood / rage spikes | **Synchro Charge** + Navigator only — MSK burst is **feel reference**, not a second meter ([ADR 006](../decisions/006-union-team-bar.md)) |

**Borrow from MSK (evaluate / later):** environmental **identity** per service (building silhouette readable in one pan); **light ambient** life in hub scene (idle NPCs, smoke — later MVP); reactive UI motion already on (launch) bar.

**Rejected unless ADR:** replacing Navigator + Synchro with MSK-style personal transform meters; action combat; manual map drawing.

### Hub presentation — EO + MSK synthesis

| Layer | EO (primary) | MSK (secondary) | Our call |
|-------|--------------|-----------------|----------|
| **Interaction** | Menus, clear service list | Base facilities, strong zone identity | Root **menu**; no hub walk |
| **World** | Camp at gate, return loop | 3D base with readable districts | **One** full-screen town scene |
| **Camera** | Mostly static / light transitions | Environmental storytelling in base | **Later** debounced pan on root focus (~150–300 ms settle) via **Cinemachine 3** ([ADR 033](../decisions/033-hub-environment-cinemachine.md)); **no pan** on locked rows or sub-menus |
| **Audio** | Facility jingles, understated camp | More atmospheric base | **Probably no** hub looping ambience; service UI SFX only (for now) |
| **Life** | Often minimal hub motion | More animated base | **Light ambient** scene motion — **later than (launch)** |

Full hub spec: [hub environment presentation](02-systems/hub-and-services.md#hub-environment-presentation).

---

## Secondary references

| Game | Relevant beats | Possible borrow (evaluate later) |
|------|----------------|----------------------------------|
| ***Mary Skelter: Nightmares*** / ***Nightmares 2*** | FPV grid labyrinth; **auto-map**; visible **strong enemies** on the map; hub/base between tower floors; turn-based combat with **ailments / binds** and flashy skill presentation; party of distinct roles | Map + FOE tension validation; reactive combat UI and telegraphing; dungeon **floor themes** and “tower climb” pacing; transformation / rage-style **burst modes** only if we want a parallel to Synchro (do **not** replace Navigator + Synchro Charge without ADR) |
| *Wizardry* | Hardcore dungeon crawl, wipe stakes | Death/save tone comparisons only — we follow EO hub model |
| *Shin Megami Tensei* / dungeon crawlers | Weaknesses, buff stacking | Light touch on elemental weaknesses ([combat](02-systems/combat.md)); full press-turn out of scope |

---

## Mary Skelter — design notes (scratchpad)

Use when reviewing exploration, combat UI, or “dungeon feel” features. **Not committed.**

| Topic | MSK angle | Grid Dungeon today |
|-------|-----------|-------------------|
| **Exploration** | FPV steps in a mapped tower | EO grid + auto-reveal ([ADR 002](../decisions/002-mapping-model.md)); floor painter + 2D HUD |
| **Map threats** | Boss / FOE-like map icons, routing matters | FOE step patrol ([ADR 003](../decisions/003-foe-step-patrol.md)) |
| **Combat read** | Strong VFX, clear hit / ailment feedback | Reactive blocking HUD ([04 — Tech notes](04-tech-notes.md#ui-reactivity)); Fixed presentation (launch) |
| **Hub loop** | Base camp between dives | Hub services + [EO/MSK hub synthesis](02-systems/hub-and-services.md#hub-environment-presentation) ([hub-and-services](02-systems/hub-and-services.md)) |
| **Burst modes** | Transform / blood / rage spikes | **Synchro Charge** + Navigator ([ADR 006](../decisions/006-union-team-bar.md), [007](../decisions/007-navigator-role.md)) — compare feel only |
| **Verticality** | Multi-floor tower structure | Strata + `level` bands ([ADR 019](../decisions/019-floor-verticality.md)) |

When a feature proposal cites Mary Skelter, link it here and note **EO compatibility** (grid step events, no action combat, read-only player map).

---

## Related

- [00 — Vision](00-vision.md)
- [00 — Release scope](00-release-scope.md)
- [(launch) spec](00-release-scope.md)
