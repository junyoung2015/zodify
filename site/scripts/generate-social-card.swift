// Local asset authoring only. The website build uses the checked-in PNG.
import AppKit

let size = NSSize(width: 1200, height: 630)
let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: 1200, pixelsHigh: 630, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
NSColor(srgbRed: 3/255, green: 0, blue: 20/255, alpha: 1).setFill()
NSRect(origin: .zero, size: size).fill()
let lavender = NSColor(srgbRed: 196/255, green: 165/255, blue: 1, alpha: 1)
let text = NSColor(srgbRed: 226/255, green: 232/255, blue: 240/255, alpha: 1)

func label(_ value: String, _ x: CGFloat, _ y: CGFloat, _ size: CGFloat, _ weight: NSFont.Weight, _ color: NSColor) {
  (value as NSString).draw(at: NSPoint(x: x, y: y), withAttributes: [
    .font: NSFont.systemFont(ofSize: size, weight: weight),
    .foregroundColor: color,
  ])
}

// Polygon follows the existing Z favicon's silhouette.
lavender.setFill()
let mark = NSBezierPath()
mark.move(to: NSPoint(x: 80, y: 490))
for point in [NSPoint(x: 174, y: 490), NSPoint(x: 174, y: 465), NSPoint(x: 113, y: 416), NSPoint(x: 174, y: 416), NSPoint(x: 174, y: 390), NSPoint(x: 80, y: 390), NSPoint(x: 80, y: 415), NSPoint(x: 142, y: 464), NSPoint(x: 80, y: 464)] { mark.line(to: point) }
mark.close()
mark.fill()
label("zodify", 204, 387, 80, .bold, .white)
label("Validation for", 80, 257, 62, .semibold, .white)
label("Python dictionaries.", 80, 177, 62, .semibold, .white)
label("Zero required runtime dependencies", 80, 96, 30, .regular, text)
label("zodify.dev", 939, 44, 24, .medium, lavender)
NSGraphicsContext.restoreGraphicsState()

let output = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("public/og-image.png")
try bitmap.representation(using: .png, properties: [:])!.write(to: output)
print("Wrote \(output.path)")
