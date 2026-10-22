import SwiftUI

// UIScreen.main.bounds and UIToolbar() in a comment never count.
/* let old = UIScreen.main.scale
   let bar = UIToolbar() */
struct ModernScreen: View {
    @State private var columns = 2
    @State private var selection: String?
    let items = ["Squat", "Bench"]

    var body: some View {
        NavigationSplitView {
            List(items, id: \.self, selection: $selection) { Text($0) }
        } detail: {
            Text(selection ?? "None")
                .toolbar {
                    ToolbarItem(placement: .topBarPinnedTrailing) {
                        Button("Done", systemImage: "checkmark") { }
                    }
                    ToolbarOverflowMenu {
                        Button("Export", systemImage: "square.and.arrow.up") { }
                    }
                }
        }
        .onGeometryChange(for: CGFloat.self) { $0.size.width } action: { width in
            columns = max(2, Int(width / 180) / 2 * 2)
        }
    }
}
