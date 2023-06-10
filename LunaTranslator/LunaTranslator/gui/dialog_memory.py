   
from PyQt5.QtWidgets import  QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog  
from PyQt5.QtWidgets import    QHBoxLayout,  QVBoxLayout,QTextEdit 

from PyQt5.QtGui import QTextCursor 
from PyQt5.QtCore import Qt,QSize   
from myutils.config import _TR 
import win32con,win32utils 
from myutils.wrapper import Singleton_close 

@Singleton_close
class dialog_memory(QDialog):
        #_sigleton=False
        def save( self   ) -> None:
                with open(self.rwpath,'w',encoding='utf8') as ff:
                        ff.write(self.showtext.toHtml()) 
        def insertpic(self):
                f=QFileDialog.getOpenFileName()
                res=f[0]
                if res!='':
                        self.showtext.insertHtml('<img src="{}">'.format(res))
        def __init__(self, object,gamemd5='0' ) -> None:
                
                super().__init__(object, Qt.WindowCloseButtonHint|Qt.WindowMinMaxButtonsHint)
                self.setWindowTitle(_TR('备忘录'))
                self.object=object
                self.gamemd5=gamemd5
                formLayout = QVBoxLayout(self)  # 
                self.showtext=QTextEdit()
                self.rwpath='./userconfig/memory/{}.html'.format(gamemd5)
                try:
                        with open(self.rwpath,'r',encoding='utf8') as ff:
                                text=(ff.read())
                except:
                        text=''
                self.showtext.insertHtml(text)
                self.showtext. moveCursor(QTextCursor.Start)
                formLayout.addWidget(self.showtext)

                x=QHBoxLayout()
                insertpicbtn=QPushButton(_TR("插入图片"))
                insertpicbtn.clicked.connect(self.insertpic)
                savebtn=QPushButton(_TR("保存"))
                savebtn.clicked.connect(self.save)
                x.addWidget(insertpicbtn)
                x.addWidget(savebtn)
                formLayout.addLayout(x)
                self.resize(QSize(800,400))
                self.show() 

