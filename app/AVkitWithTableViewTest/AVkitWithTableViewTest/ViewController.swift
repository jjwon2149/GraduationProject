//
//  ViewController.swift
//  AVkitWithTableViewTest
//
//  Created by 정종원 on 2023/02/11.
//


import UIKit
import Foundation
import Firebase
import FirebaseDatabase
import AVKit


class ViewController: UIViewController, UITableViewDelegate, UITableViewDataSource{
   
    
    
    var table = [Videos]()
    var ref: DatabaseReference!

    @IBOutlet weak var TableView: UITableView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        ref = Database.database().reference().child("videos")
        
        ref.observe(DataEventType.value, with: { [self](snapshot) in
            if snapshot.childrenCount > 0 {
                self.table.removeAll()
                
                for video in snapshot.children.allObjects as! [DataSnapshot] {
                    
                    let Object = video.value as? [String : String]
                    let Title = Object?["Title"]
                    let videolink = Object?["link"]
                    
                    print(Title)
                    print(videolink)
                    
                    
                    let video = Videos(Title: Title as? String, link: videolink as? String)
                    self.table.append(video)
                    
                    TableView.delegate = self
                    TableView.dataSource = self
                    self.TableView.reloadData()
                    
                }
            }
            
        })
        
        
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return table.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = TableView.dequeueReusableCell(withIdentifier: "cell") as! TableViewCell
        
        let video: Videos
        
        video = table[indexPath.row]
        cell.titleLabel.text = video.Title
        
        return cell
        
        
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        guard let videoURL = URL(string: table[indexPath.row].link!) else {
            return
        }
        
        let player = AVPlayer(url: videoURL)
        
        let controller = AVPlayerViewController()
        controller.player = player
        
        present(controller, animated: true) {
            player.play()
        }
        print("tabVIew clicked")
    }
    
    
    
//    @IBAction func downloadVideo(_ sender: Any) {
//        print("download")
//    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}
