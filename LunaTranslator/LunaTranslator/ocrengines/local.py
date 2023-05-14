import os  
 
from utils.config import globalconfig,_TR,static_data
 
import requests
import base64  
from ocrengines.baseocrclass import baseocr 
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
         
        path=f'./files/ocr/{static_data["language_list_translator_inner"][globalconfig["srclang3"]]}'
        if not(os.path.exists(f'{path}/det.onnx') and os.path.exists(f'{path}/rec.onnx') and os.path.exists(f'{path}/dict.txt') ):
            raise Exception(_TR('未下载该语言的OCR模型,请从软件主页下载模型解压到files/ocr路径后使用') )
        self._ocr.init(f'{path}/det.onnx',f'{path}/rec.onnx',f'{path}/dict.txt')
        self._savelang=self.srclang
    def ocr(self,imgfile):  
        self.checkchange()
        
         
        s=self._ocr.ocr(os.path.dirname(imgfile)+'/',os.path.basename(imgfile),globalconfig['verticalocr'])
        
        ls=s.split('\n') 
        juhe=[]
        box=[]
        mids=[]
        ranges=[]
        text=[]
        reverse={}
        for i in range(len(ls)//2):
            box.append([int(_)  for _ in ls[i*2].split(',')])
            text.append(ls[i*2+1]) 
        for i in range(len(box)):
            if globalconfig['verticalocr']:
                mid=box[i][0]+box[i][2]+box[i][4]+box[i][6]
            else:
                mid=box[i][1]+box[i][3]+box[i][5]+box[i][7]
            mid/=4
            mids.append(mid)
            if globalconfig['verticalocr']:
                range_=((box[i][0]+box[i][6])/2,(box[i][2]+box[i][4])/2)
            else:
                range_=((box[i][1]+box[i][3])/2,(box[i][7]+box[i][5])/2)
            ranges.append(range_) 
        passed=[] 
        for i in range(len(box)):
            ls=[i]
            if i in passed:
                continue
            for j in range(i+1,len(box)):
                if j in passed:
                    continue 
                if mids[i]>ranges[j][0] and mids[i]<ranges[j][1] \
                    and mids[j]>ranges[i][0] and mids[j]<ranges[i][1]:
                        
                    passed.append(j)
                    ls.append(j)
            juhe.append(ls)
        
        for i in range(len(juhe)):
            if globalconfig['verticalocr']:
                juhe[i].sort(key=lambda x:box[x][1])
            else:
                juhe[i].sort(key=lambda x:box[x][0])
        if globalconfig['verticalocr']:
            juhe.sort(key=lambda x:-box[x[0]][0])
        else:
            juhe.sort(key=lambda x:box[x[0]][1])
        lines=[]
        
        for _j in juhe:
            

            lines.append(' '.join([text[_] for _ in _j])) 
        
        return self.space.join(lines)