---
name: iphone-duo
description: Migrate an iPhone app to iPhone Duo, Apple's foldable, end to end. Learns what the app is for, audits every screen in every pose on the iPhone Duo simulator, proposes a layout per screen from Apple's Human Interface Guidelines, implements it in SwiftUI or UIKit, and proves it with before and after screenshots. Runs Apple's app-resizability skill as one step, so prefer this skill for end-to-end iPhone Duo work. Use when asked to support, adapt, optimize, or migrate an app for iPhone Duo or the foldable iPhone, when an app letterboxes, stretches, or shows black bars on the inner display, or when working with the vertical bars, the fold, reserved regions, or ArrangementView on iPhone Duo.
---

# iPhone Duo

**You own the app on both displays.** Rebuilding with the new SDK makes the app fill the screen. It does not make the inner display worth opening. The migration is done when each display and each pose gives the person a reason to be there, and the screenshots prove it.

**One question gets one answer.** When the user asks about a single API or rule, answer from `references/rules.md` and stop. Run the workflow when the user wants an app migrated.

## The device

- Two displays. The outer display is wider and shorter than any other iPhone, with square corners on the left and round ones on the right. The inner display opens to about 1.4 by 1.
- The system moves the status bar, the Dynamic Island, the toolbar, the navigation buttons, and the tab bar into a strip along the side. That happens on the outer display and on the inner display in landscape. The inner display in portrait keeps horizontal bars.
- The outer display is compact width. The inner display is regular width. An iPhone app can now be regular width, so regular width no longer means iPad.
- The poses are closed, open, half-open like a book, half-open like a laptop on a table, and standing on its edges. Half-open, the fold is a reserved region that splits the inner display in two.
- Multitasking puts two apps side by side at 50/50, stacks video above an app, floats picture in picture, and opens more windows of one app on the inner display.
- What the person sees depends on the SDK the app was built with. The iOS 26 SDK runs letterboxed. The iOS 27.0 SDK resizes but keeps horizontal bars. The iOS 27.1 SDK gets the full display and the strip (A1).

`references/rules.md` holds the rules, the APIs, and the Apple sources. `references/hig.md` holds Apple's Human Interface Guidelines for iPhone Duo in brief, each point tied to the rules that build it. `references/patterns.md` holds a layout for each kind of screen. `references/verify.md` holds the poses, the simulator commands, and the checks.

## Hard rules

1. **One adaptive layout, not one per pose.** Size classes, the space the view gets, and reserved regions decide the layout. The device model, the idiom, the orientation, and the screen size never do.
2. **System containers first.** Navigation stacks, split views, tab views, toolbars, sheets, lists, and arrangement views move to the strip and around the fold on their own. Custom chrome moves only when you make it.
3. **Open means more, not bigger.** If the inner display shows the phone layout scaled up, the screen is not migrated.
4. **Same features and the same state in every pose.** Content may move. Unfolding keeps what the person was looking at, and no feature exists in one pose only.
5. **Nothing tappable in the fold or under the strip.** Scrolling content may cross the fold.
6. **The proof is screenshots from the iPhone Duo simulator, before and after, in every pose.** A clean build is not proof.

## Workflow

Six phases. Each one ends in files the user can check, kept in `.duo/` at the project root. Add `.duo/` to `.gitignore` unless the user wants the files committed.

| Phase | Files |
| --- | --- |
| Learn the app | `inventory.md`, `brief.md` |
| Audit | `findings.md`, `scan-before.md`, `shots/*-before.png` |
| Propose | `proposal.md` |
| Implement | `changes.md` |
| Verify | `shots/*-after.png`, `scan-after.md`, `before-after.png` |
| Ship | `ship.md` |

### 1. Learn the app

1. Read the code before you ask anything. Find the entry point, the root navigation (`TabView`, `NavigationStack`, `NavigationSplitView`, `UITabBarController`, `UINavigationController`, or custom), every screen, every sheet, and every full-screen cover.
2. Write `.duo/inventory.md` with one row per screen. Give its archetype from `references/patterns.md`, its container, its bars, its custom chrome, and its fixed sizes.
3. Ask the user what the code can't tell you. Use one message with three questions at most.
   - Which two or three jobs do people open the app for?
   - How do they hold it? In one hand on the go, at a desk, propped up hands-free, or behind a camera?
   - Which screens matter most, and which are off-limits?
