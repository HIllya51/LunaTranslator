 
from utils.config import globalconfig
import subprocess

def ocr(imgfile,lang,space):
        st=subprocess.STARTUPINFO()
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.SW_HIDE

        p=subprocess.Popen('./files/WinOCR.exe '+lang +' '+imgfile,stdout=subprocess.PIPE,startupinfo=st)
        print('./files/WinOCR.exe '+lang +' '+imgfile)
        x=p.stdout.readlines()
         
        xx=''
        ress={}
        ress2=[]
        try:
            for _ in x:
                line=str(_,encoding='gbk',errors='ignore').replace('\r','').replace('\n','')
                
                ress[ (line.split(' ')[1])]=int(line.split(' ')[0])
                ress2.append( (line.split(' ')[1]))
            ress2.sort(key= lambda x:ress[x])

             
            xx=space.join(ress2)
        except:
            xx=''
        return xx
if __name__=="__main__":
    baiduocr('1.jpg')