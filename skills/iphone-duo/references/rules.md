# iPhone Duo rules

Each rule comes from Apple's iPhone Duo guidance, linked at the end of the rule. `hig.md` leads from each point of Apple's Human Interface Guidelines to the rules that build it. Apple's documentation, technote, and HIG pages are JavaScript apps, so read a linked one with `scripts/apple_doc.py <url>`. Every snippet type-checks against the iOS 27.1 SDK. The repo's `tests/run.sh` checks them.

The ids are stable. The scanner, `SKILL.md`, `hig.md`, and `patterns.md` cite them.

## A. Build and configuration

**A1. Build with Xcode 27.1 or later.** The SDK decides what the person sees. An app built with the iOS 26 SDK or earlier runs letterboxed and stays out from under the status bar and the camera. An app built with the iOS 27.0 SDK resizes with the display, but the strip needs the latest SDK, so its bars stay horizontal. An app built with the iOS 27.1 SDK fills the display and gets the strip. Rebuilding is the opt-in, and the person sees the difference before any code changes. [Doc][doc], [Steps][steps], [T61][t61], [T62][t62]

**A2. Remove `UIRequiresFullScreen` last.** Since iOS 27 the key no longer stops resizing. With it set, the system resizes the scene discretely, changing its size once when a resize ends instead of while it happens. Remove the key in the same change that makes every screen resize cleanly. Leave `UIRequiresFullScreenIgnoredStartingWithVersion` to the app owner, because its value decides which releases keep the old behavior. [TN3192][tn3192]

**A3. Expect every orientation on the inner display.** On the iPhone Duo simulator, a portrait-only app built with the iOS 27.1 SDK gets a landscape UI when the device opens, and a portrait UI when it is rotated. Closed, the lock holds, and the outer display stays portrait when the device turns. The lock does not protect a layout that assumes portrait. Size from the scene, never from the orientation you expect. Games may lock orientation, but they must fill the screen as the pose changes. [HIG][hig], [Steps][steps]

**A4. Declare a launch screen.** iOS 27 rejects an upload with no launch screen (`ITMS-90870`). Any one of `UILaunchScreen`, `UILaunchScreens`, `UILaunchStoryboardName`, `UILaunchStoryboards`, or `INFOPLIST_KEY_UILaunchScreen_Generation = YES` is enough. [TN3208][tn3208]

**A5. Test on the iPhone Duo simulator.** It needs the iOS 27.1 simulator runtime. Device Hub in Xcode 27.1 folds, opens, and rotates it. `verify.md` has the commands. [HIG][hig], [Doc][doc]

**A6. Gate the new APIs on iOS 27.1.** The SDK marks the vertical bar, arrangement, reserved region, and hinge APIs available from iOS 27.1. When the app supports earlier releases, wrap them in `if #available(iOS 27.1, *)` and keep the old layout in the other branch.

```swift
extension View {
    @ViewBuilder func horizontalSheetBar() -> some View {
        if #available(iOS 27.1, *) {
            toolbarVerticalBehavior(.disabled)
        } else {
            self
        }
    }
}
```

## B. Bars on the vertical axis

The system moves the toolbar, the navigation buttons, and the tab bar into one strip on the side, together with the status bar and the Dynamic Island. This happens on the outer display and on the inner display in landscape. The inner display in portrait keeps horizontal bars.

**B1. Put bars in navigation containers.** The system only moves bars it owns. In SwiftUI, use `.toolbar` inside a `NavigationStack` or a `NavigationSplitView`, and `TabView` for tabs. In UIKit, set items on a view controller inside a `UINavigationController` or a `UITabBarController`. A standalone `UIToolbar`, `UINavigationBar`, or `UITabBar`, and any custom bar view, stays where you drew it. [HIG][hig], [Doc][doc], [T62][t62]

```swift
NavigationStack {
    WorkoutList()
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Close", systemImage: "xmark") { dismiss() }
            }
            ToolbarItem(placement: .topBarPinnedTrailing) {
                Button("Done", systemImage: "checkmark") { save() }
            }
        }
}
```

