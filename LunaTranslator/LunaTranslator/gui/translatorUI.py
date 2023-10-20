
import time 
import functools   
import threading 
import os,sys
import winsharedutils
from PyQt5.QtCore import QT_VERSION_STR

from traceback import print_exc
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout,QApplication
from PyQt5.QtCore import Qt, pyqtSignal  ,QThread
import qtawesome 
from PyQt5.QtCore import pyqtSignal,Qt,QRect,QSize  
from PyQt5.QtGui import  QFont  ,QIcon,QPixmap  ,QMouseEvent,QCursor
from PyQt5.QtWidgets import  QLabel ,QPushButton ,QSystemTrayIcon ,QAction,QMenu 
import win32utils,gobject
from myutils.wrapper import threader
import winsharedutils,queue
from myutils.config import globalconfig,saveallconfig,_TR
from myutils.subproc import endsubprocs
from myutils.ocrutil import ocr_run,imageCut
import  win32con
from myutils.hwnd import mouseselectwindow ,showintab,getScreenRate,grabwindow,getExeIcon
from gui.dialog_savedgame import dialog_savedgame,dialog_savedgame_new
from gui.dialog_memory import dialog_memory
from gui.textbrowser import Textbrowser
from myutils.fullscreen import fullscreen
from gui.rangeselect  import moveresizegame ,rangeselct_function
from gui.usefulwidget import resizableframeless
class QUnFrameWindow(resizableframeless):   
    displayres =  pyqtSignal(str,str,str ,bool) 
    displayraw1 =  pyqtSignal(list, str,str,bool )  
    displaystatus=pyqtSignal(str,str,bool) 
    showhideuisignal=pyqtSignal()
    hookfollowsignal=pyqtSignal(int,tuple)
    toolbarhidedelaysignal=pyqtSignal() 
    showsavegame_signal=pyqtSignal(int) 
    clickRange_signal=pyqtSignal(bool)
    showhide_signal=pyqtSignal()
    bindcropwindow_signal=pyqtSignal()
    fullsgame_signal=pyqtSignal()
    quitf_signal=pyqtSignal() 
    refreshtooliconsignal=pyqtSignal()
    hidesignal=pyqtSignal()
    muteprocessignal=pyqtSignal()   
    entersignal=pyqtSignal()
    def hookfollowsignalsolve(self,code,other): 
        if self._move_drag:
            return 
        if code==3:
            if self.hideshownotauto:
                self.show_()
                try:
                    _h=win32utils.GetForegroundWindow()
                    _fpid=win32utils.GetWindowThreadProcessId(_h)
                    _hpid=win32utils.GetWindowThreadProcessId(other[0])
                    if _fpid!=_hpid:
                        win32utils.SetForegroundWindow(other[0])
                except:
                    pass
        elif code==4: 
            if self.hideshownotauto:
                self.hide_()
        elif code==5:
            #print(self.pos())
            #self.move(self.pos() + self._endPos)z
            try:
                gobject.baseobject.textsource.moveui(other[0],other[1])
            except:
                pass
            self.move(self.pos().x()+ other[0],self.pos().y()+ other[1])
            #self.move(self.pos().x()+self.rate *other[0],self.pos().y()+self.rate *other[1])
        
    def showres(self,name,color,res,onlyshowhist):  
        try:
            gobject.baseobject.transhis.getnewtranssignal.emit(name,res)
            if onlyshowhist:
                return 
            clear=name==''
            if globalconfig['showfanyisource']:
                #print(_type)
                #self.showline((None,globalconfig['fanyi'][_type]['name']+'  '+res),globalconfig['fanyi'][_type]['color']  )
                self.showline(clear,[None,name+'  '+res],color ,1,False )
            else:
                #self.showline((None,res),globalconfig['fanyi'][_type]['color']  )
                self.showline(clear,[None,res],color  ,1,False)
            #print(globalconfig['fanyi'][_type]['name']+'  '+res+'\n')
            
            
        except:
            print_exc() 
    def showraw(self,hira,res,color ,onlyshowhist): 
        #print(res,onlyshowhist)
        gobject.baseobject.transhis.getnewsentencesignal.emit(res) 
        if onlyshowhist:
            return 
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
            self.showline(True,[hira,res],color , 2 )
        elif globalconfig['isshowrawtext']:
            self.showline(True,[hira,res],color,1)
        else:
            self.showline(True,None,None,1) 
        
        gobject.baseobject.edittextui.getnewsentencesignal.emit(res)  
    def showstatus(self,res,color,clear): 
        self.showline(clear,[None,res],color,1)
    def showline (self,clear,res,color ,type_=1,origin=True):   
        if clear:
            self.translate_text.clear()
        self.translate_text.setnextfont(origin)
        if res is None:
            return 
        if globalconfig['showatcenter']:
            self.translate_text.setAlignment(Qt.AlignCenter)
        else:
            self.translate_text.setAlignment(Qt.AlignLeft)

        
        if globalconfig['zitiyangshi'] ==2: 
            self.translate_text.mergeCurrentCharFormat_out(globalconfig['miaobiancolor'],color, globalconfig['miaobianwidth2']) 
        elif globalconfig['zitiyangshi'] ==4: 
            self.translate_text.mergeCurrentCharFormat_out(color,globalconfig['miaobiancolor'], globalconfig['miaobianwidth2']) 
        elif globalconfig['zitiyangshi'] ==1:  
            self.translate_text.mergeCurrentCharFormat( color, globalconfig['miaobianwidth']) 
        elif globalconfig['zitiyangshi'] ==0: 
            self.translate_text.simplecharformat(color)
        elif globalconfig['zitiyangshi'] ==3: 
            self.translate_text.simplecharformat(color)  
        if type_==1: 
            self.translate_text.append (res[1],[],origin) 
        else:   
            self.translate_text.append (res[1],res[0],origin)    
        if globalconfig['zitiyangshi'] ==3:
            self.translate_text.showyinyingtext(color  ) 
        if (globalconfig['usesearchword'] or globalconfig['usecopyword'] or globalconfig['show_fenci']  ) and res[0]:
            def callback(word):
                if globalconfig['usecopyword'] :
                    winsharedutils.clipboard_set(word)
                if globalconfig['usesearchword']:
                    gobject.baseobject.searchwordW.getnewsentencesignal.emit(word)
            self.translate_text.addsearchwordmask(res[0],res[1],callback   ) 
        
        
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
        self.show_()
     
    def refreshtoolicon(self):

        iconstate = {'fullscreen': self.isletgamefullscreened, "muteprocess": self.processismuteed, "locktoolsbutton":
                     globalconfig['locktools'], "showraw": globalconfig['isshowrawtext'], "automodebutton": globalconfig['autorun']}
        colorstate = {"automodebutton": globalconfig['autorun'], "showraw": globalconfig['isshowrawtext'], "mousetransbutton": self.mousetransparent, "backtransbutton": self.backtransparent,
                      "locktoolsbutton": globalconfig['locktools'], "hideocrrange": self.showhidestate, "bindwindow": self.isbindedwindow, "keepontop": globalconfig['keepontop']}
        onstatecolor="#FF69B4"
         
        self._TitleLabel.setFixedHeight(globalconfig['buttonsize']*1.5*self.rate)  
        for i in range(len(self.buttons)):
            name=self.buttons[i].name
            if name in colorstate:
                color=onstatecolor if colorstate[name] else globalconfig['buttoncolor']
            else:
                color=globalconfig['buttoncolor']
            if name in iconstate:
                icon=globalconfig['toolbutton']['buttons'][name]['icon'] if iconstate[name] else globalconfig['toolbutton']['buttons'][name]['icon2']
            else:
                icon=globalconfig['toolbutton']['buttons'][name]['icon']
            self.buttons[i].setIcon(qtawesome.icon(icon,color=color))#(icon[i])
            self.buttons[i].resize(globalconfig['buttonsize']*2 *self.rate,globalconfig['buttonsize']*1.5*self.rate)
        
            if self.buttons[i].adjast:
                self.buttons[i].adjast()
            self.buttons[i].setIconSize(QSize(int(globalconfig['buttonsize']*self.rate),
                                 int(globalconfig['buttonsize']*self.rate)))
        self.showhidetoolbuttons()
        self.translate_text.movep(0,globalconfig['buttonsize']*1.5*self.rate)
        self.textAreaChanged()
        self.setMinimumHeight(globalconfig['buttonsize']*1.5*self.rate+10)
        self.setMinimumWidth(globalconfig['buttonsize']*2*self.rate)
    def addbuttons(self):
        def simulate_key_enter():
            win32utils.SetForegroundWindow(gobject.baseobject.textsource.hwnd)
            time.sleep(0.1)
            while win32utils.GetForegroundWindow()==gobject.baseobject.textsource.hwnd:
                time.sleep(0.001)
                win32utils.keybd_event(13,0,0,0)
            win32utils.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0)
        def simulate_key_ctrl():
            win32utils.SetForegroundWindow(gobject.baseobject.textsource.hwnd)
            time.sleep(0.1)
            win32utils.keybd_event(17,0,0,0) 
            while win32utils.GetForegroundWindow()==gobject.baseobject.textsource.hwnd:
                time.sleep(0.001)
            win32utils.keybd_event(17,0,win32con.KEYEVENTF_KEYUP,0)
        @threader
        def ocroncefunction(rect):
            img=imageCut(0,rect[0][0],rect[0][1],rect[1][0],rect[1][1]) 
            fname='./cache/ocr/once.png' 
            img.save(fname)
            text=ocr_run(fname)
            gobject.baseobject.textgetmethod(text,False)
        functions=(
            ("move",None),
            ("retrans",self.startTranslater),
            ("automodebutton",self.changeTranslateMode),
            ("setting",lambda:gobject.baseobject.settin_ui.showsignal.emit()),
            ("copy",lambda:winsharedutils.clipboard_set( gobject.baseobject.currenttext)),
            ("edit",lambda: gobject.baseobject.edittextui.showsignal.emit()),
            ("showraw",self.changeshowhideraw),
            ("history",lambda: gobject.baseobject.transhis.showsignal.emit() ),
            ("noundict",lambda: gobject.baseobject.settin_ui.button_noundict.click()),
            ("fix",lambda: gobject.baseobject.settin_ui.button_fix.click()),
            ("langdu",self.langdu),
            ("mousetransbutton",lambda: self.changemousetransparentstate(0)),
            ("backtransbutton",lambda:self.changemousetransparentstate(1)),
            ("locktoolsbutton",self.changetoolslockstate),
            ("gamepad",lambda: dialog_savedgame(gobject.baseobject.settin_ui)),
            ("gamepad_new",lambda: dialog_savedgame_new(gobject.baseobject.settin_ui)),
            ("selectgame",lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit()),
            ("selecttext",lambda:gobject.baseobject.hookselectdialog.showsignal.emit()),
            ("selectocrrange",lambda :self.clickRange(False)),
            ("hideocrrange",self.showhide),
            ("bindwindow",self.bindcropwindow_signal.emit),
            ("resize",lambda :moveresizegame(self,gobject.baseobject.textsource.hwnd) if gobject.baseobject.textsource.hwnd else 0),
            ("fullscreen",self._fullsgame),
            ("grabwindow",lambda:grabwindow()),
            ("muteprocess",self.muteprocessfuntion),
            ("memory",lambda: dialog_memory(gobject.baseobject.settin_ui,gobject.baseobject.currentmd5)),
            ("keepontop",lambda:globalconfig.__setitem__("keepontop",not globalconfig['keepontop']) is None and self.refreshtoolicon() is None and self.setontopthread()),
            ("simulate_key_ctrl",lambda:threading.Thread(target=simulate_key_ctrl).start()),
            ("simulate_key_enter",lambda:threading.Thread(target=simulate_key_enter).start() ),
            ("copy_once",lambda:gobject.baseobject.textgetmethod(winsharedutils.clipboard_get(),False) ),
            
            ("ocr_once",lambda:rangeselct_function(self,ocroncefunction,False,False) ),
            ("minmize",self.hide_and_disableautohide),
            ("quit",self.close)
        )
        adjast={"minmize":-2,"quit":-1}
        _type={"quit":2}

        for btn,func in functions:
            belong=globalconfig['toolbutton']['buttons'][btn]['belong'] if 'belong' in globalconfig['toolbutton']['buttons'][btn] else None
            _adjast=adjast[btn] if btn in adjast else 0
            tp=_type[btn] if btn in _type else 1
            self.takusanbuttons(tp,func,_adjast,globalconfig['toolbutton']['buttons'][btn]['tip'],btn,belong)
               
    def hide_(self):  
        if self.showintab: 
            win32utils.ShowWindow(self.winId(),win32con.SW_SHOWMINIMIZED )
        else:
            self.hide()
    def show_(self):   
        if self.showintab:
            win32utils.ShowWindow(self.winId(),win32con.SW_SHOWNOACTIVATE )
        else:
            self.show()
        win32utils.SetForegroundWindow(self.winId())
    def showEvent(self, a0 ) -> None: 
        if self.isfirstshow:
            self.showline(True,[None,_TR('欢迎使用')],'',1,False)
            
            
            showAction = QAction(_TR("&显示"), self, triggered = self.show_and_enableautohide)
            settingAction = QAction(_TR("&设置"), self, triggered = lambda: gobject.baseobject.settin_ui.showsignal.emit())
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
            win32utils.SetForegroundWindow(self.winId())
            self.isfirstshow=False 
            self.setontopthread()
        return super().showEvent(a0)
    def canceltop(self,hwnd=win32con.HWND_NOTOPMOST):
        win32utils.SetWindowPos(int(self.winId()), hwnd, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE) 
    def settop(self):
        win32utils.SetWindowPos(int(self.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con. SWP_NOACTIVATE |win32con. SWP_NOSIZE | win32con.SWP_NOMOVE)  
    def setontopthread(self):
        def _():
            self.settop()
            while globalconfig['keepontop']:
                
                try:   
                    hwnd=win32utils.GetForegroundWindow()
                    pid=win32utils.GetWindowThreadProcessId(hwnd)
                    if pid ==os.getpid():
                        pass
                    elif (globalconfig['focusnotop']):
                        try:
                            if gobject.baseobject.textsource.hwnd in [0,hwnd] :
                                self.settop()
                        except:
                            self.settop()
                    else:
                        self.settop() 
                except:
                    print_exc() 
                time.sleep(0.5)            
            self.canceltop()
        
        threading.Thread(target=_).start()
    def __init__(self):
        
        super(QUnFrameWindow, self).__init__(
            None,flags= Qt.FramelessWindowHint|Qt.WindowMinimizeButtonHint,dic=globalconfig,key='transuigeo')  # 设置为顶级窗口，无边框
        icon =getExeIcon(sys.argv[0])#'./LunaTranslator.exe')# QIcon()
        #icon.addPixmap(QPixmap('./files/luna.png'), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)
        self.tray = QSystemTrayIcon()  
        self.tray.setIcon(icon) 
        showintab(self.winId(),globalconfig['showintab']) 
        self.isfirstshow=True
        if QT_VERSION_STR!='5.5.1':
            self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setAttribute(Qt.WA_ShowWithoutActivating,True)
        self.showintab=  globalconfig['showintab'] 
        self.setWindowTitle('LunaTranslator')
        self.hidesignal.connect(self.hide_)
        self.lastrefreshtime=time.time()
        self.autohidestart=False
        threading.Thread(target=self.autohidedelaythread).start()
        self.rate = getScreenRate()
        self.muteprocessignal.connect(self.muteprocessfuntion) 
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)
        
         
        self.hideshownotauto=True
        self.entersignal.connect(self.enterfunction)
        self.displaystatus.connect(self.showstatus)
        self.showhideuisignal.connect(self.showhideui)
        self.hookfollowsignal.connect(self.hookfollowsignalsolve) 
        self.displayres.connect(self.showres)
        self.displayraw1.connect(self.showraw)   
        self.refreshtooliconsignal.connect(self.refreshtoolicon)
        self.showsavegame_signal.connect(self.showsavegame_f)  
        self.clickRange_signal.connect(self.clickRange )
        self.showhide_signal.connect(self.showhide )
        self.bindcropwindow_signal.connect(functools.partial(mouseselectwindow, self.bindcropwindowcallback))
        self.quitf_signal.connect(self.close)
        self.fullsgame_signal.connect(self._fullsgame) 
        
        self.isletgamefullscreened=False
        self.fullscreenmanager=fullscreen(self._externalfsend)
        self._isTracking=False
        self.isontop=True  
        self._TitleLabel = QLabel(self)   
        self._TitleLabel.move(0, 0)  
        self.showhidestate=False
        self.processismuteed=False
        self.mousetransparent=False
        self.backtransparent=False
        self.isbindedwindow=False
        self.buttons=[] 
        self.showbuttons=[] 
        self.addbuttons() 
         
        
        self.translate_text =  Textbrowser(self)  
         
        
        
        # 翻译框根据内容自适应大小
        self.document = self.translate_text.document()
        
        self.document.contentsChanged.connect(self.textAreaChanged)  
        self.set_color_transparency() 
        self.refreshtoolicon()
    def showsavegame_f(self,i):
        if i==0:
            dialog_savedgame(gobject.baseobject.settin_ui)
        else:
            dialog_savedgame_new(gobject.baseobject.settin_ui)
        
    def set_color_transparency(self ):
        self.translate_text.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']*(not self.backtransparent)/100))
        self._TitleLabel.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                           font-weight: bold;\
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(int(globalconfig['backcolor'][1:3],16),int(globalconfig['backcolor'][3:5],16),int(globalconfig['backcolor'][5:7],16),globalconfig['transparent']/200))
    
    def muteprocessfuntion(self): 
        if gobject.baseobject.textsource and gobject.baseobject.textsource.pids :
            self.processismuteed=not self.processismuteed
            self.refreshtoolicon()
            for pid in gobject.baseobject.textsource.pids:
                winsharedutils.SetProcessMute(pid,self.processismuteed)
        
    def _externalfsend(self):
        self.isletgamefullscreened=False
        self.refreshtooliconsignal.emit()
    def _fullsgame(self): 
        if gobject.baseobject.textsource and  gobject.baseobject.textsource.hwnd:
            _hwnd=gobject.baseobject.textsource.hwnd
        else:
            _hwnd=win32utils.GetForegroundWindow()
            _pid=win32utils.GetWindowThreadProcessId(_hwnd) 
            if _pid ==os.getpid():return 
        self.isletgamefullscreened=not self.isletgamefullscreened
        self.refreshtoolicon()
        self.fullscreenmanager(_hwnd,self.isletgamefullscreened) 
     
    def changemousetransparentstate(self,idx): 
        if idx==0:  
            self.mousetransparent= not self.mousetransparent
        elif idx==1:
            self.backtransparent=not self.backtransparent
        
        
        
        def _checkplace():
            hwnd =int(self.winId())
            while self.mousetransparent: 
                cursor_pos = self.mapFromGlobal(QCursor.pos()) 
                 
                if self.isinrect(cursor_pos,[self._TitleLabel.x(),self._TitleLabel.x()+self._TitleLabel.width(),self._TitleLabel.y(),self._TitleLabel.y()+self._TitleLabel.height()]): 
                    
                    win32utils.SetWindowLong(self.winId(), win32con.GWL_EXSTYLE, win32utils.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) &~ win32con.WS_EX_TRANSPARENT)
                else:  
                    win32utils.SetWindowLong(self.winId(), win32con.GWL_EXSTYLE, win32utils.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT)
                if self.isinrect(cursor_pos,[self._TitleLabel.x(),self._TitleLabel.x()+self._TitleLabel.width(),self._TitleLabel.y(),self._TitleLabel.y()+self._TitleLabel.height()+self._padding]): 
                    self.entersignal.emit()
                time.sleep(0.1) 
            #结束时取消穿透(可能以快捷键终止)
            win32utils.SetWindowLong(self.winId(), win32con.GWL_EXSTYLE, win32utils.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) &~ win32con.WS_EX_TRANSPARENT)
        if self.mousetransparent:
                #globalconfig['locktools']=True #锁定，否则无法恢复。
                threading.Thread(target=_checkplace).start()
        self.set_color_transparency()
        self.refreshtoolicon()
    def showhide(self): 
        if gobject.baseobject.textsource.rect:
            self.showhidestate=not self.showhidestate 
            self.refreshtoolicon()
            gobject.baseobject.textsource.showhiderangeui(self.showhidestate) 
    def bindcropwindowcallback(self,pid,hwnd): 
            _pid=os.getpid()
            gobject.baseobject.textsource.hwnd= hwnd if pid!=_pid else None
            if not globalconfig['sourcestatus2']['texthook']['use'] :
                gobject.baseobject.textsource.pids= [pid] if pid!=_pid else None
            self.isbindedwindow=(pid!=_pid)
            self.refreshtoolicon()  
    def changeshowhideraw(self):
        gobject.baseobject.settin_ui.show_original_switch.click()
        
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
        self.resize(width, 5+newHeight + globalconfig['buttonsize']*1.5*self.rate) 
       
        
    def clickRange(self,auto): 
        if globalconfig['sourcestatus2']['ocr']['use']==False:
            return 
        self.showhidestate=False
        
        rangeselct_function(self,self.afterrange,auto,auto)
         
    def afterrange(self,rect): 
        gobject.baseobject.textsource.setrect(rect)
        self.showhide()
        if globalconfig['showrangeafterrangeselect']==False:
            self.showhide()
        if globalconfig['ocrafterrangeselect']:
            self.startTranslater()
    def langdu(self): 
        gobject.baseobject.readcurrent(force=True)
    def startTranslater(self) :
        if gobject.baseobject.textsource :
            threading.Thread(target=gobject.baseobject.textsource.runonce).start()
         
    def toolbarhidedelay(self):
        
        for button in self.buttons:
            button.hide()    
        self._TitleLabel.hide()
     
        
    def enterEvent(self, QEvent) : 
        self.enterfunction()
    def enterfunction(self) : 
         
 
        for button in self.buttons[-2:] +self.showbuttons:
            button.show()  
        self._TitleLabel.show()

        if globalconfig['locktools']:
            return 
        def makerect(_):
            x,y,w,h=_
            return [x,x+w,y,y+h]
        def __(s):
            c=QCursor()  
            while (self.isinrect(c.pos(),makerect(self.geometry().getRect()))):
                time.sleep(0.1)
            time.sleep(0.5)
            if (globalconfig['locktools']==False) and (self.isinrect(c.pos(),makerect(self.geometry().getRect()))==False):
                s.toolbarhidedelaysignal.emit()
        threading.Thread(target=lambda:__(self) ).start()
    def resizeEvent(self, e):
        super().resizeEvent(e);
        wh=globalconfig['buttonsize'] *1.5
        height = self.height() - wh *self.rate 
         
        self.translate_text.resize(self.width()-5, height * self.rate)
        for button in self.buttons[-2:]:
              button.adjast( ) 
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width())  

    def showhidetoolbuttons(self):
        showed=0
        self.showbuttons=[] 
        
        for i,button in enumerate(self.buttons[:-2]):
            if button.belong:
                hide=True
                for k in button.belong:
                    if k in globalconfig['sourcestatus2'] and globalconfig['sourcestatus2'][k]['use']:
                        hide=False
                        break
                if hide:
                    button.hide()
                    continue 
            if  button.name in globalconfig['toolbutton']['buttons'] and globalconfig['toolbutton']['buttons'][button.name]['use']==False: 
                button.hide()
                continue 

            button.move(showed*button.width() , 0) 
            self.showbuttons.append(button)
            #button.show()
            showed+=1
        self.enterEvent(None)
    def callwrap(self,call,_):
            try: 
                call( )
            except:
                print_exc()
    def takusanbuttons(self, _type,clickfunc,adjast=None,tips=None,save=None,belong=None): 
         
        button=QPushButton(self) 
        if tips: 
            button.setToolTip(_TR(tips) )
         

        style='''
        QPushButton{
          background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;
      }
       
        '''
        if _type==1:
            style+='''
            QPushButton:hover{
           background-color: %s;
           border: 0px;
           font: 100 10pt;
            }'''%globalconfig['button_color_normal']
        elif _type==2:
            style+='''
             QPushButton:hover{
           background-color: %s;
           color: white;
           border: 0px;
           font: 100 10pt;
       }'''%(globalconfig['button_color_close'])
        


        button.setStyleSheet(style)
 
        
        if clickfunc:
            button.clicked.connect(functools.partial(self.callwrap,clickfunc)) 
        else:
            button.lower()
        
        button.name=save
        button.belong=belong
        if adjast<0: 
            button.adjast=lambda  :button.move(self.width() + adjast*button.width() , 0) 
        else:
            button.adjast=None
        self.buttons.append(button) 
         

    def closeEvent(self, a0 ) -> None: 
        gobject.baseobject.isrunning=False
        self.tray.hide()
        self.tray = None  
        self.hide()
        saveallconfig() 
         
        if gobject.baseobject.textsource:
            
            gobject.baseobject.textsource=None
        
        
        endsubprocs()
        os._exit(0) 