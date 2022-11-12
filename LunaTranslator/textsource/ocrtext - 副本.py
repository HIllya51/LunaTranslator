 
import time
from traceback import print_exc 

from utils.config import globalconfig 
def ssim_2(img1, img2):
    """Calculate SSIM (structural similarity) for one channel images.
    It is called by func:`calculate_ssim`.
    Args:
        img1 (ndarray): Images with range [0, 255] with order 'HWC'.
        img2 (ndarray): Images with range [0, 255] with order 'HWC'.
    Returns:
        float: ssim result.
    """

    C1 = (0.01 * 255)**2
    C2 = (0.03 * 255)**2

    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    kernel = cv2.getGaussianKernel(11, 1.5)
    window = np.outer(kernel, kernel.transpose())

    mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]
    mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
    mu1_sq = mu1**2
    mu2_sq = mu2**2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = cv2.filter2D(img1**2, -1, window)[5:-5, 5:-5] - mu1_sq
    sigma2_sq = cv2.filter2D(img2**2, -1, window)[5:-5, 5:-5] - mu2_sq
    sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2
	# 公式二计算
    ssim_map = ((2 * mu1_mu2 + C1) *
                (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) *
                                       (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean()
import os
import importlib 
import cv2
from difflib import SequenceMatcher
import numpy as np 
import time  
from PyQt5.QtWidgets import QApplication 
from textsource.textsourcebase import basetext
from ocr.myocr import myocr
from utils.getpidlist import getmagpiehwnd
def compareImage(  imageA, imageB):
    
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    (score ) = ssim_2(grayA, grayB )
    score = float(score)  
    return score
def getEqualRate(  str1, str2):
    
        score = SequenceMatcher(None, str1, str2).quick_ratio()
        score = score 

        return score
import win32gui ,math,win32process
class ocrtext(basetext):
    def qimg2cv2(self,qimg):
        qimg=qimg.toImage() 
         
        temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
        temp_shape += (4,)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3] 
         
        return result
    def imageCut(self,x1,y1,x2,y2):
     
        if self.hwnd:
            try:
                _hwnd_magpie=getmagpiehwnd(self.object.translation_ui.callmagpie.pid)
                if _hwnd_magpie!=0:

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
                res=self.qimg2cv2(pix)
                if res.sum()==0: 
                    pix = self.screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1)
                    res=self.qimg2cv2(pix)
                    if res.sum()!=0:
                        raise Exception
            except:
                self.hwnd=None
                print_exc()
                self.object.translation_ui.isbindedwindow=False
                self.object.translation_ui.refreshtooliconsignal.emit()
                pix = self.screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1)
                res=self.qimg2cv2(pix)
        else:
            pix = self.screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1)
            res=self.qimg2cv2(pix)
        return res
    def __init__(self,textgetmethod,object)  :
        self.screen = QApplication.primaryScreen()
        self.typename='ocr'
        self.savelastimg=None
        self.savelastrecimg=None
        self.savelasttext=None 
        self.ocr=myocr()
        self.object=object
        self.ending=False
        self.lastocrtime=0
        self.hwnd=None
        
        self.md5='0'
        self.sqlfname='./transkiroku/0_ocr.sqlite'
        self.sqlfname_all='./transkiroku/0_ocr.premt_synthesize.sqlite'
        self.jsonfname='./transkiroku/0_ocr.json'
        
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
            
            if globalconfig['mustocr'] and  time.time()-self.lastocrtime>globalconfig['mustocr_interval']:
                pass
            else:
                h,w,c=imgr.shape 
                if self.savelastimg is not None and  (imgr.shape==self.savelastimg.shape) : 
                    image_score =[ compareImage(imgr[i*h//3:(i+1)*h//3],self.savelastimg[i*h//3:(i+1)*h//3])  for i in range(3)]
                    image_score=sum(image_score)/len(image_score)
                else:
                    image_score=0
                self.savelastimg=imgr
                if image_score>0.95 :
                    
                    if self.savelastrecimg is not None and  (imgr.shape==self.savelastrecimg.shape   ) :

                        image_score2 =[ compareImage(imgr[i*h//3:(i+1)*h//3],self.savelastrecimg[i*h//3:(i+1)*h//3])  for i in range(3)]
                        image_score2=sum(image_score2)/len(image_score2)
                    else:
                        image_score2=0
                    if image_score2>0.95:
                        return None
                    else:
                        self.savelastrecimg=imgr
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
        #img=ImageGrab.grab((self.object.rect[0][0],self.object.rect[0][1],self.object.rect[1][0],self.object.rect[1][1]))
        #img= cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

        img=self.imageCut(self.object.rect[0][0],self.object.rect[0][1],self.object.rect[1][0],self.object.rect[1][1])
        
        

        text=self.ocrtest(img)
        self.textgetmethod(text,False)
    def ocrtest(self,img):
        use=None
        for k in globalconfig['ocr']:
            if globalconfig['ocr'][k]['use']==True:
                use=k
                break
        if use is None:
            return ''
        
        if use=='local':
            return self.ocr.ocr(img)
        else:
            try:
                ocr=importlib.import_module('otherocr.'+use).ocr
                cv2.imwrite('./capture/tmp.jpg',img)
                return ocr('./capture/tmp.jpg')
            except:
                print_exc()
                return ''