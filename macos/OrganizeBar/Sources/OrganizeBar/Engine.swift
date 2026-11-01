import Foundation

/// Runs the Python engine and the service script of the organize project.
/// All file operations go through the engine, so they end up in the undo history.
struct Engine: Sendable {
    let project: URL
    let config: String

    var python: URL { project.appending(path: ".venv/bin/python") }
    var serviceScript: URL { project.appending(path: "scripts/macos-service.sh") }
    var logFile: URL {
        FileManager.default.homeDirectoryForCurrentUser
            .appending(path: "Library/Logs/organize/watch.log")
    }

    struct Result: Sendable {
        let status: Int32
        let output: String
    }

    struct Failure: LocalizedError {
        let message: String
        var errorDescription: String? { message }
    }

    /// The project folder is stored in the app's Info.plist by the build script.
    static func fromBundle() -> Engine? {
        let path =
            Bundle.main.object(forInfoDictionaryKey: "OrganizeProjectPath") as? String
            ?? ProcessInfo.processInfo.environment["ORGANIZE_PROJECT"]
        guard let path else { return nil }
        let config =
            Bundle.main.object(forInfoDictionaryKey: "OrganizeConfig") as? String ?? "downloads"
        return Engine(project: URL(filePath: path), config: config)
    }

    func organize(_ args: [String]) async throws -> Result {
        try await run(python, ["-m", "organize"] + args)
    }

    func service(_ command: String) async throws -> Result {
        try await run(URL(filePath: "/bin/sh"), [serviceScript.path(percentEncoded: false), command])
    }

    func info() async throws -> AppInfo {
        let result = try await organize(["info", config])
        guard result.status == 0, let data = result.output.data(using: .utf8) else {
            throw Failure(message: result.output.trimmingCharacters(in: .whitespacesAndNewlines))
        }
        return try JSONDecoder().decode(AppInfo.self, from: data)
    }

    func duplicates() async throws -> [Duplicate] {
        let result = try await organize(["duplicates", config])
        guard result.status == 0, let data = result.output.data(using: .utf8) else {
            throw Failure(message: result.output.trimmingCharacters(in: .whitespacesAndNewlines))
        }
        return try JSONDecoder().decode([Duplicate].self, from: data)
    }

    func isServiceRunning() async -> Bool {
        let result = try? await service("status")
        return result?.output.contains("state = running") ?? false
    }

    private func run(_ executable: URL, _ args: [String]) async throws -> Result {
        let project = self.project
        return try await withCheckedThrowingContinuation { continuation in
            DispatchQueue.global().async {
                let process = Process()
                process.executableURL = executable
                process.arguments = args
                process.currentDirectoryURL = project  // so `.env` is found
                var env = ProcessInfo.processInfo.environment
                env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                env["COLUMNS"] = "200"  // keep paths on one line in rich's output
                process.environment = env
                let pipe = Pipe()
                process.standardOutput = pipe
                process.standardError = pipe
                do {
                    try process.run()
                    let data = pipe.fileHandleForReading.readDataToEndOfFile()
                    process.waitUntilExit()
                    let output = String(decoding: data, as: UTF8.self)
                    continuation.resume(returning: Result(status: process.terminationStatus, output: output))
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }
}

/// A file marked as a copy of another one by the `mark_duplicate` action.
struct Duplicate: Decodable, Identifiable, Hashable, Sendable {
    var id: String { path }
    let path: String
    let original: String
    let originalExists: Bool

    var url: URL { URL(filePath: path) }
    var originalURL: URL { URL(filePath: original) }

    enum CodingKeys: String, CodingKey {
        case path, original
        case originalExists = "original_exists"
    }
}

struct AppInfo: Decodable, Sendable {
    let folders: [String]
    let categories: [String]
    let reviewFolders: [String]
    let historyFile: String
    let configPath: String

    enum CodingKeys: String, CodingKey {
        case folders, categories
        case reviewFolders = "review_folders"
        case historyFile = "history_file"
        case configPath = "config_path"
    }
}
