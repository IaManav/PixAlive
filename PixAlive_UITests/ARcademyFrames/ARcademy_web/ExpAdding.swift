import SceneKit
import Foundation

// Check arguments
let args = CommandLine.arguments
guard args.count > 1 else {
    print("Usage: swift RenameNodeToFilename.swift <model_path>")
    exit(1)
}

let modelPath = args[1]
let modelURL = URL(fileURLWithPath: modelPath)
let modelName = modelURL.deletingPathExtension().lastPathComponent

// Load scene
guard let scene = try? SCNScene(url: modelURL, options: nil) else {
    print("❌ Failed to load \(modelPath)")
    exit(1)
}

// Rename root node (if found)
if let node = scene.rootNode.childNodes.first {
    print("🔹 Old node name: \(node.name ?? "<none>")")
    node.name = modelName
    print("✅ New node name set to: \(modelName)")
} else {
    print("⚠️ No child node found to rename.")
}

// Save scene back
scene.write(to: modelURL, options: nil, delegate: nil, progressHandler: nil)
print("💾 Scene updated successfully at: \(modelPath)")