import AppKit
import SwiftUI

struct PanelView: View {
    @Bindable var model: AppModel

    private let reviewRowHeight: CGFloat = 26
    private let recentRowHeight: CGFloat = 34
    private let rowSpacing: CGFloat = 2

    /// A scroll view in a menu bar panel has no height of its own, so size it to
    /// its rows, up to `maxRows`.
    private func listHeight(rows: Int, rowHeight: CGFloat, maxRows: Int) -> CGFloat {
        let n = CGFloat(min(rows, maxRows))
        return n * rowHeight + max(n - 1, 0) * rowSpacing
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            header
            if let message = model.message {
                Text(message)
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(8)
                    .background(.quaternary, in: RoundedRectangle(cornerRadius: 6))
                    .onTapGesture { model.message = nil }
            }
            reviewSection
            recentSection
            Divider()
            footer
        }
        .padding(14)
        .frame(width: 380)
    }

    private var header: some View {
        HStack {
            Circle()
                .fill(model.serviceRunning ? Color.green : Color.orange)
                .frame(width: 8, height: 8)
            Text(model.serviceRunning ? "Watching" : "Paused")
                .font(.headline)
            if let folders = model.info?.folders {
                Text(folders.map { URL(filePath: $0).lastPathComponent }.joined(separator: ", "))
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
            Spacer()
            if model.busy { ProgressView().controlSize(.small) }
            Button(model.serviceRunning ? "Pause" : "Resume") {
                Task { await model.toggleService() }
            }
            .disabled(model.busy)
        }
    }

    private var reviewSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Needs review (\(model.review.count))").font(.subheadline.bold())
            if model.review.isEmpty {
                Text("Nothing to review").foregroundStyle(.secondary).font(.callout)
            } else {
                ScrollView {
                    VStack(spacing: rowSpacing) {
                        ForEach(model.review) { item in reviewRow(item) }
                    }
                }
                .frame(height: listHeight(rows: model.review.count, rowHeight: reviewRowHeight, maxRows: 6))
            }
        }
    }

    private func reviewRow(_ item: ReviewItem) -> some View {
        HStack(spacing: 8) {
            FileIcon(url: item.url)
            Text(item.url.lastPathComponent)
                .lineLimit(1)
                .truncationMode(.middle)
                .frame(maxWidth: .infinity, alignment: .leading)
                .contentShape(Rectangle())
                .onTapGesture(count: 2) { model.open(item.url) }
                .help("Double-click to open")
            Menu("Move to") {
                ForEach(model.info?.categories ?? [], id: \.self) { category in
                    Button(category) { Task { await model.move(item, to: category) } }
                }
            }
            .menuStyle(.borderlessButton)
            .fixedSize()
            .disabled(model.busy)
            Button {
                model.reveal(item.url)
            } label: {
                Image(systemName: "magnifyingglass")
            }
            .buttonStyle(.borderless)
            .help("Show in Finder")
        }
        .frame(height: reviewRowHeight)
    }

    private var recentSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Recently sorted").font(.subheadline.bold())
            if model.recent.isEmpty {
                Text("Nothing sorted yet").foregroundStyle(.secondary).font(.callout)
            } else {
                ScrollView {
                    VStack(spacing: rowSpacing) {
                        ForEach(model.recent) { move in recentRow(move) }
                    }
                }
                .frame(height: listHeight(rows: model.recent.count, rowHeight: recentRowHeight, maxRows: 6))
            }
        }
    }

    private func recentRow(_ move: Move) -> some View {
        Button {
            model.reveal(move.destination)
        } label: {
            HStack(spacing: 8) {
                FileIcon(url: move.destination)
                VStack(alignment: .leading, spacing: 0) {
                    Text(move.destination.lastPathComponent).lineLimit(1).truncationMode(.middle)
                    Text(relativeFolder(of: move))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                        .truncationMode(.head)
                }
                Spacer()
                Text(move.time, style: .relative)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize()
            }
            .frame(height: recentRowHeight)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .help("Show in Finder")
    }

    /// The target folder relative to the sorted folder, e.g. "invoice/Telekom".
    private func relativeFolder(of move: Move) -> String {
        let folder = move.destination.deletingLastPathComponent().path(percentEncoded: false)
        for location in model.info?.folders ?? [] where folder.hasPrefix(location) {
            let rel = folder.dropFirst(location.count).trimmingCharacters(in: CharacterSet(charactersIn: "/"))
            return rel.isEmpty ? URL(filePath: location).lastPathComponent : rel
        }
        return (folder as NSString).abbreviatingWithTildeInPath
    }

    private var footer: some View {
        HStack {
            Button("Undo last run") { Task { await model.undoLastRun() } }
                .disabled(model.busy || model.recent.isEmpty)
            Spacer()
            Menu {
                if let folders = model.info?.folders {
                    ForEach(folders, id: \.self) { folder in
                        Button("Open \(URL(filePath: folder).lastPathComponent)") {
                            model.open(URL(filePath: folder))
                        }
                    }
                }
                if let config = model.info?.configPath {
                    Button("Edit config") { model.open(URL(filePath: config)) }
                }
                if let engine = model.engine {
                    Button("Show log") { model.open(engine.logFile) }
                }
                Divider()
                Toggle(
                    "Open at login",
                    isOn: Binding(get: { model.launchAtLogin }, set: { model.setLaunchAtLogin($0) }))
                Button("Reload config") { Task { await model.loadInfo(); await model.refresh() } }
                Divider()
                Button("Quit Organize") { NSApplication.shared.terminate(nil) }
            } label: {
                Image(systemName: "ellipsis.circle")
            }
            .menuStyle(.borderlessButton)
            .fixedSize()
        }
    }
}

struct FileIcon: View {
    let url: URL

    var body: some View {
        Image(nsImage: NSWorkspace.shared.icon(forFile: url.path(percentEncoded: false)))
            .resizable()
            .frame(width: 18, height: 18)
    }
}
