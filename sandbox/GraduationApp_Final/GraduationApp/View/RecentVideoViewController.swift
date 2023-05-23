import UIKit
import Foundation
import Firebase
import FirebaseDatabase
import AVKit

class RecentVideoViewController: UIViewController, UITableViewDelegate, UITableViewDataSource,UISearchBarDelegate {
    

    var table = [Videos]()
    var ref: DatabaseReference!
    var searchResults: [Videos] = []


    @IBOutlet weak var SearchBar: UISearchBar!
    @IBOutlet weak var TableView: UITableView!
    
    
    override func viewDidLoad() {
    
        super.viewDidLoad()
        
        //탭바 순서
        self.tabBarController?.selectedIndex = 0
        
        SearchBar.delegate = self
        
        ref = Database.database().reference().child("videos")
        
        ref.observe(DataEventType.value, with: { [self](snapshot) in
            if snapshot.childrenCount > 0 {
                self.table.removeAll()
                
                for video in snapshot.children.allObjects as! [DataSnapshot] {
                    
                    let Object = video.value as? [String : String]
                    let Title = Object?["Title"]
                    let videolink = Object?["link"]
                    
                    print("Title : ",Title as Any)
                    print("link : ",videolink as Any)
                    
                    
                    let video = Videos(Title: Title as? String, link: videolink as? String)
                    self.table.append(video)
                    
                    
                    TableView.delegate = self
                    TableView.dataSource = self
                    self.TableView.reloadData()
                }
            }
        })
    }
    
//    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
//        return table.count
//    }
//
//    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
//        let cell = TableView.dequeueReusableCell(withIdentifier: "cell") as! TableViewCell
//
//        let video: Videos
//
//        video = table[indexPath.row]
//        cell.titleLabel.text = video.Title
//
//        return cell
//    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return searchResults.isEmpty ? table.count : searchResults.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell", for: indexPath) as! TableViewCell
        
        let video: Videos
        
        if searchResults.isEmpty {
            video = table[indexPath.row]
        } else {
            video = searchResults[indexPath.row]
        }
        
        cell.titleLabel.text = video.Title
        
        //삭제 버튼 기능 구현
        cell.deleteButtonAction = { [unowned self] in
//            print("deleteButtonAction")
            
            var videoTitle: String?
            if searchResults.isEmpty {
                videoTitle = video.Title
            } else {
                videoTitle = video.Title
            }
            
            
            let databaseRef = Database.database().reference().child("videos")

            let query = databaseRef.queryOrdered(byChild: "Title").queryEqual(toValue: videoTitle)

            query.observeSingleEvent(of: .value, with: { snapshot in
                guard let snapDict = snapshot.value as? [String:AnyObject] else { return }

                for each in snapDict {
                    guard let key = each.key as? String else { continue }
                    databaseRef.child(key).removeValue()
                }
            })
            
//            ref = Database.database().reference().child("videos")
//            ref.child("\(indexPath.row + 1)").removeValue()
            print(videoTitle)
            print("remove")
        }
        
        //다운로드 버튼 기능 구현
        cell.downloadButtonAction = { [unowned self] in
//            print("downloadButtonAction")
            let videoURL: URL?
            var videoTitle: String?
            if searchResults.isEmpty {
                videoURL = URL(string: video.link!)
                videoTitle = video.Title
            } else {
                videoURL = URL(string: video.link!)
                videoTitle = video.Title
            }

            guard let url = videoURL, let title = videoTitle else {
                return
            }

            let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    
            let destinationURL = documentsDirectory.appendingPathComponent(url.lastPathComponent)

            
            let downloadTask = URLSession.shared.downloadTask(with: url) { urlOrNil, responseOrNil, errorOrNil in
                // check for and handle errors:
                // * errorOrNil should be nil
                // * responseOrNil should be an HTTPURLResponse with statusCode in 200..<299

                guard let fileURL = urlOrNil else {
                    return
                }
                
                do {
                   try FileManager.default.moveItem(at: fileURL, to: destinationURL)
                   print("File moved to documents folder")
                   
//                       VideosManager.shared.addVideo(title: title, url: destinationURL)
                   
                   } catch {
                       print("Error: \(error)")
                }
            }

            downloadTask.resume()
        }
    
        
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
    
    func searchBarCancelButtonClicked(_ searchBar: UISearchBar)
    {
        SearchBar.text = nil // 서치바의 텍스트를 지움
        SearchBar.showsCancelButton = false // 취소 버튼 감추기
        SearchBar.resignFirstResponder() // 키보드 내리기
        searchResults.removeAll() // 검색 결과 초기화
//        table.removeAll() // 테이블 뷰의 데이터 초기화
        TableView.reloadData() // 테이블 뷰 리로드
    }

        

    func searchBar(_ searchBar: UISearchBar, textDidChange searchText: String) {
        if searchText.isEmpty {
            // 검색어가 없을 경우, 모든 동영상을 표시
            searchResults = table
        } else {
            // 검색어가 있을 경우, 검색 결과를 찾아서 searchResults에 저장
            searchResults = table.filter { video in
                // 동영상 제목이나 설명에 검색어가 포함되어 있는지 확인
                if let title = video.Title {
                    return title.lowercased().contains(searchText.lowercased())
                } else {
                    return false
                }
            }
        }
        TableView.reloadData()
    }
    
    func searchBarSearchButtonClicked(_ searchBar: UISearchBar) {
        searchBar.resignFirstResponder() // 키보드 내리기
        if let searchText = searchBar.text, !searchText.isEmpty {
            // 검색어가 입력되었을 경우, 검색 실행
            searchResults = table.filter { video in
                if let title = video.Title {
                    return title.lowercased().contains(searchText.lowercased())
                } else {
                    return false
                }
            }
        } else {
            // 검색어가 입력되지 않았을 경우, 모든 동영상을 표시
            searchResults = table
        }
        TableView.reloadData()
    }

    //키보드 올리기
    func searchBarTextDidBeginEditing(_ searchBar: UISearchBar) {
        searchBar.showsCancelButton = true
        searchBar.becomeFirstResponder()
    }
    
    //키보드내리기
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        self.view.endEditing(true)
    }
    func searchBarTextDidEndEditing(_ searchBar: UISearchBar) {
        searchBar.showsCancelButton = false
        searchBar.resignFirstResponder()
    }
    
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }
    
}
