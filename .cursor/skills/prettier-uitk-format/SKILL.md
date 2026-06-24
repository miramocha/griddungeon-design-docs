---
name: prettier-uitk-format
description: >-
  Formats UXML and USS with Prettier across a repo or selected paths. Use when the user asks to run Prettier,
  format UXML/USS, or fix UI Toolkit markup/styles before handoff or commit.
---

# Prettier — format UXML and USS

## When to use

- User wants `*.uxml` or `*.uss` files formatted, or a directory run through Prettier.
- **Before handoff** or **before commit** when UXML/USS is in scope (`format-before-handoff-and-commit.mdc`).

## Preconditions

- [Prettier](https://prettier.io) + [`@prettier/plugin-xml`](https://github.com/prettier/plugin-xml) installed via `npm install` at repo root (`package.json`).
- **Cursor extension:** `esbenp.prettier-vscode` — Format Document / format on save (`.vscode/settings.json` maps `*.uss` → CSS).
- Run from **griddungeon-game** root (folder with `Assets/` and `package.json`).

## Commands

From repo root:

```powershell
npm install
npx prettier --write path/to/File.uxml
npx prettier --write path/to/File.uss
npx prettier --write "Assets/UI/**/*.{uxml,uss}"
npm run format:uitk
npm run format:uitk:check
```

Config: `.prettierrc` — UXML: `parser: xml`, 4-space indent; USS: `parser: css`, 4-space indent.

## Agent workflow

1. Confirm root: `griddungeon-game` (parent of `Assets/`).
2. If `node_modules/` is missing: `npm install` once.
3. Format **changed paths only** unless the user asked for the whole tree:
   ```powershell
   npx prettier --write path/to/Changed.uxml path/to/Changed.uss
   ```
4. Re-run `git diff` after formatting.
5. If `npm install` or `npx prettier` fails, report it; do not substitute another formatter.

## Notes

- Prettier formats **`.uxml` and `.uss` only** in this repo — not `.cs` or YAML.
- USS uses Unity-specific properties (`-unity-*`); Prettier treats files as CSS — valid USS should still parse.
- CLI output should match **Format Document** with the Prettier extension on the same files.
- **Windows PowerShell:** use `;` instead of `&&` when chaining commands.
