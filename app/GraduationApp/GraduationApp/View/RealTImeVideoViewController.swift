import UIKit
import WebKit

class RealTImeVideoViewController: UIViewController, WKUIDelegate {
    

    @IBOutlet weak var testLabel: UILabel!
    
    @IBOutlet weak var webView: WKWebView!
    
    override func viewDidLoad() {
        super.viewDidLoad()

        //탭바 순서
        self.tabBarController?.selectedIndex = 1
        
        self.tabBarController?.tabBar.isHidden = false
                
//        loadWebPage("http://192.168.99.122:2204/")
        loadWebPage("http://192.168.123.167:2204/")

        
//        let stream_url = "http://192.168.35.11:2204/"
//
//        webView.uiDelegate = self
//        webView.load(NSURLRequest(url: NSURL(string: stream_url )! as URL) as URLRequest)
    }
    
//    override func viewWillAppear(_ animated: Bool) {
//        let tabbar = tabBarController as! BaseTabbarController
//        testLabel.text = String(describing: tabbar.theURL)
//
//    }
    

    func loadWebPage(_ url:String){
        let myUrl = URL(string: url)
        let myRequest = URLRequest(url:myUrl!)
        webView.load(myRequest)
    }


    @IBAction func refreshButton(_ sender: UIButton) {
        
        print("testLabel : " ,testLabel.text!)
        
        let tabbar = tabBarController as! BaseTabbarController
        testLabel.text = String(describing: tabbar.theURL)
        
        loadWebPage(tabbar.theURL)
    }
}