**B2. Order the strip from the top.** Put primary navigation first, like Back or Close (`.cancellationAction`, or `leadingItemGroups` in UIKit). Put the prominent action next, like Done (`.topBarPinnedTrailing`, or `pinnedTrailingGroup`). Keep the other items in their original groups. The system adds space between what came from the top bar and what came from the bottom bar. [HIG][hig], [T62][t62]

**B3. Give every item a title and a symbol.** The strip shows the symbol. Overflow shows both. By default, an item with only a title or only a custom view stays out of the strip. Use `Label`, `Button(_:systemImage:action:)`, or `UIBarButtonItem(title:image:primaryAction:menu:)`. [HIG][hig], [Doc][doc]

**B4. Prefer symbols over text buttons.** Text-labeled items stay in a horizontal bar. Keep text only when the text is the information, like a price. Show counts as badges: `.badge(3)` in SwiftUI, `item.badge = .count(3)` in UIKit. [HIG][hig], [T62][t62]

**B5. Set the axis when the default is wrong.** `.axisBehavior(.verticalPreferred)` keeps an item in the strip. `.axisBehavior(.horizontalOnly)` keeps it horizontal. UIKit uses `item.axisBehavior`. [T62][t62]

```swift
ToolbarItem { ProfileButton() }
    .axisBehavior(.verticalPreferred)
```

**B6. Rank what overflows.** Items overflow from the bottom up by default. Set `.visibilityPriority(.high)` or `.low` on whole groups first, then on single items. Keep the most used action, like compose or new, and status items with badges visible longest. UIKit uses `item.visibilityPriority = .high`. [HIG][hig]

```swift
ToolbarItemGroup(placement: .bottomBar) {
    Button("Filter", systemImage: "line.3.horizontal.decrease") { }
    Button("Share", systemImage: "square.and.arrow.up") { }
}
.visibilityPriority(.low)
```

**B7. Keep one overflow menu.** Move the actions of a custom "more" menu into the system one, with `ToolbarOverflowMenu` or `navigationItem.additionalOverflowItems`. The ellipsis symbol means overflow only. Give other menus another symbol. [HIG][hig]

```swift
ToolbarOverflowMenu {
    Button("Export", systemImage: "square.and.arrow.up.on.square") { }
    Button("Duplicate", systemImage: "plus.square.on.square") { }
}
```

**B8. Choose what compresses first.** When the strip runs out of room, navigation-led screens keep the tab bar and send toolbar items to overflow. That is the default. Task-led screens keep their toolbar and minimize the tab bar with `.toolbarVerticalCompressionBehavior(.prefersToolbarItems)`, or with `navigationItem.verticalBarCompressionBehavior = .prefersBarItems` in UIKit. [HIG][hig], [T62][t62]

**B9. Opt out only where the strip doesn't fit.** A bottom-heavy single screen, like a keypad, and a sheet with one button may disable the strip with `.toolbarVerticalBehavior(.disabled)`. In UIKit, override `preferredVerticalBarBehavior` to return `.disabled`. On the outer display the sheet then starts below the camera, and the status bar moves back to the top. Without it, a sheet with a title-only Done keeps a horizontal bar that runs into the camera. Don't opt out to keep a layout you already had. [HIG][hig], [T62][t62], [T66][t66]

**B10. Group items, don't space them.** `ToolbarItemGroup` and `UIBarButtonItemGroup` add the spacing and adapt it as space changes. In the strip, a flexible spacer collapses to zero and a fixed spacer keeps its size. [HIG][hig], [T62][t62]

**B11. Fit custom views to a fixed-width strip.** Apple's doc points to `@Environment(\.toolbarVerticalEdge)` in SwiftUI and `traitCollection.verticalBarEdge` in UIKit to tell whether the system presents bars vertically. The UIKit header adds that the trait names the preferred edge even while no strip shows, and is `.unspecified` only where the system never uses one. So check each custom view in every pose of the matrix. The strip has no scroll edge effect, but it gets a background under Reduce Transparency, so test both. [Doc][doc], [T62][t62]

```swift
struct TimerChip: View {
    @Environment(\.toolbarVerticalEdge) private var verticalEdge
    let seconds: Int

    var body: some View {
        if verticalEdge == nil {
            Label("\(seconds)s", systemImage: "timer")
        } else {
            Image(systemName: "timer")
        }
    }
}
```

