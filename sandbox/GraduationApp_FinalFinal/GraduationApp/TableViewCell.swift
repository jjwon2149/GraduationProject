import UIKit

class TableViewCell: UITableViewCell {


    @IBOutlet weak var titleLabel : UILabel!
    @IBOutlet weak var downloadBtn: UIButton!
    @IBOutlet weak var deleteBtn: UIButton!
    
    //다운로드 버튼의 클로저 프로퍼티
    var downloadButtonAction : (() -> ())?
    var deleteButtonAction : (() -> ())?
    
    
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    @IBAction func deleteBtnClicked(_ sender: Any) {
        print("Delete Button Clicked")
        deleteButtonAction?()
    }
    
    @IBAction func downloadBtnClicked(_ sender: Any) {
        print("Download Button Clicked")
        downloadButtonAction?()
    }
    
    
    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)
    }

}
