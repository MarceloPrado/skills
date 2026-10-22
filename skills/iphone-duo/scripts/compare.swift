#!/usr/bin/env swift
// Usage: swift compare.swift <shots-dir> <out.png> [--title "App on iPhone Duo"] [--only screen1,screen2] [--per-page 6]
//
// Pairs <screen>-<pose>-before.png with <screen>-<pose>-after.png and stacks the pairs, before on the left, one row per
// screen and pose. More pairs than fit one sheet go to <out>-2.png, <out>-3.png, and so on.

import AppKit

let poseOrder = ["closed", "closed-landscape", "open", "book", "laptop", "open-portrait", "split"]
let imageHeight: CGFloat = 900
let margin: CGFloat = 64
let gap: CGFloat = 40
let background = NSColor(srgbRed: 0.96, green: 0.96, blue: 0.97, alpha: 1)
let ink = NSColor(srgbRed: 0.11, green: 0.11, blue: 0.12, alpha: 1)
let muted = NSColor(srgbRed: 0.43, green: 0.43, blue: 0.45, alpha: 1)

struct Pair {
    let screen: String
    let pose: String
    let before: NSImage
    let after: NSImage
}

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(1)
}

var arguments = Array(CommandLine.arguments.dropFirst())
func option(_ name: String) -> String? {
    guard let index = arguments.firstIndex(of: name), index + 1 < arguments.count else { return nil }
    let value = arguments[index + 1]
    arguments.removeSubrange(index...index + 1)
    return value
}
let title = option("--title")
let only = option("--only").map { Set($0.split(separator: ",").map(String.init)) }
let perPage = option("--per-page").flatMap(Int.init) ?? 6
guard arguments.count == 2, perPage > 0 else {
    fail("usage: swift compare.swift <shots-dir> <out.png> [--title T] [--only a,b] [--per-page N]")
}
let directory = URL(fileURLWithPath: arguments[0])
let output = URL(fileURLWithPath: arguments[1])

func split(_ stem: String) -> (screen: String, pose: String) {
    for pose in poseOrder.sorted(by: { $0.count > $1.count }) where stem.hasSuffix("-" + pose) {
        return (String(stem.dropLast(pose.count + 1)), pose)
    }
    guard let dash = stem.firstIndex(of: "-") else { return (stem, "") }
    return (String(stem[..<dash]), String(stem[stem.index(after: dash)...]))
}

func load(_ name: String) -> NSImage {
    guard let image = NSImage(contentsOf: directory.appendingPathComponent(name)), image.isValid else {
        fail("can't read \(directory.appendingPathComponent(name).path)")
    }
    return image
}

let names = Set((try? FileManager.default.contentsOfDirectory(atPath: directory.path)) ?? [])
var pairs: [Pair] = []
var screens: [String] = []
var unpaired: [String] = []
for name in names.sorted() where name.hasSuffix("-before.png") {
    let stem = String(name.dropLast("-before.png".count))
    let (screen, pose) = split(stem)
    if let only, !only.contains(screen) { continue }
    guard names.contains(stem + "-after.png") else {
        unpaired.append(stem)
        continue
    }
    if !screens.contains(screen) { screens.append(screen) }
    pairs.append(Pair(screen: screen, pose: pose, before: load(name), after: load(stem + "-after.png")))
}
if !unpaired.isEmpty {
    FileHandle.standardError.write(Data("no after shot for: \(unpaired.joined(separator: ", "))\n".utf8))
}
guard !pairs.isEmpty else { fail("no <name>-before.png with a matching <name>-after.png in \(directory.path)") }
pairs.sort {
    let screenOrder = (screens.firstIndex(of: $0.screen)!, screens.firstIndex(of: $1.screen)!)
    if screenOrder.0 != screenOrder.1 { return screenOrder.0 < screenOrder.1 }
    return (poseOrder.firstIndex(of: $0.pose) ?? poseOrder.count) < (poseOrder.firstIndex(of: $1.pose) ?? poseOrder.count)
}

