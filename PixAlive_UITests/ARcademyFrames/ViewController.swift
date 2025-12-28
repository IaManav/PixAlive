//
//  ViewController.swift
//  ARcademyFrames
//
//  Created by Karman Singh on 11/3/25.
//
import UIKit
import SceneKit
import ARKit
import AVFoundation
import SpriteKit

class ViewController: UIViewController, ARSCNViewDelegate {
    
    @IBOutlet var sceneView: ARSCNView!
    var videoPlayers: [UUID: AVPlayer] = [:]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        sceneView.delegate = self
        sceneView.showsStatistics = true
        sceneView.autoenablesDefaultLighting = true
        //sceneView.debugOptions = [.showFeaturePoints]
        
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        sceneView.addGestureRecognizer(tapGesture)
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        
       
        let configuration = ARWorldTrackingConfiguration()
        
       
        var allReferenceImages = Set<ARReferenceImage>()
        
        if let newsImages = ARReferenceImage.referenceImages(inGroupNamed: "VideoBaseImg", bundle: .main) {
            allReferenceImages.formUnion(newsImages)
        }
        if let baseCards = ARReferenceImage.referenceImages(inGroupNamed: "horizontal3D", bundle: .main) {
            allReferenceImages.formUnion(baseCards)
        }
        if let baseCardsV = ARReferenceImage.referenceImages(inGroupNamed: "vertical3d", bundle: .main) {
            allReferenceImages.formUnion(baseCardsV)
        }
        
        configuration.detectionImages = allReferenceImages
        configuration.maximumNumberOfTrackedImages = 5
        
        sceneView.session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
        
        print("AR session started with \(allReferenceImages.count) total reference images.")
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        sceneView.session.pause()
    }
    
    
    // MARK: - ARSCNViewDelegate
    func renderer(_ renderer: SCNSceneRenderer, nodeFor anchor: ARAnchor) -> SCNNode? {
        let node = SCNNode()
        guard let imageAnchor = anchor as? ARImageAnchor,
              let imageName = imageAnchor.referenceImage.name else { return node }
        
        print("Detected image: \(imageName)")
        
        let imageWidth = imageAnchor.referenceImage.physicalSize.width
        let imageHeight = imageAnchor.referenceImage.physicalSize.height
        
        
        if imageAnchor.referenceImage.resourceGroupName == "horizontal3D" {
            // --- Display 3D model ---
            let plane = SCNPlane(width: imageWidth, height: imageHeight)
            plane.firstMaterial?.diffuse.contents = UIColor(white: 1.0, alpha: 0.5)
            let planeNode = SCNNode(geometry: plane)
            planeNode.eulerAngles.x = -.pi / 2
            node.addChildNode(planeNode)
            
            if let organScene = SCNScene(named: "art.scnassets/\(imageName).scn"),
               let organNode = organScene.rootNode.childNodes.first {
                organNode.eulerAngles.x = .pi / 2
                planeNode.addChildNode(organNode)
                print("3D model loaded for \(imageName)")
            } else {
                print("No 3D model found for \(imageName)")
            }
        }
        else if imageAnchor.referenceImage.resourceGroupName == "vertical3d" {
            
            let plane = SCNPlane(width: imageWidth, height: imageHeight)
            plane.firstMaterial?.diffuse.contents = UIColor(white: 1.0, alpha: 0.5)
            let planeNode = SCNNode(geometry: plane)
            planeNode.eulerAngles.x = .pi / 2
            node.addChildNode(planeNode)
            
            if let organScene = SCNScene(named: "art.scnassets/\(imageName).scn"),
               let organNode = organScene.rootNode.childNodes.first {
                organNode.eulerAngles.x = -.pi / 2
                planeNode.addChildNode(organNode)
                print("3D model loaded for \(imageName)")
            } else {
                print("No 3D model found for \(imageName)")
            }
        }
        else if imageAnchor.referenceImage.resourceGroupName == "VideoBaseImg" {
            
            guard let videoURL = Bundle.main.url(forResource: imageName, withExtension: "mp4") else {
                print("No video file found for \(imageName)")
                return node
            }
            
            let player = AVPlayer(url: videoURL)
            player.play()
            let videoNode = SKVideoNode(avPlayer: player)
            videoNode.play()
            let videoScene = SKScene(size: CGSize(width: 480, height: 360))
            videoNode.position = CGPoint(x: videoScene.size.width / 2, y: videoScene.size.height / 2)
            videoNode.size = videoScene.size
            videoNode.yScale = -1.0
            videoScene.addChild(videoNode)
            
            let plane = SCNPlane(width: imageWidth, height: imageHeight)
            plane.firstMaterial?.diffuse.contents = videoScene
            plane.firstMaterial?.isDoubleSided = true
            
            let planeNode = SCNNode(geometry: plane)
            planeNode.eulerAngles.x = -.pi / 2
            node.addChildNode(planeNode)
            
           
            videoPlayers[imageAnchor.identifier] = player
            planeNode.name = imageAnchor.identifier.uuidString
            print("Video ready for \(imageName)")
        }
        
        return node
    }
    
    
    // MARK: - Pause Video When Image Disappears
    func renderer(_ renderer: SCNSceneRenderer, didUpdate node: SCNNode, for anchor: ARAnchor) {
        guard let imageAnchor = anchor as? ARImageAnchor else { return }
        if !imageAnchor.isTracked {
               if let player = videoPlayers[imageAnchor.identifier] {
                   player.pause()
                   print("Paused video as image lost.")
               }
           } else {
               if let player = videoPlayers[imageAnchor.identifier] {
                   player.play()
                   player.rate = 1.0
                   print("Resumed video as image found again.")
               }
           }
    }
    
    func renderer(_ renderer: SCNSceneRenderer, didRemove node: SCNNode, for anchor: ARAnchor) {
        guard let imageAnchor = anchor as? ARImageAnchor else { return }
        if let player = videoPlayers[imageAnchor.identifier] {
            player.pause()
            videoPlayers.removeValue(forKey: imageAnchor.identifier)
            print("Removed video as image disappeared.")
        }
    }
    
    
    // MARK: - Tap Gesture to Play/Pause
    @objc func handleTap(_ gestureRecognizer: UITapGestureRecognizer) {
        let touchLocation = gestureRecognizer.location(in: sceneView)
        let hitTestResults = sceneView.hitTest(touchLocation, options: nil)
        
        for hitResult in hitTestResults {
            if let uuidString = hitResult.node.name,
               let uuid = UUID(uuidString: uuidString),
               let player = videoPlayers[uuid] {
                
                
                for (otherUUID, otherPlayer) in videoPlayers where otherUUID != uuid {
                    otherPlayer.pause()
                }
                
                if player.timeControlStatus == .paused {
                    player.play()
                    print("Playing video \(uuid)")
                } else {
                    player.pause()
                    print("Pausing video \(uuid)")
                }
                return
            }
        }
    }
}
