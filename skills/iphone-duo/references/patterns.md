# Patterns by kind of screen

Find each screen's archetype, then start from its row. Every pattern keeps the closed layout as the base and spends the inner display on more content or one more level of hierarchy. Rule ids point to `rules.md`.

The poses in the table:

- **Closed.** The outer display, compact width, with the strip on the side.
- **Open.** The inner display flat in landscape, regular width, with the strip on the side.
- **Book.** Half-open with the fold running top to bottom. Two pages.
- **Laptop.** Half-open on a table with the fold running across. Content on top, controls at the bottom.

The inner display flat in portrait keeps horizontal bars and lays out like a tall Open.

| Archetype | Closed | Open | Book | Laptop | Build with |
| --- | --- | --- | --- | --- | --- |
| List and detail (mail, notes, chats, settings, a library) | The list, pushing to the detail | The list and the detail side by side | One column per half | Same as Open, columns split at the fold | `NavigationSplitView`, `UISplitViewController` (L4) |
| Feed or grid (social, photos, a catalog) | One or two columns | Three or four columns, an even count | The grid splits cleanly at the fold | The grid scrolls across the fold | `LazyVGrid` with a computed even count, compositional layout (L6, F6) |
| Media and text (a product, a post, a recipe, an exercise) | Media above the text | Media leading, text trailing | Media on one page, text on the other | Media on top, text and actions below | `ArrangementView` with `.split` (F3) |
| Conversation | The thread and the composer | The conversation list and the thread | List on one page, thread on the other | Thread on top, keyboard below | `NavigationSplitView` (L4) |
| Player (video, audio, live) | The player at full width, controls in the strip | Video full bleed, with the queue, chat, or transcript beside it | Video on one page, the queue on the other | Video on top, transport controls below | `ArrangementView` (`.split` or `.overlay`), `.backgroundExtensionEffect()` (F3, B12, P2) |
| Dashboard (health, money, training stats) | One column of cards | Two columns or a card grid, a sidebar if there are many sections | Cards split at the fold | The key number on top, actions below | `Grid`, `ViewThatFits`, `.sidebarAdaptable` (L5, L6) |
| Editor or form | Fields, with tools in the strip | The canvas and a tools panel, or a two-column form | The canvas on one page, tools on the other | The canvas on top, tools and keyboard below | `.inspector`, `Form` in a split view (B15, L4) |
| Capture (camera, scanner) | The preview fills the display, controls in the strip | The preview offset or filling, controls in the strip | Preview and controls on separate pages | Hands-free capture with the preview on top and controls below | `AVCaptureDeviceDirectionCoordinator`, `CameraCaptureAccessory` (P4, M4) |
| Focused task (a timer, a workout in progress, a calculator, a checkout) | Full width, nothing under the strip or the island | The task and its context side by side | The task on one page, context on the other | What to glance at on top, large controls below | `ArrangementView` with `.split`, reserved regions (F3, F4, P2) |
| Onboarding and hero | Art above the text | Art leading, text trailing at a readable width | Art on one page, text on the other | Same as Open | `ArrangementView`, `.backgroundExtensionEffect()` (F3, B12) |
| Search | The field in the strip or at the top | Results with a preview of the selected one | Results on one page, the preview on the other | Results on top, the keyboard below | `Tab(role: .search)`, `.searchable`, `NavigationSplitView` |
| Game | Fills the display, nothing under the strip | Fills the display at the new aspect ratio | Plays across both halves or one per half | The board on top, controls below | Size from the scene, never letterbox (P5) |

## Notes per archetype

**List and detail.** Closed shows the list or the item, never both. Open shows both, and the selection survives the transition (C2). Keep the list's own controls, like filters and sort, above the list (B13).

**Feed or grid.** Count columns from the width you get and round down to an even number on the inner display (L1, L6). Keep the item the person was looking at in view across the fold (C1).

**Media and text.** Don't let a hero image crop its subject at 1.4 to 1 (L7). Plain `.split` puts media and text side by side when the view is wider than tall and stacks them when it is taller. Add `.axes(.horizontal)` only when the media alone is right for tall layouts.

**Player.** A video that stays phone-sized after the device opens wastes the inner display (L7). Let it grow when open. Put the queue, chat, or transcript beside it, not under it. In the laptop pose, the controls go to the bottom half (P2).

**Focused task.** These screens often hide the tab bar and draw their own chrome. Put the chrome back into the toolbar where possible (B1). What stays custom needs reserved regions (F4). The laptop pose is often the best pose for these screens, because the person sets the device down to do the task.

**Onboarding.** Paging art and a text block centered at phone width look empty on the inner display. Put the art and the text side by side, and keep the text at a readable width (L6).

## ASCII wireframes

Sketch the inner display at about 1.4 to 1, with the strip on the trailing side, and the laptop pose as two stacked halves.

```
Open (inner, landscape)                      Laptop (half-open, fold across)
+------------------------------------+---+   +------------------------------+
| list          | detail             | < |   |  content to watch            |
|               |                    | + |   |                              |
|               |                    | . |   +------------ fold ------------+
|               |                    |   |   |  large controls              |
+------------------------------------+---+   +------------------------------+
```
