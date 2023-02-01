  
import functools 
from PyQt5.QtWidgets import  QCheckBox,QLabel ,QLineEdit,QSpinBox,QPushButton,QDialog,QVBoxLayout ,QHeaderView 
from PyQt5.QtWidgets import    QHBoxLayout, QTableView 
from PyQt5.QtGui import QStandardItem, QStandardItemModel 
from PyQt5.QtWidgets import   QComboBox    
from PyQt5.QtCore import Qt,QSize  
from utils.chaos import checkencoding
from utils.config import globalconfig ,_TR,_TRL

from utils.wrapper import Singleton
@Singleton
class codeacceptdialog(QDialog):
    def __init__(dialog, object ) -> None:
        super().__init__(object,Qt.WindowCloseButtonHint)
    
        title=  '接受的编码' 
        dialog.setWindowTitle(_TR(title))
        #dialog.setWindowModality(Qt.ApplicationModal)
        
        formLayout = QVBoxLayout(dialog)  # 配置layout
            
        model=QStandardItemModel(len(globalconfig['accept_encoding']),1 , dialog)
        nowsuppertcodes=_TRL(['日语(SHIFT-JIS)','简体中文(GBK)','繁体中文(BIG5)','韩语(EUC-KR)','英语(ASCII)' ,'其他'])
        nowsuppertcodespy=['SHIFT-JIS','GBK','BIG5','EUC-KR','ASCII' ]
        model.setHorizontalHeaderLabels(_TRL(['接受的编码']))
        table = QTableView(dialog)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        def _setcode_i(combox:QComboBox, itemsaver_,code='',idx=0): 
                    itemsaver_.saveidx=idx
                    if idx<len(nowsuppertcodespy):
                            itemsaver_.setText(nowsuppertcodespy[idx])
                            combox.setEditable(False)
                    else:
                            itemsaver_.setText(code)
                            combox.setCurrentText(code)
                            combox.setEditable(True) 
                            combox.setEditText(code) 
        def _setcode_c(combox:QComboBox, itemsaver_,code='' ):  
                    if combox.currentIndex()==len(nowsuppertcodespy):
                            itemsaver_.setText(code)
        row=0
        for code in  (globalconfig['accept_encoding']):                                   # 2
            
            if code in nowsuppertcodespy:
                    idx=nowsuppertcodespy.index(code)
            else:
                    idx=len(nowsuppertcodespy)
            itemsaver=QStandardItem('')
            model.setItem(row,0,itemsaver) 
            index=model.index(row,0)
            codecombox=QComboBox() 
            codecombox.addItems((nowsuppertcodes)) 
            codecombox.setCurrentIndex(idx)
            table.setIndexWidget(index,codecombox)
            _setcode_i(codecombox,itemsaver,code,idx)
            
            codecombox.currentIndexChanged.connect(functools.partial(_setcode_i,codecombox, itemsaver,''))
            codecombox.currentTextChanged.connect(functools.partial(_setcode_c,codecombox, itemsaver ))

            row+=1
        
        button=QPushButton(dialog)
        button.setText(_TR('添加行'))
        def clicked1(): 
            itemsaver=QStandardItem('')
            model.insertRow(0,[itemsaver]) 
            codecombox=QComboBox() 
            codecombox.addItems((nowsuppertcodes)) 
            _setcode_i(codecombox,itemsaver)
            codecombox.currentIndexChanged.connect(functools.partial(_setcode_i,codecombox, itemsaver,''))
            codecombox.currentTextChanged.connect(functools.partial(_setcode_c,codecombox, itemsaver ))
            index=model.index(0,0) 
            table.setIndexWidget(index,codecombox)
            
        button.clicked.connect(clicked1)
        button2=QPushButton(dialog)
        button2.setText(_TR('删除选中行'))
        def clicked2():
            
            model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2) 

        
        
        def clicked3(_): 
            button.setFocus() 
            rows=model.rowCount() 
            ll=[]
            for row in range(rows):
                print(row)
                code=model.item(row,0).text() 
                idx=model.item(row,0).saveidx
                print(idx,code)
                
                if idx==len(nowsuppertcodespy) :
                    if code.upper() in nowsuppertcodespy:
                            code=code.upper()
                    elif checkencoding(code)==False:
                            continue
                else:
                    code=nowsuppertcodespy[idx]
                if code in ll:
                    continue
                ll.append(code) 
            globalconfig['accept_encoding']=ll  
        dialog.closeEvent=(clicked3)
        formLayout.addWidget(table)
        formLayout.addWidget(button)
        formLayout.addWidget(button2) 
        formLayout.addWidget(QLabel()) 
        
        _checkunicode=QCheckBox(_TR("使用Unicode范围过滤"))
        _checkunicode.setChecked(globalconfig['accept_use_unicode'])
        _checkunicode.stateChanged.connect(lambda x: globalconfig.__setitem__('accept_use_unicode',x)) 
        formLayout.addWidget(_checkunicode)
        liwai=QLineEdit(globalconfig['accept_character']) 
        liwai.textChanged.connect(lambda x: globalconfig.__setitem__('accept_character',x))
        _hb=QHBoxLayout()
        _hb.addWidget(QLabel(_TR("Unicode范围"))) 
        _hb.addWidget(object.getspinbox(0,65535,globalconfig,'accept_use_unicode_start' ))
        _hb.addWidget(object.getspinbox(0,65535,globalconfig,'accept_use_unicode_end' )) 
        formLayout.addLayout(_hb)

        formLayout.addWidget(QLabel()) 
        _hb=QHBoxLayout()
        _hb.addWidget(QLabel(_TR("例外允许的字符")))
        _hb.addWidget(liwai) 
        
        formLayout.addLayout(_hb)
        dialog.resize(QSize(600,500))
        dialog.show()

