
import win32pipe, win32file,win32con,win32security
PIPE_TEXT_EMBED_agent2host="\\\\.\\Pipe\\PIPE_TEXT_EMBED_agent2host"
PIPE_TEXT_EMBED_host2agent="\\\\.\\Pipe\\PIPE_TEXT_EMBED_host2agent" 
from traceback import print_exc
import threading,time ,json
from utils.subproc import subproc
from utils.getpidlist import pid_running
import subprocess,queue,functools
class embedtranslater():
    def __init__(self,pid,waitfortransfunction ,parentgetline  ) -> None:
        def _():
            self.engine=embedtranslater_(waitfortransfunction,parentgetline ) 
            self.engine.parent=self
        t=threading.Thread(target=_)
        t.start()
         
        
        self.proc=subproc('./files/embedded/main.exe '+str(pid),cwd='./files/embedded/' )
        
        #self.proc=subprocess.Popen('C:\\Python27_32\\python.exe -B C:\\Users\\11737\\Documents\\GitHub\\vnr_embedded_translation\\main.py '+str(pid),cwd='C:\\Users\\11737\\Documents\\GitHub\\vnr_embedded_translation')

        t.join()
        self.end()
    def end(self):
        try:
            self.engine.send(json.dumps({"command":"end"}))
        except:
            pass
        self.proc.kill()
class embedtranslater_():
    def __init__(self,waitfortransfunction,parentgetline ) -> None: 
        t1=threading.Thread(target=self._creater1) 
        t2=threading.Thread(target=self._creater2)
        self.waitfortransfunction=waitfortransfunction
        self.parentgetline=parentgetline 
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.donestamp=set()
        t=threading.Thread(target=self._listener)
        t.start()  
        t.join()
    def send(self,s):
        try: 
            print("host send",s)
            win32file.WriteFile(self.pipe_send,s.encode('utf8'))
        except:
            print_exc()
    def _creater1(self):
                self.pipe_get=win32pipe.CreateNamedPipe(PIPE_TEXT_EMBED_agent2host,win32con.PIPE_ACCESS_DUPLEX,win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_READMODE_MESSAGE | win32con.PIPE_WAIT,win32con.PIPE_UNLIMITED_INSTANCES, 0, 0, win32con.NMPWAIT_WAIT_FOREVER, win32security.SECURITY_ATTRIBUTES());
                win32pipe.ConnectNamedPipe(self.pipe_get)  
    def _creater2(self):
                self.pipe_send=win32pipe.CreateNamedPipe(PIPE_TEXT_EMBED_host2agent,win32con.PIPE_ACCESS_DUPLEX,win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_READMODE_MESSAGE | win32con.PIPE_WAIT,win32con.PIPE_UNLIMITED_INSTANCES, 0, 0, win32con.NMPWAIT_WAIT_FOREVER, win32security.SECURITY_ATTRIBUTES());
                win32pipe.ConnectNamedPipe(self.pipe_send)  
                 
    def _listener(self):     
        try:
                while True:
                    rd=win32file.ReadFile(self.pipe_get, 65535, None)[1].decode('utf8',errors='ignore')
                    print('raw',rd)
                    rd=json.loads(rd)
                    print("received",type(rd),rd )
                    if self._onreceive_callback(rd) ==False:
                        break
        except: 
            print_exc()
    
    def embedcallback(self,rd,timestamp,ts):
        if timestamp in self.donestamp:
            return 
        self.donestamp.add(timestamp)
        rd['text']=ts 
        self.send(json.dumps(rd,ensure_ascii=False))
    def _onreceive_callback(self,rd):
        if rd['command']=='trans': 
                self.now_wait_sentence=rd['text']
                t=time.time()
                self.parentgetline(rd['text'])
                self.waitfortransfunction(rd['text'],False,functools.partial(self.embedcallback,rd,t))
                return True
        elif rd['command']=="no_connection":
            return False
        elif rd['command']=="badengine":
            return False 
        elif rd['command']=="disconnect":
            return False