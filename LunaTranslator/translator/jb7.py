 
import re
import time
from urllib.parse import quote 
from translator.basetranslator import basetrans
import platform 
import ctypes
import re
import os
import json
from utils.config import globalconfig
import subprocess

class TS(basetrans):
    @classmethod
    def defaultsetting(self):
        return {
            "args": {
                "路径": "" 
            } 
        }
    def inittranslator(self ) : 
        configfile=globalconfig['fanyi'][self.typename]['argsfile']
        if os.path.exists(configfile) ==False:
            return 
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        if js['args']['路径']=="":
            return 
        else:
            path = js['args']['路径'] 
  
        self.path=os.path.join(path,'JBJCT.dll')
        if platform.architecture()[0]=='32bit':
            self._x64=False
            try:
                self.dll=  ctypes.CDLL(self.path)
            except:
                pass
        else:
            self._x64=True
            self.x64('おはおよう')
    def x64(self,content):
         
        ress=''
        for line in content.split('\n'):
            if len(line)==0:
                continue
            if ress!='':
                ress+='\n'
                        
            st=subprocess.STARTUPINFO()
            st.dwFlags=subprocess.STARTF_USESHOWWINDOW
            st.wShowWindow=subprocess.SW_HIDE
            
            p=subprocess.Popen(r'./files/jb7x64runner/win32dllforward.exe "'+self.path+'"  "'+line+'"', stdout=subprocess.PIPE,startupinfo=st)
            ress+=str(p.stdout.readline(),encoding='GB2312',errors='ignore')
            
        ress=ress.replace('Translation(TaskNo = 1) is OK. (remainder threads = 0)\r\n','')
        return ress
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
        if self._x64:
            return self.x64(content)
        else:
            return self.x86(content)
        
          