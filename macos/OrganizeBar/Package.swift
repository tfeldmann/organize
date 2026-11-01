// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "OrganizeBar",
    platforms: [.macOS(.v14)],
    targets: [
        .executableTarget(name: "OrganizeBar"),
        .testTarget(name: "OrganizeBarTests", dependencies: ["OrganizeBar"]),
    ]
)
