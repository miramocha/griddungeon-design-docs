---
name: validate-unity-meta
description: >-
  Validates Unity .meta GUIDs in griddungeon-game. Use when creating Assets from
  design-docs sessions or diagnosing CS0246 after agent-added scripts.
---

# Validate Unity metadata (game repo)

Implementation lives in **griddungeon-game** only (this repo has no `Assets/`).

Follow the full workflow in:

[griddungeon-game/.cursor/skills/validate-unity-meta/SKILL.md](https://github.com/miramocha/griddungeon-game/blob/main/.cursor/skills/validate-unity-meta/SKILL.md)

Quick run from game repo root:

```powershell
python Tools/validate_unity_meta.py
```

Rule (game repo): `unity-meta-files.mdc` — link via `scripts/link-cursor-rules.ps1` if needed.
