 
from cmath import exp
import functools
from PyQt5.QtWidgets import  QWidget,QLabel 
from PyQt5.QtCore import QThread
import subprocess
from utils.config import globalconfig 
import threading
import json
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
import os
import win32con,win32api,win32process,win32gui
self_pid=os.getpid()
st=subprocess.STARTUPINFO()
st.dwFlags=subprocess.STARTF_USESHOWWINDOW
st.wShowWindow=subprocess.SW_HIDE
def setTab4(self) :
     
        self.tab_4 = QWidget()
        self.tab_widget.addTab(self.tab_4, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_4), " 其他设置")
 
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 20, 200, 20)
        label.setText("textractor模式特殊设置")

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 50, 200, 20)
        label.setText("游戏最小化时窗口隐藏")
        self.minifollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['minifollow'],textOff='关闭',textOn='使用')
        self.customSetGeometry(self.minifollowswitch, 200, 50, 20,20)
        self.minifollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('minifollow',x)) 

        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 80, 200, 20)
        label.setText("游戏窗口移动时同步移动")
        
        self.movefollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['movefollow'],textOff='关闭',textOn='使用')
        self.customSetGeometry(self.movefollowswitch, 200, 80,20,20)
        self.movefollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('movefollow',x)) 
        
        
        label = QLabel(self.tab_4)
        self.customSetGeometry(label, 20, 110, 200, 20)
        label.setText("检测到游戏时自动开始")
        
        self.movefollowswitch =gui.switchbutton.MySwitch(self.tab_4, sign= globalconfig['autostarthook'],textOff='关闭',textOn='使用')
        self.customSetGeometry(self.movefollowswitch, 200, 110,20,20)
        self.movefollowswitch.clicked.connect(lambda x:globalconfig.__setitem__('autostarthook',x)) 
        
        # label = QLabel(self.tab_4)
        # self.customSetGeometry(label, 20, 110, 200, 20)
        # #label.setText("窗口失去焦点不再置顶")
        # label.setText("窗口失去焦点最小化")
        # self.focusfollowswitch =gui.switch.SwitchButton(self.tab_4, sign= globalconfig['focusfollow'], startX=(65-20)*self.rate,textOff='关闭',textOn='使用')
        # self.customSetGeometry(self.focusfollowswitch, 200,110, 65, 20)
        # self.focusfollowswitch.checkedChanged.connect(lambda x:globalconfig.__setitem__('focusfollow',x)) 
        # #self.focusfollowswitch.checkedChanged.connect(lambda x:setss(self,x)) 
        self.hookpid=None
        self.minmaxmoveoberve=subprocess.Popen('./files/minmaxmoveobserve.exe',stdout=subprocess.PIPE,startupinfo=st)
        self.minmaxmoveobservethread=threading.Thread(target=minmaxmoveobservefunc,args=(self,))
        self.minmaxmoveobservethread.start()

        self.autostarthooksignal.connect(functools.partial(autostarthookfunction,self))
def autostarthookfunction(self,pid,pname,hookcode):
        try:
                process=win32api.OpenProcess(2097151,False, pid) #PROCESS_ALL_ACCESS
        except  : 
                return
        
        arch='86' if win32process.IsWow64Process( process)  else '64' 
         
        self.hookpid=pid
        from textsource.textractor import textractor
        self.hookselectdialog.changeprocessclearsignal.emit()
        
        self.object.textsource=textractor(self.object.textgetmethod,self.hookselectdialog,pid,pname,arch) 
        self.object.textsource.autostart=True
        self.object.textsource.autostarthookcode=hookcode[-1]
        x=subprocess.run(f'./files/hookcodecheck.exe {hookcode}',stdout=subprocess.PIPE)
        #print(hookcode,x.stdout[0])
        if(x.stdout[0]==ord('1')):
            
                self.object.textsource.inserthook(hookcode[-1] )
        
def getwindowlist():
        windows_list=[]
        pidlist=[]
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), windows_list)
        for hwnd in windows_list:
                try:
                        tid, pid=win32process.GetWindowThreadProcessId(hwnd) 
                        pidlist.append(pid)
                except:
                        pass
        return pidlist
def minmaxmoveobservefunc(self):
        while(True):
                x=self.minmaxmoveoberve.stdout.readline()
                if globalconfig['sourcestatus']['textractor']==False:
                        continue
                x=str(x,encoding='utf8')
                x=x.replace('\r','').replace('\n','')
                 
                x=x.split(' ')
                 
                if len(x) not in [2,6]:
                        break
                x=[int(_) for _ in x]
                if len(x)==2:
                        pid,action=x
                elif len(x)==6:
                        pid,action,x1,y1,x2,y2=x
                
                if self.hookpid:
                      
                     if pid==self_pid:
                            continue
                     plist=getwindowlist()
                     if self.hookpid not in plist:
                            #print('game exit')
                            self.hookpid=None
                            self.object.textsource=None
                            continue
                     if pid==self.hookpid: 
                        if action==1 and globalconfig['movefollow']:
                                self.movestart=[x1,y1,x2,y2]
                                
                        elif action==2 and globalconfig['movefollow']: 
                                moveend=[x1,y1,x2,y2]
                                self.object.translation_ui.hookfollowsignal.emit(5,(moveend[0]-self.movestart[0],moveend[1]-self.movestart[1]))
                        elif action==3 and globalconfig['minifollow']: 
                                self.object.translation_ui.hookfollowsignal.emit(4,(0,0))
                        elif action==4 and  globalconfig['minifollow']:
                                self.object.translation_ui.hookfollowsignal.emit(3,(0,0))
                #         elif action==5 and globalconfig['minifollow']:
                #                 self.object.translation_ui.hookfollowsignal.emit(3,(0,0))
                #      else:
                #         if action==5 and globalconfig['minifollow']:
                #             self.object.translation_ui.hookfollowsignal.emit(4,(0,0))

                if globalconfig['autostarthook'] and action==5:
                        if globalconfig['sourcestatus']['textractor']==False:
                                continue 
                        if  os.path.exists('./files/savehook.json'):
                                if 'textsource' not in dir(self.object) or self.object.textsource is None:
                                        with open('./files/savehook.json','r',encoding='utf8') as ff:
                                                js=json.load(ff)
                                        try:
                                                hwnd=win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,False, (pid))
                                                name_=win32process.GetModuleFileNameEx(hwnd,None)
                                        except:
                                                continue
                                        if name_ in js:
                                                        
                                                self.autostarthooksignal.emit(pid,name_,tuple(js[name_]))