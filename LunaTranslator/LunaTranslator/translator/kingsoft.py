
from utils.subproc import subproc_w  
from translator.basetranslator import basetrans 
import os  ,time,win32utils,win32con

class TS(basetrans): 
    def inittranslator(self ) : 
        self.path11=None
        self.pair=None
        self.checkpath()
    def end(self):
        try:
            self.engine.kill()
        except:
            pass
    def checkpath(self):
        
        pairs=(self.srclang,self.tgtlang) 
        if   self.config['路径']!=self.path11 or pairs!=self.pair:
            
            base=os.path.join(self.config['路径'],'GTS/'+self.srclang+self.tgtlang)
            if os.path.exists(base)==False:
                return False
            dll=None
            for f in os.listdir(base):
                if f.split('.')[-1]=='dll':
                    dll=f
                    break
            if dll is None:
                return False
            self.path11=self.config['路径']
            self.pair=pairs
            self.path=os.path.join(base,dll)
            self.path2=os.path.join(base,'DCT')

            t=time.time()
            t= str(t) 
            pipename='\\\\.\\Pipe\\ks_'+t
            waitsignal='kswaitload_'+t 
            self.engine=subproc_w(f'./files/plugins/shareddllproxy32.exe kingsoft "{self.path}"  "{self.path2}"   {pipename} {waitsignal} ',name='ks')
            
            win32utils.WaitForSingleObject(win32utils.CreateEvent(False, False, waitsignal),win32utils.INFINITE); 
            win32utils.WaitNamedPipe(pipename,win32con.NMPWAIT_WAIT_FOREVER)
            self.hPipe = win32utils.CreateFile( pipename, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                    None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
        return True
    def x64(self,content):  
            if self.checkpath()==False:return 'error'
            ress=[]
            for line in content.split('\n'):
                if len(line)==0:
                    continue
                win32utils.WriteFile(self.hPipe,line.encode('utf-16-le'))
                x=win32utils.ReadFile(self.hPipe,4096,None)
                ress.append(x.decode('utf-16-le'))
                 
            return '\n'.join(ress )
    def translate(self,content): 
        return self.x64(content)
    def langmap(self):
        return {"zh":"SChinese","cht":"TChinese","en":"English","ja":"Japanese"}