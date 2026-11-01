import AppKit
import Foundation
import Observation
import OSLog
import ServiceManagement
import UserNotifications

/// A file or folder waiting in a review folder.
struct ReviewItem: Identifiable, Hashable, Sendable {
    var id: URL { url }
    let url: URL
    /// The sorted folder the review folder belongs to, e.g. ~/Downloads.
    let location: URL
}

private let log = Logger(subsystem: "local.organize.bar", category: "model")

@MainActor
@Observable
final class AppModel {
    let engine: Engine?

    var info: AppInfo?
    var serviceRunning = false
    var recent: [Move] = []
    var review: [ReviewItem] = []
    var busy = false
    var message: String?
    var launchAtLogin = SMAppService.mainApp.status == .enabled

    private var knownRuns: Set<String>?

    /// Notifications only work in an app bundle, not when running the bare binary.
    private static let canNotify = Bundle.main.bundleIdentifier != nil
    private var refreshTask: Task<Void, Never>?

    init() {
        engine = Engine.fromBundle()
        if engine == nil {
            message = "The organize project folder is not set. Rebuild the app with build-app.sh."
        }
        if Self.canNotify {
            UNUserNotificationCenter.current().requestAuthorization(options: [.alert]) { _, _ in }
        }
        refreshTask = Task { [weak self] in
            await self?.loadInfo()
            while !Task.isCancelled {
                await self?.refresh()
                try? await Task.sleep(for: .seconds(3))
            }
        }
    }

    // MARK: - Reading state

    func loadInfo() async {
        guard let engine else { return }
        do {
            let info = try await engine.info()
            self.info = info
            log.info("Loaded config \(info.configPath, privacy: .public): \(info.folders.count) folders, \(info.categories.count) categories")
        } catch {
            log.error("Could not read the config: \(error.localizedDescription, privacy: .public)")
            message = "Could not read the config: \(error.localizedDescription)"
        }
    }

    func refresh() async {
        guard let engine else { return }
        serviceRunning = await engine.isServiceRunning()
        guard let info else { return }

        let history = History.load(from: URL(filePath: info.historyFile))
        // leave out items that were deleted or moved on since
        recent = history.recent.filter {
            FileManager.default.fileExists(atPath: $0.destination.path(percentEncoded: false))
        }
        notifyAboutNewRuns(history)

        var items: [ReviewItem] = []
        let fm = FileManager.default
        for folder in info.folders {
            let location = URL(filePath: folder)
            for name in info.reviewFolders {
                let dir = location.appending(path: name)
                let entries = (try? fm.contentsOfDirectory(
                    at: dir, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles])) ?? []
                items += entries.map { ReviewItem(url: $0, location: location) }
            }
        }
        let sorted = items.sorted { $0.url.lastPathComponent < $1.url.lastPathComponent }
        if sorted != review || knownRuns == nil {
            log.info("Watching: \(self.serviceRunning), recent moves: \(history.recent.count), to review: \(sorted.count)")
        }
        review = sorted
    }

    private func notifyAboutNewRuns(_ history: History) {
        let runs = Set(history.runs)
        defer { knownRuns = runs }
        guard let known = knownRuns, Self.canNotify else { return }  // not about old runs at launch
        let newMoves = history.recent.filter { !known.contains($0.run) && runs.contains($0.run) }
        guard !newMoves.isEmpty else { return }

        let content = UNMutableNotificationContent()
        if newMoves.count == 1, let move = newMoves.first {
            content.title = "Sorted \(move.destination.lastPathComponent)"
            content.body = "into \(move.destination.deletingLastPathComponent().lastPathComponent)"
        } else {
            content.title = "Sorted \(newMoves.count) items"
            content.body = newMoves.prefix(3).map(\.destination.lastPathComponent)
                .joined(separator: ", ")
        }
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }

    // MARK: - Actions

    func toggleService() async {
        await perform(serviceRunning ? "stop" : "start", service: true)
    }

    func undoLastRun() async {
        await perform("undo", service: false)
    }

    func move(_ item: ReviewItem, to category: String) async {
        guard let engine else { return }
        busy = true
        defer { busy = false }
        let dest = item.location.appending(path: category).path(percentEncoded: false)
        do {
            let result = try await engine.organize(["move", item.url.path(percentEncoded: false), dest])
            message = result.status == 0
                ? "Moved \(item.url.lastPathComponent) to \(category)" : result.output
        } catch {
            message = error.localizedDescription
        }
        await refresh()
    }

    private func perform(_ command: String, service: Bool) async {
        guard let engine else { return }
        busy = true
        defer { busy = false }
        do {
            let result = service ? try await engine.service(command) : try await engine.organize([command])
            let lines = result.output.split(separator: "\n").map(String.init)
            message = lines.last(where: { !$0.trimmingCharacters(in: .whitespaces).isEmpty })?
                .trimmingCharacters(in: .whitespaces)
            if command == "undo", result.status == 0 {
                message = "Undid the last run (\(max(lines.count - 1, 0)) changes)"
            }
        } catch {
            message = error.localizedDescription
        }
        await refresh()
    }

    func setLaunchAtLogin(_ enabled: Bool) {
        do {
            if enabled {
                try SMAppService.mainApp.register()
            } else {
                try SMAppService.mainApp.unregister()
            }
        } catch {
            message = "Launch at login: \(error.localizedDescription)"
        }
        launchAtLogin = SMAppService.mainApp.status == .enabled
    }

    // MARK: - Finder

    func reveal(_ url: URL) {
        NSWorkspace.shared.activateFileViewerSelecting([url])
    }

    func open(_ url: URL) {
        NSWorkspace.shared.open(url)
    }
}
