import os
import winrtutils
from myutils.config import _TR ,static_data 
from ocrengines.baseocrclass import baseocr  
class OCR(baseocr):
    def initocr(self):    
        _allsupport=winrtutils.getlanguagelist()
        self.supportmap={}
        for lang in static_data["language_list_translator_inner"]+['zh-Hans','zh-Hant']:
            if lang=='zh' or lang=='cht':continue
            for s in _allsupport:
                if s.startswith(lang) or lang.startswith(s):
                    self.supportmap[lang]=s
                    break
        if 'zh-Hans' in self.supportmap:
            v=self.supportmap.pop('zh-Hans')
            self.supportmap['zh']=v
        if 'zh-Hant' in self.supportmap:
            v=self.supportmap.pop('zh-Hant')
            self.supportmap['cht']=v
    def ocr(self,imgfile):  
        if self.srclang not in self.supportmap: 
            idx=static_data["language_list_translator_inner"].index(self.srclang)
            raise Exception(_TR('系统未安装')+_TR(static_data["language_list_translator"][idx])+_TR('的OCR模型'))
        
        if self.srclang in ['zh','ja','cht']:
            space=''
        else:
            space=' '
        
        ress={}
        ress2=[]  
        ret=winrtutils.OCR_f(os.path.abspath(imgfile),self.supportmap[self.srclang],space)
        for i in range(len(ret)): 
        
            ress2.append( ret[i][0])
            ress[ress2[-1]]=ret[i][1]
        ress2.sort(key= lambda x:ress[x])

            
        xx=self.space.join(ress2) 
        return xx
        