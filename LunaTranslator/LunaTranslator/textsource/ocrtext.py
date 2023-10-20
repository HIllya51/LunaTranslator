 
import time,os
from traceback import print_exc 
from myutils.config import globalconfig,_TR
import importlib  
from difflib import SequenceMatcher 
from myutils.exceptions import ArgsEmptyExc
from gui.rangeselect    import rangeadjust
from myutils.ocrutil import imageCut,ocr_run,ocr_end
import time  ,gobject
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtGui import QImage
from textsource.textsourcebase import basetext  
def qimge2np(img:QImage):
    #img=img.convertToFormat(QImage.Format_Grayscale8)
    shape=img.height(),img.width(),1
    img=img.scaled(128,8*3) 
    img.shape=shape
    return img
def sample_compare(img1,img2,h=24,w=128):
    cnt=0
    for i in range(w):
        for j in range(h):
            cnt+=(img1.pixel(i,j)==img2.pixel(i,j)) 
    return cnt/(w*h)
     
def compareImage(img1:QImage,img2): 
    if globalconfig['ocr_presolve_method'] in [2,3]:
        return sample_compare(img1,img2,img1.height(),img1.width())
    else:
        return sample_compare(img1,img2)
def getEqualRate(  str1, str2):
    
        score = SequenceMatcher(None, str1, str2).quick_ratio()
        score = score 

        return score
class ocrtext(basetext):
     
    def __init__(self,textgetmethod)  :
        self.screen = QApplication.primaryScreen() 
        self.savelastimg=None
        self.savelastrecimg=None
        self.savelasttext=None 
        self.lastocrtime=0
        self.rect=None
        self.range_ui = rangeadjust(gobject.baseobject.translation_ui)   
        self.timestamp=time.time() 
        super(ocrtext,self ).__init__(textgetmethod,'0','0_ocr') 
    def resetrect(self):
        self.rect=None
        self.range_ui.hide()
    def moveui(self,x,y):
        _r=self.range_ui
        _r.move(_r.pos().x()+ x,_r.pos().y()+ y)
    def setrect(self,rect):
        (x1,y1),(x2,y2)=rect
        self.rect=[(x1,y1),(x2,y2)]
        self.range_ui.setGeometry(x1-globalconfig['ocrrangewidth'],y1-globalconfig['ocrrangewidth'],x2-x1+2*globalconfig['ocrrangewidth'],y2-y1+2*globalconfig['ocrrangewidth']) 
        self.range_ui.show() 
    def setstyle(self):
        self.range_ui.setstyle()
    def showhiderangeui(self,b):
        self.range_ui.setVisible(b)
    def gettextthread(self ):
                 
            if self.rect is None:
                time.sleep(1)
                return None
            
            time.sleep(0.1)
            #img=ImageGrab.grab((self.rect[0][0],self.rect[0][1],self.rect[1][0],self.rect[1][1]))
            #imgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            if self.rect is None:
                return None 
            imgr=imageCut(self.hwnd,self.rect[0][0],self.rect[0][1],self.rect[1][0],self.rect[1][1])
            ok=True
            
            if globalconfig['ocr_auto_method'] in [0,2]: 
                imgr1=qimge2np(imgr)
                h,w,c=imgr1.shape 
                if self.savelastimg is not None and  (imgr1.shape==self.savelastimg.shape) : 
                    
                    image_score=compareImage(imgr1 ,self.savelastimg )
                    
                else:
                    image_score=0 
                gobject.baseobject.settin_ui.threshold1label.setText(str(image_score))
                self.savelastimg=imgr1
                
                if image_score>globalconfig['ocr_stable_sim'] : 
                    if self.savelastrecimg is not None and  (imgr1.shape==self.savelastrecimg.shape   ) :
                        image_score2=compareImage(imgr1 ,self.savelastrecimg ) 
                    else:
                        image_score2=0 
                    gobject.baseobject.settin_ui.threshold2label.setText(str(image_score2))
                    if image_score2>globalconfig['ocr_diff_sim']:
                        ok=False
                    else: 
                        self.savelastrecimg=imgr1
                else:
                    ok=False
            if globalconfig['ocr_auto_method'] in [1,2]:
                if time.time()-self.lastocrtime>globalconfig['ocr_interval']:
                    ok=True
                else:
                    ok=False
            if ok==False:
                return None
            text=self.ocrtest(imgr)  
            self.lastocrtime=time.time()
            
            if self.savelasttext is not None:
                sim=getEqualRate(self.savelasttext,text)
                #print('text',sim)
                if sim>0.9: 
                    return  None
            self.savelasttext=text
            
            return (text)
            
    def runonce(self): 
        
        if self.rect is None:
            return
        if self.rect[0][0]>self.rect[1][0] or self.rect[0][1]>self.rect[1][1]:
            return  
        img=imageCut(self.hwnd,self.rect[0][0],self.rect[0][1],self.rect[1][0],self.rect[1][1])
        

        text=self.ocrtest(img)
        imgr1=qimge2np(img)
        self.savelastimg=imgr1
        self.savelastrecimg=imgr1
        self.lastocrtime=time.time()
        self.savelasttext=text
        self.textgetmethod(text,False)
    def ocrtest(self,img):
         
        fname='./cache/ocr/{}.png'.format(self.timestamp)
        img.save(fname)
        print(fname)
        text=ocr_run(fname)
        print(text)
        return text
        

    def end(self):
        super().end()
        try: ocr_end()
        except:pass

        self.range_ui.close()