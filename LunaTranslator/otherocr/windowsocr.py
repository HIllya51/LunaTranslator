 
from utils.config import globalconfig
import subprocess
def ocr(imgfile):
        st=subprocess.STARTUPINFO()
        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow=subprocess.SW_HIDE

        p=subprocess.Popen('./files/Windows.Media.Ocr.Cli.exe -l ja '+imgfile,stdout=subprocess.PIPE,startupinfo=st)
        x=p.stdout.readlines()
         
        xx=''
        for _ in x:
            xx+=str(_,encoding='gbk',errors='ignore').replace(' ','').replace('\r','').replace('\n','')
        return xx
if __name__=="__main__":
    baiduocr('1.jpg')