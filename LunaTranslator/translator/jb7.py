
from utils.subproc import subproc    
from translator.basetranslator import basetrans
import platform 
import ctypes
import re
import os
import json
from utils.config import translatorsetting
import subprocess

class TS(basetrans): 
    # def inittranslator(self ) : 
        
    #     if platform.architecture()[0]=='32bit':
    #         self._x64=False
    #         try:
    #             self.dll=  ctypes.CDLL(self.path)
    #         except:
    #             pass
    #     else:
    #         self._x64=True
    #         self.x64('おはおよう')
    def x64(self,content): 
            js=translatorsetting[self.typename]
            if js['args']['路径']=="":
                return 
            else:
                path = js['args']['路径'] 
    
            self.path=os.path.join(path,'JBJCT.dll')
            ress=''
            for line in content.split('\n'):
                if len(line)==0:
                    continue
                if ress!='':
                    ress+='\n'
                            
                 
                p=subproc(r'./files/x64_x86_dll/jbj7.exe "'+self.path+'" '+self.tgtlang+' "'+line+'"', stdout=subprocess.PIPE )
                
                l=p.stdout.readline() 
                
                res=str(l,encoding='utf8',errors='ignore').replace('\r','').replace('\n','') 
                #print(res)
                x=res.split(' ')
                
                #print(x)
                for _x in x:
                    if _x=='0':
                        break
                    ress+=chr(int(_x))
                    #print(ress)
                #print(l)
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
         
            return self.x64(content)
        
        
          