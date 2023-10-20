
import base64  ,os
from myutils.config import _TR,ocrsetting

from ocrengines.baseocrclass import baseocr 
from myutils.subproc import subproc_w
def list_langs():
    path=ocrsetting['tesseract5']['args']['路径']
    if os.path.exists(path)==False:
        return []
    res=subproc_w('"{}" --list-langs'.format(path),needstdio=True,run=True).stdout
    return res.split('\n')[1:-1]
class OCR(baseocr):
      
    def ocr(self,imgfile):  
        self.checkempty(['路径'])
        path = self.config['路径'] 
        if os.path.exists(path)==False:
            raise Exception(_TR('路径不存在') )
        res=subproc_w('"{}" "{}" - -l {} {}'.format(path,imgfile,"jpn",self.config['附加参数']),needstdio=True,run=True).stdout 
        
        
        
        return self.space.join(res.split('\n'))