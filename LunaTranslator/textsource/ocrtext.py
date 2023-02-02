 
import time
from traceback import print_exc 

from utils.ocrdll import ocrwrapper
from utils.config import globalconfig 
import win32file,win32pipe,win32con
import os
import importlib  
from difflib import SequenceMatcher 
import time  
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import QPoint
from textsource.textsourcebase import basetext  
from utils.getpidlist import getpidhwnds
def qimge2np(img:QImage):
    #img=img.convertToFormat(QImage.Format_Grayscale8)
    shape=img.height(),img.width(),1
    img=img.scaled(128,8*3) 
    img.shape=shape
    return img
def compareImage(img1:QImage,img2):
    cnt=0
    for i in range(128):
        for j in range(24):
            cnt+=(img1.pixel(i,j)==img2.pixel(i,j)) 
    return cnt/(128*24)
     
def getEqualRate(  str1, str2):
    
        score = SequenceMatcher(None, str1, str2).quick_ratio()
        score = score 

        return score
import win32gui ,math,win32process
class ocrtext(basetext):
    
    def imageCut(self,x1,y1,x2,y2):
     
        if self.hwnd:
            try: 
                hwnds=getpidhwnds( self.object.translation_ui.fullscreenmanager.savemagpie_pid)  
                if len(hwnds): 

                    hwnduse=QApplication.desktop().winId()
                else:
                    hwnduse=self.hwnd
                rect=win32gui.GetWindowRect(hwnduse)  
                rect2=win32gui.GetClientRect(hwnduse)
                windowOffset = math.floor(((rect[2]-rect[0])-rect2[2])/2)
                h= ((rect[3]-rect[1])-rect2[3]) - windowOffset
                # print(h)
                # print(rect)
                # print(rect2)
                # print(x1-rect[0], y1-rect[1]-h, x2-x1, y2-y1)
 
                 
                pix = self.screen.grabWindow(hwnduse, x1-rect[0], y1-rect[1]-h, x2-x1, y2-y1) 
                
            except:
                self.hwnd=None
                print_exc()
                self.object.translation_ui.isbindedwindow=False
                self.object.translation_ui.refreshtooliconsignal.emit()
                pix = self.screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1) 
        else:
            pix = self.screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1) 
        return pix.toImage()
    def __init__(self,textgetmethod,object)  :
        self.screen = QApplication.primaryScreen()
        self.typename='ocr'
        self.savelastimg=None
        self.savelastrecimg=None
        self.savelasttext=None  
        self.object=object
        self.ending=False
        self.lastocrtime=0
        self.hwnd=None
        
        self.md5='0' 
        self.prefix='0_ocr'
        
        super(ocrtext,self ).__init__(textgetmethod) 
    def gettextthread(self ):
                 
            if self.object.rect is None:
                time.sleep(1)
                return None
            if self.object.rect[0][0]>self.object.rect[1][0] or self.object.rect[0][1]>self.object.rect[1][1]:
                time.sleep(1)
                return None
            time.sleep(0.1)
            #img=ImageGrab.grab((self.object.rect[0][0],self.object.rect[0][1],self.object.rect[1][0],self.object.rect[1][1]))
            #imgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            imgr=self.imageCut(self.object.rect[0][0],self.object.rect[0][1],self.object.rect[1][0],self.object.rect[1][1])
            
            if globalconfig['ocr_auto_method'] ==1:
                if time.time()-self.lastocrtime>globalconfig['ocr_interval']:
                    pass
                else:
                    return None
            elif globalconfig['ocr_auto_method'] ==0: 
                imgr1=qimge2np(imgr)
                h,w,c=imgr1.shape 
                if self.savelastimg is not None and  (imgr1.shape==self.savelastimg.shape) : 
                    
                    image_score=compareImage(imgr1 ,self.savelastimg )
                    
                else:
                    image_score=0 
                self.savelastimg=imgr1
                
                if image_score>globalconfig['ocr_stable_sim'] : 
                    if self.savelastrecimg is not None and  (imgr1.shape==self.savelastrecimg.shape   ) :
                        image_score2=compareImage(imgr1 ,self.savelastrecimg ) 
                    else:
                        image_score2=0 
                    if image_score2>globalconfig['ocr_diff_sim']:
                        return None
                    else: 
                        self.savelastrecimg=imgr1
                else:
                    return  None 
            text=self.ocrtest(imgr) 
            if self.savelasttext is not None:
                sim=getEqualRate(self.savelasttext,text)
                #print('text',sim)
                if sim>0.9: 
                    return  None
            self.lastocrtime=time.time()
            self.savelasttext=text
            
            return (text)
            
    def runonce(self): 
        if self.object.rect is None:
            return
        if self.object.rect[0][0]>self.object.rect[1][0] or self.object.rect[0][1]>self.object.rect[1][1]:
            return  
        img=self.imageCut(self.object.rect[0][0],self.object.rect[0][1],self.object.rect[1][0],self.object.rect[1][1])
        
        

        text=self.ocrtest(img)
        imgr1=qimge2np(img)
        self.savelastimg=imgr1
        self.savelastrecimg=imgr1
        self.lastocrtime=time.time()
        self.savelasttext=text
        self.textgetmethod(text,False)
    def ocrtest(self,img):
        use=None
        for k in globalconfig['ocr']:
            if globalconfig['ocr'][k]['use']==True:
                use=k
                break
        if use is None:
            return ''
        img.save(f'./cache/ocr/{self.object.timestamp}.png')
        try:
            lang=self.language(use)
            if globalconfig['ocrmergelines']==False:
                space='\n'
            elif lang in ['zh','ja']:
                space=''
            else:
                space=' '
            
        
            ocr=importlib.import_module('otherocr.'+use).ocr 
            return ocr(f'./cache/ocr/{self.object.timestamp}.png',lang,space)
        except:
            print_exc()
            return ''
    def language(self,tp):
        l=globalconfig['normallanguagelist'][globalconfig['srclang2']]
        if l=='cht' and l not in globalconfig['fanyi'][self.typename]['lang']:
            l='zh'
        if l in globalconfig['ocr'][tp]['lang']:
            return globalconfig['ocr'][tp]['lang'][l]
        else:
            return l