4. If the user doesn't answer, or the run has no user, infer the answers from the code, the onboarding, and the App Store copy. Write them in `brief.md` as assumptions and go on.
5. Write `.duo/brief.md` with one line per display and pose. Say what the outer display is for, what the inner display adds, and what the half-open poses make possible. The proposal must serve this brief.

### 2. Audit

1. Check the toolchain. You need Xcode 27.1 or later, the iOS 27.1 simulator runtime, an iPhone Duo simulator, and a way to fold it from the agent. `xcrun simctl` can't fold the device. Device Hub can, by hand. [Argent](https://github.com/software-mansion/argent) can, from an agent. `references/verify.md` has the commands.
2. Read `UIRequiresFullScreen`, the supported orientations, and the launch screen in the Info.plist and the build settings (rules A2 to A4). Find which Xcode builds the App Store release. The before matrix is an Xcode 27.1 build, so a release from an older Xcode looks worse today than the matrix shows (A1).
3. Run the scanner on the app's sources: `python3 <skill-dir>/scripts/duo_scan.py <source-root> > .duo/scan-before.md`. It reports code that breaks on resize, bars the system can't move, fixed sizes, and orientation locks. Each finding names its rule. It reads lines, not Swift syntax, so treat it as a lead list.
4. Find Apple's `app-resizability` skill. Xcode 27.1 ships it for its coding assistant. For another agent, `xcrun agent plugin path --plugin-format claude </dev/null` prints the folder where Xcode keeps it, under `skills/app-resizability`. Don't run it yet. It edits code, and the before matrix must show the app as it is. List what its task registry would touch.
5. Capture the before matrix. Shoot every screen in the inventory in every pose of `references/verify.md`, saved as `.duo/shots/<screen>-<pose>-before.png`.
6. Write `.duo/findings.md`. For each screen, list what breaks, in which pose, and which rule it breaks. Match the shots against the symptom table below.

### 3. Propose

1. Pick each screen's pattern from `references/patterns.md` and check the choice against `references/hig.md`. If the app also runs on iPad, start the inner display from the iPad layout, because Apple wants the inner display to read as an extension of it. In `.duo/proposal.md`, write one row per screen with what it shows closed, open, half-open like a book, and half-open like a laptop. Change how much shows at once and where it sits. Keep the hierarchy and the features.
2. Sketch the two screens that matter most as ASCII wireframes, open and in the laptop pose.
3. When two layouts both fit the brief, build both behind a flag and shoot them on the simulator. Let the screenshots decide.
4. Show the proposal and ask one question. Ship it as proposed, or what should change? If the user doesn't answer in the same session, treat the proposal as approved for reversible work and say so in the reply.

### 4. Implement

Work in this order. End each step with a build and one pose on the simulator. Note what changed per screen in `.duo/changes.md`.

1. Build with the iOS 27.1 SDK (A1).
2. Run Apple's `app-resizability` skill, then fix the scanner's blockers (L1 to L3).
3. Gate every iOS 27.1 API with `#available(iOS 27.1, *)` when the deployment target is lower (A6).
4. Move custom bars into system containers so the system can place them (B1).
5. Tune the bars. Give items titles and symbols, set placements, priorities, one overflow menu, and what compresses first, and opt out only where it fits (B2 to B15).
6. Build the regular-width layouts from the proposal (L4 to L9).
7. Handle the fold in custom layouts with arrangement views or reserved regions (F1 to F6).
8. Keep the person's place across fold and unfold (C1 to C3).
9. Add a pose-specific capability only when the brief asks for it. That means laptop-pose controls, hinge input, a second-display accessory, or more windows (M3, M4, P1 to P5).

Follow the project's conventions for its design system, string catalogs, and accessibility identifiers. Give each new control an identifier so the matrix can drive it.

### 5. Verify

