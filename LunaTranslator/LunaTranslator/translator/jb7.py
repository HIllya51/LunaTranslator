from translator.basetranslator import basetrans 
import ctypes 
import os ,time 
import  win32con ,win32utils
from utils.subproc import subproc_w
class TS(basetrans):  
    def inittranslator(self ) : 
                 
        self.path=None
        self.userdict=None
        self.checkpath()
    def end(self):
        try:
            self.engine.kill()
        except:
            pass
    def checkpath(self):
        if self.config['路径']=="":
            return False
        if os.path.exists(self.config['路径'])==False:
            return False
        if   self.config['路径']!=self.path or self.userdict!=(self.config['用户词典1(可选)'],self.config['用户词典2(可选)'],self.config['用户词典3(可选)']):
            self.path=self.config['路径']
            self.userdict=(self.config['用户词典1(可选)'],self.config['用户词典2(可选)'],self.config['用户词典3(可选)'])
            self.dllpath=os.path.join(self.path,'JBJCT.dll')
            dictpath=''
            for d in self.userdict:
                if os.path.exists(d):
                    d=os.path.join(d,'Jcuser')
                    dictpath+=f' "{d}" '
            
            t=time.time()
            t= str(t) 
            pipename='\\\\.\\Pipe\\jbj7_'+t
            waitsignal='jbjwaitload_'+t

            self.engine=subproc_w(f'./files/plugins/shareddllproxy32.exe jbj7 "{self.dllpath}" {pipename} {waitsignal} '+dictpath,name='jbj7')
            #!!!!!!!!!!!!!!stdout=subprocess.PIPE 之后，隔一段时间之后，exe侧writefile就写不进去了！！！！！不知道为什么！！！
           
            win32utils.WaitForSingleObject(win32utils.CreateEvent(False, False, waitsignal),win32utils.INFINITE); 
            win32utils.WaitNamedPipe(pipename,win32con.NMPWAIT_WAIT_FOREVER)
            self.hPipe = win32utils.CreateFile( pipename, win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                    None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
        return True
    def packuint32(self,i): # int -> str 
        return bytes(chr((i >> 24) & 0xff) + chr((i >> 16) & 0xff) + chr((i >> 8) & 0xff) + chr(i & 0xff),encoding='latin-1')
    def unpackuint32(self,s ): #
        print(s)
        return ( (s[0]) << 24) | ( (s[1]) << 16) | ( (s[2]) << 8) |  (s[3]) 
      
    def x64(self,content:str):   
            if self.tgtlang not in ['936','950']:
                return ''  
            t=time.time()
            if self.checkpath()==False:return 'error'
            content=content.replace('\r','\n')
            lines=content.split('\n')
            ress=[]
            for line in lines: 
                if len(line)==0:continue
                code1=line.encode('utf-16-le') 
                win32utils.WriteFile(self.hPipe,self.packuint32(int(self.tgtlang))+code1) 
                xx=win32utils.ReadFile(self.hPipe, 65535, None)
                xx=xx.decode('utf-16-le',errors='ignore') 
                ress.append(xx)  
            return '\n'.join(ress)
    def x86(self,content):
        CODEPAGE_JA = 932
        CODEPAGE_GB = 936
        CODEPAGE_BIG5 = 950
        BUFFER_SIZE = 3000
        # if globalconfig['fanjian'] in [0,1,4]:
        #     code=CODEPAGE_GB
        # else:
        #     code=CODEPAGE_BIG5
        code=CODEPAGE_GB
            
        size = BUFFER_SIZE 
        out = ctypes.create_unicode_buffer(size) 
        buf = ctypes.create_unicode_buffer(size) 
        outsz = ctypes.c_int(size) 
        bufsz = ctypes.c_int(size) 
        try:
            self.dll.JC_Transfer_Unicode( 0, # int, unknown 
                CODEPAGE_JA    , # uint     from, supposed to be 0x3a4 (cp932) 
                code, # uint to, eighter cp950 or cp932 
                1, # int, unknown 
                1, # int, unknown 
                content, #python 默认unicode 所有不用u'
                out, # wchar_t* 
                ctypes.byref(outsz), # ∫ 
                buf, # wchar_t* 
                ctypes.byref(bufsz)) # ∫ 
        except:
            pass
        return out.value
    def translate(self,content): 
         
            return self.x64(content)
        
    def langmap(self):
        return {"zh":"936","cht":"950"}