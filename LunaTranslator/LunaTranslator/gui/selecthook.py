import threading ,functools
from traceback import print_exc
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QStyledItemDelegate,QFrame,QVBoxLayout,QComboBox,QPlainTextEdit,QDialogButtonBox,QLineEdit,QPushButton,QTableView,QAbstractItemView,QApplication,QHeaderView,QCheckBox,QStyleOptionViewItem,QStyle ,QLabel
from utils.config import savehook_new_list,savehook_new_data
from PyQt5.QtGui import QStandardItem, QStandardItemModel,QTextDocument,QAbstractTextDocumentLayout,QPalette 
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal,QSize,QModelIndex
import qtawesome
from gui.dialog_savedgame import dialog_setting_game
from utils.hookcode import Parsecode
import re
import os,time 
from utils.config import globalconfig ,_TR,_TRL,checkifnewgame
from collections import OrderedDict
from gui.usefulwidget import closeashidewindow,getQMessageBox
from utils.utils import checkchaos
from utils.subproc import subproc_w
class HTMLDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QTextDocument(self)
        f=QFont()
        f.setFamily(globalconfig['settingfonttype'])
        f.setPointSizeF(11) 
        self.doc.setDefaultFont(f) 
    def paint(self, painter, option, index):
        painter.save()

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index) 
        self.doc.setHtml(options.text)
        options.text = ""

        style = QApplication.style() if options.widget is None \
            else options.widget.style()
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(QPalette.Text, option.palette.color(
                                QPalette.Active, QPalette.HighlightedText))

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        #textRect.adjust(0, 0, 0, 0)
        painter.translate(textRect.topLeft())
        self.doc.documentLayout().draw(painter, ctx) 
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(self.doc.idealWidth(), self.doc.size().height())
class hookselect(closeashidewindow):
    addnewhooksignal=pyqtSignal(tuple,bool,bool)
    getnewsentencesignal=pyqtSignal(str)
    changeprocessclearsignal=pyqtSignal()
    okoksignal=pyqtSignal() 
    update_item_new_line=pyqtSignal(tuple,str)  
    def __init__(self,object,p):
        super(hookselect, self).__init__(p)
        self.object=object
        self._settingui=p
        self.setupUi( )
        
        self.changeprocessclearsignal.connect(self.changeprocessclear)
        self.addnewhooksignal.connect(self.addnewhook)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.update_item_new_line.connect(self.update_item_new_line_function) 
        self.okoksignal.connect(self.okok)  
        self.setWindowTitle(_TR('选择文本'))
    def update_item_new_line_function(self,hook,output): 
        if hook in self.save:
            row=self.save.index(hook)
            if  len(self.object.textsource.pids)>1:
                self.ttCombomodelmodel.item(row,4).setText(output) 
            else:
                self.ttCombomodelmodel.item(row,3).setText(output) 
    def changeprocessclear(self):
        #self.ttCombo.clear() 
        self.ttCombomodelmodel.clear()
        [_.hide() for _ in self.multipidswidgets]
        self.save=[]
        self.selectionbutton=[]
        self.saveinserthook=[]
    def addnewhook(self,ss ,select,isname):
        if len(self.save)==0:
            if  len(self.object.textsource.pids)>1: 
                self.selectpid.addItems([str(_) for _ in self.object.textsource.pids])
                [_.show() for _ in self.multipidswidgets]
                self.ttCombomodelmodel.setHorizontalHeaderLabels(_TRL(['选择','类型','进程', 'HOOK','文本']))
            else:
                self.ttCombomodelmodel.setHorizontalHeaderLabels(_TRL(['选择','类型','HOOK','文本']))
        self.save.append(ss ) 
 
        rown=self.ttCombomodelmodel.rowCount()
        selectionitem=QStandardItem()
        typeitem=QStandardItem()
        if  len(self.object.textsource.pids)>1:
            self.ttCombomodelmodel.insertRow(rown,[selectionitem,typeitem,QStandardItem('%s' %(int(ss[1],16))),QStandardItem('%s %s %s:%s' %(ss[-1],ss[-2],ss[-3],ss[-4])),QStandardItem()])  
        else:
            self.ttCombomodelmodel.insertRow(rown,[selectionitem,typeitem,QStandardItem('%s %s %s:%s' %(ss[-1],ss[-2],ss[-3],ss[-4])),QStandardItem()])  
                    
                #self.hctable.setIndexWidget(self.hcmodel.index(row, 0),self.object.getcolorbutton('','',self.clicked2,icon='fa.times',constcolor="#FF69B4")) 
        
        self.selectionbutton.append(self._settingui.getsimpleswitch({1:False},1,callback=functools.partial(self.accept,ss))) 
        if select:self.selectionbutton[-1].click()
        self.tttable.setIndexWidget(self.ttCombomodelmodel.index(rown,0),self.selectionbutton[-1])
 
        self.tttable.setIndexWidget(self.ttCombomodelmodel.index(rown,1),self._settingui.getsimplecombobox(_TRL(["文本","人名"]),{1:isname},1,callback=functools.partial(self.selecttextypecallback,ss)))
    def selecttextypecallback(self,key,idx):
        if idx==1:
            if 'namehook' in savehook_new_data[self.object.textsource.pname]:
                savehook_new_data[self.object.textsource.pname]['namehook']+=[key[-4:]]
            else:
                savehook_new_data[self.object.textsource.pname]['namehook']=[key[-4:]]
            self.object.textsource.namehook.append(key)
        else:
            if 'namehook' in savehook_new_data[self.object.textsource.pname] and list(key[-4:]) in savehook_new_data[self.object.textsource.pname]['namehook']:
                savehook_new_data[self.object.textsource.pname]['namehook'].remove(key[-4:])
            if key in self.object.textsource.namehook:
                self.object.textsource.namehook.remove(key)
    def setupUi(self  ):
        
        self.resize(1200, 600) 
        self.save=[]
        self.selectionbutton=[] 
        self.centralWidget = QWidget(self) 
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        self.hboxlayout = QHBoxLayout(self.centralWidget)  
        self.processFrame = QFrame(self.centralWidget)
        self.processFrame.setEnabled(True)  
        self.hboxlayout.addWidget(self.processFrame)
        self.vboxlayout = QVBoxLayout()    
        self.ttCombomodelmodel=QStandardItemModel(self) 
        #self.ttCombomodelmodel.setColumnCount(2)
        self.ttCombomodelmodel.setHorizontalHeaderLabels(_TRL(['显示','类型','进程', 'HOOK','文本']))
        
        self.at1=1
        self.tttable = QTableView(self)
        self.tttable .setModel(self.ttCombomodelmodel)
        #self.tttable .horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.tttable .horizontalHeader().setStretchLastSection(True) 
        self.tttable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tttable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tttable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tttable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tttable.doubleClicked.connect(self.table1doubleclicked)
        self.tttable.clicked.connect(self.ViewThread)
        #self.tttable.setFont(font)
        self.vboxlayout.addWidget(self.tttable)
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        

        
        #self.ttCombo.setMaxVisibleItems(50) 
        
        self.userhooklayout = QHBoxLayout() 
        self.vboxlayout.addLayout(self.userhooklayout)
        self.userhook=QLineEdit() 
        self.userhooklayout.addWidget(self.userhook)
        self.userhookinsert=QPushButton(_TR("插入特殊码")) 
        self.userhookinsert.clicked.connect(self.inserthook)
        self.userhooklayout.addWidget(self.userhookinsert)

        self.userhookfind=QPushButton(_TR("搜索特殊码")) 
        self.userhookfind.clicked.connect(self.findhook)
        self.userhooklayout.addWidget(self.userhookfind)
        self.multipidswidgets=[QLabel(_TR("到进程"))]
        self.selectpid=QComboBox()
        self.multipidswidgets.append(self.selectpid)
        [_.hide() for _ in self.multipidswidgets]
        [self.userhooklayout.addWidget(_) for _ in self.multipidswidgets]
        self.opensolvetextb=QPushButton(_TR("文本处理")) 
        self.opensolvetextb.clicked.connect(self.opensolvetext)
        self.userhooklayout.addWidget(QLabel("      "))
        self.userhooklayout.addWidget(self.opensolvetextb)

        
        self.settingbtn=QPushButton(_TR("游戏设置")) 
        self.settingbtn.clicked.connect(self.opengamesetting)
        self.userhooklayout.addWidget(self.settingbtn)

        #################
        self.searchtextlayout = QHBoxLayout() 
        self.vboxlayout.addLayout(self.searchtextlayout)
        self.searchtext=QLineEdit() 
        self.searchtextlayout.addWidget(self.searchtext)
        self.searchtextbutton=QPushButton(_TR("搜索包含文本的条目"))
         
        self.searchtextbutton.clicked.connect(self.searchtextfunc)
        self.searchtextlayout.addWidget(self.searchtextbutton)
        ###################
        self.ttCombomodelmodel2=QStandardItemModel(self) 
        #self.ttCombomodelmodel.setColumnCount(2)
        self.ttCombomodelmodel2.setHorizontalHeaderLabels(_TRL([ 'HOOK','文本']))
        
        
        self.tttable2 = QTableView(self)
        self.tttable2 .setModel(self.ttCombomodelmodel2)
        #self.tttable2 .horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 
        self.tttable2.horizontalHeader().setStretchLastSection(True) 
        self.tttable2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tttable2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tttable2.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        self.tttable2.clicked.connect(self.ViewThread2) 
         
        self.vboxlayout.addWidget(self.tttable2)
        self.searchtextlayout2 = QHBoxLayout()   
        self.vboxlayout.addLayout(self.searchtextlayout2)
        self.searchtext2=QLineEdit() 
        self.searchtextlayout2.addWidget(self.searchtext2)
        self.searchtextbutton2=QPushButton(_TR("搜索包含文本的条目"))
        self.checkfilt_notcontrol=QCheckBox(_TR("过滤控制字符"))
        self.checkfilt_notpath=QCheckBox(_TR("过滤路径"))
        self.checkfilt_dumplicate=QCheckBox(_TR("过滤重复")) 
        self.checkfilt_notascii=QCheckBox(_TR("过滤纯英文")) 
        self.checkfilt_notshiftjis=QCheckBox(_TR("过滤乱码文本"))  
        self.checkfilt_dumplicate.setChecked(True) 
        self.checkfilt_notcontrol.setChecked(True)
        self.checkfilt_notpath.setChecked(True)
        self.checkfilt_notascii.setChecked(True) 
        self.checkfilt_notshiftjis.setChecked(True)  
        self.searchtextlayout2.addWidget(self.checkfilt_notcontrol)
        self.searchtextlayout2.addWidget(self.checkfilt_notpath)
        self.searchtextlayout2.addWidget(self.checkfilt_dumplicate)
        self.searchtextlayout2.addWidget(self.checkfilt_notascii)  
        self.searchtextlayout2.addWidget(self.checkfilt_notshiftjis)   
        self.searchtextbutton2.clicked.connect(self.searchtextfunc2)
        self.searchtextlayout2.addWidget(self.searchtextbutton2) 
        self.textOutput = QPlainTextEdit(self.centralWidget)
         
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True) 
        self.vboxlayout.addWidget(self.textOutput)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setCentralWidget(self.centralWidget)
  
        self.hidesearchhookbuttons()
        
 
        self.tttable.setItemDelegateForColumn(1,HTMLDelegate(self))
        self.tttable2.setItemDelegateForColumn(1,HTMLDelegate(self))
    def opensolvetext(self):
        self._settingui.opensolvetextsig.emit()
    def opengamesetting(self):
        try:
            dialog_setting_game(self,self.object.textsource.pname, settingui=self._settingui) 
        except:
            print_exc()
    def gethide(self,res,savedumpt ):
        hide=False
        if self.checkfilt_dumplicate.isChecked():
            if res in savedumpt:
                hide=True
            else:
                savedumpt.add(res)
        if self.checkfilt_notascii.isChecked():
            try:
                res.encode('ascii')
                hide=True
            except:
                pass
        if self.checkfilt_notshiftjis.isChecked():
            if checkchaos(res):
                hide=True
             
        if self.checkfilt_notcontrol.isChecked():
            lres=list(res)
            
            for r in lres:
                _ord=ord(r)
                if _ord<0x20 or (_ord>0x80 and _ord<0xa0):

                    hide=True
                    break
        if self.checkfilt_notpath.isChecked():
            if os.path.isdir(res) or os.path.isfile(res): 
                hide=True 
         
        return hide
    def searchtextfunc2(self):
        searchtext=self.searchtext2.text() 
        savedumpt=set()
        for index in range(len(self.allres)):   
            _index=len(self.allres)-1-index
            
            resbatch=self.allres[self.allres_k[_index]] 
             
            hide=all([ (searchtext not in res) or self.gethide(res ,savedumpt) for res in resbatch]) 
            self.tttable2.setRowHidden(_index,hide)  
            
    def searchtextfunc(self):
        searchtext=self.searchtext.text() 
 
        #self.ttCombomodelmodel.blockSignals(True)
        try:
            for index,key in enumerate(self.object.textsource.hookdatacollecter):   
                ishide=True  
                for i in range(min(len(self.object.textsource.hookdatacollecter[key]),20)):
                    
                    if searchtext  in self.object.textsource.hookdatacollecter[key][-i]:
                        ishide=False
                        break
                self.tttable.setRowHidden(index,ishide) 
        except:
            pass
        #self.ttCombomodelmodel.blockSignals(False)  
            #self.ttCombo.setItemData(index,'',Qt.UserRole-(1 if ishide else 0))
            #self.ttCombo.setRowHidden(index,ishide)
    def inserthook(self): 
        hookcode=self.userhook.text().replace('\r','').replace('\n','').replace('\t','')
        if len(hookcode)==0:
            return 
        x=Parsecode(hookcode)
        #print(hookcode,x.stdout[0])
        if(x is None):
            self.getnewsentence(_TR('！特殊码格式错误！'))
            return
        
        if  self.object.textsource:
            
            if len(self.object.textsource.pids)==1:
                pid=self.object.textsource.pids[0]
            else:
                pid=int(self.selectpid.currentText())
            self.object.textsource.inserthook(hookcode,pid)
            self.saveinserthook.append(hookcode)
            
        else:
            self.getnewsentence(_TR('！未选定进程！'))
    def hidesearchhookbuttons(self,hide=True):
         
        self.tttable2.setHidden(hide)
        self.searchtextbutton2.setHidden(hide)
        self.searchtext2.setHidden(hide)
        self.checkfilt_notcontrol.setHidden(hide)
        self.checkfilt_notpath.setHidden(hide)
        self.checkfilt_notascii.setHidden(hide)
        self.checkfilt_notshiftjis.setHidden(hide)  
        self.checkfilt_dumplicate.setHidden(hide) 
    def findhook(self): 
        if globalconfig['sourcestatus']['textractor']['use']==False:
            return 
        getQMessageBox(self,"警告","该功能可能会导致游戏崩溃！",True,True,self.findhookchecked)
    def findhookchecked(self): 
            
            if os.path.exists('hook.txt'):
                try:
                    os.remove('hook.txt')
                except:
                    pass
            if  self.object.textsource: 
                if len(self.object.textsource.pids)==1:
                    pid=self.object.textsource.pids[0]
                else:
                    pid=int(self.selectpid.currentText())
                self.object.textsource.findhook(pid)
                self.userhookfind.setEnabled(False)
                self.userhookfind.setText(_TR("正在搜索特殊码，请让游戏显示更多文本"))
                
                self.hidesearchhookbuttons()
                self.ttCombomodelmodel2.clear()
                self.ttCombomodelmodel2.setHorizontalHeaderLabels(_TRL([ 'HOOK','文本']))
                threading.Thread(target=self.timewaitthread).start()
                
            else:
                self.getnewsentence(_TR('！未选定进程！'))
    def okok(self):
        if self.isMaximized()==False:
            self.showNormal()
            if self.height()<600+300:
                
                self.resize(self.width(),900)
        self.userhookfind.setText(_TR("搜索特殊码"))
        #self.findhookoksignal.emit()
        self.userhookfind.setEnabled(True)
        with open('hook.txt','r',encoding='utf8') as ff:
            allres=ff.read()#.split('\n')
        
        self.allres=OrderedDict()  
        for hc,text in re.findall("(.*)=>(.*)",allres): 
            try: 
                        if text.strip()=='':
                            continue  
                        if hc not in self.allres:
                            self.allres[hc]=[text]
                        else:
                            self.allres[hc].append(text)
            except:
                print_exc() 
         
        self.allres_k=list(self.allres.keys())
         
        for i,hc in enumerate( self.allres):
            try:  
                        item = QStandardItem(hc ) 
                        self.ttCombomodelmodel2.setItem(i, 0, item)
                        item = QStandardItem(self.allres[hc][0] )
                        self.ttCombomodelmodel2.setItem(i, 1, item) 
            except:
                print_exc() 
        self.searchtextfunc2()
        
        self.hidesearchhookbuttons(False)
        
    def timewaitthread(self):
 
        while True:
            if os.path.exists('hook.txt'):
                big=os.path.getsize('hook.txt')
                if big<10:
                    pass
                else:
                    self.okoksignal.emit()
                    break
            else:
                pass
            time.sleep(1)  
    def accept(self,key,select):
        try: 

            self.object.textsource.lock.acquire()
            
            if key in self.object.textsource.selectedhook:
                self.object.textsource.selectedhook.remove(key)
            if select :
                self.object.textsource.selectedhook.append(key)
            else:
                pass
             
            self.object.textsource.autostarthookcode=[]
            self.object.textsource.autostarting=False
            checkifnewgame(self.object.textsource.pname)
             
            needinserthookcode= savehook_new_data[self.object.textsource.pname]['needinserthookcode']  
            needinserthookcode=list(set(needinserthookcode+self.saveinserthook))
            
            savehook_new_data[self.object.textsource.pname].update({  'needinserthookcode':needinserthookcode } )

            savehook_new_data[self.object.textsource.pname].update({ 'hook':self.object.textsource.selectedhook } )
            self.object.textsource.lock.release()
        except:
            print_exc()
        #self.object.settin_ui.show()
    def showEvent(self,e):   
        self.object.AttachProcessDialog.realshowhide.emit(False)
        try:  
            for i in range(len(self.save)):  
                if self.save[i] in self.object.textsource.selectedhook: 
                    self.tttable.setCurrentIndex(self.ttCombomodelmodel.index(i,0)) 
                    break
        except:
            print_exc()
    def getnewsentence(self,sentence):
        if self.at1==2:
            return 
        scrollbar = self.textOutput.verticalScrollBar()
        atBottom = scrollbar.value() + 3 > scrollbar.maximum() or scrollbar.value() / scrollbar.maximum() > 0.975 
        cursor=QTextCursor (self.textOutput.document())
        cursor.movePosition(QTextCursor.End)
        cursor.insertText('\n'+sentence)
        if (atBottom):
            scrollbar.setValue(scrollbar.maximum())
    def ViewThread2(self, index:QModelIndex):   
        self.at1=2
        self.userhook.setText(self.allres_k[index.row()])
        self.textOutput. setPlainText('\n'.join(self.allres[self.allres_k[index.row()]] )) 
    def ViewThread(self, index:QModelIndex):    
        self.at1=1 
        try:
            self.object.textsource.selectinghook=self.save[index.row()]
            
            self.textOutput. setPlainText('\n'.join(self.object.textsource.hookdatacollecter[self.save[index.row()]]))
            self.textOutput. moveCursor(QTextCursor.End)
            
        except:
            print_exc()
    def table1doubleclicked(self,index:QModelIndex): 
            self.selectionbutton[index.row()].click()