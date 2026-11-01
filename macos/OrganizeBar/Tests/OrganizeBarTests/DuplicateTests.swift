import Foundation
import Testing

@testable import OrganizeBar

@Test func decodesDuplicatesFromEngine() throws {
    let json = #"[{"path": "/dl/invoice/a-2.pdf", "original": "/dl/invoice/a.pdf", "original_exists": true}]"#
    let items = try JSONDecoder().decode([Duplicate].self, from: Data(json.utf8))
    #expect(items.count == 1)
    #expect(items[0].url.lastPathComponent == "a-2.pdf")
    #expect(items[0].originalURL.lastPathComponent == "a.pdf")
    #expect(items[0].originalExists)
}
