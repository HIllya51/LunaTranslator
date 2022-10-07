 
import re
import time
from traceback import print_exc
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
     
    def x64(self,content): 
        try:
            configfile=globalconfig['fanyi'][self.typename]['argsfile']
            
            if os.path.exists(configfile) ==False:
                return ''
            
            with open(configfile,'r',encoding='utf8') as ff:
                js=json.load(ff)
             
            if js['args']['路径']=="":
                return ''
            else:
                path = js['args']['路径'] 
            path=os.path.join(path,'DreyeMT\\SDK\\bin')
            path2=os.path.join(path,"TransCOM.dll")
            ress=''
            for line in content.split('\n'):
                if len(line)==0:
                    continue
                if ress!='':
                    ress+='\n' 
                st=subprocess.STARTUPINFO()
                st.dwFlags=subprocess.STARTF_USESHOWWINDOW
                st.wShowWindow=subprocess.SW_HIDE 


                exec=r'./files/x64_x86_dll/dreyec.exe "'+path+'"  "'+path2+'" '
                
                linebyte=bytes(line,encoding='shift-jis')
                for b in linebyte:
                    exec+=str(b)+' '
                p=subprocess.Popen(exec,stdin=subprocess.PIPE,  stdout=subprocess.PIPE,startupinfo=st,cwd=path)
                l=p.stdout.readline()   
                #print(l)
                
                res=str(l,encoding='gbk',errors='ignore').replace('\r','').replace('\n','') 
                #print(res)
                x=res.split(' ')
                bs=[]
                #print(x)
                for _x in x:
                    try:
                        bs.append(int(_x))
                    except:
                        break
                #print(bs)
                ress+=str(bytes(bs),encoding='gbk')

                #print(1,ress,2)
            #ress=ress.replace('Translation(TaskNo = 1) is OK. (remainder threads = 0)\r\n','')
            return ress 
        except:
            print_exc()
            return ''
    def translate(self,content): 
        return self.x64(content)
         