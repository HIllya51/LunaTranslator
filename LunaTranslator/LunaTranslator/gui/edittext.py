 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QTextBrowser,QMainWindow,QFontDialog,QAction,QMenu,QHBoxLayout,QWidget,QPushButton,QVBoxLayout
from PyQt5.QtGui import QFont,QFontMetrics
from PyQt5.QtCore import Qt,pyqtSignal ,QSize,QPoint
import qtawesome 
import json,threading 

from utils.config import globalconfig ,_TR,_TRL
from gui.closeashidewindow import closeashidewindow
from utils.config import globalconfig
class edittext(closeashidewindow): 
    getnewsentencesignal=pyqtSignal(str)   
    def __init__(self,p):
        super(edittext, self).__init__(p,globalconfig,'edit_geo')
        self.p=p
        self.sync=True
        self.setupUi() 
        
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)   
        self.setWindowTitle(_TR('编辑'))  
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"  ))
        font = QFont() 
        font.fromString(globalconfig['edit_fontstring'])
 
        self.textOutput = QTextBrowser(self)
        
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.charformat=self.textOutput.currentCharFormat()
        self.textOutput.customContextMenuRequested.connect(self.showmenu  )
        #self.setCentralWidget(self.textOutput) 
        
        self.textOutput.setUndoRedoEnabled(True)
        self.textOutput.setReadOnly(False)
        self.textOutput.setObjectName("textOutput") 

        qv=QHBoxLayout() 
        w=QWidget()
        self.setCentralWidget(w)
        w.setLayout(qv)


       
        bt1=QPushButton(icon=qtawesome.icon("fa.rotate-right" ,color=globalconfig['buttoncolor'])) 
        bt2=QPushButton(icon=qtawesome.icon("fa.forward" if self.sync else 'fa.play' ,color="#FF69B4" if self.sync else globalconfig['buttoncolor']))
         
        self.bt2=bt2
        self.bt1=bt1
        bt2.clicked.connect(self.changestate)
        bt1.clicked.connect(self.run)
        qvb=QVBoxLayout()
        qvb.addWidget(bt1)
        qvb.addWidget(bt2)

        qv.addLayout(qvb) 
        qv.addWidget(self.textOutput)

        

        self.hiding=True
        self.setfonts()
    def setfonts(self):
        font = QFont() 
        font.fromString(globalconfig['sw_fontstring'])
        fm=QFontMetrics(font)
        self.bt1.setIconSize(QSize(fm.height(),fm.height() )) 
        self.bt2.setIconSize(QSize(fm.height(),fm.height() ))
        self.textOutput.setFont(font) 
    def run(self):
        threading.Thread(target=self.p.object.textgetmethod,args=(self.textOutput.toPlainText(),False)).start()
    def changestate(self):
        self.sync=not self.sync 
        self.bt2.setIcon(qtawesome.icon("fa.forward" if self.sync else 'fa.play' ,color="#FF69B4" if self.sync else globalconfig['buttoncolor']))
    def showmenu(self,p:QPoint):  
        menu=QMenu(self.textOutput ) 
        qingkong=QAction(_TR("清空"))  
        ziti=QAction(_TR("字体") ) 
        menu.addAction(qingkong)  
        menu.addAction(ziti)
        action=menu.exec(self.mapToGlobal(self.textOutput.pos())+p)
        if action==qingkong:
            self.textOutput.clear()
         
        elif action==ziti :
            
            font, ok = QFontDialog.getFont(self.textOutput.font(), parent=self)
            
             
            if ok : 
                globalconfig['edit_fontstring']=font.toString()
                self.setfonts()
    def getnewsentence(self,sentence):
        if self.sync: 
            self.textOutput.setCurrentCharFormat(self.charformat)
            self.textOutput.setPlainText(sentence) 
    