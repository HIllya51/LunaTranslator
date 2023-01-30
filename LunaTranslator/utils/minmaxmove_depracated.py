import os,win32gui,subprocess
from utils.getpidlist import getpidexe

from utils.subproc import subproc
from utils.config import globalconfig
def minmaxmoveobservefunc(self):
        self.minmaxmoveoberve=subproc('./files/minmaxmoveobserve.exe',stdout=subprocess.PIPE,keep=True)  
        self_pid=os.getpid()   
        while(True):
                x=self.minmaxmoveoberve.stdout.readline()
                #print(x)
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
                 
                try:
                    if self.object.textsource.pid: 
                        
                        if pid==self.object.textsource.pid:  
                            if action==1 and globalconfig['movefollow']:
                                    self.movestart=[x1,y1,x2,y2] 
                            elif action==2 and globalconfig['movefollow']: 
                                    moveend=[x1,y1,x2,y2]
                                    self.hookfollowsignal.emit(5,(moveend[0]-self.movestart[0],moveend[1]-self.movestart[1]))
                            elif action==3 and globalconfig['minifollow']: 
                                    self.hookfollowsignal.emit(4,(0,0))
                                    continue
                            elif action==4 and  globalconfig['minifollow']:
                                    self.hookfollowsignal.emit(3,(0,0))
                                    continue
                        # if action==5 and  globalconfig['focusfollow']:   
                        #     if pid==self_pid: 
                        #             self.hookfollowsignal.emit(3,(0,0))  
                        #     elif pid==self.object.textsource.pid: 
                        #             self.hookfollowsignal.emit(3,(0,0))   
                        #     elif pid==self.callmagpie.pid:
                        #             self.hookfollowsignal.emit(3,(0,0))   
                        #     else: 
                        #             try:
                        #                     cn=win32gui.GetClassName(win32gui.GetForegroundWindow()) 
                                            
                        #                     if cn=='Shell_TrayWnd':
                        #                             continue 
                        #                     exe=getpidexe(pid)
                        #                     if os.path.basename(exe).lower()=='magpie.exe':
                        #                             continue
                        #             except:
                        #                     pass
                        #             self.hookfollowsignal.emit(4,(0,0)) 
                except:
                  #print_exc()
                  pass