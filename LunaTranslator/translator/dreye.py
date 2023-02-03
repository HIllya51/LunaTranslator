
from utils.subproc import subproc       
from translator.basetranslator import basetrans 
import os 
import subprocess

class TS(basetrans): 
     
    def x64(self,content):  
            if self.config['args']['路径']=="":
                return ''
            else:
                path = self.config['args']['路径'] 
            path=os.path.join(path,'DreyeMT\\SDK\\bin')
             
            path2=os.path.join(path,'TransCOM.dll')
            pairs=(self.srclang,self.tgtlang)
            mp={('zh','en'):2,('en','zh'):1,('zh','ja'):3,('ja','zh'):10}
            if pairs not in mp:
                
                return
            if mp[pairs] in [3,10]:
                path2=os.path.join(path,'TransCOM.dll')
            else:
                path2=os.path.join(path,'TransCOMEC.dll')
            codes={'zh':'gbk','ja':'shift-jis','en':'utf8'}
            ress=''
            for line in content.split('\n'):
                if len(line)==0:
                    continue
                if ress!='':
                    ress+='\n'  

                exec=r'./files/x64_x86_dll/dreyec.exe "'+path+'"  "'+path2+'" '+str(mp[pairs])+' '#+apiinit+' '+apitrans+' '
                 
                linebyte=bytes(line,encoding=codes[self.srclang])
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
                ress+=str(bytes(bs),encoding=codes[self.tgtlang]).replace(chr(0),'')

                #print(1,ress,2)
            #ress=ress.replace('Translation(TaskNo = 1) is OK. (remainder threads = 0)\r\n','')
            return ress 
         
    def translate(self,content): 
        return self.x64(content)
         