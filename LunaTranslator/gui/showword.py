
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QMainWindow,QFrame,QVBoxLayout,QComboBox,QPlainTextEdit,QTextBrowser,QLineEdit,QPushButton,QTabWidget
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal
import qtawesome
import threading 
from utils.config import globalconfig
class searchwordW(QMainWindow): 
    getnewsentencesignal=pyqtSignal(str) 
    searchthreadsignal=pyqtSignal(int,list,str)
    def __init__(self,p):
        super(searchwordW, self).__init__(p)
        self.setupUi() 
        self.getnewsentencesignal.connect(self.getnewsentence) 
        self.setWindowTitle('查词')
        self.p=p
    def closeEvent(self, event) :  
        self.hide()
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.search"  ))
        font = QFont()
        #font.setFamily("Arial Unicode MS")
        font.setFamily(globalconfig['fonttype'])
        font.setPointSize(10)
        self.setGeometry(0,0,400,500)
        self.centralWidget = QWidget(self) 
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        self.hboxlayout = QHBoxLayout(self.centralWidget)  
        self.vboxlayout = QVBoxLayout()   
        
        self.userhooklayout = QHBoxLayout()  
        self.vboxlayout.addLayout(self.userhooklayout)
        self.userhook=QLineEdit()
        self.userhook.setFont(font)
        self.userhooklayout.addWidget(self.userhook)
        self.userhookinsert=QPushButton("搜索")
        self.userhookinsert.setFont(font) 
        self.userhookinsert.clicked.connect(lambda :self.search(self.userhook.text()))
        self.userhooklayout.addWidget(self.userhookinsert)
 
        self.tab=QTabWidget(self)

         
        self.vboxlayout.addWidget(self.tab)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setCentralWidget(self.centralWidget)
  
        
        self.textbs=[]
        _=['MeCab','小学馆',"灵格斯词典","EDICT"]
        for i in range(4):

            textOutput = QTextBrowser(self)
            textOutput.setFont(font) 
            textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
            textOutput.setUndoRedoEnabled(False)
            textOutput.setReadOnly(True)
            self.tab.addTab(textOutput,_[i])
            self.textbs.append(textOutput)
   
        self.hiding=True
        self.searchthreadsignal.connect(self.searchthread)
    def getnewsentence(self,sentence):
        self.userhook.setText(sentence)
        self.search(sentence)

    def searchthread(self,i,_d,sentence):
        self.textbs[i].clear()

        res=_d[i].search(sentence) 
        if res is None or res=='':
            res='未查到' 
        self.textbs[i].append(res) 
        scrollbar = self.textbs[i].verticalScrollBar()
        scrollbar.setValue(0)
    def search(self,sentence):
        if sentence=='':
            return
        _d=[self.p.object.hira_,self.p.object.xiaoxueguan,self.p.object.linggesi,self.p.object.edict]
        for i in range(4):
            
            threading.Thread(target=self.searchthreadsignal.emit,args=(i,_d,sentence)).start()
 