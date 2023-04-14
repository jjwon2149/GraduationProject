import UIKit



class SettingViewController: UIViewController {

    @IBOutlet weak var UrlTextField: UITextField!
    @IBOutlet weak var UrlSendButton: UIButton!
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
                
        //탭바 순서
        self.tabBarController?.selectedIndex = 2
        
        
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        let tabbar = tabBarController as! BaseTabbarController
        tabbar.theURL = UrlTextField.text!
    }
    
    
    @IBAction func UrlSend(_ sender: UIButton) {
        
        print("SendButton Clicked")
        
        let tabbar = tabBarController as! BaseTabbarController
        tabbar.theURL = UrlTextField.text!

    }
    

}
