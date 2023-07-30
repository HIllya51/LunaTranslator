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
         
        ret=winrtutils.OCR_f(os.path.abspath(imgfile),self.supportmap[self.srclang],space)
         
        juhe=[] 
        mids=[]
        ranges=[] 
        for i in range(len(ret)):
            mid=ret[i][2]+ret[i][3]//2 
            mids.append(mid)
            range_=(ret[i][2],ret[i][2]+ret[i][3])
            ranges.append(range_) 
        passed=[] 
        
        for i in range(len(ret)):
            ls=[i]
            if i in passed:
                continue
            for j in range(i+1,len(ret)):
                if j in passed:
                    continue 
                if mids[i]>ranges[j][0] and mids[i]<ranges[j][1] \
                    and mids[j]>ranges[i][0] and mids[j]<ranges[i][1]:
                        
                    passed.append(j)
                    ls.append(j)
            juhe.append(ls)
        for i in range(len(juhe)):
            juhe[i].sort(key=lambda x:ret[x][1])
        juhe.sort(key=lambda x:ret[x[0]][2])
        lines=[]
        
        for _j in juhe:
            

            lines.append(' '.join([ret[_][0] for _ in _j])) 
        return self.space.join(lines)