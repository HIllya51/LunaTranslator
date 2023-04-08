 
from utils.config import _TR 

from ocrengines.baseocrclass import baseocr 
from utils.subproc import subproc_w
class OCR(baseocr):
      
    def ocr(self,imgfile):  
        print('./files/plugins/WinOCR.exe '+self.srclang +' '+imgfile)
        p=subproc_w('./files/plugins/WinOCR.exe '+self.srclang +' '+imgfile,needstdio=True,encoding='utf8')
        x=p.stdout.readlines()
        y=p.stderr.readlines()
        print("X",x)
        print("Y",y)
        
        if len(y):
            raise Exception(_TR('系统未安装该语言的OCR模型'))
         
        ress={}
        ress2=[]
        
    
        for _ in x:
            line=_.replace('\r','').replace('\n','')
            
            ress[ (line[len(line.split(' ')[0]):])]=int(line.split(' ')[0])
            ress2.append( (line[len(line.split(' ')[0]):]))
        ress2.sort(key= lambda x:ress[x])

            
        xx=self.space.join(ress2)
        print(xx)
        return xx
        