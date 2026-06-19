# UITK UXML visualization examples

## CommandRail — static UXML tree

Source: `Assets/UI/Screens/Shared/CommandRail.uxml` (current shipped layout).

```
CommandRailPresenter (UIDocument, sort 15 / 255 party)
└── command-rail                          [context BEM picks mode]
    ├── command-rail-combat               [Combat phase]
    │   └── command-panel
    │         ├── cmd-target-prompt
    │         └── cmd-attack … cmd-back
    ├── hub-command-rail                  [Hub phase, Tab closed]
    │   ├── command-rail__header
    │   │     ├── hub-title
    │   │     └── hub-credits
    │   └── hub-rail-body
    │         ├── hub-root-menu           ← town services
    │         └── hub-service-rail        ← Buy/Sell built in code
    └── party-menu-nav                    [Tab — Hub or Exploration]
          └── command-panel
                └── party-menu-section-* 
```

## Phase → visible branch

| Phase | Tab | Context class | Visible rail branch |
|-------|-----|---------------|---------------------|
| Hub | closed | `command-rail--context-hub` | `hub-root-menu` |
| Hub | closed, Shop open | `command-rail--context-hub` | `hub-service-rail` |
| Hub / Exploration | Tab | `command-rail--context-party-menu` | `party-menu-nav` |
| Exploration | closed | hidden | *(none)* |
| Combat | — | `command-rail--context-combat` | `command-rail-combat` |

## Related overlays (separate UIDocuments)

```
HubHud
└── hub-hud
      └── item-list-picker              [Shop stock — not CommandRail]

PartyMenuOverlay
└── party-menu                          [Tab backdrop + dialog]
      └── party-menu-stage (--rail-docked 240px)

ExplorationMap (MinimapPanel / ExpandedMapPanel — C# grid host)
└── map-view                         [MapGridHostBuilder per UIDocument]

PartyFormationFloater
└── party-formation-floater          [bottom 2×4 strip]

PartyMenuOverlay
└── party-menu                       [Esc / Tab pause shell]

CombatHud
└── combat-hud
      ├── center / rosters / log modal
      └── skill-picker / item-list-picker
```

## Rail transition targets (animation only)

| User action | Animated node | Document |
|-------------|---------------|----------|
| Hub → Shop | `hub-service-rail` | CommandRail |
| Hub / Exploration → Tab | `party-menu-nav` | CommandRail |
| Shop → Buy/Sell list | `item-list-picker` | HubHud (PopIn) |
| Tab → Z open pane | `party-menu-dialog` | PartyMenu (PopIn) |

## Code-built hosts (annotate in trees)

| Host | Builder | Notes |
|------|---------|-------|
| `hub-service-rail` | `HubHudServicePanelView.Populate` | Buttons created at runtime |
| `hub-root-menu` | UXML today; planned code-driven refactor | |
| `party-menu-nav` | UXML today | Same `CommandRail` instance for Hub + Exploration Tab |

## Grep starters (CommandRail)

```powershell
rg "CommandRail\.|hub-btn-|party-menu-section|cmd-" Assets/Scripts --glob "*.cs"
rg "CommandRailPresenter|CommandRailView" Assets/Scripts Assets/Tests
```