func width(of image: NSImage) -> CGFloat {
    let rep = image.representations.first
    let size = rep.map { CGSize(width: $0.pixelsWide, height: $0.pixelsHigh) } ?? image.size
    return imageHeight * size.width / size.height
}

let titleFont = NSFont.systemFont(ofSize: 56, weight: .bold)
let rowFont = NSFont.systemFont(ofSize: 40, weight: .semibold)
let labelFont = NSFont.systemFont(ofSize: 32, weight: .medium)
let titleHeight: CGFloat = title == nil ? 0 : 110
let rowHeader: CGFloat = 70
let labelHeight: CGFloat = 52
let rowHeight = rowHeader + labelHeight + imageHeight + gap * 1.5

func render(_ page: ArraySlice<Pair>, title: String?, to url: URL) {
    let rowWidths = page.map { width(of: $0.before) + gap + width(of: $0.after) }
    let widest = rowWidths.max() ?? 0
    let canvas = CGSize(width: widest + margin * 2, height: margin * 2 + titleHeight + rowHeight * CGFloat(page.count))
    guard let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(canvas.width), pixelsHigh: Int(canvas.height),
                                        bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                                        colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0) else { fail("no bitmap") }
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
    NSGraphicsContext.current?.imageInterpolation = .high
    background.setFill()
    NSRect(origin: .zero, size: canvas).fill()

    // AppKit draws from the bottom left; `top` converts a distance from the top edge.
    func top(_ y: CGFloat, _ height: CGFloat) -> CGFloat { canvas.height - y - height }
    func draw(_ text: String, font: NSFont, color: NSColor, x: CGFloat, y: CGFloat) {
        let attributed = NSAttributedString(string: text, attributes: [.font: font, .foregroundColor: color])
        attributed.draw(at: CGPoint(x: x, y: top(y, attributed.size().height)))
    }
    func draw(_ image: NSImage, x: CGFloat, y: CGFloat) {
        let rect = NSRect(x: x, y: top(y, imageHeight), width: width(of: image), height: imageHeight)
        NSGraphicsContext.saveGraphicsState()
        NSBezierPath(roundedRect: rect, xRadius: 36, yRadius: 36).addClip()
        image.draw(in: rect)
        NSGraphicsContext.restoreGraphicsState()
    }

    var y = margin
    if let title {
        draw(title, font: titleFont, color: ink, x: margin, y: y)
        y += titleHeight
    }
    for (pair, rowWidth) in zip(page, rowWidths) {
        let x = margin + (widest - rowWidth) / 2
        let name = pair.pose.isEmpty ? pair.screen : "\(pair.screen) · \(pair.pose)"
        draw(name.replacingOccurrences(of: "-", with: " ").capitalized, font: rowFont, color: ink, x: x, y: y)
        y += rowHeader
        let afterX = x + width(of: pair.before) + gap
        draw("Before", font: labelFont, color: muted, x: x, y: y)
        draw("After", font: labelFont, color: muted, x: afterX, y: y)
        y += labelHeight
        draw(pair.before, x: x, y: y)
        draw(pair.after, x: afterX, y: y)
        y += imageHeight + gap * 1.5
    }
    NSGraphicsContext.restoreGraphicsState()

    guard let png = bitmap.representation(using: .png, properties: [:]) else { fail("could not encode PNG") }
    do { try png.write(to: url) } catch { fail("could not write \(url.path): \(error.localizedDescription)") }
    print("\(url.path): \(page.count) pairs, \(Int(canvas.width))x\(Int(canvas.height))")
}

let pages = stride(from: 0, to: pairs.count, by: perPage).map { pairs[$0..<min($0 + perPage, pairs.count)] }
let base = output.deletingPathExtension()
for (index, page) in pages.enumerated() {
    let url = index == 0 ? output : base.deletingLastPathComponent().appendingPathComponent("\(base.lastPathComponent)-\(index + 1).png")
    let pageTitle = pages.count > 1 ? title.map { "\($0) (\(index + 1)/\(pages.count))" } : title
    render(page, title: pageTitle, to: url)
}
