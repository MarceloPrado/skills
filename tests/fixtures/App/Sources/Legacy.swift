import SwiftUI
import UIKit

final class LegacyViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        let width = UIScreen.main.bounds.width // expect: L1
        let window = UIWindow(frame: .zero) // expect: L1
        if traitCollection.userInterfaceIdiom == .pad { } // expect: L2
        if UIDevice.current.orientation.isLandscape { } // expect: L2
        if view.bounds.height == 844 { } // expect: L2
        let isPad = width > 700 // expect: L2
        let inner = view.bounds.width - view.safeAreaInsets.left * 2 // expect: L3
        let toolbar = UIToolbar() // expect: B1
        let save = UIBarButtonItem(title: "Save", style: .done, target: nil, action: nil) // expect: B3
        _ = (window, isPad, inner, toolbar, save)
    }

    override var supportedInterfaceOrientations: UIInterfaceOrientationMask { .portrait } // expect: A3
}

struct LegacyScreen: View {
    var body: some View {
        NavigationStack {
            content
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Save") { } // expect: B3
                    }
                    ToolbarItem {
                        Menu("More", systemImage: "ellipsis.circle") { } // expect: B7
                    }
                }
                .toolbar(.hidden, for: .tabBar) // expect: B1
        }
    }

    var content: some View {
        VStack {
            Image("hero").resizable().scaledToFill() // expect: L7
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3)) { } // expect: L6
            Color.red.frame(width: 390, height: 120) // expect: L8
        }
        .ignoresSafeArea() // expect: F2
        .safeAreaInset(edge: .bottom) { HStack { } } // expect: B1
    }
}
