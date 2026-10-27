#!/usr/bin/env swift
import AppKit
import Foundation

guard CommandLine.arguments.count >= 3 else {
    print("Uso: render_icon.swift <input.svg> <output_dir>")
    exit(1)
}

let svgPath = CommandLine.arguments[1]
let outputDir = CommandLine.arguments[2]
let svgUrl = URL(fileURLWithPath: svgPath)

guard let svgImage = NSImage(contentsOf: svgUrl) else {
    print("Erro: Não foi possível carregar o SVG em \(svgPath)")
    exit(1)
}

let sizes: [(String, Int)] = [
    ("icon_16x16.png", 16),
    ("icon_16x16@2x.png", 32),
    ("icon_32x32.png", 32),
    ("icon_32x32@2x.png", 64),
    ("icon_128x128.png", 128),
    ("icon_128x128@2x.png", 256),
    ("icon_256x256.png", 256),
    ("icon_256x256@2x.png", 512),
    ("icon_512x512.png", 512),
    ("icon_512x512@2x.png", 1024)
]

let fm = FileManager.default
try? fm.createDirectory(atPath: outputDir, withIntermediateDirectories: true)

for (filename, size) in sizes {
    let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: size,
        pixelsHigh: size,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    )!
    rep.size = NSSize(width: size, height: size)

    NSGraphicsContext.saveGraphicsState()
    let ctx = NSGraphicsContext(bitmapImageRep: rep)
    ctx?.imageInterpolation = .high
    NSGraphicsContext.current = ctx

    // Garante 100% de transparência alpha (sem fundo branco)
    NSColor.clear.set()
    NSRect(x: 0, y: 0, width: size, height: size).fill()

    svgImage.draw(
        in: NSRect(x: 0, y: 0, width: size, height: size),
        from: NSRect(origin: .zero, size: svgImage.size),
        operation: .sourceOver,
        fraction: 1.0
    )

    NSGraphicsContext.restoreGraphicsState()

    if let pngData = rep.representation(using: .png, properties: [:]) {
        let outUrl = URL(fileURLWithPath: "\(outputDir)/\(filename)")
        try? pngData.write(to: outUrl)
    }
}

print("✓ [Icon Renderer] Todas as 10 resoluções do ícone foram geradas com transparência real (alpha=0).")
