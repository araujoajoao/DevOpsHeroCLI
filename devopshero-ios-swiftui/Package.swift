// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "DevOpsHero",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .executable(name: "DevOpsHero", targets: ["DevOpsHero"])
    ],
    targets: [
        .executableTarget(
            name: "DevOpsHero",
            path: "Sources",
            resources: [
                .process("Resources")
            ]
        )
    ]
)

