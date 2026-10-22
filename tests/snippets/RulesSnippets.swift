import SwiftUI

struct SnippetB1: View {
    @Environment(\.dismiss) private var dismiss
    func save() {}

    var body: some View {
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
    }
}

struct SnippetToolbars: View {
    var body: some View {
        NavigationStack {
            Text("Toolbars")
                .toolbar {
                    ToolbarItem { ProfileButton() }
                        .axisBehavior(.verticalPreferred)
                    ToolbarItemGroup(placement: .bottomBar) {
                        Button("Filter", systemImage: "line.3.horizontal.decrease") { }
                        Button("Share", systemImage: "square.and.arrow.up") { }
                    }
                    .visibilityPriority(.low)
                    ToolbarOverflowMenu {
                        Button("Export", systemImage: "square.and.arrow.up.on.square") { }
                        Button("Duplicate", systemImage: "plus.square.on.square") { }
                    }
                }
        }
    }
}

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

struct SnippetL1: View {
    @State private var columns = 2

    var body: some View {
        Color.clear
            .onGeometryChange(for: CGFloat.self) { proxy in
                proxy.size.width
            } action: { width in
                columns = max(2, Int(width / 180) / 2 * 2)
            }
    }
}

struct SnippetL4: View {
    let workouts: [Workout] = []
    @State private var selection: Workout.ID?

    var body: some View {
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
    }
}

struct SnippetF3: View {
    var body: some View {
        NavigationStack {
            ArrangementView {
                ExerciseVideo()
            } secondary: {
                SetLog()
            }
            .arrangementViewStyle(.split)
        }
    }
}

struct SnippetF3Fold: View {
    let currentSet = 0
    @State private var paneSize: CGSize = .zero

    var body: some View {
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
    }
}

struct SnippetF4: View {
    var body: some View {
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
    }
}

struct SnippetC1: View {
    let items: [Item] = []
    @State private var visibleItem: Item.ID?

    var body: some View {
        ScrollView {
            LazyVStack {
                ForEach(items) { item in Row(item: item) }
            }
            .scrollTargetLayout()
        }
        .scrollPosition(id: $visibleItem, anchor: .top)
    }
}

struct SnippetM4: View {
    @State private var showsTeleprompter = false
    @State private var canShowTeleprompter = false

    var body: some View {
        CameraScreen()
            .sceneAccessory {
                CameraCaptureAccessory(isEnabled: $showsTeleprompter) {
                    Teleprompter()
                }
                .onAvailabilityChange { canShowTeleprompter = $0 }
            }
    }
}

struct SnippetP1: View {
    @State private var tilt = 0.0

    var body: some View {
        Color.clear
            .onHingeChange { _, new in
                if let hinge = new.hinge, hinge.status == .partiallyOpen {
                    tilt = hinge.angle.degrees
                } else {
                    tilt = 0
                }
            }
    }
}

extension View {
    @ViewBuilder func horizontalSheetBar() -> some View {
        if #available(iOS 27.1, *) {
            toolbarVerticalBehavior(.disabled)
        } else {
            self
        }
    }
}
