 
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

import importlib
import cv2
from difflib import SequenceMatcher
import numpy as np 
import time  
from PyQt5.QtWidgets import QApplication 
from textsource.textsourcebase import basetext
from ocr.myocr import myocr
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
     
        
        pix = self.screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1)
         
        return self.qimg2cv2(pix)
    def __init__(self,textgetmethod,object)  :
        self.screen = QApplication.primaryScreen()
        self.typename='ocr'
        self.savelastimg=None
        self.savelasttext=None
        self.savelastimgsim=0
        self.ocr=myocr()
        self.object=object
        self.ending=False
        super( ).__init__(textgetmethod) 
    def gettextthread(self ):
                 
            if self.object.rect is None:
                time.sleep(1)
                return
            if self.object.rect[0][0]>self.object.rect[1][0] or self.object.rect[0][1]>self.object.rect[1][1]:
                time.sleep(1)
                return
             
            #img=ImageGrab.grab((self.object.rect[0][0],self.object.rect[0][1],self.object.rect[1][0],self.object.rect[1][1]))
            #imgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            imgr=self.imageCut(self.object.rect[0][0],self.object.rect[0][1],self.object.rect[1][0],self.object.rect[1][1])
            
            if self.savelastimg is not None:
                h,w,c=self.savelastimg.shape
                
                if imgr.shape!=self.savelastimg.shape:
                    self.image_score=0
                else:
                    self.image_score =[ compareImage(imgr[i*h//3:(i+1)*h//3],self.savelastimg[i*h//3:(i+1)*h//3])  for i in range(3)]
                    self.image_score=min(self.image_score)
                    #self.image_score= compareImage(imgr ,self.savelastimg )
            else:
                self.image_score=0
            self.savelastimg=imgr
            #print(image_score)
            if self.image_score>0.95 and self.savelastimgsim<0.95:
                
                self.savelastimgsim=self.image_score
            else:
                self.savelastimgsim=self.image_score
                return 
            text=self.ocrtest(imgr)
            if self.savelasttext is not None:
                sim=getEqualRate(self.savelasttext,text)
                #print('text',sim)
                if sim>0.9:
                    return 
                 
            self.savelasttext=text
            self.textgetmethod(text)
            time.sleep(0.1)
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
                ocr=importlib.import_module('ocr.'+use).ocr
                cv2.imwrite('./tmp.jpg',img)
                return ocr('./tmp.jpg')
            except:
                print_exc()
                return ''