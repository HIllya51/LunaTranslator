
import os

last='C:\\tmp\\LunaTranslatorlast'
new='C:\\tmp\\LunaTranslator'


import os,shutil
import sys
import hashlib


def getall(p):
    saveplast=[] 
    for root, dirs, files in os.walk(p):   
            for file in files:
                f=os.path.join(root,file)
                with open(f,'rb') as ff:
                    d=hashlib.md5(ff.read()).hexdigest()
                saveplast.append(f.replace(p,'')+'-'+d) 
    return saveplast
def contrastDir( ):
  
    saveplast=getall(last)
    savenew=getall(new)
    #print(F_list) 
    print(set(savenew).difference(set(saveplast)))
    print(set(saveplast).difference(set(savenew)))
    shutil.rmtree('./diff')
     
    os.mkdir('./diff')
    for diff in set(savenew).difference(set(saveplast)):
        diff=diff[:-len('-7277eb0a496a1ac64e90d11c990544e6')]
        print(new+diff)
        dst='./diff'+diff
        d=os.path.dirname(dst)
        try:
            os.makedirs(d)
        except:
            1
        shutil.copy((new+diff),dst)
contrastDir()