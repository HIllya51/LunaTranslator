 
from utils.config import _TR 

from utils.exceptions import ApiExc
from ocrengines.baseocrclass import baseocr 
from utils.subproc import subproc_w
class OCR(baseocr):
      
    def ocr(self,imgfile):  
          
        p=subproc_w('./files/WinOCR.exe '+self.srclang +' '+imgfile,needstdio=True)
        x=p.stdout.readlines()
        y=p.stderr.readlines()
        # print("X",x)
        # print("Y",y)
        
        if len(y):
            raise ApiExc(_TR('系统未安装该语言的OCR模型'))
        xx=''
        ress={}
        ress2=[]
        
    
        for _ in x:
            line=str(_,encoding='gbk',errors='ignore').replace('\r','').replace('\n','')
            
            ress[ (line.split(' ')[1])]=int(line.split(' ')[0])
            ress2.append( (line.split(' ')[1]))
        ress2.sort(key= lambda x:ress[x])

            
        xx=self.space.join(ress2)
        
        return xx
        