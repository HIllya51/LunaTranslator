
import time 
import functools   
import threading 
import os
import subprocess
from traceback import print_exc
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout,QApplication
from PyQt5.QtCore import Qt, pyqtSignal  
import qtawesome 
from PyQt5.QtCore import pyqtSignal,Qt,QRect,QSize  
from PyQt5.QtGui import  QFont  ,QIcon,QPixmap  
from PyQt5.QtWidgets import  QLabel ,QPushButton ,QSystemTrayIcon ,QAction,QMenu 
import pyperclip 
from PyQt5.QtCore import QProcess ,QByteArray  
from utils.config import globalconfig,saveallconfig
from utils.subproc import endsubprocs,mutiproc
import  win32gui,win32api,win32process,win32con,multiprocessing
import gui.rangeselect
import gui.transhist 

from utils.subproc import subproc
from utils.getpidlist import getwindowhwnd,mouseselectwindow,letfullscreen,recoverwindow
from gui.settingpage4 import autosaveshow
from gui.settingpage1 import settingsource,settingtextractor
from gui.textbrowser import Textbrowser
from gui.showword import searchwordW
from gui.rangeselect  import moveresizegame
from utils.magpie import callmagpie 
class QTitleButton(QPushButton):
    def __init__(self, *args):
        super(QTitleButton, self).__init__(*args)
        self.setFont(QFont("Webdings"))   
  
