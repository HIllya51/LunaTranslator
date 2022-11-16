
from utils.subproc import subproc       
from translator.basetranslator import basetrans
import platform 
import ctypes
import re
import os
import json
from utils.config import globalconfig,translatorsetting
import subprocess

class TS(basetrans): 
     
    def x64(self,content): 
        
            js=translatorsetting[self.typename]
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

                exec=r'./files/x64_x86_dll/dreyec.exe "'+path+'"  "'+path2+'" '
                
                linebyte=bytes(line,encoding='shift-jis')
                for b in linebyte:
                    exec+=str(b)+' '
                p=subproc(exec,stdin=subprocess.PIPE,  stdout=subprocess.PIPE ,cwd=path)
                l=p.stdout.readline()   
                #print(l)
                
                res=str(l,encoding='utf8',errors='ignore').replace('\r','').replace('\n','') 
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
                ress+=str(bytes(bs),encoding='gbk').replace(chr(0),'')

                #print(1,ress,2)
            #ress=ress.replace('Translation(TaskNo = 1) is OK. (remainder threads = 0)\r\n','')
            return ress 
         
    def translate(self,content): 
        return self.x64(content)
         