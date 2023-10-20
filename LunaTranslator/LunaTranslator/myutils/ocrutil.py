
import win32utils,time
import math,os,importlib
from myutils.config import globalconfig,_TR,ocrerrorfix
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QByteArray,QBuffer
from myutils.exceptions import ArgsEmptyExc
from traceback import print_exc
import gobject,winsharedutils
def togray(image):
    gray_image=image.convertToFormat(QImage.Format_Grayscale8)
    return gray_image
 
def otsu_threshold_fast(image:QImage,thresh):   
    
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.WriteOnly)
    image.save(buffer, "BMP") 
    buffer.close()
    image_data = byte_array.data()

    solved=winsharedutils.otsu_binary(image_data,thresh)
    image=QImage()
    image.loadFromData(solved)
    return image
def imagesolve(image):
    if globalconfig['ocr_presolve_method']==0:
        image2=image
    elif globalconfig['ocr_presolve_method']==1:
        image2=togray(image)
    elif globalconfig['ocr_presolve_method']==2:
        image2=otsu_threshold_fast(image,globalconfig['binary_thresh'])
    elif globalconfig['ocr_presolve_method']==3:
        image2=otsu_threshold_fast(image,-1)
    return image2
def imageCut(hwnd,x1,y1,x2,y2):
    screen = QApplication.primaryScreen() 
    if hwnd:
        try:   
            rect=win32utils.GetWindowRect(hwnd)  
            if rect==(0,0,0,0):
                raise Exception
            rect2=win32utils.GetClientRect(hwnd)
            windowOffset = math.floor(((rect[2]-rect[0])-rect2[2])/2)
            h= ((rect[3]-rect[1])-rect2[3]) - windowOffset
                
            pix = screen.grabWindow(hwnd, x1-rect[0], y1-rect[1]-h, x2-x1, y2-y1) 
            if pix.toImage().allGray():
                raise Exception()
        except:
            pix = screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1) 
    else:
        pix = screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2-x1, y2-y1) 
    image= pix.toImage()
    image2=imagesolve(image)
    gobject.baseobject.showocrimage.setimage.emit([image,image2])
    return image2

_nowuseocr=None
_ocrengine=None

def ocr_end():
    global _ocrengine,_nowuseocr
    try:
        _ocrengine.end()
    except:
        pass
    _nowuseocr=None
    _ocrengine=None

def _100_f(line):
        filters=ocrerrorfix['args']['替换内容']
        for fil in filters: 
                if fil=="":
                        continue
                else:
                        line=line.replace(fil,filters[fil])
        return line

def ocr_run(img):
    global _nowuseocr,_ocrengine
     
    use=None
    for k in globalconfig['ocr']:
        if globalconfig['ocr'][k]['use']==True and os.path.exists(('./LunaTranslator/ocrengines/'+k+'.py')):
            use=k
            break
    if use is None:
        return ''
       
    try:
        if _nowuseocr!=use:
            try: _ocrengine.end()
            except:pass
            aclass=importlib.import_module('ocrengines.'+use).OCR 
            _ocrengine=aclass(use)   
            _nowuseocr=use
        text= _ocrengine.ocr(img)
        text=_100_f(text)
    except Exception as e:
        if isinstance(e,ArgsEmptyExc):
            msg=str(e)
        else:
            print_exc()
            msg=str(type(e))[8:-2]+' '+str(e).replace('\n','').replace('\r','')
        msg='<msg>'+_TR(globalconfig['ocr'][use]['name'])+' '+msg
        text= msg
    return text
    
    