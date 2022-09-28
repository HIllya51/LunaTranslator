
from re import search
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QMainWindow,QFrame,QVBoxLayout,QComboBox,QPlainTextEdit,QDialogButtonBox,QLineEdit,QPushButton
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal
import qtawesome
import subprocess
import json
import os
import re
import sys
class hookselect(QMainWindow):
    addnewhooksignal=pyqtSignal(tuple)
    getnewsentencesignal=pyqtSignal(str)
    def __init__(self,object):
        super(hookselect, self).__init__()
        self.setupUi(self)
        self.object=object
        self.addnewhooksignal.connect(self.addnewhook)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.setWindowFlags(Qt.WindowStaysOnTopHint |Qt.WindowCloseButtonHint)
        self.setWindowTitle('选择文本')
    def addnewhook(self,ss ):
        self.save.append(ss)
        thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode=ss 
        self.ttCombo.addItem('%s:%s:%s:%s:%s:%s (%s)' %(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode))
    def setupUi(self, hookselect):
    
        hookselect.setObjectName("hookselect")
        hookselect.resize(1000, 400)
        hookselect.setStyleSheet("\n"
"       QPushButton, QComboBox\n"
"       {\n"
"       padding-top: 3px;\n"
"       padding-bottom: 3px;\n"
"       padding-right: 5px;\n"
"       padding-left: 5px;\n"
"       text-align: left;\n"
"       }\n"
"     ")
        self.save=[]
        self.centralWidget = QWidget(hookselect)
        self.centralWidget.setObjectName("centralWidget")
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        self.hboxlayout = QHBoxLayout(self.centralWidget)
        self.hboxlayout.setContentsMargins(6, 6, 6, 6)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        self.processFrame = QFrame(self.centralWidget)
        self.processFrame.setEnabled(True)
        self.processFrame.setObjectName("processFrame")
        # self.processLayout = QVBoxLayout(self.processFrame)
        # self.processLayout.setContentsMargins(0, 0, 0, 0)
        # self.processLayout.setSpacing(6)
        # self.processLayout.setObjectName("processLayout")
        # # self.processCombo = QComboBox(self.processFrame)
        # # self.processCombo.setEditable(False)
        # # self.processCombo.setInsertPolicy(QComboBox.InsertAtBottom)
        # # self.processCombo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        # # self.processCombo.setObjectName("processCombo")
        # self.processLayout.addWidget(self.processCombo)
        self.hboxlayout.addWidget(self.processFrame)
        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        font = QFont()
        #font.setFamily("Arial Unicode MS")
        font.setPointSize(13)
        self.ttCombo = QComboBox(self.centralWidget)
        self.ttCombo.setEditable(False)
        self.ttCombo.setMaxVisibleItems(50)
        self.ttCombo.setObjectName("ttCombo")         
        self.ttCombo.setFont(font)
        self.vboxlayout.addWidget(self.ttCombo)

        self.userhooklayout = QHBoxLayout()
        self.userhooklayout.setSpacing(6)
        self.vboxlayout.addLayout(self.userhooklayout)
        self.userhook=QLineEdit()
        self.userhooklayout.addWidget(self.userhook)
        self.userhookinsert=QPushButton("插入特殊码")
        
        self.userhookinsert.setFont(font)
        self.userhookinsert.clicked.connect(self.inserthook)
        self.userhooklayout.addWidget(self.userhookinsert)


        #################
        self.searchtextlayout = QHBoxLayout()
        self.searchtextlayout.setSpacing(6)
        self.vboxlayout.addLayout(self.searchtextlayout)
        self.searchtext=QLineEdit()
        self.searchtext.setFont(font)
        self.searchtextlayout.addWidget(self.searchtext)
        self.searchtextbutton=QPushButton("搜索包含文本的条目")
        
        self.searchtextbutton.setFont(font)
        self.searchtextbutton.clicked.connect(self.searchtextfunc)
        self.searchtextlayout.addWidget(self.searchtextbutton)
        ###################


        self.textOutput = QPlainTextEdit(self.centralWidget)
        
        self.textOutput.setFont(font)
        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True)
        self.textOutput.setObjectName("textOutput")
        self.vboxlayout.addWidget(self.textOutput)
        self.hboxlayout.addLayout(self.vboxlayout)
        hookselect.setCentralWidget(self.centralWidget)
  

        self.ttCombo.currentIndexChanged.connect(self.ViewThread)

        self.buttonBox=QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.vboxlayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.hide) 
        self.buttonBox.setFont(font) 
        self.hiding=True
    def searchtextfunc(self):
        searchtext=self.searchtext.text()
        try:
            lst=self.object.object.textsource.hookdatasort
        except:
            return 
        self.ttCombo.blockSignals(True)
        self.ttCombo.clear() 
        self.save=[]
        for index in range(len(lst)):   
            ishide=True  
            for i in range(min(len(self.object.object.textsource.hookdatacollecter[lst[index]]),10)):
                
                if searchtext  in self.object.object.textsource.hookdatacollecter[lst[index]][i]:
                    ishide=False
                    break
            if ishide==False:
                    
                # thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode=re.search('([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):([0-9a-fA-F]*):(.*):(.*@.*)' ,lst[index][i]).groups()
                # self.ttCombo.addItem('%s:%s:%s:%s:%s:%s (%s)' %(thread_handle,thread_tp_processId, thread_tp_addr, thread_tp_ctx, thread_tp_ctx2, thread_name,HookCode))
                self.ttCombo.addItem('%s:%s:%s:%s:%s:%s (%s)' %lst[index])
                self.save.append(lst[index])
        self.ttCombo.blockSignals(False)

            #self.ttCombo.setItemData(index,'',Qt.UserRole-(1 if ishide else 0))
            #self.ttCombo.setRowHidden(index,ishide)
    def inserthook(self): 
        hookcode=self.userhook.text()
        if len(hookcode)==0:
            return 
        x=subprocess.run(f'./files/hookcodecheck.exe {hookcode}',stdout=subprocess.PIPE)
        print(hookcode,x.stdout[0])
        if(x.stdout[0]==ord('0')):
            self.getnewsentence('！特殊码格式错误！')
            return
        
        if 'textsource' in dir(self.object.object):

            self.object.object.textsource.inserthook(hookcode)
        else:
            self.getnewsentence('！未选定进程！')
    def hide(self):
        if 'realclose' in dir(self):
            print(3)
        #print('hide')
        self.hiding=True
        super(QMainWindow,self).hide()
        if 'closed' not in dir(self.object):
            self.object.show()
    
    # 窗口关闭处理
    def closeEvent(self, event) : 
        if 'realclose' in dir(self):
            #print(2)
            event.accept()
        else:
            #print(1)
            self.hide()
    def accept(self):
        #print('show')
        self.hiding=True
        self.hide()
        try:
            self.object.object.textsource.selectedhook=self.object.object.textsource.selectinghook
            if not os.path.exists('./files/savehook.json'):
                    js={}
            with open('./files/savehook.json','r',encoding='utf8') as ff:
                js=json.load(ff)
        except:
            pass
        self.object.show()
    def getnewsentence(self,sentence):
        scrollbar = self.textOutput.verticalScrollBar()
        atBottom = scrollbar.value() + 3 > scrollbar.maximum() or scrollbar.value() / scrollbar.maximum() > 0.975 
        cursor=QTextCursor (self.textOutput.document())
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(sentence+'\n')
        if (atBottom):
            scrollbar.setValue(scrollbar.maximum())
    def ViewThread(self, index):  
        #print(self.combo_hook_map)
        key=self.save[ self.ttCombo.currentIndex()]
         
        self.object.object.textsource.selectinghook=key
        self.textOutput. setPlainText('\n'.join(self.object.object.textsource.hookdatacollecter[key]))
        self.textOutput. moveCursor(QTextCursor.End)
        
# if __name__=="__main__":
#     app = QApplication(sys.argv) 
#     a=hookselect()
#     a.show()

#     app.exit(app.exec_())
