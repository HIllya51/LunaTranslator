 
import time  
from queue import Queue
from PyQt5.QtWidgets import  QFileDialog 
from utils.config import globalconfig
import  threading 
from textsource.textsourcebase import basetext
class txt(basetext):
    def __init__(self,textgetmethod) -> None:
        self.last_paste_str = '' 
        f=QFileDialog.getOpenFileName(  )
        res=f[0]
        if res!='':
            with open(res,'r',encoding='utf8') as ff:
                self.txtlines=ff.read().split('\n')
        else:
            self.txtlines=[]
        self.ending=False
        self.typename='txt'
        self.runonceline=''
        self.md5='0' 
        self.queue=Queue()
        self.prefix='0_txt'
        super(txt,self).__init__(textgetmethod)
        threading.Thread(target=self.txtgetline).start()
    def ignoretext(self):
        while self.queue.empty()==False:
            self.queue.get()
    def txtgetline(self):
        for line in self.txtlines: 
            self.queue.put(line)
            self.runonceline=line 
            time.sleep(globalconfig['txtreadlineinterval'])
    def gettextthread(self ):
                  
            return self.queue.get()
    def runonce(self):  
        self.textgetmethod(self.runonceline,False)