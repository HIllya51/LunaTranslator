
import time 
import functools   
import threading 
import os
import subprocess
from traceback import print_exc
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout,QApplication
from PyQt5.QtCore import Qt, pyqtSignal  ,QThread
import qtawesome 
from PyQt5.QtCore import pyqtSignal,Qt,QRect,QSize  
from PyQt5.QtGui import  QFont  ,QIcon,QPixmap  ,QMouseEvent
from PyQt5.QtWidgets import  QLabel ,QPushButton ,QSystemTrayIcon ,QAction,QMenu 

import pyperclip,queue
from utils.config import globalconfig,saveallconfig,_TR
from utils.subproc import endsubprocs,mutiproc
import  win32gui,win32api,win32process,win32con,multiprocessing
import gui.rangeselect
from utils.update import update
from utils.subproc import subproc
from utils.getpidlist import mouseselectwindow 
from gui.dialog_savedgame import dialog_savedgame
from gui.textbrowser import Textbrowser
from utils.fullscreen import fullscreen
from gui.rangeselect  import moveresizegame 
class QTitleButton(QPushButton):
    def __init__(self, parent):
        super(QTitleButton, self).__init__(parent)
        self.setFont(QFont("Webdings"))   
    def enterEvent(self, a0 ) -> None:
        return super().enterEvent(a0)
    def leaveEvent(self, a0 ) -> None:
        return super().leaveEvent(a0)
