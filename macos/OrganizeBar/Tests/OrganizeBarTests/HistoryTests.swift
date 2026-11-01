import Foundation
import Testing

@testable import OrganizeBar

@Test func parsesMovesAndSkipsUndoneRuns() throws {
    let lines = [
        #"{"run": "r1", "time": "2026-11-01T10:00:00", "op": "mkdir", "dst": "/dl/invoice"}"#,
        #"{"run": "r1", "time": "2026-11-01T10:00:01", "op": "move", "src": "/dl/a.pdf", "dst": "/dl/invoice/a.pdf"}"#,
        #"{"run": "r2", "time": "2026-11-01T11:00:00", "op": "move", "src": "/dl/b.zip", "dst": "/dl/Archives/b.zip"}"#,
        #"{"run": "r3", "time": "2026-11-01T12:00:00", "op": "rename", "src": "/dl/c.txt", "dst": "/dl/d.txt"}"#,
        #"{"undone": "r2"}"#,
        "not json",
    ]
    let file = FileManager.default.temporaryDirectory.appending(path: "history-\(UUID()).jsonl")
    try lines.joined(separator: "\n").write(to: file, atomically: true, encoding: .utf8)
    defer { try? FileManager.default.removeItem(at: file) }

    let history = History.load(from: file)
    #expect(history.runs == ["r1", "r3"])
    #expect(history.recent.map(\.destination.lastPathComponent) == ["d.txt", "a.pdf"])
    #expect(history.recent.last?.source.path() == "/dl/a.pdf")
    #expect(history.recent.first?.time != .distantPast)
}

@Test func missingFileIsEmpty() {
    let history = History.load(from: URL(filePath: "/nonexistent/history.jsonl"))
    #expect(history.runs.isEmpty && history.recent.isEmpty)
}
