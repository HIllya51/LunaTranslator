
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QMainWindow,QFrame,QVBoxLayout,QComboBox,QPlainTextEdit,QTextBrowser,QLineEdit,QPushButton,QTabWidget,QMenu,QAction
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal
import qtawesome,functools,json
import threading 
from utils.config import globalconfig
from traceback import print_exc
from utils.config import globalconfig ,_TR,_TRL
class searchwordW(QMainWindow): 
    getnewsentencesignal=pyqtSignal(str) 
    searchthreadsignal=pyqtSignal(int,list,tuple)
    def __init__(self,p):
        super(searchwordW, self).__init__(p)
        self.setupUi() 
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence) 
        self.setWindowTitle(_TR('查词'))
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
        self.userhookinsert=QPushButton(_TR("搜索"))
        self.userhookinsert.setFont(font) 
        self.userhookinsert.clicked.connect(lambda :self.search((self.userhook.text(),None,None)))
        self.userhooklayout.addWidget(self.userhookinsert)
 
        self.tab=QTabWidget(self)

         
        self.vboxlayout.addWidget(self.tab)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setCentralWidget(self.centralWidget)
  
        
        self.textbs=[]

        _=_TRL(['MeCab','小学馆',"灵格斯词典","EDICT","EDICT2"])#,"JMdict"])
        self._=_
        for i in range(len(_)):

            textOutput = QTextBrowser(self)
            textOutput.setFont(font) 
            textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
            textOutput.setUndoRedoEnabled(False)
            textOutput.setReadOnly(True)
            self.tab.addTab(textOutput,_[i])
            self.textbs.append(textOutput)
            
            textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        
        
            textOutput.customContextMenuRequested.connect(functools.partial( self.showmenu ,i,textOutput) )
        self.hiding=True
        self.searchthreadsignal.connect(self.searchthread)
    def showmenu(self,ii,to:QTextBrowser,p):  
        menu=QMenu(self ) 
        save=QAction(_TR("保存"))  
        menu.addAction(save) 
        action=menu.exec( to.mapToGlobal(p))
        if action==save: 
            try:
                try:
                    with open('dict_result.json','r',encoding='utf8') as ff:
                        js=json.loads(ff.read())
                except:
                    js={"note":[]}
                
                word=self.userhook.text()
                gana=self.textbs[0].toPlainText().split('\n')[0][len(word)+1:]
                meaning=''

                for i in range(1,len(self.textbs)):
                    if i!=ii:
                        continue
                    if self.textbs[i].firsttext!='':
                        meaning= self.textbs[i].firsttext 
                item={ 
                    "fields": {
                        "Expression": word,
                        "Meaning": meaning,
                        "Furigana": gana,
                        "Sentence": self.p.original,
                    }
                }
                js['note'].append(item)
                with open('dict_result.json','w',encoding='utf8') as ff:
                    ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
            except:
                print_exc()
    def getnewsentence(self,sentence):
        self.userhook.setText(sentence[0] )
         
        self.search(sentence)

    def searchthread(self,i,_d,sentence):
        self.textbs[i].clear()
        
        res=_d[i].search(sentence if i==0 else sentence[0]) 
        if res is None or res=='':
            res=_TR('未查到' )
            self.tab.setTabVisible(i,False)
        else:
            self.tab.setTabVisible(i,True)
        first=res.split('<hr>')[0]
        self.textbs[i].insertHtml(first)  
        self.textbs[i].firsttext=self.textbs[i].toPlainText()
        self.textbs[i].insertHtml(res[len(first):])  
        scrollbar = self.textbs[i].verticalScrollBar()
        scrollbar.setValue(0)
    def search(self,sentence):
        if  sentence[0]=='':
            return
        _d=[self.p.object.hira_,self.p.object.xiaoxueguan,self.p.object.linggesi,self.p.object.edict,self.p.object.edict2]#,self.p.object.jmdict]
        for i in range(len(_d)): 
            threading.Thread(target=self.searchthreadsignal.emit,args=(i,_d,sentence)).start()
 