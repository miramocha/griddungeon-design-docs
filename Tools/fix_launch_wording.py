#!/usr/bin/env python3
"""Editorial cleanup: fix awkward (launch) parentheticals from MVP1 migration."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

EXACT = [
    ("(launch)+", "later"),
    ("(launch) spec", "release scope"),
    ("[(launch) spec]", "[release scope]"),
    ("(launch) (locked):", "**Launch (locked):**"),
    ("(launch) (S1 unlock)", "Launch (S1 unlock)"),
    ("(launch) schema", "Launch schema"),
    ("(launch) UI", "Launch UI"),
    ("(launch) implementation", "Launch implementation"),
    ("(launch) equip reference", "Launch equip reference"),
    ("(launch) content:", "Launch content:"),
    ("(launch) use context", "Launch use context"),
    ("(launch) identify", "Identify at launch"),
    ("(launch) presents", "Launch presents"),
    ("(launch) S1:", "Launch S1:"),
    ("(launch) S1 uses", "Launch S1 uses"),
    ("(launch) S1 Story Events", "MVP1 S1 Story Events"),
    ("(launch) class skill", "launch class skill"),
    ("(launch) roster:", "Launch roster:"),
    ("(launch) kits:", "Launch kits:"),
    ("(launch) has no", "Launch has no"),
    ("(launch) ships", "Launch ships"),
    ("(launch) keeps", "Launch keeps"),
    ("(launch) Protocol", "Launch Protocol"),
    ("(launch) portrait", "launch portrait"),
    ("(launch) summon kit", "Launch summon kit"),
    ("(launch) migration:", "Launch migration:"),
    ("(launch) floors", "launch floors"),
    ("(launch) floor sizes", "launch floor sizes"),
    ("(launch) limit:", "Launch limit:"),
    ("(launch) authority", "Launch authority"),
    ("(launch) — Stratum 1", "Launch — Stratum 1"),
    ("(launch) layouts", "S1 layouts"),
    ("(launch) ASCII", "S1 ASCII"),
    ("(launch) dungeon floors", "launch dungeon floors"),
    ("(launch) instant loot", "instant loot at launch"),
    ("(launch) win condition", "required-slice win condition"),
    ("(launch) baseline", "launch baseline"),
    ("(launch) ailments", "launch ailments"),
    ("(launch) aux deploy", "launch aux deploy"),
    ("(launch) autopilot", "Launch autopilot"),
    ("(launch) exploration map", "launch exploration map"),
    ("(launch) combat", "launch combat"),
    ("(launch) exploration & map", "launch exploration & map"),
    ("Not (launch)", "Later"),
    ("Not (launch).", "Later."),
    ("for (launch)", "for launch"),
    ("within (launch)", "within the launch slice"),
    ("before (launch)", "before launch"),
    ("after (launch)", "after launch"),
    ("later than (launch)", "later than launch"),
    ("during (launch)", "during launch"),
    ("close (launch) on", "close the launch slice on"),
    ("optional (launch)", "optional at launch"),
    ("required (launch)", "required at launch"),
    ("(launch) has no autosave", "launch has no autosave"),
    ("(launch) menu tree", "launch menu tree"),
    ("(launch) bar", "launch bar"),
    ("(launch) default", "launch default"),
    ("(launch):", "At launch:"),
    ("(launch) =", "Launch ="),
    ("(launch) playtest)", "launch playtest)"),
    ("(launch) checklist", "launch checklist"),
    ("(launch) media", "launch media"),
    ("(launch) codex", "launch codex"),
    ("(launch) relies", "launch relies"),
    ("(launch) full coach", "Launch full coach"),
    ("(launch) coach", "launch coach"),
    ("(launch) targets", "launch targets"),
    ("(launch) summons", "launch summons"),
    ("(launch) `SummonScriptRunner`", "launch `SummonScriptRunner`"),
    ("(launch) uses **player control**", "Launch uses **player control**"),
    ("(launch) ships **`Fixed` only**", "Launch ships **`Fixed` only**"),
    ("(launch) ships static pins", "Launch ships static pins"),
    ("(launch) 2D map", "At launch, 2D map"),
    ("(launch) shows", "At launch, shows"),
    ("(launch) **content**", "Launch **content**"),
    ("(launch) world scale", "Launch world scale"),
    ("(launch) team burst", "Launch team burst"),
    ("(launch) folder tree", "folder tree"),
    ("(launch) save file", "MVP1 save file"),
    ("Apply s1_B1F (launch) layout", "Apply s1_B1F MVP1 layout"),
    ("Apply s1_B*n*F (launch) layout", "Apply s1_B*n*F MVP1 layout"),
    ("Grid Dungeon (launch)", "Grid Dungeon (launch slice)"),
    ("no labyrinth save (launch)", "no labyrinth save at launch"),
    ("not (launch) mechanics", "not launch mechanics"),
    ("Fixed presentation (launch)", "Fixed presentation at launch"),
    ("locked (launch))", "locked at launch)"),
    ("per row, (launch))", "per row, launch)"),
    ("unchanged from (launch) skeleton", "unchanged from launch skeleton"),
    ("click-block (launch)", "click-block launch UI"),
    ("Disabled (launch)", "Disabled at launch"),
    ("Concern | (launch)", "Concern | Launch"),
    ("| (launch) ([#87]", "| Launch ([#87]"),
    ("**(launch) (shipped):**", "**Launch (shipped):**"),
    ("## (launch) implementation", "## Launch implementation"),
    ("## (launch) checklist", "## Launch checklist"),
    ("### (launch) summon kit", "### Launch summon kit"),
    ("## Bag model (launch)", "## Bag model"),
    ("## Party menu shell (launch)", "## Party menu shell"),
    ("## Equipment pane (launch)", "## Equipment pane"),
    ("## ASCII symbols (launch)", "## ASCII symbols"),
    ("## Damage pipeline (launch)", "## Damage pipeline"),
    ("**Status:** Accepted (launch)", "**Status:** Accepted (required slice)"),
    ("## Decision (launch)", "## Decision"),
    ("## Decisions (launch)", "## Decisions"),
    ("## Rejected (for (launch))", "## Rejected for launch"),
    ("(launch) alternates", "Launch flow alternates"),
    ("early (launch) docs", "early launch docs"),
    ("mvp1-class-skills", "class-skills"),
    ("| No (launch) |", "| No at launch |"),
    ("| Method | (launch) input |", "| Method | Launch input |"),
    ("| Unit | (launch) control |", "| Unit | Launch control |"),
    ("| Player need | (launch) spec |", "| Player need | Release scope |"),
    ("PC (launch))", "PC launch)"),
    ("picker (launch)", "picker at launch"),
    ("enemy AI picks from `skillIds` (launch):", "enemy AI picks from `skillIds` at launch:"),
    ("+5% Synchro Charge gain (launch) starter)", "+5% Synchro Charge gain (launch starter)"),
    ("Does **not** change (launch) portrait", "Does **not** change launch portrait"),
    ("Coexists with (launch) **portrait strip**", "Coexists with launch **portrait strip**"),
    ("replacing (launch) portrait-only", "replacing launch portrait-only"),
    ("(launch) starter)", "launch starter)"),
    ("(launch) classes", "launch classes"),
    ("(launch) content", "Launch content"),
    ("(launch) trees:", "launch trees:"),
    ("(launch) uses", "Launch uses"),
    ("(launch) limit:", "Launch limit:"),
    ("(launch) §", "launch §"),
    ("dungeons — (launch) §", "dungeons — launch §"),
    ("# (launch) — Stratum 1", "# Launch — Stratum 1"),
    ("do not close (launch)", "do not close launch"),
    ("(launch) on this alone", "launch on this alone"),
    ("(launch) path linear", "launch path linear"),
    ("keep (launch) path linear", "keep launch path linear"),
    ("does not block (launch)", "does not block launch"),
    ("(launch) path", "launch path"),
    ("(launch) limit", "launch limit"),
    ("(launch) floors are", "launch floors are"),
    ("(launch) shows party", "At launch, shows party"),
    ("(launch) `Fixed` only)", "launch `Fixed` only)"),
    ("(launch) ships **`Fixed` only**", "Launch ships **`Fixed` only**"),
    ("Assigned at **Navigator Office** (launch).", "Assigned at **Navigator Office** at launch."),
    ("swap only at hub (launch).", "swap only at hub at launch."),
    ("stratum (launch):", "stratum at launch:"),
    ("six (launch) classes", "six launch classes"),
    ("| **Commands (launch)** |", "| **Commands (launch)** |"),
    ("| **(launch)** |", "| **Launch** |"),
    ("| **(launch)+** |", "| **Later** |"),
    ("(launch)+);", "later);"),
    ("**Tree (launch)**", "**Tree (launch)**"),
    ("every (launch) class skill", "every launch class skill"),
    ("**Visual rules (launch):**", "**Visual rules (launch):**"),
    ("**Roster vitals (launch):**", "**Roster vitals (launch):**"),
    ("| Event | UI reaction (launch) |", "| Event | UI reaction (launch) |"),
    ("| Keyboard (launch) |", "| Keyboard (launch) |"),
    ("Tab rules (launch):", "Tab rules (launch):"),
    ("### AGI turn phase (default (launch))", "### AGI turn phase (default at launch)"),
    ("Rebindable** in settings menu (launch):", "Rebindable** in settings menu at launch:"),
    ("rebind screen (optional at launch", "rebind screen (optional at launch"),
    ("Goals (launch)", "Goals (launch slice)"),
    ("## Phase 0 — Now (launch), single project)", "## Phase 0 — Now (launch slice, single project)"),
    ("## Phase 1 — Hardening (before launch ship", "## Phase 1 — Hardening (before launch ship"),
    ("Locked (launch) S1)", "Locked (S1 launch)"),
    ("S1 (launch)):", "S1 launch):"),
    ("Speaker | (launch) S1 |", "Speaker | S1 launch |"),
    ("Reveal pacing (S1 (launch)):", "Reveal pacing (S1 launch):"),
    ("(launch) = click-through block", "Launch = click-through block"),
    ("(launch) ships office", "Launch ships office"),
    ("(launch) (locked):**", "Launch (locked):**"),
    ("| Aura (launch) |", "| Aura (launch) |"),
    ("S1 gate (launch):", "S1 gate (launch):"),
    ("## Not in scope (launch)", "## Not in scope (launch)"),
    ("## Narrative role (launch)", "## Narrative role (launch)"),
    ("## Hub locations (launch)", "## Hub locations (launch slice)"),
    ("### Story events (launch)", "### Story events (launch)"),
    ("### Timing — core turn action (launch)", "### Timing — core turn action (launch)"),
    ("### Flee success (launch)", "### Flee success (launch)"),
    ("## `sortingOrder` stack (launch)", "## `sortingOrder` stack (launch)"),
    ("### Service migration status (launch)", "### Service migration status (launch)"),
    ("## Implementation checklist (launch)", "## Implementation checklist (launch)"),
    ("Stratum 1 (launch)", "Stratum 1 (launch)"),
    ("hub-and-services.md#hub-locations-mvp1", "hub-and-services.md#hub-locations-launch"),
]


def process(text: str) -> str:
    for old, new in EXACT:
        text = text.replace(old, new)
    # Remaining mid-sentence (launch) → at launch
    text = re.sub(r"\*\*\(launch\)\s+", "**Launch ", text)
    text = re.sub(r"(?<!\w)\(launch\)(?=[,.\s;])", "at launch", text)
    text = re.sub(r"At launch,\s+At launch,", "At launch,", text)
    text = re.sub(r"Launch Launch", "Launch", text)
    text = re.sub(r"launch launch", "launch", text)
    text = re.sub(r"at launch at launch", "at launch", text)
    return text


def main() -> None:
    # One-off fixes after bulk pass
    p = ROOT / "decisions/002-mapping-model.md"
    t = p.read_text(encoding="utf-8", errors="replace")
    if "At launch, shows" in t:
        t = t.replace(
            "At launch, shows party",
            "at launch, map shows party",
        )
        p.write_text(t, encoding="utf-8", newline="\n")

    p2 = ROOT / "docs/02-dungeon-navigation.md"
    t2 = p2.read_text(encoding="utf-8", errors="replace")
    t2 = t2.replace("**Grid → world (launch)**", "**Grid → world**")
    p2.write_text(t2, encoding="utf-8", newline="\n")

    changed = []
    for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.mdc")):
        rel = path.relative_to(ROOT).as_posix()
        if rel == "docs/archive/mvp1-spec.md":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        new = process(text)
        if new != text:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed.append(rel)

    rem = sum(
        path.read_text(encoding="utf-8", errors="replace").count("(launch)")
        for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.mdc"))
    )
    print(f"updated {len(changed)} files; remaining (launch): {rem}")


if __name__ == "__main__":
    main()