class QUnFrameWindow(QWidget):   
    displayres =  pyqtSignal(str,str ) 
    displayraw1 =  pyqtSignal(list, str,str,int )  
    displaystatus=pyqtSignal(str,str,bool) 
    showhideuisignal=pyqtSignal()
    hookfollowsignal=pyqtSignal(int,tuple)
    toolbarhidedelaysignal=pyqtSignal() 
    showsavegame_signal=pyqtSignal() 
    clickRange_signal=pyqtSignal(bool)
    rangequick=pyqtSignal()
    showhide_signal=pyqtSignal()
    grabwindowsignal=pyqtSignal()
    bindcropwindow_signal=pyqtSignal()
    fullsgame_signal=pyqtSignal()
    quitf_signal=pyqtSignal() 
    refreshtooliconsignal=pyqtSignal()
    hidesignal=pyqtSignal()
    muteprocessignal=pyqtSignal()  
    showlinesignal=pyqtSignal(list,str,int)
    clearsignal=pyqtSignal()
    def hookfollowsignalsolve(self,code,other): 
        if self._move_drag:
            return 
        if code==3:
            if self.hideshownotauto:
                self.show_()
        elif code==4: 
            if self.hideshownotauto:
                self.hide_()
        elif code==5:
            #print(self.pos())
            #self.move(self.pos() + self._endPos)
            self.move(self.pos().x()+ other[0],self.pos().y()+ other[1])
            #self.move(self.pos().x()+self.rate *other[0],self.pos().y()+self.rate *other[1])
        elif code==6:
            #print(self.pos())
            #self.move(self.pos() + self._endPos)
            self.move(self.pos().x()+ other[0],self.pos().y()+ other[1])
    def showres(self,_type,res):  
        try:
            if globalconfig['showfanyisource']:
                #print(_type)
                #self.showline((None,globalconfig['fanyi'][_type]['name']+'  '+res),globalconfig['fanyi'][_type]['color']  )
                self.showtask.put(([None,globalconfig['fanyi'][_type]['name']+'  '+res],globalconfig['fanyi'][_type]['color']  ))
            else:
                #self.showline((None,res),globalconfig['fanyi'][_type]['color']  )
                self.showtask.put(([None,res],globalconfig['fanyi'][_type]['color']  ))
            #print(globalconfig['fanyi'][_type]['name']+'  '+res+'\n')
            
            self.object.transhis.getnewtranssignal.emit(globalconfig['fanyi'][_type]['name'],res)
        except:
            print_exc() 
    def showraw(self,hira,res,color,show ): 
        #self.translate_text.clear_and_setfont()
        self.showtask.queue.clear()
        self.showtask.put(1)
        self.original=res 
        if show==1: 
            #self.showline((hira,res),color )
            self.showtask.put(([hira,res],color))
        elif show==0:
            pass
        elif show==2:
            #self.showline((hira,res),color ,type_=2 )
            self.showtask.put(([hira,res],color , 2 ))
        self.object.transhis.getnewsentencesignal.emit(res) 
        self.object.edittextui.getnewsentencesignal.emit(res) 
    # def showtaskthreadfun(self):
    #     while True:
    #         res,color ,type_=self.showtask.get()
    #         self.showline_real(res,color ,type_)
    # def showline(self,res,color ,type_=1):
    #     self.showtask.put((res,color ,type_))
    def showstatus(self,res,color,clear):
        if clear:
            #self.translate_text.clear_and_setfont()
            self.showtask.queue.clear()
            self.showtask.put(1)
        #self.showline([None,res],color)
        self.showtask.put(([None,res],color))
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
            self.translate_text.simplecharformat(color)  
        if type_==1: 
            self.translate_text.append (res[1],[]) 
        else:   
            self.translate_text.append (res[1],res[0])    
        if globalconfig['zitiyangshi'] ==3:
            self.translate_text.showyinyingtext(color  ) 
        if (globalconfig['usesearchword'] or globalconfig['show_fenci']  ) and res[0]:
            self.translate_text.addsearchwordmask(res[0],res[1],self.object.searchwordW.getnewsentencesignal.emit   ) 
        
        
        if globalconfig['autodisappear']:
            if self.hideshownotauto:
                flag=(self.showintab and self.isMinimized()) or (not self.showintab and self.isHidden())
        
                if flag:
                    self.show_()
            self.lastrefreshtime=time.time()
            self.autohidestart=True 
    def autohidedelaythread(self):
        while True:
            if globalconfig['autodisappear'] and self.autohidestart:
                tnow=time.time()
                if tnow-self.lastrefreshtime>=globalconfig['disappear_delay']:
                    self.hidesignal.emit() 
                    self.autohidestart=False
                    self.lastrefreshtime=tnow
                    
            time.sleep(0.5) 
     
    def showhideui(self): 
        if self._move_drag:
            return 
         
        flag=(self.showintab and self.isMinimized()) or (not self.showintab and self.isHidden())
        
        if flag:
            self.show_and_enableautohide() 
        else:
            self.hide_and_disableautohide()
    def leftclicktray(self,reason):
            #鼠标左键点击
            if reason == QSystemTrayIcon.Trigger:
                self.showhideui()
                 
    def hide_and_disableautohide(self):
        self.hideshownotauto=False
        self.hide_()
    def show_and_enableautohide(self): 
        self.hideshownotauto=True
        win32gui.SetForegroundWindow(self.winId() )   
        self.show_()
     
    def refreshtoolicon(self):
        icon=[
            qtawesome.icon("fa.hand-paper-o" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.rotate-right" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.forward" if globalconfig['autorun'] else 'fa.play' ,color="#FF69B4" if globalconfig['autorun'] else globalconfig['buttoncolor']),
            qtawesome.icon("fa.gear",color=globalconfig['buttoncolor'] ),
            qtawesome.icon("fa.copy" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.edit" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.eye"   if globalconfig['isshowrawtext'] else "fa.eye-slash" ,color="#FF69B4" if globalconfig['isshowrawtext'] else globalconfig['buttoncolor']),
            qtawesome.icon("fa.rotate-left" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.book" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.music" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.mouse-pointer" ,color="#FF69B4" if self.mousetransparent else globalconfig['buttoncolor']),
            qtawesome.icon("fa.lock" if globalconfig['locktools'] else 'fa.unlock',color="#FF69B4" if globalconfig['locktools'] else globalconfig['buttoncolor']),
            qtawesome.icon("fa.gamepad" ,color= globalconfig['buttoncolor']),
            qtawesome.icon("fa.link" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.tasks" ,color= globalconfig['buttoncolor']),
            qtawesome.icon("fa.crop" ,color=globalconfig['buttoncolor']),
            qtawesome.icon("fa.square" ,color=  "#FF69B4" if self.showhidestate else globalconfig['buttoncolor']),
            qtawesome.icon("fa.windows" ,color= "#FF69B4"  if self.isbindedwindow else globalconfig['buttoncolor']),
            qtawesome.icon("fa.arrows" ,color= globalconfig['buttoncolor']),
            qtawesome.icon("fa.compress"  if self.isletgamefullscreened else 'fa.expand',color=    globalconfig['buttoncolor']),
            qtawesome.icon("fa.volume-off"  if self.processismuteed else "fa.volume-up" ,color= globalconfig['buttoncolor']),
            qtawesome.icon("fa.minus",color=globalconfig['buttoncolor'] ),
            qtawesome.icon("fa.times" ,color=globalconfig['buttoncolor']),
        ]
        for i in range(len(self.buttons)):
            self.buttons[i].setIcon(icon[i])
    def addbuttons(self):
        self.takusanbuttons("MinMaxButton",None,0,"移动","move")
        self.takusanbuttons("MinMaxButton",self.startTranslater,0,"重新翻译")
        self.takusanbuttons("MinMaxButton",self.changeTranslateMode,1,"自动翻译",'automodebutton') 
        self.takusanbuttons("MinMaxButton",lambda:self.object.settin_ui.showsignal.emit(),2,"打开设置")


        self.takusanbuttons("MinMaxButton",lambda:pyperclip.copy( self.original),6,"复制到剪贴板",'copy') 
        self.takusanbuttons("MinMaxButton",lambda: self.object.edittextui.showsignal.emit(),6,"编辑",'edit') 
        self.takusanbuttons("MinMaxButton", self.changeshowhideraw,7,"显示/隐藏原文",'showraw') 
        
        self.takusanbuttons("MinMaxButton",lambda: self.object.transhis.showsignal.emit() ,8,"显示/隐藏历史翻译",'history') 
        self.takusanbuttons("MinMaxButton",lambda: self.object.settin_ui.button_noundict.click() ,8,"专有名词翻译设置",'noundict') 
        self.takusanbuttons("MinMaxButton",self.langdu,9,"朗读",'langdu') 
        self.takusanbuttons("MinMaxButton",self.changemousetransparentstate,10,"鼠标穿透窗口",'mousetransbutton') 
         
        self.takusanbuttons("MinMaxButton",self.changetoolslockstate,11,"锁定工具栏",'locktoolsbutton') 
        
        
        self.takusanbuttons("MinMaxButton",lambda: dialog_savedgame(self.object.settin_ui),3,"打开保存的游戏",'gamepad') 

        self.takusanbuttons("MinMaxButton",lambda :self.object.AttachProcessDialog.showsignal.emit(),4,"选择游戏",None,["textractor","embedded"] )  
        self.takusanbuttons("MinMaxButton",lambda:self.object.hookselectdialog.showsignal.emit(),5,"选择文本",None ,["textractor","embedded"]) 
         
        self.takusanbuttons("MinMaxButton",lambda :self.clickRange(False),4,"选取OCR范围",None,[ "ocr"])
        self.takusanbuttons("MinMaxButton",self.showhide,5,"显示/隐藏范围框",None,["ocr"])
         
        self.takusanbuttons("MinMaxButton",self.bindcropwindow_signal.emit,5,"绑定截图窗口，避免遮挡（部分软件不支持）（点击自己取消）",None,["ocr"])
          
        self.takusanbuttons("MinMaxButton",lambda :moveresizegame(self,self.object.textsource.hwnd),5,"调整游戏窗口(需要绑定ocr窗口，或选择hook进程)",'resize' ,["textractor","ocr","embedded"]) 
  
        self.takusanbuttons("MinMaxButton",self._fullsgame,5,"全屏/恢复游戏窗口(需要绑定ocr窗口，或选择hook进程)" ,"fullscreen",["textractor","ocr","embedded"]) 
        
        self.takusanbuttons("MinMaxButton",self.muteprocessfuntion,5,"游戏静音(需要绑定ocr窗口，或选择hook进程)" ,"muteprocess",["textractor","ocr",'embedded']) 
        
        
        self.takusanbuttons("MinMaxButton",self.hide_and_disableautohide,-2,"最小化到托盘")
        self.takusanbuttons("CloseButton",self.close,-1,"退出")
    def hide_(self):  
        if self.showintab: 
            win32gui.ShowWindow(self.winId(),win32con.SW_SHOWMINIMIZED )
        else:
            self.hide()
    def show_(self):   
        if self.showintab:
            win32gui.ShowWindow(self.winId(),win32con.SW_SHOWNORMAL )
        else:
            self.show()
    def showEvent(self, a0 ) -> None: 
        if self.isfirstshow:
            icon = QIcon()
            icon.addPixmap(QPixmap('./files/luna.jpg'), QIcon.Normal, QIcon.On)
            self.setWindowIcon(icon)
            self.tray = QSystemTrayIcon()  
            self.tray.setIcon(icon) 
            
            showAction = QAction(_TR("&显示"), self, triggered = self.show_and_enableautohide)
            settingAction = QAction(_TR("&设置"), self, triggered = lambda: self.object.settin_ui.showsignal.emit())
            quitAction = QAction(_TR("&退出"), self, triggered = self.close)
                    
            
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
            self.isfirstshow=False 
        return super().showEvent(a0)
    def realshowthread(self):
        while True:
            task=self.showtask.get()
            #print(task)
            if type(task)==int:
                self.clearsignal.emit()
                continue
            if len(task)==3:
                res,color ,type1=task
            else:
                res,color =task
                type1=1 
            self.showlinesignal.emit(res,color ,type1)
    def __init__(self, object):
        
        super(QUnFrameWindow, self).__init__(
            None, Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.WindowSystemMenuHint|Qt.WindowMinimizeButtonHint)  # 设置为顶级窗口，无边框
        #self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowFlag(Qt.Tool,not globalconfig['showintab'])
        self.isfirstshow=True
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setAttribute(Qt.WA_ShowWithoutActivating,True)
        self.showintab=  globalconfig['showintab']
        self.showlinesignal.connect(self.showline)
        self.showtask=queue.Queue() 
        threading.Thread(target=self.realshowthread).start()
        self.setWindowTitle('LunaTranslator')
        self.hidesignal.connect(self.hide_)
        self.object = object
        self.lastrefreshtime=time.time()
        self.autohidestart=False
        threading.Thread(target=self.autohidedelaythread).start()
        self.rate = self.object.screen_scale_rate  
        self.muteprocessignal.connect(self.muteprocessfuntion) 
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)
        self._padding = 5*self.rate  # 设置边界宽度为5
        self.setMinimumWidth(100)
        self.setMinimumHeight(100)
        self.hideshownotauto=True
        self.displaystatus.connect(self.showstatus)
        self.showhideuisignal.connect(self.showhideui)
        self.hookfollowsignal.connect(self.hookfollowsignalsolve) 
        self.displayres.connect(self.showres)
        self.displayraw1.connect(self.showraw)   
        self.refreshtooliconsignal.connect(self.refreshtoolicon)
        self.showsavegame_signal.connect(lambda:dialog_savedgame(self.object.settin_ui))  
        self.clickRange_signal.connect(self.clickRange )
        self.rangequick.connect(self.quickrange)
        self.showhide_signal.connect(self.showhide )
        self.bindcropwindow_signal.connect(functools.partial(mouseselectwindow, self.bindcropwindowcallback))
        self.grabwindowsignal.connect(self.grabwindow)
        self.quitf_signal.connect(self.close)
        self.fullsgame_signal.connect(self._fullsgame) 

        self.object = object  
        
        self.isletgamefullscreened=False
        self.fullscreenmanager=fullscreen()
        self.original = ""    
        self._isTracking=False
        self.quickrangestatus=False
        self.isontop=True 
        self.initTitleLabel()  # 安放标题栏标签
          
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
          background-color: %s;
          border: 0px;
          font: 100 10pt;
      }
      QTitleButton#CloseButton:hover{
          background-color: %s;
          color: white;
          border: 0px;
          font: 100 10pt;
      }'''%(globalconfig['button_color_normal'],globalconfig['button_color_close']))
          
         
        self.showhidestate=False
        self.processismuteed=False
        self.mousetransparent=False
        self.isbindedwindow=False
        self.buttons=[] 
        self.showbuttons=[] 
        self.addbuttons() 
        self.refreshtoolicon()
        self.showhidetoolbuttons()
        d=QApplication.desktop()

        globalconfig['position'][0]=min(max(globalconfig['position'][0],0),d.width()-globalconfig['width'])
        globalconfig['position'][1]=min(max(globalconfig['position'][1],0),d.height()-globalconfig['height'])
        
        self.setGeometry( globalconfig['position'][0],globalconfig['position'][1],int(globalconfig['width'] ), int(globalconfig['height'])) 

        
        self.translate_text =  Textbrowser(self)  
        
        self.clearsignal.connect(self.translate_text.clear_and_setfont)
        self.showtask.put(1)
        self.showtask.put(([None,_TR('欢迎使用')],''))
        self.translate_text.move(0,30*self.rate) 
        # 翻译框根据内容自适应大小
        self.document = self.translate_text.document()
        self.document.contentsChanged.connect(self.textAreaChanged)  
        self.set_color_transparency()
    def set_color_transparency(self ):
        self.translate_text.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']*(not self.mousetransparent)/100))
        self._TitleLabel.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                           font-weight: bold;\
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
    def grabwindow(self): 
        
        try:
            hwnd=win32gui.FindWindow('Window_Magpie_967EB565-6F73-4E94-AE53-00CC42592A22',None) 
            tm=time.localtime()
            if hwnd:
                hwnd=QApplication.desktop().winId() 
                self.hide()
                QApplication.primaryScreen().grabWindow(hwnd).save(f'./cache/screenshot/{tm.tm_year}-{tm.tm_mon}-{tm.tm_mday}-{tm.tm_hour}-{tm.tm_min}-{tm.tm_sec}.png')
                self.show() 
                
            else:
                hwnd=win32gui.GetForegroundWindow()   
                if hwnd==int(self.winId()):
                    hwnd=self.object.textsource.hwnd 
                QApplication.primaryScreen().grabWindow(hwnd).save(f'./cache/screenshot/{tm.tm_year}-{tm.tm_mon}-{tm.tm_mday}-{tm.tm_hour}-{tm.tm_min}-{tm.tm_sec}.png')
                
                
        except:
            pass
    def muteprocessfuntion(self): 
        try:
            pid= self.object.textsource.pid 
            self.processismuteed=not self.processismuteed
            
            self.refreshtoolicon()
            
            subproc(f'./files/muteprocess.exe {pid}  {int(self.processismuteed)}')
        except:
            print_exc()
    
    def _fullsgame(self): 
        self.isletgamefullscreened=not self.isletgamefullscreened
        self.refreshtoolicon()
        if self.object.textsource:
            self.fullscreenmanager(self.object.textsource.hwnd,self.isletgamefullscreened) 
     
    def changemousetransparentstate(self): 
        self.mousetransparent= not self.mousetransparent
        self.set_color_transparency()
        
        self.refreshtoolicon()
     
    def showhide(self): 
        if self.object.rect:
            self.showhidestate=not self.showhidestate 
            self.refreshtoolicon()
            self.object.range_ui.setVisible(self.showhidestate) 
    def bindcropwindowcallback(self,pid,hwnd,name_): 
            _pid=os.getpid()
            self.object.textsource.hwnd= hwnd if pid!=_pid else None
            self.object.textsource.pid= pid if pid!=_pid else None
            self.isbindedwindow=(pid!=_pid)
            self.refreshtoolicon()  
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
        if self.translate_text.cleared:
            return
        newHeight = self.document.size().height() 
        width = self.width()
        self.resize(width, newHeight + 30*self.rate) 
      
    def quickrange(self): 
        if self.quickrangestatus:
            self.object.screen_shot_ui.immediateendsignal.emit()
            # if globalconfig['autorun']==False:
            #     self.startTranslater()
        else:
            self.clickRange(True)
        
    def clickRange(self,auto): 
        if globalconfig['sourcestatus']['ocr']==False:
                return 
        self.showhidestate=False
        
        self.quickrangestatus=not self.quickrangestatus
        self.object.range_ui.hide()
        self.object.screen_shot_ui =gui.rangeselect.rangeselct(self.object)
        self.object.screen_shot_ui.show()
        self.object.screen_shot_ui.callback=self.afterrange
        win32gui.SetFocus(self.object.screen_shot_ui.winId() )   
         
        self.object.screen_shot_ui.startauto=auto
        self.object.screen_shot_ui.clickrelease=auto
    def afterrange(self): 
        self.showhide()
        if globalconfig['showrangeafterrangeselect']==False:
            self.showhide()
        if globalconfig['ocrafterrangeselect']:
            self.startTranslater()
    def langdu(self): 
        if self.object.reader:
            self.object.reader.read(self.original )  
    def startTranslater(self) :
        if self.object.textsource :
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
        self._TitleLabel = QLabel(self) 
        self._TitleLabel.setFixedHeight(30*self.rate) 
        self._TitleLabel.setMouseTracking(True) 
        self._TitleLabel.move(0, 0)  
 
    def toolbarhidedelay(self):
        
        for button in self.buttons:
            button.hide()    
        self._TitleLabel.hide()
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
        self._TitleLabel.show()
    def resizeEvent(self, QResizeEvent):
         
         
        height = self.height() - 30*self.rate 
         
        self.translate_text.resize(self.width(), height * self.rate)
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
            if button.belong:
                hide=True
                for k in button.belong:
                    if globalconfig['sourcestatus'][k]:
                        hide=False
                        break
                if hide:
                    button.hide()
                    continue 
            if  button.name in globalconfig['buttonuse'] and globalconfig['buttonuse'][button.name]==False: 
                button.hide()
                continue 

            button.move(showed*button.width() , 0) 
            self.showbuttons.append(button)
            #button.show()
            showed+=1
        self.enterEvent(None)
    def takusanbuttons(self, objectname,clickfunc,adjast=None,tips=None,save=None,belong=None): 
         
        button=QTitleButton(self) 
        if tips: 
            button.setToolTip(_TR(tips) )
        button.setIconSize(QSize(int(20*self.rate),
                                 int(20*self.rate)))
        button.name=save
        button.belong=belong
        button.setObjectName(objectname)
        button.setFixedWidth(40*self.rate)
        button.setMouseTracking(True)
        button.setFixedHeight( self._TitleLabel.height() )
        if clickfunc:
            button.clicked.connect(clickfunc) 
        if adjast<0: 
            button.adjast=lambda  :button.move(self.width() + adjast*button.width() , 0) 
        else:
            button.adjast=None
        self.buttons.append(button) 
        
        if save=='move':
            button.lower() 
     
    def closeEvent(self, a0 ) -> None: 
        self.tray.hide()
        self.tray = None  
        self.hide()
        globalconfig['position']=[self.pos().x(),self.pos().y()]
        
        globalconfig['width']=self.width() 
        globalconfig['height']=self.height() 
        saveallconfig() 
         
        if self.object.textsource:
            self.object.textsource.end()
           
        if self.object.settin_ui.needupdate and globalconfig['autoupdate']: 
            update()
        endsubprocs()
        os._exit(0) 