class QUnFrameWindow(QWidget): 
    keeptopsignal=pyqtSignal()
    clear_text_sign = pyqtSignal() 
    displayres =  pyqtSignal(str,str ) 
    displayraw1 =  pyqtSignal(list, str,str,int )  
    displaystatus=pyqtSignal(str) 
    startprocessignal=pyqtSignal(str,list)
    writeprocesssignal=pyqtSignal(QByteArray)
    killprocesssignal=pyqtSignal()
    hookfollowsignal=pyqtSignal(int,tuple)
    toolbarhidedelaysignal=pyqtSignal()
    clickSettin_signal=pyqtSignal()
    showsavegame_signal=pyqtSignal()
    settingprocess_signal=pyqtSignal()
    settinghookthread_signal=pyqtSignal()
    clickRange_signal=pyqtSignal()
    showhide_signal=pyqtSignal()
    grabwindowsignal=pyqtSignal()
    bindcropwindow_signal=pyqtSignal()
    fullsgame_signal=pyqtSignal()
    quitf_signal=pyqtSignal() 
    refreshtooliconsignal=pyqtSignal()
    muteprocessignal=pyqtSignal()
    def keeptopfuntion(self):
        win32gui.BringWindowToTop(int(self.winId()))
    def hookfollowsignalsolve(self,code,other): 
        if code==3:
            if self.hideshownotauto:
                self.show()
        elif code==4:
            if self.hideshownotauto:
                self.hide() 
        elif code==5:
            #print(self.pos())
            #self.move(self.pos() + self._endPos)
            self.move(self.pos().x()+self.rate *other[0],self.pos().y()+self.rate *other[1])
        elif code==6:
            #print(self.pos())
            #self.move(self.pos() + self._endPos)
            self.move(self.pos().x()+ other[0],self.pos().y()+ other[1])
    def showres(self,_type,res): 
        try:
            if globalconfig['showfanyisource']:
                #print(_type)
                self.showline((None,globalconfig['fanyi'][_type]['name']+'  '+res),globalconfig['fanyi'][_type]['color']  )
            else:
                self.showline((None,res),globalconfig['fanyi'][_type]['color']  )
            
            #print(globalconfig['fanyi'][_type]['name']+'  '+res+'\n')
            
            self.transhis.getnewsentencesignal.emit(globalconfig['fanyi'][_type]['name']+'  '+res)
        except:
            print_exc()
    def showraw(self,hira,res,color,show ):
        self.clearText()
        self.original=res 
        if show==1: 
            self.showline((hira,res),color )
        elif show==0:
            pass
        elif show==2:
            self.showline((hira,res),color ,type_=2 )
        self.transhis.getnewsentencesignal.emit('\n'+res)
    # def showtaskthreadfun(self):
    #     while True:
    #         res,color ,type_=self.showtask.get()
    #         self.showline_real(res,color ,type_)
    # def showline(self,res,color ,type_=1):
    #     self.showtask.put((res,color ,type_))
    def showline (self,res,color ,type_=1): 
         
        if globalconfig['showatcenter']:
            self.translate_text.setAlignment(Qt.AlignCenter)
        else:
            self.translate_text.setAlignment(Qt.AlignLeft)

        
        if globalconfig['zitiyangshi'] ==2: 
            self.translate_text.mergeCurrentCharFormat_out(globalconfig['miaobiancolor'],color, globalconfig['miaobianwidth2']) 
        elif globalconfig['zitiyangshi'] ==1:  
            self.translate_text.mergeCurrentCharFormat( color, globalconfig['miaobianwidth']) 
        elif globalconfig['zitiyangshi'] ==0: 
            self.translate_text.simplecharformat(color)
        elif globalconfig['zitiyangshi'] ==3: 
            self.translate_text.textbrowser.show() 
            if type_==1: 
                self.translate_text.append(res[1]) 
            else:  
                self.translate_text.append(res[1])  
                #self.translate_text.addtag(res[0]) 
            self.translate_text.showyinyingtext(color,res[1]  )
            self.translate_text.textbrowser.hide()
            if (globalconfig['usesearchword'] or globalconfig['show_fenci'] or globalconfig['showcixing']) and res[0]: 
                self.translate_text.addsearchwordmask(res[0],res[1],self.showsearchword,0  )
            return 
        self.translate_text.textbrowser.show()
        
        if type_==1: 
            self.translate_text.append(res[1]) 
        else: 
            self.translate_text.append(' ')
            self.translate_text.append(res[1])  
            self.translate_text.addtag(res[0]) 
        if (globalconfig['usesearchword'] or globalconfig['show_fenci'] or globalconfig['showcixing']) and res[0]:
            self.translate_text.addsearchwordmask(res[0],res[1],self.showsearchword,0 if type_==1 else 2) 
    def showsearchword(self,word):   
        self.searchwordW.showNormal()
        self.searchwordW.getnewsentence(word) 
    def clearText(self) :
     
        # 翻译界面清屏
        self.translate_text.clear()

        # 设定翻译时的字体类型和大小
        self.font.setFamily(globalconfig['fonttype'])
        self.font.setPointSizeF(globalconfig['fontsize']) 
        self.font.setBold(globalconfig['showbold'])
        self.translate_text.setFont(self.font) 
    def showhideui(self):
        if self.isHidden():
            self.show_and_enableautohide() 
        else:
            self.hide_and_disableautohide()
    def leftclicktray(self,reason):
            #鼠标左键点击
            if reason == QSystemTrayIcon.Trigger:
                
                if self.isHidden():
                    self.show_and_enableautohide() 
                else:
                    self.hide_and_disableautohide()
    def hide_and_disableautohide(self):
        self.hideshownotauto=False
        self.hide()
    def show_and_enableautohide(self):
        self.hideshownotauto=True
        self.show()
    def startprocessfunction(self,path,stdoutcallback):
        if 'p' in dir(self):
            self.p.kill()
        self.p = QProcess()    
        self.p.readyReadStandardOutput.connect(functools.partial(stdoutcallback[0],self.p))  
        self.p.start(path)

    def writeprocess(self,qb):
        self.p.write(qb)
    def killprocess(self):
        if 'p' in dir(self):
            self.p.kill() 
    def refreshtoolicon(self):
        icon=[
            qtawesome.icon("fa.rotate-right" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.forward" ,color="#FF69B4" if globalconfig['autorun'] else globalconfig['buttoncolor']),
            qtawesome.icon("fa.gear",color=globalconfig['buttoncolor'] ),
            qtawesome.icon("fa.copy" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.eye"   if globalconfig['isshowrawtext'] else "fa.eye-slash" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.rotate-left" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.music" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.mouse-pointer" ,color="#FF69B4" if self.mousetransparent else globalconfig['buttoncolor']),
            qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else globalconfig['buttoncolor']),
            qtawesome.icon("fa.gamepad" ,color= globalconfig['buttoncolor']),
            qtawesome.icon("fa.link" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.tasks" ,color= globalconfig['buttoncolor']),
            qtawesome.icon("fa.crop" ,color=globalconfig['buttoncolor']),
            (qtawesome.icon("fa.square" ,color=  "#FF69B4" if self.showhidestate else globalconfig['buttoncolor'])),
            (qtawesome.icon("fa.windows" ,color= "#FF69B4"  if self.isbindedwindow else globalconfig['buttoncolor'])),
            qtawesome.icon("fa.expand" ,color= globalconfig['buttoncolor']),
            qtawesome.icon("fa.window-maximize" ,color=  "#FF69B4" if self.isletgamefullscreened else globalconfig['buttoncolor']),
            qtawesome.icon("fa.microphone-slash" ,color="#FF69B4" if self.processismuteed else globalconfig['buttoncolor']),
            qtawesome.icon("fa.minus",color=globalconfig['buttoncolor'] ),
            qtawesome.icon("fa.times" ,color=globalconfig['buttoncolor']),
        ]
        for i in range(len(self.buttons)):
            self.buttons[i].setIcon(icon[i])
    def __init__(self, object):
        super(QUnFrameWindow, self).__init__(
            None, Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool )  # 设置为顶级窗口，无边框
        #self.setFocusPolicy(Qt.StrongFocus)

        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setAttribute(Qt.WA_ShowWithoutActivating,True)
        
        self.object = object
        self.rate = self.object.screen_scale_rate 
        self.callmagpie=None
        self.muteprocessignal.connect(self.muteprocessfuntion)
        self.startprocessignal.connect(self.startprocessfunction)
        self.writeprocesssignal.connect(self.writeprocess)
        self.killprocesssignal.connect(self.killprocess)
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)
        self._padding = 5*self.rate  # 设置边界宽度为5
        self.setMinimumWidth(300)
        self.hideshownotauto=True
        self.transhis=gui.transhist.transhist() 
        self.keeptopsignal.connect(self.keeptopfuntion) 
        self.hookfollowsignal.connect(self.hookfollowsignalsolve) 
        self.displayres.connect(self.showres)
        self.displayraw1.connect(self.showraw)  
        self.clickSettin_signal.connect(self.clickSettin_funtion)
        self.refreshtooliconsignal.connect(self.refreshtoolicon)
        self.showsavegame_signal.connect(self.showsavegame_function)
        self.settinghookthread_signal.connect(self.settinghookthread_funtion)
        self.settingprocess_signal.connect(self.settingprocess_function)
        self.clickRange_signal.connect(self.clickRange_funtion)
        self.showhide_signal.connect(self.showhide_function)
        self.bindcropwindow_signal.connect(functools.partial(mouseselectwindow, self.bindcropwindowcallback))
        self.grabwindowsignal.connect(self.grabwindow)
        self.quitf_signal.connect(self.quitf_funtion)
        self.fullsgame_signal.connect(self._fullsgame)
        # self.showtask=Queue()
        # self.showtaskthread=threading.Thread(target=self.showtaskthreadfun).start()
        self.clear_text_sign.connect(self.clearText)
        self.object = object  
        # 界面缩放比例
        self.searchwordW=searchwordW(self)
        self.selfpid=win32api.GetCurrentProcessId()
        self.HWNDStyle=None
        self.HWNDStyleEx =None
        self.isletgamefullscreened=False
        self.original = ""    
        self._isTracking=False
        self.isontop=True
        self.atback=QLabel(self)
        self.atback.setGeometry(0,30*self.rate,9999,9999)
        self.atback.setMouseTracking(True)
        self.initTitleLabel()  # 安放标题栏标签
         
        self.initLayout()  # 设置框架布局
        # self.setMinimumWidth(500)
        # self.setMinimumHeight(100)
        self.setMouseTracking(True)  # 设置widget鼠标跟踪
        self.initDrag()  # 设置鼠标跟踪判断默认值
        self.setStyleSheet(''' 
      QTitleButton{
          background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;
      }
      QTitleButton#MinMaxButton:hover{
          background-color: #D0D0D1;
          border: 0px;
          font: 100 10pt;
      }
      QTitleButton#CloseButton:hover{
          background-color: #D32424;
          color: white;
          border: 0px;
          font: 100 10pt;
      }''')
          
        
        # label = QLabel(self.tab_3)
        # self.customSetGeometry(label, 20, 270, 100, 20)
        # label.setText("鼠标穿透窗口:")
 
        # self.fixedheight_switch =gui.switchbutton.MySwitch(self.tab_3, sign=globalconfig['fixedheight'] )
        # self.customSetGeometry(self.fixedheight_switch, 120, 270,20,20)
        # self.fixedheight_switch.clicked.connect(lambda x:globalconfig.__setitem__('fixedheight',x)) 

        # self.object.translation_ui.setAttribute(Qt.WA_TransparentForMouseEvents, True);
        
        self.showhidestate=False
        self.processismuteed=False
        self.mousetransparent=False
        self.isbindedwindow=False
        self.buttons=[] 
        self.showbuttons=[]
        
        self.takusanbuttons("MinMaxButton",self.startTranslater,0,"重新翻译")
        self.takusanbuttons("MinMaxButton",self.changeTranslateMode,1,"自动翻译",'automodebutton')
        self.takusanbuttons("MinMaxButton",self.clickSettin,2,"打开设置")


        self.takusanbuttons("MinMaxButton",lambda: pyperclip.copy(self.original),6,"复制到剪贴板",'copy') 
        self.takusanbuttons("MinMaxButton", self.changeshowhideraw,7,"显示/隐藏原文",'showraw') 
        
        self.takusanbuttons("MinMaxButton", self.transhis.showsignal.emit  ,8,"显示历史翻译",'history') 
        self.takusanbuttons("MinMaxButton",self.langdu,9,"朗读",'langdu') 
        self.takusanbuttons("MinMaxButton",self.changemousetransparentstate,10,"鼠标穿透窗口",'mousetransbutton') 
         
        self.takusanbuttons("MinMaxButton",self.changetoolslockstate,11,"锁定工具栏",'locktoolsbutton') 
        
        
        self.takusanbuttons("MinMaxButton",lambda: autosaveshow(None),3,"打开保存的游戏",'gamepad') 

        self.takusanbuttons("MinMaxButton",lambda :settingtextractor(self.object.settin_ui,False),4,"选择游戏" ) 
        self.takusanbuttons("MinMaxButton",lambda :settingsource(self.object.settin_ui),5,"选择文本" ) 
         
        self.takusanbuttons("MinMaxButton",self.clickRange,4,"选取OCR范围")
        self.takusanbuttons("MinMaxButton",self.showhide,5,"显示/隐藏范围框")
         
        self.takusanbuttons("MinMaxButton",self.bindcropwindow_signal.emit,5,"绑定截图窗口，避免遮挡（部分软件不支持）（点击自己取消）")
         
        def _moveresizegame(self):
             
            try:  
                    hwnd= self.object.textsource.hwnd 
                    moveresizegame(self,hwnd)
            except:
                    print_exc()
        self.takusanbuttons("MinMaxButton",lambda :_moveresizegame(self),5,"调整游戏窗口(需要绑定ocr窗口，或选择hook进程)",'resize' ) 

        def __initmulti(self):
            while True:
                if globalconfig['usemagpie']:
                    break
                time.sleep(1)
            self.multiprocesshwnd=multiprocessing.Queue()
            self.callmagpie=mutiproc(callmagpie,(r'./files/Magpie_v0.9.1' ,self.multiprocesshwnd))
            self.callmagpie.start() 
        threading.Thread(target=__initmulti,args=(self,)).start() 
        
        self.takusanbuttons("MinMaxButton",self._fullsgame,5,"全屏/恢复游戏窗口(需要绑定ocr窗口，或选择hook进程)" ,"fullscreen") 
        
        self.takusanbuttons("MinMaxButton",self.muteprocessfuntion,5,"游戏静音(需要绑定ocr窗口，或选择hook进程)" ,"muteprocess") 
        
        
        self.takusanbuttons("MinMaxButton",self.hide_and_disableautohide,-2,"最小化到托盘")
        self.takusanbuttons("CloseButton",self.quitf,-1,"退出")

        self.refreshtoolicon()
        self.showhidetoolbuttons()
        self.setGeometry( globalconfig['position'][0],globalconfig['position'][1],int(globalconfig['width'] ), int(150*self.rate)) 
         
        icon = QIcon()
        icon.addPixmap(QPixmap('./files/luna.jpg'), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)
        self.setWindowTitle('LunaTranslator')

        self.tray = QSystemTrayIcon()  
        self.tray.setIcon(icon) 
        
        showAction = QAction("&显示", self, triggered = self.show_and_enableautohide)
        settingAction = QAction("&设置", self, triggered = self.clickSettin)
        quitAction = QAction("&退出", self, triggered = self.quitf)
                
        
        self.tray.activated.connect(self.leftclicktray)

        # 创建菜单对象
        self.trayMenu = QMenu(self)
        # 将动作对象添加到菜单
        self.trayMenu.addAction(showAction)
        self.trayMenu.addAction(settingAction)
        # 增加分割线
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(quitAction)
        # 将菜单栏加入到右键按钮中
        self.tray.setContextMenu(self.trayMenu) 
        self.tray.show()
        self.font = QFont() 
        self.font.setFamily(globalconfig['fonttype'])
        self.font.setPointSize(globalconfig['fontsize']) 
        self.translate_text =  Textbrowser(self) 
        self.translate_text.setText('欢迎使用') 
        self.translate_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.translate_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.translate_text.setFont(self.font)
        self.translate_text.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/100))
        self._TitleLabel.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                           font-weight: bold;\
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
        self.translate_text.move(0,30*self.rate) 
        # 翻译框根据内容自适应大小
        self.document = self.translate_text.document()
        self.document.contentsChanged.connect(self.textAreaChanged) 
          
        

        self.masklabel = QLabel(self.translate_text.textbrowser)  

        self.masklabel.setGeometry( 0,0,9999,9999)
        self.masklabel.setMouseTracking(True)
        
        self.masklabelback = QLabel(self.translate_text.textbrowserback)  

        self.masklabelback.setGeometry( 0, 0,9999,9999)
        self.masklabelback.setMouseTracking(True)
        self.masklabelback.setStyleSheet("background-color: rgba(0,0,0,0)")
        if globalconfig['selectable']:
            self.masklabel.hide()
    def grabwindow(self): 
        if os.path.exists('./capture')==False:
            os.mkdir('./capture')

        try:
            if self.isletgamefullscreened:
                hwnd=QApplication.desktop().winId() 
                self.hide()
                QApplication.primaryScreen().grabWindow(hwnd).save(f'./capture/{time.time()}.png')
                self.show()
            else:
                hwnd=win32gui.GetForegroundWindow()  
                QApplication.primaryScreen().grabWindow(hwnd).save(f'./capture/{time.time()}.png')
        except:
            pass
    def muteprocessfuntion(self): 
        try:
            
            self.processismuteed=not self.processismuteed
            
            self.refreshtoolicon()
            pid= self.object.textsource.pid 
            subproc(f'./files/muteprocess.exe {pid}  {int(self.processismuteed)}')
        except:
            print_exc()
    def _fullsgame(self): 
            try:  
                    self.isletgamefullscreened=not self.isletgamefullscreened
                    self.refreshtoolicon()
                    hwnd= self.object.textsource.hwnd 
                    if globalconfig['usemagpie']:  
                        if self.isletgamefullscreened: 
                            win32gui.SetForegroundWindow(hwnd )   
                            self.multiprocesshwnd.put([hwnd,globalconfig['magpiescalemethod'],globalconfig['magpieflags'],globalconfig['magpiecapturemethod']])   
                            if self.showhidestate:
                                self.object.range_ui.letontopisignal.emit() 
                        else:
                            win32gui.SetForegroundWindow(self.winId() )   
                    else: 
                        if self.isletgamefullscreened: 
                            self.savewindowstatus=letfullscreen(hwnd)
                        else:
                            recoverwindow(hwnd,self.savewindowstatus)
                    
            except:
                    print_exc()
    def changemousetransparentstate(self):
         
        
        
        self.translate_text.setStyleSheet("border-width:0;\
                                                                border-style:outset;\
                                                                border-top:0px solid #e8f3f9;\
                                                                color:white;\
                                                            background-color: rgba(%s, %s, %s, %s)"
                                        %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']*self.mousetransparent/100))
        self.mousetransparent= not self.mousetransparent
        self.refreshtoolicon()
    def showhide_function(self):
        self.showhide()
    def showhide(self): 
        self.showhidestate=not self.showhidestate 
        self.refreshtoolicon()
        self.object.range_ui.setVisible(self.showhidestate) 
    def bindcropwindowcallback(self,pid,hwnd,name_): 
            
            self.object.textsource.hwnd= hwnd if pid!=self.selfpid else None
            self.object.textsource.pid= pid if pid!=self.selfpid else None
            self.isbindedwindow=(pid!=self.selfpid)
            self.refreshtoolicon() 
             
    def showsavegame_function(self):
        autosaveshow(None)
    def settingprocess_function(self):
        settingtextractor(self.object.settin_ui,False)
    def settinghookthread_funtion(self):
        settingsource(self.object.settin_ui)
    def changeshowhideraw(self):
        self.object.settin_ui.show_original_switch.click()
        
    def changeTranslateMode(self) : 
        globalconfig['autorun']=not globalconfig['autorun'] 
        self.refreshtoolicon()
    def changetoolslockstate(self): 
        globalconfig['locktools']=not globalconfig['locktools'] 
        self.refreshtoolicon()
    def textAreaChanged(self) :
        if globalconfig['fixedheight']:
            return
        newHeight = self.document.size().height()
        
        width = self.width()
        self.resize(width, newHeight + 30*self.rate) 
    def clickSettin_funtion(self):  
        self.object.settin_ui.showNormal() 
        win32gui.BringWindowToTop(int(self.object.settin_ui.winId())) 
    def clickSettin(self) : 
        self.clickSettin_signal.emit()
        # 按下范围框选键
    def clickRange_funtion(self):
        self.clickRange()
    def clickRange(self): 
        if globalconfig['sourcestatus']['ocr']==False:
                return 
        self.showhidestate=False
        self.showhide()
        
        self.object.range_ui.hide()
        self.object.screen_shot_ui =gui.rangeselect.rangeselct(self.object)
        self.object.screen_shot_ui.show()
        
        self.show()
    def langdu(self): 
        if self.object.reader:
            self.object.reader.read(self.original )  
    def startTranslater(self) :
        if hasattr(self.object,'textsource') and  self.object.textsource :
            threading.Thread(target=self.object.textsource.runonce).start()
         
    def initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._lcorner_drag = False
        self._right_drag = False
        self._left_drag = False

    def initTitleLabel(self):
        # 安放标题栏标签
        self._TitleLabel = QLabel(self)
        self._TitleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._TitleLabel.setFixedHeight(30*self.rate)
        # 设置标题栏标签鼠标跟踪（如不设，则标题栏内在widget上层，无法实现跟踪）
        self._TitleLabel.setMouseTracking(True)
        self._TitleLabel.setIndent(10)  # 设置标题栏文本缩进
        self._TitleLabel.move(0, 0)  # 标题栏安放到左上角

    def initLayout(self):
        # 设置框架布局
        self._MainLayout = QVBoxLayout()
        self._MainLayout.setSpacing(0)
        # 顶一个QLabel在竖放框架第一行，以免正常内容挤占到标题范围里
        self._MainLayout.addWidget(QLabel(), Qt.AlignLeft)
        self._MainLayout.addStretch()
        self.setLayout(self._MainLayout)
 
    def toolbarhidedelay(self):
        
        for button in self.buttons:
            button.hide()    
        self._TitleLabel.setStyleSheet("  background-color: rgba(0,0,0,0)")
    def leaveEvent(self, QEvent) : 
        if globalconfig['locktools']:
            return 
        self.ison=False
        def __(s):
            time.sleep(0.5)
            if self.ison==False:
                s.toolbarhidedelaysignal.emit()
        threading.Thread(target=lambda:__(self) ).start()
        
    def enterEvent(self, QEvent) : 
        
        self.ison=True
 
        for button in self.buttons[-2:] +self.showbuttons:
            button.show()  
        self._TitleLabel.setStyleSheet("border-width:0;\
                                                                 border-style:outset;\
                                                                 border-top:0px solid #e8f3f9;\
                                                                 color:white;\
                                                                 font-weight: bold;\
                                                                background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
    def resizeEvent(self, QResizeEvent):
         
         
        height = self.height() - 30*self.rate 
        
        #self.translate_text.resize(self.width(), height )
        self.translate_text.setGeometry(0, 30 * self.rate, self.width(), height * self.rate)
         
        for button in self.buttons[-2:]:
              button.adjast( ) 
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width())  

        if self._move_drag ==False: 
            self._right_rect = [self.width() - self._padding, self.width() + 1 ,30*self.rate, self.height() - self._padding]
            self._left_rect = [-1, self._padding,30*self.rate, self.height() - self._padding]
            self._bottom_rect = [self._padding, self.width() - self._padding,self.height() - self._padding, self.height() + 1]
            self._corner_rect = [self.width() - self._padding, self.width() + 1,self.height() - self._padding, self.height() + 1]
            self._lcorner_rect = [-1, self._padding,self.height() - self._padding, self.height() + 1]
    def isinrect(self,pos,rect):
        x,y=pos.x(),pos.y()
        x1,x2,y1,y2=rect
        if x>=x1 and x<=x2 and y<=y2 and y>=y1:
            return True
        else:
            return False
    def mousePressEvent(self, event):
        # 重写鼠标点击的事件 
        if (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(), self._corner_rect)):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True 
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._right_rect)):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True 
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._left_rect)):
            # 鼠标左键点击右侧边界区域
            self._left_drag = True 
            self.startxp=(event.globalPos() - self.pos() ) 
            self.startx=event.globalPos().x()
            self.startw=self.width()
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._bottom_rect)):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True 
        elif (event.button() == Qt.LeftButton) and (self.isinrect(event.pos(),self._lcorner_rect)):
            # 鼠标左键点击下侧边界区域
            self._lcorner_drag = True 
            self.startxp=(event.globalPos() - self.pos() ) 
            self.startx=event.globalPos().x()
            self.startw=self.width()
        # and (event.y() < self._TitleLabel.height()):
        elif (event.button() == Qt.LeftButton):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos() 

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势 
        pos=QMouseEvent.pos()
        if self._move_drag ==False:
            if self.isinrect( pos,self._corner_rect):
                self.setCursor(Qt.SizeFDiagCursor)
            elif self.isinrect( pos,self._lcorner_rect):
                self.setCursor(Qt.SizeBDiagCursor)
            elif self.isinrect(pos ,self._bottom_rect):
                self.setCursor(Qt.SizeVerCursor)
            elif self.isinrect(pos ,self._right_rect):
                self.setCursor(Qt.SizeHorCursor)
            elif self.isinrect(pos ,self._left_rect):
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        if Qt.LeftButton and self._right_drag:
            
            # 右侧调整窗口宽度
            self.resize(pos.x(), self.height())
        elif Qt.LeftButton and self._left_drag:
            # 右侧调整窗口宽度  
            self.setGeometry((QMouseEvent.globalPos() - self.startxp).x(),self.y(),self.startw-(QMouseEvent.globalPos().x() - self.startx),self.height())
            #self.resize(pos.x(), self.height())
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y()) 
        elif Qt.LeftButton and self._lcorner_drag:
            # 下侧调整窗口高度
            self.setGeometry((QMouseEvent.globalPos() - self.startxp).x(),self.y(),self.startw-(QMouseEvent.globalPos().x() - self.startx),QMouseEvent.pos().y())
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(pos.x(),pos.y()) 
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition) 

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._lcorner_drag = False
        self._right_drag = False
        self._left_drag = False
    def showhidetoolbuttons(self):
        showed=0
        self.showbuttons=[]
        
        
        for i,button in enumerate(self.buttons[:-2]):
            
            if i in [12,13,14] and globalconfig['sourcestatus']['ocr'] ==False:
                button.hide()
                continue
            if i in [10,11] and globalconfig['sourcestatus']['textractor'] ==False:
                button.hide()
                continue
            if globalconfig['sourcestatus']['textractor'] ==False and globalconfig['sourcestatus']['ocr'] ==False and i in [15,16,17]:
                button.hide()
                
                continue
            if 'name' in dir(button) and button.name in globalconfig['buttonuse'] and globalconfig['buttonuse'][button.name]==False: 
                button.hide()
                continue 
            button.move(showed*button.width() , 0) 
            self.showbuttons.append(button)
            #button.show()
            showed+=1
        self.enterEvent(None)
    def takusanbuttons(self, objectname,clickfunc,adjast=None,tips=None,save=None): 
         
        button=QTitleButton(self) 
        if tips:
            
            button.setToolTip(tips) 
        button.setIconSize(QSize(int(20*self.rate),
                                 int(20*self.rate)))
        button.name=save
        button.setObjectName(objectname)
        button.setFixedWidth(40*self.rate)
        button.setMouseTracking(True)
        button.setFixedHeight( self._TitleLabel.height() )
        button.clicked.connect(clickfunc) 
        if adjast<0: 
            button.adjast=lambda  :button.move(self.width() + adjast*button.width() , 0) 
        else:
            button.adjast=None
        self.buttons.append(button)
        
    def customSetGeometry(self, object, x, y, w, h):
    
        object.setGeometry(QRect(int(x * self.rate),
                                 int(y * self.rate), int(w * self.rate),
                                 int(h * self.rate)))
    def quitf_funtion(self):
        self.quitf()
    def quitf(self) :  
        import json  
        globalconfig['position']=[self.pos().x(),self.pos().y()]
        
        globalconfig['width']=self.width() 
        saveallconfig()
        self.tray.hide()
        self.tray = None 
        self.object.range_ui.close()
        self.object.settin_ui.close()
        #print(4)
        self.object.hookselectdialog.realclose=True 
        
        self.searchwordW.close()
        self.object.hookselectdialog.close() 
        if self.object.textsource:
            self.object.textsource.end()
        
        self.close() 
        #print('closed')
        import win32pipe,win32file
        try:
            win32pipe.WaitNamedPipe("\\\\.\\Pipe\\newsentence",win32con.NMPWAIT_WAIT_FOREVER)
            hPipe = win32file.CreateFile( "\\\\.\\Pipe\\newsentence", win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                    None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
            win32file.WriteFile(hPipe,"end".encode('utf8'))
        except:
            pass
         
        #sys.exit()
        if self.object.settin_ui.needupdate:
            with open('./update/update.bat','w',encoding='utf8') as ff:
                
                ff.write('''
timeout 1
xcopy update\LunaTranslator\ .\ /s /e /c /y /h /r
exit

                ''')
            

            subprocess.Popen('update\\update.bat' ,shell=True)
        endsubprocs()
        os._exit(1) 