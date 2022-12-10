import time
import win32pipe,win32file,win32con
from utils.ocrdll import ocrwrapper
from utils.config import globalconfig
_ocr=ocrwrapper()
_savelang=None
def ocr(imgfile,lang,space): 
    global _savelang,_ocr
    if _savelang!=lang: 
        _ocr.trydestroy()
        path=f'./files/ocr/{globalconfig["normallanguagelist"][globalconfig["srclang2"]]}'
        _ocr.init(f'{path}/det.onnx',f'{path}/rec.onnx',f'{path}/dict.txt')
        _savelang=lang
        
    s=_ocr.ocr('./capture/',imgfile[10:])
   
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
        mid=box[i][1]+box[i][3]+box[i][5]+box[i][7]
        mid/=4
        mids.append(mid)
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
        juhe[i].sort(key=lambda x:box[x][0])
    juhe.sort(key=lambda x:box[x[0]][1])
    lines=[]
    
    for _j in juhe:
        

        lines.append(' '.join([text[_] for _ in _j])) 
    
    return space.join(lines)