
import win32pipe, win32file,win32con,win32security
PIPE_TEXT_EMBED_agent2host="\\\\.\\Pipe\\PIPE_TEXT_EMBED_agent2host"
PIPE_TEXT_EMBED_host2agent="\\\\.\\Pipe\\PIPE_TEXT_EMBED_host2agent" 
from traceback import print_exc
import threading,time ,json
class embedtranslater():
    def __init__(self) -> None: 
        t1=threading.Thread(target=self._creater1) 
        t2=threading.Thread(target=self._creater2)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        threading.Thread(target=self._listener).start() 
    def send(self,s):
        try: 
            print("send",s)
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
                    print("received",rd )
                    rd=json.loads(rd)
                    
                    if rd['command']=='trans':
                        import random
                        x=list(rd['text'])
                        random.shuffle(x)
                        rd['text']=''.join(x)
                        time.sleep(3)
                        self.send(json.dumps(rd))
                        
        except: 
            print_exc()
embedtranslater()