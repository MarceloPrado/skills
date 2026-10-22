# Verify on the iPhone Duo simulator

## Set up

1. Use Xcode 27.1 or later. `xcodebuild -version` prints it.
2. The iPhone Duo device type needs the iOS 27.1 simulator runtime. Install it with `xcodebuild -downloadPlatform iOS` (about 8 GB). `xcrun simctl list runtimes` then lists `iOS 27.1`.
3. Create a simulator with a name of its own, so no other build installs over yours, and keep the UDID it prints:

```bash
xcrun simctl create "Duo Migration" com.apple.CoreSimulator.SimDeviceType.iPhone-Duo com.apple.CoreSimulator.SimRuntime.iOS-27-1
xcrun simctl boot <udid>
```

4. Build the app with the project's own command for that UDID. Then install and launch it with `xcrun simctl install <udid> <path to the .app>` and `xcrun simctl launch <udid> <bundle id>`.
5. Get the app to each screen with data in it. Use the project's deep links, test modes, or seed data rather than tapping through onboarding every time.
6. To fold the device from an agent, install [Argent](https://github.com/software-mansion/argent) with `npx @swmansion/argent@latest init -y`. `xcrun simctl` has no fold command, and Device Hub folds the device only by hand.

## Fold, turn, and capture

```bash
argent run fold --udid <udid> --posture half-open
argent run rotate --udid <udid> --orientation LandscapeLeft
argent run screenshot --udid <udid> --scale 1 --out .duo/shots/<screen>-<pose>-before.png
```

Argent captures the display that shows the UI, at a quarter of full size unless you pass `--scale 1`. Don't use `xcrun simctl io <udid> screenshot` on iPhone Duo. With the device closed it captured the dark inner display, not the outer one.

On an open iPhone Duo, `rotate` sets the orientation of the device, not of the UI. `Portrait` gives a landscape UI and `LandscapeLeft` gives a portrait UI.

| Pose | Fold | `rotate` | What shows |
| --- | --- | --- | --- |
| `closed` | `closed` | `Portrait` | The outer display, 1398 x 2034 px, with the strip on the side |
| `closed-landscape` | `closed` | `LandscapeLeft` | The outer display turned, compact in both directions, where the strip overflows most. A portrait-only app stays portrait |
| `open` | `open` | `Portrait` | The inner display in landscape, with the strip on the side |
| `open-portrait` | `open` | `LandscapeLeft` | The inner display in portrait, with horizontal bars |
| `book` | `half-open` | `Portrait` | The inner display in landscape, with the fold top to bottom |
| `laptop` | `half-open` | `LandscapeLeft` | The inner display in portrait, with the fold across |
| `split` | `open` | `Portrait` | Two apps at 50/50, after you drag the app by its home indicator to one side |

A screenshot of the inner display with a landscape UI comes out turned 90 degrees. Turn it upright with `sips -r 90 <file>`.

## Shoot the matrix

Name each shot `.duo/shots/<screen>-<pose>-before.png` or `-after.png`. Shoot every screen of the inventory closed, open, book, and laptop. Add `closed-landscape`, `open-portrait`, and `split` for the screens where they change something.

## Check each pose

- **Closed.** The app's bars sit in the strip. Nothing sits under the strip or the camera. A sheet's bar is vertical, or the sheet starts below the camera (B9).
- **Closed, landscape.** The most used toolbar items stay visible, and the rest go to one overflow menu (B6 to B8).
- **Open.** No black bars. More content, or one more level of hierarchy, than closed. Lines of text stay at a readable length.
- **Open, portrait.** Horizontal bars. The layout reflows instead of stretching.
- **Book.** Nothing tappable in the middle of the display. Columns and cards split at the fold. Alerts and menus stay off the fold.
- **Laptop.** What to watch is in the top half and the controls are in the bottom half, where the brief asks for it. Nothing tappable at the fold.
- **Continuity.** Scroll a list while closed, then open the device. The same item is on screen. Do the same with a selection and a draft.
- **Fold with the screen up.** Go from open to half-open and back while a screen with a bottom bar shows. The row the person was on stays in view, and every control in the bar still draws (F3).
- **Everywhere.** Check a large Dynamic Type size, dark mode, and Split View with the app on the left.

## Build the comparison sheet

```bash
swift <skill-dir>/scripts/compare.swift .duo/shots .duo/before-after.png --title "<App> on iPhone Duo"
```

It pairs each `-before` shot with its `-after` shot and stacks the pairs, before on the left, six pairs to a sheet. It names any before shot that has no after shot. `--only screen1,screen2` limits the sheet to some screens, and `--per-page` changes the pairs per sheet.

## Say what the simulator can't show

The feel of the crease, the under-display camera, heat, battery, and the hinge at angles you didn't test. Name them in the reply as untested.
