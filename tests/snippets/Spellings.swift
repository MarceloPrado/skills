// Every API that rules.md names in prose, so the compiler checks its spelling against the SDK.
import AVFoundation
import AVKit
import SwiftUI
import UIKit

struct SwiftUISpellings: View {
    @Environment(\.overlayArrangementZIndex) private var zIndex
    @Environment(\.horizontalSizeClass) private var widthClass
    @SceneStorage("selection") private var selection: String?
    @State private var position = ScrollPosition(edge: .top)
    @State private var query = ""
    @State private var showsInspector = false

    var body: some View {
        TabView {
            Tab("Search", systemImage: "magnifyingglass", role: .search) {
                NavigationStack {
                    content
                        .searchable(text: $query)
                        .toolbar {
                            ToolbarItem { Button("Inbox", systemImage: "tray") { }.badge(3) }
                                .axisBehavior(.horizontalOnly)
                                .visibilityPriority(.high)
                        }
                        .toolbarVerticalCompressionBehavior(.prefersToolbarItems)
                        .toolbarVerticalBehavior(.disabled)
                        .inspector(isPresented: $showsInspector) { Text("Tools") }
                }
            }
        }
        .tabViewStyle(.sidebarAdaptable)
        .defaultTabBarPlacement(.sidebar)
    }

    private var content: some View {
        GeometryReader { proxy in
            let cameras = proxy.reservedRegions(kind: .occlusion, options: .includeInactive)
            VStack {
                ArrangementView { Text("Primary") } secondary: { Text("Secondary") }
                    .arrangementViewStyle(.overlay)
                ConcentricRectangle()
                    .frame(width: cameras.first?.margins.leading)
                Image(systemName: "photo")
                    .backgroundExtensionEffect()
                    .containerRelativeFrame(.horizontal)
                ViewThatFits { Text("Wide"); Text("W") }
            }
            .scrollPosition($position)
            .sheet(isPresented: .constant(false)) {
                Text("Sheet").presentationPlacement(.trailing)
            }
        }
    }
}

final class UIKitSpellings: UIViewController {
    override var preferredVerticalBarBehavior: UIVerticalBarBehavior { .disabled }

    func configure() {
        let share = UIBarButtonItem(title: "Share", image: UIImage(systemName: "square.and.arrow.up"), primaryAction: nil, menu: nil)
        share.axisBehavior = .verticalPreferred
        share.visibilityPriority = .high
        share.badge = .count(3)
        navigationItem.leadingItemGroups = []
        navigationItem.pinnedTrailingGroup = UIBarButtonItemGroup(barButtonItems: [share], representativeItem: nil)
        navigationItem.verticalBarCompressionBehavior = .prefersBarItems
        navigationItem.additionalOverflowItems = UIDeferredMenuElement.uncached { completion in completion([]) }

        switch traitCollection.verticalBarEdge {
        case .leading, .trailing: break
        default: break
        }
        _ = traitCollection.displayScale
        _ = view.bounds.inset(by: view.safeAreaInsets)
        _ = view.readableContentGuide
        _ = view.reservedRegions(kind: .division).map(\.frame)
        _ = UICornerConfiguration.self

        let extensionView = UIBackgroundExtensionView()
        extensionView.contentView = UIImageView()
        sheetPresentationController?.preferredPlacement = .trailing
        tabBarController?.sidebar.preferredPlacement = .sidebar

        let arrangement = UIArrangementViewController()
        arrangement.setViewController(UIViewController(), for: .primary)
        arrangement.setViewController(UIViewController(), for: .secondary)
        arrangement.updateArrangement(.split.axes(.horizontal))
        _ = arrangement.state(for: .primary)?.zIndex

        view.addInteraction(UIHingeInteraction { _, update in
            _ = update.hinge?.status == .partiallyOpen
            _ = update.hinge?.angle
        })
        _ = UIWindowScene.ActivationAction.self
        _ = UISceneAccessory.self
    }

    func camera(in view: UIView) {
        _ = AVCaptureDeviceDirectionCoordinator(view: view,
                                                deviceTypes: [.builtInOuterUltraWideCamera, .builtInInnerUltraWideCamera],
                                                changeHandler: { _ in })
        _ = AVCaptureDevice.RotationCoordinator.self
        AVCapturePhotoOutput().isCameraSensorOrientationCompensationEnabled = false
        _ = AVCaptureDevice.DiscoverySession(deviceTypes: [.builtInOuterUltraWideCamera, .builtInInnerUltraWideCamera],
                                             mediaType: .video, position: .front)
        if let device = AVCaptureDevice.default(for: .video), let ratio = device.dynamicAspectRatio {
            device.setDynamicAspectRatio(ratio) { _, _ in }
        }
    }
}
