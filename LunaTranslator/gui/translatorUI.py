from queue import Queue 
import functools  
from threading import Thread
import threading 
import time
t1=time.time()
import os
import subprocess
from traceback import print_exc
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal  
import qtawesome 
from PyQt5.QtCore import pyqtSignal,Qt,QRect,QSize  
from PyQt5.QtGui import  QFont  ,QIcon,QPixmap  
from PyQt5.QtWidgets import  QLabel ,QPushButton ,QSystemTrayIcon ,QAction,QMenu 
import pyperclip 
from PyQt5.QtCore import QProcess ,QByteArray  
from utils.config import globalconfig,postprocessconfig,transerrorfixdictconfig,noundictconfig
from utils.subproc import endsubprocs,mutiproc
import  win32gui,win32api,win32process,win32con,multiprocessing
import gui.rangeselect
import gui.transhist

from utils.getpidlist import getwindowhwnd
from gui.settingpage4 import autosaveshow
from gui.settingpage1 import settingsource,settingtextractor
from gui.textbrowser import Textbrowser
from gui.showword import searchwordW
from gui.rangeselect  import moveresizegame
from utils.magpie import callmagpie
class QTitleButton(QPushButton):
    """
    新建标题栏按钮类
    """

    def __init__(self, *args):
        super(QTitleButton, self).__init__(*args)
        self.setFont(QFont("Webdings"))  # 特殊字体以不借助图片实现最小化最大化和关闭按钮
        
  
