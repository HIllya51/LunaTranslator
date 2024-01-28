import os  
 
from myutils.config import globalconfig,_TR,static_data
 
import requests
import base64  
from ocrengines.baseocrclass import baseocr 
from ctypes import CDLL,c_char_p ,create_string_buffer,c_uint32,POINTER,c_int32
import os
import gobject
class ocrwrapper:
    def __init__(self) -> None: 
        self.dll=CDLL(gobject.GetDllpath(('LunaOCR32.dll','LunaOCR64.dll')))
    def _OcrInit(self,szDetModel, szRecModel, szKeyPath,szClsModel='', nThreads=4):
        
        _OcrInit=self.dll.OcrInit
        _OcrInit.restype=POINTER(c_uint32)
        self.pOcrObj=_OcrInit(c_char_p(szDetModel.encode('utf8')),c_char_p(szClsModel.encode('utf8')),c_char_p(szRecModel.encode('utf8')),c_char_p(szKeyPath.encode('utf8')),nThreads)
        
    def _OcrDetect( self,imgPath, imgName ,angle) :
        _OcrDetect=self.dll.OcrDetect
        return _OcrDetect(  self.pOcrObj ,c_char_p(imgPath.encode('utf8')),c_char_p(imgName.encode('utf8')),c_int32(angle))
    def _OcrGet(self):
        _OcrGetLen=self.dll.OcrGetLen
        _OcrGetResult=self.dll.OcrGetResult
        length=_OcrGetLen(self.pOcrObj)
        buff = create_string_buffer(length)

        _OcrGetResult(self.pOcrObj,buff,length)
        return buff.value
    def _OcrDestroy(self):
        _OcrDestroy=self.dll.OcrDestroy
        _OcrDestroy(self.pOcrObj)
    def init(self,det,rec,key):
        self._OcrInit(det,rec,key)
    def ocr(self,path,name,angle=0):
        try:
            if (self._OcrDetect(path,name,angle) ):
                return self._OcrGet().decode('utf8')
            else:
                return ''
        except:
        
            return ''
    def trydestroy(self):
        try:
            self._OcrDestroy()
        except:
            pass
        
class OCR(baseocr):
    def end(self): 
        self._ocr.trydestroy()
    def initocr(self):
        self._ocr=ocrwrapper()
        self._savelang=None
        self.checkchange()
    def checkchange(self):
        if self._savelang==self.srclang: 
            return 
        self._ocr.trydestroy() 
         
        path='./files/ocr/{}'.format(static_data["language_list_translator_inner"][globalconfig["srclang3"]])
        if not(os.path.exists(path+'/det.onnx') and os.path.exists(path+'/rec.onnx') and os.path.exists(path+'/dict.txt') ):
            raise Exception(_TR('未下载该语言的OCR模型,请从软件主页下载模型解压到files/ocr路径后使用') )
        self._ocr.init(path+'/det.onnx',path+'/rec.onnx',path+'/dict.txt')
        self._savelang=self.srclang
    def ocr(self,imgfile):  
        self.checkchange()
        
         
        s=self._ocr.ocr(os.path.dirname(imgfile)+'/',os.path.basename(imgfile),globalconfig['verticalocr'])
        
        ls=s.split('\n')  
        box=[] 
        text=[] 
        for i in range(len(ls)//2):
            box.append([int(_)  for _ in ls[i*2].split(',')])
            text.append(ls[i*2+1])   
        
        return self.common_solve_text_orientation(box,text)