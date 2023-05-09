from ctypes import CDLL,c_char_p ,create_string_buffer,c_uint32,POINTER,c_int32
import os
import platform
class ocrwrapper:
    def __init__(self) -> None:
                
        if platform.architecture()[0]=='64bit':
            bit='64' 
        else:
            bit='32' 
        self.dll=CDLL(os.path.abspath(f'./files/plugins/ocr{bit}.dll') )
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
            self._OcrDetect(path,name,angle) 
            return self._OcrGet().decode('utf8')
        except:
        
            return ''
    def trydestroy(self):
        try:
            self._OcrDestroy()
        except:
            pass
        