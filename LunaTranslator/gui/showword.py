
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QMainWindow,QApplication,QVBoxLayout,QFontDialog,QTextBrowser,QLineEdit,QPushButton,QTabWidget,QMenu,QAction
from PyQt5.QtGui import QFont,QTextCursor,QFontMetrics
from PyQt5.QtCore import Qt,pyqtSignal,QSize
import qtawesome,functools,json
import threading 
from queue import Queue
from utils.config import globalconfig
from traceback import print_exc
from utils.config import globalconfig ,_TR,_TRL
class searchwordW(QMainWindow): 
    getnewsentencesignal=pyqtSignal(str) 
    searchthreadsignal=pyqtSignal(str,dict,str)
    showsignal=pyqtSignal(str,str)
    def __init__(self,p):
        super(searchwordW, self).__init__(p)
        self.setupUi() 
        #self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence) 
        self.setWindowTitle(_TR('查词'))
        self.p=p
    def closeEvent(self, event) :  
        globalconfig['sw_geo']=list(self.geometry().getRect())
        self.hide()
     
    
    def showresfun(self,k,res):
            first=res.split('<hr>')[0]
            
            self.textbs[k].insertHtml(first)  
            self.textbs[k].firsttext=self.textbs[k].toPlainText()
            self.textbs[k].insertHtml(res[len(first):])  
            
            scrollbar = self.textbs[k].verticalScrollBar()
            scrollbar.setValue(0)
            self.tab.setTabVisible(self._k.index(k),True)
    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.search"  ))
         
         
        self.showsignal.connect(self.showresfun)
        font = QFont() 
        font.fromString(globalconfig['sw_fontstring'])

        d=QApplication.desktop()

        globalconfig['sw_geo'][0]=min(max(globalconfig['sw_geo'][0],0),d.width()-globalconfig['sw_geo'][2])
        globalconfig['sw_geo'][1]=min(max(globalconfig['sw_geo'][1],0),d.height()-globalconfig['sw_geo'][3])
        self.setGeometry(*globalconfig['sw_geo'])
        self.centralWidget = QWidget(self) 
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        self.hboxlayout = QHBoxLayout(self.centralWidget)  
        self.vboxlayout = QVBoxLayout()   
        
        self.searchlayout = QHBoxLayout()  
        self.vboxlayout.addLayout(self.searchlayout)
        self.searchtext=QLineEdit()
        #self.searchtext.setFont(font)
        self.searchlayout.addWidget(self.searchtext)
        self.searchbutton=QPushButton(qtawesome.icon("fa.search"),'')#_TR("搜索"))

        fm=QFontMetrics(font)
        self.searchbutton.setIconSize(QSize(fm.height(),fm.height() ))


        #self.searchbutton.setFont(font) 
        self.searchbutton.clicked.connect(lambda :self.search((self.searchtext.text(),None,None)))
        self.searchlayout.addWidget(self.searchbutton)

        self.soundbutton=QPushButton(qtawesome.icon("fa.music"), "")
        self.soundbutton.setIconSize(QSize(fm.height(),fm.height() ))
        #self.searchbutton.setFont(font) 
        self.soundbutton.clicked.connect(self.langdu)
        self.searchlayout.addWidget(self.soundbutton)


        self.tab=QTabWidget(self)

        self.setFont(font)
        self.vboxlayout.addWidget(self.tab)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setCentralWidget(self.centralWidget)
  
        
        self.textbs={}

        _k=[ ]
        _name=[ ]
        for cishu in globalconfig['cishu']:
            _name.append(globalconfig['cishu'][cishu]['name'])
            _k.append(cishu)
        self._k=_k
        _name=_TRL(_name)
        
        for i in range(len(_name)):

            textOutput = QTextBrowser(self)
            #textOutput.setFont(font) 
            textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
            textOutput.setUndoRedoEnabled(False)
            textOutput.setReadOnly(True)
            textOutput.setOpenLinks(False)
            self.tab.addTab(textOutput,_name[i])
            self.textbs[self._k[i]]=(textOutput)
            
            textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        
        
            textOutput.customContextMenuRequested.connect(functools.partial( self.showmenu ,i,textOutput) )
        self.hiding=True
        self.searchthreadsignal.connect(self.searchthread)
    def langdu(self): 
        if self.p.object.reader:
            self.p.object.reader.read(self.searchtext.text() )  
    def showmenu(self,ii,to:QTextBrowser,p):  
        menu=QMenu(self ) 
        save=QAction(_TR("保存"))  
        ziti=QAction(_TR("字体") ) 
        menu.addAction(save) 
        menu.addAction(ziti)
        action=menu.exec( to.mapToGlobal(p))
        if action==save: 
            try:
                try:
                    with open('dict_result.json','r',encoding='utf8') as ff:
                        js=json.loads(ff.read())
                except:
                    js={"note":[]}
                
                word=self.searchtext.text()
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
        elif action==ziti :
            
            font, ok = QFontDialog.getFont(self.font(), parent=self)
            
             
            if ok : 
                globalconfig['sw_fontstring']=font.toString()
                self.setFont(font)
                 
                for _ in self.textbs:
                    self.textbs[_].setFont(font)
    def getnewsentence(self,sentence):
        self.searchtext.setText(sentence  )
         
        self.search(sentence)

    def searchthread(self,k,_mp,sentence):
        
        _mp[k].callback=functools.partial(self.showsignal.emit,k)
        _mp[k].search( sentence ) 
        
    
    def search(self,sentence):
        if  sentence =='':
            return
         
        _mp={ }
        _mp.update(self.p.object.cishus)
         
        for k in self._k : 
            self.tab.setTabVisible(self._k.index(k),False)
            self.textbs[k].clear()
            if k  in _mp:                 
                threading.Thread(target=self.searchthreadsignal.emit,args=(k,_mp,sentence)).start()
 