**B12. Extend hero backgrounds under the strip.** Apply `.backgroundExtensionEffect()` in SwiftUI or wrap the view in `UIBackgroundExtensionView` in UIKit. A screen that doesn't scroll and has no bars, like a keypad or a full-screen visual, may span the whole display if nothing tappable sits under the Dynamic Island or the status bar. [Doc][doc], [HIG][hig]

**B13. Keep controls with the content they act on.** A control for a leading pane, like filters for a list, stays above that pane instead of moving to the strip. [HIG][hig]

**B14. Place sheets on purpose.** On the outer display, a sheet's bar goes vertical by default. A one-button sheet should disable it (B9). On the inner display, centered and leading sheets keep horizontal bars and trailing sheets get the strip. Choose with `.presentationPlacement(.leading)`, `.center`, or `.trailing`, or `sheetPresentationController.preferredPlacement` in UIKit. [Doc][doc], [T62][t62]

**B15. Know what never goes vertical.** Inspectors keep horizontal bars. In a split view showing several columns, only the detail column gets the strip. Keyboard accessory bars stay on the keyboard. [Doc][doc], [T62][t62]

## L. Layout

**L1. Size from the space you get.** Read the view's size with `onGeometryChange` or `GeometryReader` in SwiftUI, and `view.bounds` in UIKit. Never use `UIScreen.main`. Re-read the size on every change, because a fold resizes the app in the middle of a session. In UIKit, lay out in `layoutSubviews` or `viewDidLayoutSubviews`, and use `viewWillTransition(to:with:)` for work that must run on a size change. [HIG][hig], [Steps][steps]

```swift
.onGeometryChange(for: CGFloat.self) { proxy in
    proxy.size.width
} action: { width in
    columns = max(2, Int(width / 180) / 2 * 2)
}
```

**L2. Decide with size classes or the available space.** The outer display is compact width. The inner display is regular width. Regular width no longer means iPad. Remove `userInterfaceIdiom` checks, `UIDevice.current.orientation`, `interfaceOrientation`, `statusBarOrientation`, and device-size constants like `bounds.height == 844`. To know whether the app is wider than tall, compare the width and height of the space you have. [HIG][hig], [Steps][steps], [T61][t61]

**L3. Treat each safe-area edge on its own.** The strip makes the insets uneven, and the side changes in Split View. Use `bounds.inset(by: safeAreaInsets)`, never `width - safeAreaInsets.left * 2`. Pin content to `safeAreaLayoutGuide` and `layoutMarginsGuide`, and let backgrounds run to the edges. Add extra margin with `.safeAreaPadding`, which adds to the insets. On the simulator, `.contentMargins` on a `List` replaced the strip's inset and pushed the rows under the strip. [T61][t61], [HIG][hig]

**L4. Show one more level of hierarchy when open.** A list and its detail go side by side on the inner display and collapse to one column closed. Use `NavigationSplitView` or `UISplitViewController`. Keep the same hierarchy. Closed shows the list or the item, open shows both. [HIG][hig], [T66][t66]

```swift
NavigationSplitView {
    List(workouts, selection: $selection) { workout in
        Text(workout.name)
    }
} detail: {
    if let selection {
        WorkoutDetail(id: selection)
    } else {
        ContentUnavailableView("Pick a workout", systemImage: "dumbbell")
    }
}
```

**L5. Turn tabs into a sidebar in information-dense apps.** With many sections, present the tab bar as a sidebar on the inner display. Use `.tabViewStyle(.sidebarAdaptable)` with `.defaultTabBarPlacement(.sidebar)`, or `tabBarController.sidebar.preferredPlacement = .sidebar` in UIKit. An app with a few tabs keeps them in the strip. [T61][t61], [T66][t66]

**L6. Rearrange instead of stretching.** A vertical stack of sections becomes two columns. A grid gains columns. Prefer an even column count on the inner display so the fold splits the grid cleanly, and use inactive division regions (F4) to plan it while the device is flat. Keep text columns to a readable width with `readableContentGuide` in UIKit or a maximum width on the text column in SwiftUI. [HIG][hig], [T63][t63]

**L7. Pick fill or fit for media by aspect ratio.** Full-bleed media with `.fill` or `.scaleAspectFill` can crop the subject on the wide inner display. Choose fill or fit from the aspect ratio, or set a focal point. Video should grow when the device opens, without making the person rotate it. [Steps][steps]