1. Re-run the matrix to `.duo/shots/<screen>-<pose>-after.png`.
2. Check every shot against the pose checklist in `references/verify.md`.
3. Build the comparison sheet: `swift <skill-dir>/scripts/compare.swift .duo/shots .duo/before-after.png`.
4. Re-run the scanner to `.duo/scan-after.md`. Fix every blocker that remains, or explain why it is safe.
5. Check the inner display at a large Dynamic Type size and in dark mode, and run the app on the left side of Split View.
6. Run the self-check under **Never ship**.

### 6. Ship

1. Build the release with Xcode 27.1, in CI as well. A release from an older Xcode ships the old layout (A1).
2. Add iPhone Duo screenshots in App Store Connect. They put the iPhone Duo badge on the product page (S1).
3. Draft the What's New line in the app's voice and the featuring nomination, which says the app supports every pose (S2). Put both in `.duo/ship.md`.

## Symptom table

What reviewers found in shipping apps. Before launch, [HTX Studio](https://www.youtube.com/watch?v=o1qc29t04GI) tested 25 popular apps and found 60% not updated, and [9to5Mac](https://9to5mac.com/2026/10/21/iphone-duo-review/) saw the same black bars. The rest comes from testing a real app. Match the before matrix against it.

| What you see | Cause | Rules |
| --- | --- | --- |
| Black bars beside the app on the inner display or in Split View | Built with the iOS 26 SDK or earlier | A1 |
| The inner display shows the phone layout, bigger, with no more messages or items than closed | One layout for every width | L4, L5, L6 |
| Open, the controls under a media header are off screen | A header sized from the width, like 4:3, is taller than the open display | L1, L7 |
| On the outer display the status bar sits alone in the strip while the app's bars stay at the bottom | A build older than the iOS 27.1 SDK, a custom tab bar, or a standalone bar | A1, B1 |
| A toolbar item stays horizontal or overflows first | A title-only or custom-view item, or no priority | B3, B5, B6 |
| A sheet's Done button runs into the camera on the outer display | A title-only Done keeps the sheet's bar horizontal | B3, B9 |
| Content runs under the strip | Fixed or symmetric insets, or `.contentMargins` on a `List` | L3 |
| A control sits in the crease when half-open | A custom control placed by hand at the center | F1, F2, F4 |
| A bar of your own crosses the fold | A full-width bottom inset | B1, F2 |
| After unfolding, the item the person was about to tap has moved | Scroll position and selection reset on resize | C1, C2 |
| Video stays small until the person also rotates the phone | The player keeps a phone-width frame when open | L6, L7 |
| A hero image or video crops its subject | Aspect fill with no focal point | L7 |
| A grid splits a card across the fold | An odd column count | L6, F6 |
| The keyboard squeezes the app in the stacked layout | Height taken from the screen, not the view | L1, M2 |
| A game letterboxes | A fixed aspect ratio | P5 |

## Never ship

| Never | Instead |
| --- | --- |
| `UIScreen.main.bounds` or a device height in layout code | The view's bounds or `onGeometryChange` |
| `userInterfaceIdiom == .pad` to pick a layout | The size class or the available width |
| A custom tab bar, or a standalone `UIToolbar` for a screen's actions | `TabView`, `.toolbar`, `UITabBarController`, `UINavigationController` |
| A toolbar item with only a title, unless the text is the information | A `Label` with a title and a symbol |
| A second "more" menu with an ellipsis | `ToolbarOverflowMenu` or `additionalOverflowItems` |
| `width - safeAreaInsets.left * 2` | `bounds.inset(by: safeAreaInsets)` |
| A tappable control at the center of the inner display | System components, an arrangement view, or reserved regions |
| A view tree per size class that owns its own state | One view tree, with state in the model or `@SceneStorage` |
| An odd column count in an inner-display grid | An even count, so the fold splits it cleanly |
| `.toolbarVerticalBehavior(.disabled)` across the app | Only bottom-heavy single screens and one-button sheets |
| A feature that exists only when the device is open | The same features in every pose |
| Calling it done from a build | The after matrix and the comparison sheet |

**Reply:** the brief, the proposal table, what changed per screen, the path to the comparison sheet, the scanner counts before and after, and what still needs a real device (the feel of the crease, the under-display camera, heat, and battery).
