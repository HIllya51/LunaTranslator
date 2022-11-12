 
import time
from traceback import print_exc 

from utils.config import globalconfig 
import win32file,win32pipe,win32con
import os
import importlib  
from difflib import SequenceMatcher 
import time  
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QPoint
from textsource.textsourcebase import basetext 
from utils.getpidlist import getmagpiehwnd
import numpy as np
def qimge2np( qimg): 
         
        temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
        temp_shape += (4,)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3] 
         
        return result

def rgb2gray(rgb):

    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray
def ssim_1(img1, img2, L=255):
    """Calculate SSIM (structural similarity) for one channel images.
    Args:
        img1 (ndarray): Images with range [0, 255].
        img2 (ndarray): Images with range [0, 255].
    Returns:
        float: ssim result.
    """
    K1 = 0.01
    K2 = 0.03
    C1 = (K1 * L)**2
    C2 = (K2 * L)**2
    C3 = C2/2

    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    # ux
    ux = img1.mean()
    # uy
    uy = img2.mean()
    # ux^2
    ux_sq = ux**2
    # uy^2
    uy_sq = uy**2
    # ux*uy
    uxuy = ux * uy
    # ox、oy方差计算
    ox_sq = img1.var()
    oy_sq = img2.var()
    ox = np.sqrt(ox_sq)
    oy = np.sqrt(oy_sq)
    oxoy = ox * oy
    oxy = np.mean((img1 - ux) * (img2 - uy))
    # 公式一计算
    L = (2 * uxuy + C1) / (ux_sq + uy_sq + C1)
    C = (2 * ox * oy + C2) / (ox_sq + oy_sq + C2)
    S = (oxy + C3) / (oxoy + C3)
    ssim = L * C * S
    # 验证结果输出
    # print('ssim:', ssim, ",L:", L, ",C:", C, ",S:", S)
    return ssim 
def compareImage(  imageA, imageB):
    
    grayA = rgb2gray(imageA)
    grayB =  rgb2gray(imageB)

    (score ) = ssim_1(grayA, grayB )
    score = float(score)  
    return score
def getEqualRate(  str1, str2):
    
        score = SequenceMatcher(None, str1, str2).quick_ratio()
        score = score 

        return score
import win32gui ,math,win32process
class ocrtext(basetext):
    
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
                imgr1=qimge2np(imgr)
                h,w,c=imgr1.shape 
                if self.savelastimg is not None and  (imgr1.shape==self.savelastimg.shape) : 
                    image_score =[ compareImage(imgr1[i*h//3:(i+1)*h//3],self.savelastimg[i*h//3:(i+1)*h//3])  for i in range(3)]
                    image_score=sum(image_score)/len(image_score)
                    
                else:
                    image_score=0
                print(image_score)
                self.savelastimg=imgr1
                if image_score>0.95 : 
                    if self.savelastrecimg is not None and  (imgr1.shape==self.savelastrecimg.shape   ) :

                        image_score2 =[ compareImage(imgr1[i*h//3:(i+1)*h//3],self.savelastrecimg[i*h//3:(i+1)*h//3])  for i in range(3)]
                        image_score2=sum(image_score2)/len(image_score2)
                    else:
                        image_score2=0
                    if image_score2>0.95:
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
        self.textgetmethod(text,False)
    def ocrtest(self,img):
        use=None
        for k in globalconfig['ocr']:
            if globalconfig['ocr'][k]['use']==True:
                use=k
                break
        if use is None:
            return ''
        img.save('./capture/tmp.jpg')
        try:
            if use=='local':
                win32pipe.WaitNamedPipe("\\\\.\\Pipe\\ocrwaitsignal",win32con.NMPWAIT_WAIT_FOREVER)
                hPipe = win32file.CreateFile( "\\\\.\\Pipe\\ocrwaitsignal", win32con.GENERIC_READ | win32con.GENERIC_WRITE, 0,
                        None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None);
                #win32file.WriteFile(hPipe,'haha'.encode('utf8'))
                return (win32file.ReadFile(hPipe, 65535, None)[1].decode('utf8')).replace('\n','')
            else:
            
                ocr=importlib.import_module('otherocr.'+use).ocr 
                return ocr('./capture/tmp.jpg')
        except:
            print_exc()
            return ''