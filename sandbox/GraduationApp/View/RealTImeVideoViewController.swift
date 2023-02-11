//
//  RealTImeVideoViewController.swift
//  GraduationApp
//
//  Created by 정종원 on 2023/02/06.
//

import UIKit
import WebKit

class RealTImeVideoViewController: UIViewController, WKUIDelegate {

    @IBOutlet weak var webView: WKWebView!
    
    
    override func viewDidLoad() {
        super.viewDidLoad()

        //탭바 순서
        self.tabBarController?.selectedIndex = 1
        
        self.tabBarController?.tabBar.isHidden = false
        
        loadWebPage("http://192.168.35.11:2204/")
        
//        let stream_url = "http://192.168.35.11:2204/"
//
//        webView.uiDelegate = self
//        webView.load(NSURLRequest(url: NSURL(string: stream_url )! as URL) as URLRequest)
    }
    

    func loadWebPage(_ url:String){
        let myUrl = URL(string: url)
        let myRequest = URLRequest(url:myUrl!)
        webView.load(myRequest)
    }

}