**L8. Size from containers, never from a known iPhone.** No fixed widths or heights for containers, and no breakpoints tied to one display. Use flexible frames, `containerRelativeFrame`, layout margins, and Auto Layout. [HIG][hig], [Doc][doc]

**L9. Follow the display's corners.** The outer display has square corners on one side and round ones on the other. For a shape that hugs the display, use `ConcentricRectangle` in SwiftUI or `UICornerConfiguration` in UIKit instead of a fixed radius. [T61][t61]

## F. The fold and reserved regions

Reserved regions are parts of the display your content avoids or adapts to. A division region is the fold. It splits the inner display in two when half-open, and has zero width when flat. An occlusion region is a camera. The outer camera always occludes. The inner camera occludes only while it's active.

**F1. Let system components avoid the fold.** Alerts, menus, popovers, action sheets, sheets, toolbar buttons, and split view columns move off the fold on their own. Use them before you place anything by hand. [HIG][hig], [T66][t66]

**F2. Keep tappable things out of the fold.** Scrolling content like articles, feeds, documents, and lists may cross it and should not move. Never hide key content under the fold or a camera. A full-width bar of your own, like a resume bar in a bottom `safeAreaInset`, crosses the fold when the device is half-open. Keep it to the leading half on regular width. [HIG][hig], [T63][t63], [T66][t66]

**F3. Use an arrangement view for two-part screens.** `ArrangementView` and `UIArrangementViewController` hold a primary and a secondary view and place them by size, aspect, and the fold. Use `.split` for main and detail content where neither may be covered, which is what an `HStack` or a `VStack` becomes. Use `.overlay` for a foreground over a background, which is what a `ZStack` becomes. `.split.axes(.horizontal)` shows only the primary view when the arrangement is taller than wide, so limit axes only when the primary alone is right for tall layouts. Keep navigation containers outside the arrangement, and never put an arrangement inside a `List` or a `ScrollView`. [HIG][hig], [Doc][doc], [T63][t63]

```swift
NavigationStack {
    ArrangementView {
        ExerciseVideo()
    } secondary: {
        SetLog()
    }
    .arrangementViewStyle(.split)
}
```

In an overlay arrangement, read `@Environment(\.overlayArrangementZIndex)` to collapse the view that's covered. In UIKit, read `state(for: .primary)?.zIndex`. [T63][t63]

What `.split` did on the iPhone Duo simulator:

- It put the panes side by side when the arrangement was wider than tall, and stacked them when it was taller.
- In both half-open poses it left the fold empty, so a button in either pane stayed out of the crease.
- Each pane clipped to the arrangement. A pane got no bottom safe area while the arrangement ignored it. To run media under the home indicator, let the arrangement ignore the bottom edge, and give the other pane its inset back with `.safeAreaPadding(.bottom, inset)`.
- The gap at the fold showed whatever was behind the arrangement. Give the arrangement the panes' background.
- Going from open to half-open moved the split from about 54/46 to an even split around the fold, with no change in screen size. A scroll view in the shrinking pane kept its offset, and the row the person was on slid under the pane's bottom bar. Scroll that row back into view when the pane gets shorter.
- After that resize, a Liquid Glass button in a `GlassEffectContainer` in the pane's bottom bar stopped drawing, though VoiceOver still found it. Giving the bar a new identity from the pane's size drew it again.

Both fixes in the pane that holds the list and its bar:

```swift
ArrangementView {
    ExerciseVideo()
} secondary: {
    ScrollViewReader { proxy in
        ScrollView {
            SetRows()
        }
        .onScrollGeometryChange(for: CGFloat.self) { $0.containerSize.height } action: { old, new in
            if new < old { proxy.scrollTo(currentSet) }
        }
    }
    .safeAreaBar(edge: .bottom) {
        RestControls()
            .id(paneSize)
    }
    .onGeometryChange(for: CGSize.self) { $0.size } action: { paneSize = $0 }
}
.arrangementViewStyle(.split)
```

