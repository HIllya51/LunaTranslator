
import os
import time 
import pyperclip
from queue import Queue
from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog ,QGridLayout
from utils.config import globalconfig
import json,sqlite3,threading
from traceback import print_exc
from textsource.textsourcebase import basetext
class txt(basetext):
    def __init__(self,textgetmethod) -> None:
        self.last_paste_str = '' 
        f=QFileDialog.getOpenFileName(  )
        res=f[0]
        if res!='':
            with open(res,'r',encoding='utf8') as ff:
                self.txtlines=ff.read().split('\n')
            self.txtsavename=res+'.trans.txt'
             
        self.ending=False
        self.typename='txt'
        self.runonceline=''
        self.md5='0' 
        self.queue=Queue()
        self.prefix='0_txt'
        super(txt,self).__init__(textgetmethod)
        threading.Thread(target=self.txtgetline).start()
    def writetxt(self,xx):
        with open(self.txtsavename,'a',encoding='utf8') as ff:
            ff.write(xx)
            ff.write('\n')
    def txtgetline(self):
        for line in self.txtlines:
            print(line)
            self.queue.put(line)
            self.runonceline=line
            self.writetxt('')
            self.writetxt(line)
            time.sleep(globalconfig['txtreadlineinterval'])
    def gettextthread(self ):
                  
            return self.queue.get()
    def runonce(self):  
        self.textgetmethod(self.runonceline,False)