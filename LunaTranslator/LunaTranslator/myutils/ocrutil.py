
import win32utils
import math,os,importlib
from myutils.config import globalconfig,_TR
from PyQt5.QtWidgets import QApplication
from myutils.exceptions import ArgsEmptyExc
from traceback import print_exc
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
    return pix.toImage()

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
    except Exception as e:
        if isinstance(e,ArgsEmptyExc):
            msg=str(e)
        else:
            print_exc()
            msg=str(type(e))[8:-2]+' '+str(e).replace('\n','').replace('\r','')
        msg='<msg>'+_TR(globalconfig['ocr'][use]['name'])+' '+msg
        text= msg
    return text
    
    