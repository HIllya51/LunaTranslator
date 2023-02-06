
import win32pipe, win32file,win32con,win32security
PIPE_TEXT_EMBED_agent2host="\\\\.\\Pipe\\PIPE_TEXT_EMBED_agent2host"
PIPE_TEXT_EMBED_host2agent="\\\\.\\Pipe\\PIPE_TEXT_EMBED_host2agent" 
from traceback import print_exc
import threading,time ,json
from utils.subproc import subproc
import subprocess,queue,functools
class embedtranslater():
    def __init__(self,pid,waitfortransfunction ,parentgetline ,callfornoconnect) -> None:
        def _():
            self.engine=embedtranslater_(waitfortransfunction,parentgetline,callfornoconnect) 
        t=threading.Thread(target=_)
        t.start()
         
        
        #self.proc=subprocess.Popen('./files/embedded/main.exe '+str(pid),cwd='./files/embedded/')
        
        self.proc=subprocess.Popen('C:\\Python27_32\\python.exe -B C:\\Users\\11737\\Documents\\GitHub\\vnr_embedded_translation\\main.py '+str(pid),cwd='C:\\Users\\11737\\Documents\\GitHub\\vnr_embedded_translation')
        t.join()
    def end(self):
        self.engine.send(json.dumps({"commmand":"end"}))
        self.proc.kill()
class embedtranslater_():
    def __init__(self,waitfortransfunction,parentgetline,callfornoconnect) -> None: 
        t1=threading.Thread(target=self._creater1) 
        t2=threading.Thread(target=self._creater2)
        self.waitfortransfunction=waitfortransfunction
        self.parentgetline=parentgetline
        self.callfornoconnect=callfornoconnect
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.donestamp=set()
        threading.Thread(target=self._listener).start()  
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
                    self._onreceive_callback(rd) 
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
        elif rd['command']=="no_connection":
            print("embed failt")
            self.callfornoconnect()

if __name__=='__main__':
    threading.Thread(target=lambda: embedtranslater()).start() 
    import subprocess 
    subprocess.Popen('./files/embedded/main.exe 4660',cwd='./files/embedded/')