**F4. Query reserved regions for custom controls.** Call `reservedRegions(kind:)` on a `GeometryProxy` or a `UIView`. Use `.division` for the fold and `.occlusion` for cameras. Each region has a `frame`, `margins`, and `isActive`. Pass `.includeInactive` to plan with the fold while the device is flat. [HIG][hig], [Doc][doc], [T63][t63]

```swift
GeometryReader { proxy in
    let fold = proxy.reservedRegions(kind: .division).first(where: \.isActive)?.frame
    let foldAcross = fold.flatMap { $0.width > $0.height ? $0 : nil }
    VStack(spacing: 0) {
        ExerciseVideo()
            .frame(height: foldAcross?.minY)
        Color.clear
            .frame(height: foldAcross?.height ?? 0)
        SetControls()
    }
}
```

One view tree serves every pose, so state survives the fold (C2). A fold running across means the laptop pose. A fold running top to bottom means the book pose.

**F5. Move as little as possible.** Move only what would land in the fold. Move related elements together. Don't move an element so far that it loses its link to its source. The pose decides where content goes. Half-open like a book, alerts go to the trailing side, where they come back when the device closes. Half-open like a laptop, content to watch goes in the top half and touch controls in the bottom half. Search stays over what it searches. [T63][t63], [HIG][hig]

**F6. Space grids around the fold.** Keep the outer margins and widen the spacing at the fold. Split columns settle into an even 50/50. [HIG][hig], [T63][t63]

## C. Continuity

**C1. Keep the person's place.** When the device opens or closes, the item the person was looking at stays on screen. Anchor scroll position to an item with `.scrollPosition(id:)` or `ScrollPosition`, not to an offset. In UIKit, record the first visible index path before the transition and restore it after. [HIG][hig]

```swift
ScrollView {
    LazyVStack {
        ForEach(items) { item in Row(item: item) }
    }
    .scrollTargetLayout()
}
.scrollPosition(id: $visibleItem, anchor: .top)
```

**C2. Keep the same state on both displays.** Selection, drafts, playback, and presented sheets survive the resize. Don't branch into two view trees by size class that each own their state. Keep the state in the model or in `@SceneStorage` and change only the layout. [HIG][hig]

**C3. Keep the same features in every pose.** Controls may overflow and content may move. No control or content disappears in a pose. [HIG][hig]

## M. Multitasking and scenes

**M1. Expect Split View at 50/50.** Every app takes part. Each app puts its strip on its outer edge, so the app on the left gets its strip on the left. Test both sides. [T66][t66], [HIG][hig]

**M2. Expect less height.** Video stacked above the app, picture in picture, and the keyboard all shrink the app vertically. Lay out from the height you get. [T64][t64], [T66][t66]

**M3. Support more windows on the inner display.** iPhone Duo opens several windows of one app, on the inner display only. Use `UIWindowScene.ActivationAction` (`UIWindowSceneActivationAction` in Objective-C), which hides itself when a new window isn't possible, and handle errors when you request a scene. [T64][t64]

**M4. Use a scene accessory for paired UI on the other display.** `.sceneAccessory { }` shows extra UI on the other display next to the main UI. `CameraCaptureAccessory` shows it on the outer display while the camera UI stays inside. Availability changes at any time, so observe it with `.onAvailabilityChange`. [T64][t64]

```swift
CameraScreen()
    .sceneAccessory {
        CameraCaptureAccessory(isEnabled: $showsTeleprompter) {
            Teleprompter()
        }
        .onAvailabilityChange { canShowTeleprompter = $0 }
    }
```

## P. Poses and hardware

**P1. Use hinge data for interactions, not layout.** `.onHingeChange` in SwiftUI and `UIHingeInteraction` in UIKit report the status (`.closed`, `.partiallyOpen`, `.fullyOpen`) and the angle as they change. `hinge` is `nil` on a device without one. Lay out with arrangement views and reserved regions instead. [T64][t64]

```swift
.onHingeChange { _, new in
    if let hinge = new.hinge, hinge.status == .partiallyOpen {
        tilt = hinge.angle.degrees
    } else {
        tilt = 0
    }
}
```

**P2. Make the laptop pose hands-free.** Propped on a table, the top half is for content seen from a distance and the bottom half is a stable base for touch controls. The controls and the hierarchy stay the same as in other poses. [T66][t66], [T63][t63]

