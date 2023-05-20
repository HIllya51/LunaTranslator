
from utils.subproc import subproc_w       
from translator.basetranslator import basetrans 
import os  ,time,win32utils,win32con

class TS(basetrans): 
    def inittranslator(self ) : 
        self.path=None
        self.pair=None
        self.checkpath()
    def end(self):
        try:
            self.engine.kill()
        except:
            pass
    def checkpath(self):
        if self.config['路径']=="":
            return  False
        if os.path.exists(self.config['路径'])==False:
            return False
        pairs=(self.srclang,self.tgtlang) 
        if   self.config['路径']!=self.path or pairs!=self.pair:
            self.path=self.config['路径']

            self.pair=pairs
            t=time.time()
            t= str(t) 
            pipename='\\\\.\\Pipe\\dreye_'+t
            waitsignal='dreyewaitload_'+t
            mp={('zh','en'):2,('en','zh'):1,('zh','ja'):3,('ja','zh'):10}
            path=os.path.join(self.path,'DreyeMT\\SDK\\bin')
            if mp[pairs] in [3,10]:
                path2=os.path.join(path,'TransCOM.dll')
            else:
                path2=os.path.join(path,'TransCOMEC.dll')
            
            self.engine=subproc_w(f'./files/plugins/shareddllproxy32.exe dreye "{path}"  "{path2}" {str(mp[pairs])} {pipename} {waitsignal} ',name='dreye')
            
            win32utils.WaitForSingleObject(win32utils.CreateEvent(False, False, waitsignal),win32utils.INFINITE); 
            win32utils.WaitNamedPipe(pipename,win32con.NMPWAIT_WAIT_FOREVER)
            self.hPipe = win32utils.CreateFile( pipename, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                    None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
        return True
    def x64(self,content):  
            
            if self.checkpath()==False:return 'error'
            codes={'zh':'gbk','ja':'shift-jis','en':'utf8'}
            ress=[]
            for line in content.split('\n'):
                if len(line)==0:
                    continue
                win32utils.WriteFile(self.hPipe,line.encode(codes[self.srclang])) 
                ress.append(win32utils.ReadFile(self.hPipe,4096,None).decode(codes[self.tgtlang]))
            return '\n'.join(ress)
              
    def translate(self,content): 
        return self.x64(content)
         