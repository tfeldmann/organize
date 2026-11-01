import AppKit
import SwiftUI

@main
struct OrganizeBarApp: App {
    private let model: AppModel

    init() {
        let model = AppModel()
        self.model = model
        // shows the panel in a regular window too, e.g. to take screenshots
        if ProcessInfo.processInfo.environment["ORGANIZE_DEBUG_WINDOW"] == "1" {
            DispatchQueue.main.async { DebugWindow.show(model: model) }
        }
    }

    var body: some Scene {
        MenuBarExtra {
            PanelView(model: model)
        } label: {
            Image(systemName: icon)
        }
        .menuBarExtraStyle(.window)
    }

    private var icon: String {
        if !model.serviceRunning { return "tray.and.arrow.down" }
        return model.review.isEmpty ? "tray.full" : "tray.full.fill"
    }
}

@MainActor
enum DebugWindow {
    private static var window: NSWindow?

    static func show(model: AppModel) {
        let window = NSWindow(contentViewController: NSHostingController(rootView: PanelView(model: model)))
        window.title = "Organize (debug)"
        window.setFrameTopLeftPoint(NSPoint(x: 100, y: (NSScreen.main?.frame.height ?? 900) - 100))
        window.makeKeyAndOrderFront(nil)
        NSApp.activate()
        self.window = window
    }
}