**P3. Make the book pose two pages.** Half-open like a book, content moves off the curve and controls move to the sides. A split view shows one pane per half. [T66][t66]

**P4. Choose a camera by the direction it faces.** iPhone Duo has an outer and an inner front camera. Both report `position == .front` even when one faces away, so position doesn't tell you who is in the frame. The virtual front camera switches between them for you, up to 1080p at 60 fps. For more, find `.builtInOuterUltraWideCamera` and `.builtInInnerUltraWideCamera` with `AVCaptureDevice.DiscoverySession`, and follow which way each one faces with `AVCaptureDeviceDirectionCoordinator`. Mirror the preview when a rear camera faces the person. Adopt `AVCaptureDevice.RotationCoordinator`, then set `isCameraSensorOrientationCompensationEnabled` to `false`. To fill the wide display, set a landscape aspect ratio with `setDynamicAspectRatio(_:completionHandler:)`, because `dynamicAspectRatio` is read-only. [T65][t65], [Doc][doc]

**P5. Fill the screen in games.** Prefer changing the aspect ratio over letterboxing. If bars can't be avoided, fill them with artwork. Keep text and control sizes steady as the size changes. [HIG][hig]

## S. App Store

**S1. Upload iPhone Duo screenshots.** They add the iPhone Duo badge to the product page. Show more than one orientation and pose. [Steps][steps], [Shots][shots]

**S2. Nominate the app.** In the featuring nomination, say the app is optimized for iPhone Duo and supports every pose. [Steps][steps]

## Quick reference

| Need | SwiftUI | UIKit |
| --- | --- | --- |
| Bars the system can move | `.toolbar` in `NavigationStack`, `TabView` | items on a view controller in `UINavigationController` |
| Back or Close at the top of the strip | `.cancellationAction` | `leadingItemGroups` |
| Prominent action next | `.topBarPinnedTrailing` | `pinnedTrailingGroup` |
| Keep an item vertical or horizontal | `.axisBehavior(.verticalPreferred)` | `axisBehavior` |
| Overflow order | `.visibilityPriority(.high)` | `visibilityPriority` |
| One overflow menu | `ToolbarOverflowMenu` | `additionalOverflowItems` |
| Keep the toolbar, shrink the tab bar | `.toolbarVerticalCompressionBehavior(.prefersToolbarItems)` | `verticalBarCompressionBehavior = .prefersBarItems` |
| No strip for this screen | `.toolbarVerticalBehavior(.disabled)` | `preferredVerticalBarBehavior` |
| Is the strip showing, and where | `\.toolbarVerticalEdge` | `traitCollection.verticalBarEdge` |
| Hero under the strip | `.backgroundExtensionEffect()` | `UIBackgroundExtensionView` |
| Sheet side | `.presentationPlacement(.trailing)` | `preferredPlacement` |
| Sidebar for tabs | `.defaultTabBarPlacement(.sidebar)` | `sidebar.preferredPlacement` |
| List and detail | `NavigationSplitView` | `UISplitViewController` |
| Two views that adapt to the fold | `ArrangementView` | `UIArrangementViewController` |
| Where the fold and cameras are | `GeometryProxy.reservedRegions(kind:)` | `UIView.reservedRegions(kind:)` |
| Hinge status and angle | `.onHingeChange` | `UIHingeInteraction` |
| UI on the other display | `.sceneAccessory`, `CameraCaptureAccessory` | `UISceneAccessory` |
| Keep the place across a fold | `.scrollPosition(id:)` | restore the first visible index path |

[hig]: https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo
[doc]: https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo
[steps]: https://developer.apple.com/iphone-duo/prepare/
[shots]: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications
[tn3192]: https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key
[tn3208]: https://developer.apple.com/documentation/technotes/tn3208-preparing-your-apps-launch-screen-to-meet-app-store-requirements
[t61]: https://developer.apple.com/videos/play/tech-talks/111461/
[t62]: https://developer.apple.com/videos/play/tech-talks/111462/
[t63]: https://developer.apple.com/videos/play/tech-talks/111463/
[t64]: https://developer.apple.com/videos/play/tech-talks/111464/
[t65]: https://developer.apple.com/videos/play/tech-talks/111465/
[t66]: https://developer.apple.com/videos/play/tech-talks/111466/
