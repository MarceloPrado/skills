import SwiftUI
import UIKit

final class EdgeCases: UIViewController {
    func layout() {
        let label = "UIScreen.main.bounds"
        let old = 1 /* UIScreen.main.scale */ + 1
        let inner = view.bounds.width - 2 * view.safeAreaInsets.left // expect: L3
        let share = UIBarButtonItem(title: "Share",
                                    image: UIImage(systemName: "square.and.arrow.up"),
                                    primaryAction: nil, menu: nil)
        let accessory = UIToolbar() // expect: B1
        if traitCollection.userInterfaceIdiom == .mac { } // expect: L2
        _ = (label, old, inner, share, accessory)
    }
}

struct EdgeScreen: View {
    @State private var text = ""

    var body: some View {
        NavigationStack {
            TextField("Weight", text: $text)
                .toolbar {
                    ToolbarItemGroup(placement: .keyboard) {
                        Button("Done") { }
                    }
                    ToolbarItem {
                        Menu("Sort", systemImage: "arrow.up.arrow.down") {
                            Button("Newest") { }
                        }
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Save") { } // expect: B3
                    }
                }
        }
    }
}