class QUnFrameWindow(QWidget):
    """
    无边框窗口类
    """
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
    bindcropwindow_signal=pyqtSignal()
    quitf_signal=pyqtSignal()
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
            self.translate_text.showyinyingtext(color,res[1])
            self.translate_text.textbrowser.hide()
            if (globalconfig['usesearchword'] or globalconfig['show_fenci'] or globalconfig['showcixing']) and res[0]: 
                self.translate_text.addsearchwordmask(res[0],res[1],self.showsearchword,0)
            return 
        self.translate_text.textbrowser.show()
        
        if type_==1: 
            self.translate_text.append(res[1]) 
        else: 
            self.translate_text.append(' ')
            self.translate_text.append(res[1])  
            self.translate_text.addtag(res[0]) 
        if (globalconfig['usesearchword'] or globalconfig['show_fenci'] or globalconfig['showcixing']) and res[0]:
            self.translate_text.addsearchwordmask(res[0],res[1],self.showsearchword) 
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
           
    def __init__(self, object):
        super(QUnFrameWindow, self).__init__(
            None, Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool )  # 设置为顶级窗口，无边框
        #self.setFocusPolicy(Qt.StrongFocus)

        self.setAttribute(Qt.WA_TranslucentBackground) 

        
        self.object = object
        self.rate = self.object.screen_scale_rate 
        self.callmagpie=None
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

        self.showsavegame_signal.connect(self.showsavegame_function)
        self.settinghookthread_signal.connect(self.settinghookthread_funtion)
        self.settingprocess_signal.connect(self.settingprocess_function)
        self.clickRange_signal.connect(self.clickRange_funtion)
        self.showhide_signal.connect(self.showhide_function)
        self.bindcropwindow_signal.connect(self.bindcropwindow_function)
        self.quitf_signal.connect(self.quitf_funtion)
        # self.showtask=Queue()
        # self.showtaskthread=threading.Thread(target=self.showtaskthreadfun).start()
        self.clear_text_sign.connect(self.clearText)
        self.object = object  
        # 界面缩放比例
        self.searchwordW=searchwordW(self)
        
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

        self.mousetransparent=False
        self.buttons=[] 
        self.showbuttons=[]
         
        self.takusanbuttons(qtawesome.icon("fa.rotate-right" ,color="white"),"MinMaxButton",self.startTranslater,0,"重新翻译")
        self.takusanbuttons(qtawesome.icon("fa.forward" ,color="#FF69B4" if globalconfig['autorun'] else 'white'),"MinMaxButton",self.changeTranslateMode,1,"自动翻译",'automodebutton')
        self.takusanbuttons(qtawesome.icon("fa.gear",color="white" ),"MinMaxButton",self.clickSettin,2,"打开设置")


        self.takusanbuttons(qtawesome.icon("fa.copy" ,color="white"),"MinMaxButton",lambda: pyperclip.copy(self.original),6,"复制到剪贴板") 
        self.takusanbuttons(qtawesome.icon("fa.eye"   if globalconfig['isshowrawtext'] else "fa.eye-slash" ,color="white"),"MinMaxButton", self.changeshowhideraw,7,"显示/隐藏原文",'showhiderawbutton') 
        
        self.takusanbuttons(qtawesome.icon("fa.rotate-left" ,color="white"),"MinMaxButton", self.transhis.showsignal.emit  ,8,"显示历史翻译") 
        self.takusanbuttons(qtawesome.icon("fa.music" ,color="white"),"MinMaxButton",self.langdu,9,"朗读") 
        self.takusanbuttons(qtawesome.icon("fa.mouse-pointer" ,color="white"),"MinMaxButton",self.changemousetransparentstate,10,"鼠标穿透窗口",'mousetransbutton') 
         
        self.takusanbuttons(qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else 'white'),"MinMaxButton",self.changetoolslockstate,11,"锁定工具栏",'locktoolsbutton') 
        
        
        self.takusanbuttons(qtawesome.icon("fa.gamepad" ,color= 'white'),"MinMaxButton",lambda: autosaveshow(None),3,"打开保存的游戏") 

        self.takusanbuttons(qtawesome.icon("fa.link" ,color= 'white'),"MinMaxButton",lambda :settingtextractor(self.object.settin_ui,False),4,"选择游戏" ) 
        self.takusanbuttons(qtawesome.icon("fa.tasks" ,color= 'white'),"MinMaxButton",lambda :settingsource(self.object.settin_ui),5,"选择文本" ) 
        

        self.takusanbuttons(qtawesome.icon("fa.crop" ,color="white"),"MinMaxButton",self.clickRange,4,"选取OCR范围")
        self.takusanbuttons((qtawesome.icon("fa.square" ,color='white')),"MinMaxButton",self.showhide,5,"显示/隐藏范围框",'showhidebutton')
         
        self.takusanbuttons((qtawesome.icon("fa.windows" ,color='white')),"MinMaxButton",self.bindcropwindow,5,"绑定截图窗口，避免遮挡（部分软件不支持）（点击自己取消）",'bindcropwindowbutton')
        
        # self.takusanbuttons(qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else 'white'),"MinMaxButton",self.changetoolslockstate,10,"锁定工具栏",'locktoolsbutton') 
        def _moveresizegame(self):
            
            if ('moveresizegame'   in dir(self)) : 
                if self.moveresizegame :
                    self.moveresizegame.close()
            try: 
                if (self.object.settin_ui.hookpid and globalconfig['sourcestatus']['textractor'])or (globalconfig['sourcestatus']['ocr'] and self.object.textsource.hwnd):
                
                    if globalconfig['sourcestatus']['ocr']:
                        hwnd= self.object.textsource.hwnd 
                    elif globalconfig['sourcestatus']['textractor']:
                        hwnd=getwindowhwnd(self.object.settin_ui.hookpid)
                    self.moveresizegame=moveresizegame(self,hwnd)
            except:
                    print_exc()
        self.takusanbuttons(qtawesome.icon("fa.expand" ,color= 'white'),"MinMaxButton",lambda :_moveresizegame(self),5,"调整游戏窗口(需要绑定ocr窗口，或选择hook进程)" ) 

        def __initmulti(self):
            self.multiprocesshwnd=multiprocessing.Queue()
            self.callmagpie=mutiproc(callmagpie,(self.multiprocesshwnd,r'./files/Magpie_v0.9.1' ))
            self.callmagpie.start() 
        threading.Thread(target=__initmulti,args=(self,)).start() 
        def _fullsgame(self):
            
            if ('moveresizegame'   in dir(self)) : 
                if self.moveresizegame :
                    self.moveresizegame.close()
            try: 
                if (self.object.settin_ui.hookpid and globalconfig['sourcestatus']['textractor'])or (globalconfig['sourcestatus']['ocr'] and self.object.textsource.hwnd):
                
                    if globalconfig['sourcestatus']['ocr']:
                        hwnd= self.object.textsource.hwnd 
                    elif globalconfig['sourcestatus']['textractor']:
                        hwnd=getwindowhwnd(self.object.settin_ui.hookpid)

                    if globalconfig['usemagpie']: 
                        
                        if self.callmagpie  : 
                            self.isletgamefullscreened=not self.isletgamefullscreened
                            self.letgamefullscreenbutton.setIcon(qtawesome.icon("fa.window-maximize" ,color="#FF69B4" if self.isletgamefullscreened else "white"))
                            if self.isletgamefullscreened:
                               
                                win32gui.SetForegroundWindow(hwnd )   
                                self.multiprocesshwnd.put(hwnd)  
                                def __makerangetop():
                                    for i in range(3):
                                        time.sleep(0.3)
                                        try:    
                                            win32gui.SetWindowPos(int(self.object.range_ui.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOSIZE | win32con.SWP_NOMOVE)  
                                        except:
                                            pass
                                if self.showhidestate:
                                    threading.Thread(target=__makerangetop).start()
                                
                            else:
                                pass
                    else:

                        self.isletgamefullscreened=not self.isletgamefullscreened
                        self.letgamefullscreenbutton.setIcon(qtawesome.icon("fa.window-maximize" ,color="#FF69B4" if self.isletgamefullscreened else "white"))
                        if self.isletgamefullscreened:
                            self.wpc=win32gui. GetWindowPlacement( hwnd )
                            self.HWNDStyle = win32gui.GetWindowLong( hwnd, win32con.GWL_STYLE )
                            self.HWNDStyleEx = win32gui.GetWindowLong( hwnd, win32con.GWL_EXSTYLE  )
                            NewHWNDStyle=self.HWNDStyle
                            NewHWNDStyle &= ~win32con.WS_BORDER;
                            NewHWNDStyle &= ~win32con.WS_DLGFRAME;
                            NewHWNDStyle &= ~win32con.WS_THICKFRAME;
                            NewHWNDStyleEx=self.HWNDStyleEx
                            NewHWNDStyleEx &= ~win32con.WS_EX_WINDOWEDGE;
                            win32gui.SetWindowLong( hwnd, win32con.GWL_STYLE, NewHWNDStyle | win32con.WS_POPUP );
                            win32gui.SetWindowLong( hwnd, win32con.GWL_EXSTYLE, NewHWNDStyleEx | win32con.WS_EX_TOPMOST )
                            win32gui.ShowWindow(hwnd,win32con.SW_SHOWMAXIMIZED )
                        else:
                            win32gui.SetWindowLong( hwnd, win32con.GWL_STYLE, self.HWNDStyle );
                            win32gui.SetWindowLong( hwnd, win32con.GWL_EXSTYLE, self.HWNDStyleEx );
                            win32gui.ShowWindow( hwnd, win32con.SW_SHOWNORMAL );
                            win32gui.SetWindowPlacement( hwnd, self.wpc );
                    
            except:
                    print_exc()
        self.takusanbuttons(qtawesome.icon("fa.window-maximize" ,color= 'white'),"MinMaxButton",lambda :_fullsgame(self),5,"全屏/恢复游戏窗口(需要绑定ocr窗口，或选择hook进程)" ,"letgamefullscreenbutton") 
        
        
        self.takusanbuttons(qtawesome.icon("fa.minus",color="white" ),"MinMaxButton",self.hide_and_disableautohide,-2,"最小化到托盘")
        self.takusanbuttons(qtawesome.icon("fa.times" ,color="white"),"CloseButton",self.quitf,-1,"退出")
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
        self.showhidestate=False

    

    def changemousetransparentstate(self):
         
        self.mousetransparent= not self.mousetransparent
        if self.mousetransparent:
            # self.masklabel.setAttribute(Qt.WA_TransparentForMouseEvents,  self.mousetransparent) 
            # self.translate_text.setAttribute(Qt.WA_TransparentForMouseEvents,  self.mousetransparent)  
            self.translate_text.setStyleSheet("border-width:0;\
                                                                    border-style:outset;\
                                                                    border-top:0px solid #e8f3f9;\
                                                                    color:white;\
                                                               \
                                                                    background-color: rgba(%s, %s, %s, %s)"
                                            %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),0))
            # if globalconfig['locktools']==False:
            #     globalconfig['locktools']=not globalconfig['locktools'] 
            #     self.locktoolsbutton.setIcon(qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else 'white'))
        
        else:
            self.object.translation_ui.translate_text.setStyleSheet("border-width:0;\
                                                                 border-style:outset;\
                                                                 border-top:0px solid #e8f3f9;\
                                                                 color:white;\
                                                                background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/100))
        self.mousetransbutton.setIcon(qtawesome.icon("fa.mouse-pointer" ,color="#FF69B4" if self.mousetransparent else 'white'))
    def showhide_function(self):
        self.showhide()
    def showhide(self):
        
        self.showhidestate=not self.showhidestate
        #self.showhidebutton.setIcon(qtawesome.icon("fa.eye" if self.showhidestate else "fa.eye-slash" ,color="white"))
        self.showhidebutton.setIcon(qtawesome.icon("fa.square" ,color="#FF69B4" if self.showhidestate else 'white'))
        if self.showhidestate:
            self.object.range_ui.show()
        else:
            self.object.range_ui.hide()
    def bindcropwindow_function(self):
        self.bindcropwindow()
    def bindcropwindow(self):
        import PyHook3
        hm = PyHook3.HookManager()
        def OnMouseEvent(event): 
            
            p=win32api.GetCursorPos()

            hwnd_=win32gui.WindowFromPoint(p)

            
            selfpid=win32api.GetCurrentProcessId()
            pid=win32process.GetWindowThreadProcessId(hwnd_) [1]
            #print(pid,selfpid)
            if pid==selfpid  :
                self.object.textsource.hwnd= None
                self.bindcropwindowbutton.setIcon(qtawesome.icon("fa.windows" ,color="white" ))
            #for pid in pids:
            else:
                self.object.textsource.hwnd= (hwnd_)  
                self.bindcropwindowbutton.setIcon(qtawesome.icon("fa.windows" ,color="#FF69B4" ))
            
            hm.UnhookMouse()   
            return True
        hm.MouseAllButtonsDown = OnMouseEvent
        hm.HookMouse()
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
        self.automodebutton.setIcon(qtawesome.icon("fa.forward" ,color="#FF69B4" if globalconfig['autorun'] else 'white'))
    def changetoolslockstate(self):
        # if self.mousetransparent: 
        #     self.mousetransbutton.click()
        globalconfig['locktools']=not globalconfig['locktools'] 
        self.locktoolsbutton.setIcon(qtawesome.icon("fa.lock" ,color="#FF69B4" if globalconfig['locktools'] else 'white'))
        
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
        #print(self.original)
        
        if self.object.reader:
            self.object.reader.read(self.original )
        else:
            pass
    # 按下翻译键
    def startTranslater(self) :
        if hasattr(self.object,'textsource') and  self.object.textsource :
            Thread(target=self.object.textsource.runonce).start()
         
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
            # self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
            #                     for y in range(1, self.height() - self._padding)]
            # self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
            #                     for y in range(self.height() - self._padding, self.height() + 1)]
            # self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
            #                     for y in range(self.height() - self._padding, self.height() + 1)]
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
            
            if globalconfig['sourcestatus']['textractor'] ==False and globalconfig['sourcestatus']['ocr'] ==False and i in [15,16]:
                button.hide()
                
                continue
            if globalconfig['useresizebutton']==False and i==15:
                button.hide()
                continue
            if globalconfig['usefullscreenbutton']==False and i==16:
                button.hide()
                continue
            if i in [10,11] and globalconfig['sourcestatus']['textractor'] ==False:
                button.hide()
                continue
            button.move(showed*button.width() , 0) 
            self.showbuttons.append(button)
            #button.show()
            showed+=1
        self.enterEvent(None)
    def takusanbuttons(self,iconname,objectname,clickfunc,adjast=None,tips=None,save=None): 
        
        button=QTitleButton(self)
        button.setIcon(iconname)
        if tips:
            
            button.setToolTip(tips) 
        button.setIconSize(QSize(int(20*self.rate),
                                 int(20*self.rate)))
        if save:
              setattr(self,save,button)
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
        
        with open('./userconfig/config.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(globalconfig,ensure_ascii=False,sort_keys=False, indent=4))
        #self.hide()
        with open('./userconfig/postprocessconfig.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(postprocessconfig,ensure_ascii=False,sort_keys=False, indent=4))
        with open('./userconfig/transerrorfixdictconfig.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(transerrorfixdictconfig,ensure_ascii=False,sort_keys=False, indent=4))
        with open('./userconfig/noundictconfig.json','w',encoding='utf-8') as ff:
            ff.write(json.dumps(noundictconfig,ensure_ascii=False,sort_keys=False, indent=4))
        self.tray.hide()
        self.tray = None 
        self.object.range_ui.close()
        self.object.settin_ui.close()
        #print(4)
        self.object.hookselectdialog.realclose=True 
        
        self.searchwordW.close()
        self.object.hookselectdialog.close()
        #print(5)
        # if 'textsource' in dir(self.object) and self.object.textsource and self.object.textsource.ending==False:
        #     self.object.textsource.end()
        #     if 'p' in dir(self.object.textsource):
        #         self.object.textsource.p.kill()
        #         self.object.textsource.p.terminate()
        #         self.object.textsource.p.waitForFinished () 
          
        # import ctypes 
        # for hookID in self.object.settin_ui.hooks:
        #     ctypes.windll.user32.UnhookWinEvent(hookID)
        #print(aa)  
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