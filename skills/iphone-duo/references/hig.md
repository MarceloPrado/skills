# Apple's Human Interface Guidelines for iPhone Duo

[Designing for iPhone Duo][hig] is the one HIG page about the device. No other HIG page mentions it. Apple published it on September 9, 2026, and this digest was checked against it on October 22, 2026.

The digest follows the page's sections in our words. Each point ends with the rules in `rules.md` that build it. Read it in Propose to choose a layout and in Verify to judge a screenshot. The page outranks the digest and the rules, so when they disagree, fix them.

The page is a JavaScript app, and fetching its URL returns no text. This prints it, change log last, so you can see whether Apple changed it since the date above:

```bash
python3 <skill-dir>/scripts/apple_doc.py https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo
```

The script also reads the developer documentation and technotes that `rules.md` links. Figures come through as their descriptions only. Open the page in a browser when a decision turns on a figure.

## Anatomy

- Closed, people use the outer display, and the system lines the toolbar and the tab bar up along its side so content keeps the height. Open in landscape, the bars stay on the side, so moving between displays feels the same. (B1)
- The hinge lets people hold the device and set it down in many ways, and folding it takes space away from content. (F4)
- The outer camera sits in a corner, always visible and lined up with the side controls. The inner camera stays hidden under the display until it's in use. (F4)

## Device poses

- People fold it partway like a book, lay it on a surface, or stand it on its edges. Don't design a layout per pose. Lay out for compact width closed and regular width open, and every pose follows. Let the layout you have grow into the space instead of reinventing the app. (L2, L6)
- Device Hub in Xcode previews the app in each pose. (A5)

## Best practices

- **Plan for many sizes.** Two displays, many poses, and Split View give the app many sizes. Lay out from safe area insets, layout margins, and size classes, with no fixed widths and nothing tied to one display. (L1, L2, L3, L8)
- **One app on both displays.** Features and the state of every element carry over. The hierarchy stays the same, and the inner display may add one level of it when the content has one. Mail shows a list or a message closed, and both side by side open. (C1, C2, L4)
- **Nothing goes missing in a pose.** Controls can spill into overflow and content can shift or resize, but people reach the same controls and content however they hold the device. (C3, B6)
- **Let the system put the bars on the side.** Next to other iPhones the outer display is short and wide, so the system moves the bars to the side to save height and to suit that asymmetry. Standard components get this for free. Refine it rather than replace it. (B1, B2)
- **Games fill every pose.** A game may lock its orientation, but it fills the screen as the pose changes and keeps text and controls the same size. Change the aspect ratio rather than letterbox, and put artwork in any bars you can't avoid. (A3, P5)

## Dynamic layouts

- As on any iOS device, start from the safe area and the layout margins, and avoid fixed widths and anything specific to one display. (L3, L8)

### Reserved regions

- Reserved regions also shape the space. Content stays out of them, or components adapt around them, as layouts do around the window controls on iPad. (F4)
- The outer camera is always reserved, and the reservation widens into the Dynamic Island while a Live Activity runs. Bars on the side already make room for it. (F4)
- The inner camera is reserved only while it's on. The UI moves aside when it turns on, which shows the camera is there. (F4)
- The fold is reserved only while the device is partly open. It splits the inner display and takes its center out of use. (F2, F4)
- Alerts, context menus, and sheets move off the fold on their own. Split views match their column widths and margins to the inner display's symmetry. Custom components find the regions with `ReservedRegion` in SwiftUI and `UIView.ReservedRegion` in UIKit. (F1, F4)
- As the device folds, a container that adjusts itself works best. Notes' split view evens out its panes as it folds. A grid takes an even column count so the fold falls between columns. Where the system doesn't move an important element, keep it off the center with `ReservedRegion`. (F1, F3, F6, L6)
- Avoid big layout changes as the device folds. Move only what must move to stay visible and easy to tap, and prefer small shifts to rearranging, because a control that vanishes or jumps is hard to find again. (F5)

### Split views

- A split view is several columns open and one column closed, the same switch it makes between regular and compact width on other iPhones. Built from standard components, it adjusts its widths and margins around the fold by itself. (L4, F1)

### Arrangement views

- An arrangement view holds a primary and a secondary view and places them by the display's size and orientation and by the reserved regions. (F3)
- A split arrangement divides the space between them. They sit side by side when it's wider than tall and stack when it's taller than wide. (F3)
- An overlay arrangement layers them. Partly folded, each takes one side of the fold. Otherwise the primary view sits on top of the secondary. (F3)
- A split arrangement can be held to one axis, and an overlay can hide its secondary view. (F3)
- Reach for one when the layout already looks like one. Views side by side or stacked, as in an `HStack` or a `VStack`, become a split arrangement. Layered views, as in a `ZStack`, become an overlay. (F3)
- Keep navigation outside it. It only arranges content, so navigation split views and tab views wrap it. (F3)

## Vertical controls

- Bars that usually sit at the top and bottom move to the side, which saves height and keeps them in reach. The inner display in portrait keeps horizontal bars. (B1)
- The status bar and the Dynamic Island share the side with the app's toolbar, its navigation buttons, and its tab bar. (B1)
- With two apps side by side on the inner display, each keeps its controls on the edge away from the other, so the left app's controls are on the left. (M1)
- The side controls belong to the hardware. They keep their place next to the outer camera and don't swap sides for right-to-left languages. (L3)
- **Expect uneven space.** Controls along one edge leave the content area lopsided. Use safe areas so no control covers content, including the other app's controls on the far edge in Split View. (L3, M1)
- **Keep controls where people left them.** Not every pose puts controls on the side, and the room changes, so keep their relative positions as close as possible and people don't relearn where actions are. (C3, F5)
- **Order the strip from the top.** Primary navigation like Back or Close goes first, then prominent actions like Done. Other items keep their original groups, and the system adds space between what came from the top bar and what came from the bottom bar. (B2)
- **Rank items by use.** Items overflow from the bottom up by default. Set visibility priority on whole groups first, then on single items. Keep the most used actions, such as Mail's Compose and Notes' New Note, and items that carry status in a badge, visible longest. (B6)
- **Leave the bars on the side.** Their place on the side is a core pattern of the device, and familiar positions help people learn the app. Override it only with a reason. (B9)
- **Go full width only without bars.** A screen that doesn't scroll and needs no bars, like Calculator, can span the display if the Dynamic Island and the status bar stay clear. A background or a header can also span it while scrolling content stays inset. (B12)
- **Group items instead of spacing them.** Toolbar item groups space themselves and adapt as the room changes, so add no fixed spacing. (B10)
- **Put controls by the content they change.** Controls that belong to a leading pane stay with it rather than joining the strip on the trailing edge. Mail keeps its list's controls above the list. (B13)
- **Give items a title and a symbol.** Every item that isn't text only gets both, and the system picks the form that fits. The title shows in the overflow menu and wherever the item expands, even when the item shows a symbol. (B3)
- **Few text buttons.** An item labeled with text stays in a horizontal bar, so use a symbol wherever one works. (B4)
- **Choose the bar to keep when room runs out.** A screen people navigate from keeps its tab bar and sends toolbar items to overflow, which is the default. A screen built around a task minimizes the tab bar to keep its toolbar, like the minimized tab bar on other iPhones. (B8)
- **One overflow menu.** Move the actions of your own overflow menu into the system one. The ellipsis means overflow, so give other menus another symbol. (B7)

## Rules from other sources

The rules not named above come from the developer documentation, the tech talks, the technotes, App Store Connect, or what the simulator showed. The links at the end of each rule in `rules.md` say which.

[hig]: https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo
