import Foundation

/// A file or folder moved by organize, read from the engine's history.jsonl.
struct Move: Identifiable, Hashable, Sendable {
    let id: String
    let run: String
    let time: Date
    let source: URL
    let destination: URL
}

struct History: Sendable {
    /// Ids of all runs that were not undone, oldest first.
    var runs: [String] = []
    /// The most recent moves of runs that were not undone, newest first.
    var recent: [Move] = []

    static func load(from file: URL, limit: Int = 25) -> History {
        guard let text = try? String(contentsOf: file, encoding: .utf8) else { return History() }
        var undone = Set<String>()
        var runs: [String] = []
        var moves: [Move] = []
        let dates = ISO8601DateFormatter()
        dates.formatOptions = [.withFullDate, .withTime, .withColonSeparatorInTime, .withDashSeparatorInDate]
        dates.timeZone = .current

        for (nr, line) in text.split(separator: "\n").enumerated() {
            guard
                let data = line.data(using: .utf8),
                let entry = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
            else { continue }
            if let id = entry["undone"] as? String {
                undone.insert(id)
                continue
            }
            guard let run = entry["run"] as? String else { continue }
            if runs.last != run { runs.append(run) }
            guard
                let op = entry["op"] as? String, op == "move" || op == "rename",
                let src = entry["src"] as? String, let dst = entry["dst"] as? String
            else { continue }
            let time = (entry["time"] as? String).flatMap { dates.date(from: $0) } ?? .distantPast
            moves.append(
                Move(
                    id: "\(nr)", run: run, time: time,
                    source: URL(filePath: src), destination: URL(filePath: dst)))
        }
        let active = moves.filter { !undone.contains($0.run) }
        return History(
            runs: runs.filter { !undone.contains($0) },
            recent: Array(active.reversed().prefix(limit)))
    }
}
