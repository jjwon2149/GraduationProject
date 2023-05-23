import UIKit
import WebKit

class RealTImeVideoViewController: UIViewController, WKUIDelegate {
    

    @IBOutlet weak var testLabel: UILabel!
    
    @IBOutlet weak var indicator: UIActivityIndicatorView!
    
    @IBOutlet weak var webView: WKWebView!
    
    override func viewDidLoad() {
        super.viewDidLoad()

        //탭바 순서
        self.tabBarController?.selectedIndex = 1
        
        self.tabBarController?.tabBar.isHidden = false
                
//        loadWebPage("http://192.168.99.122:2204/")
        loadWebPage("http://52.79.155.38:2204/")

        
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
    @objc func didEnterBackground() {
            print("didEnterBackgroud")
            
            let RealTImeVideoVC = self.storyboard?.instantiateViewController(identifier: "RealTImeVideoViewController") as! RealTImeVideoViewController
            self.modalPresentationStyle = .fullScreen
            self.present(RealTImeVideoVC, animated: true, completion: nil)
        }
    
    

    func loadWebPage(_ url:String){
        let myUrl = URL(string: url)
        let myRequest = URLRequest(url:myUrl!)
        webView.load(myRequest)
    }


    @IBAction func refreshButton(_ sender: UIButton) {
        loadWebPage("http://52.79.155.38:2204/")
    }
    
    @IBAction func callButtonClicked(_ sender: UIButton) {
        let number:Int = 1011112222
                
        // URLScheme 문자열을 통해 URL 인스턴스를 만들어 줍니다.
        if let url = NSURL(string: "tel://0" + "\(number)"),
        
               //canOpenURL(_:) 메소드를 통해서 URL 체계를 처리하는 데 앱을 사용할 수 있는지 여부를 확인
               UIApplication.shared.canOpenURL(url as URL) {
               
               //사용가능한 URLScheme이라면 open(_:options:completionHandler:) 메소드를 호출해서
               //만들어둔 URL 인스턴스를 열어줍니다.
                UIApplication.shared.open(url as URL, options: [:], completionHandler: nil)
        }
    }
    
    
    @IBAction func messageButtonClicked(_ sender: UIButton) {
        let message = "??시???동 ??에서 폭력상황 발생하였습니다. 출동해주세요."
        var sms : String = "sms:01011211211"
 
        sms = sms + "&body=" + message
        sms = sms.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!   // 인코딩
 
        // UIApplication.shared.open : 지정된 url을 비동기로 연다
        UIApplication.shared.open( URL.init(string: sms)!, options: [:], completionHandler: nil )
    }
    
}
