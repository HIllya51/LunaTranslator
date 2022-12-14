
from utils.subproc import subproc  
from translator.basetranslator import basetrans 
import os
import json
from utils.config import translatorsetting
import subprocess

class TS(basetrans): 
    def x64(self,content): 
            js=translatorsetting[self.typename]
            if js['args']['路径']=="":
                return 
            else:
                path = js['args']['路径'] 
            base=os.path.join(path,'GTS/'+self.srclang+self.tgtlang)
            if os.path.exists(base)==False:
                return 
            dll=None
            for f in os.listdir(base):
                if f.split('.')[-1]=='dll':
                    dll=f
                    break
            if dll is None:
                return 
            self.path=os.path.join(base,dll)
            self.path2=os.path.join(base,'DCT')
            ress=''
            for line in content.split('\n'):
                if len(line)==0:
                    continue
                if ress!='':
                    ress+='\n'
                             
                p=subproc(r'./files/x64_x86_dll/ks.exe "'+self.path+'"  "'+self.path2+'"  "'+line+'"', stdout=subprocess.PIPE )
                l=p.stdout.readline()  
                 
                res=str(l,encoding='utf8',errors='ignore')
                #print(res)
                x=res.split(' ')
                #print(x)
                #print(x)
                for _x in x:
                    if _x=='0':
                        break
                    ress+=chr(int(_x)).replace('\r','').replace('\n','') 
                #ress+=str(l,encoding='utf16',errors='ignore').replace('\r','').replace('\n','')
                #print(1,ress,2)
            #ress=ress.replace('Translation(TaskNo = 1) is OK. (remainder threads = 0)\r\n','')
            return ress 
    def translate(self,content): 
        return self.x64(content)
         