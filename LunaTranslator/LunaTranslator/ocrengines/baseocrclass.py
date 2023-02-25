
from utils.config import globalconfig,ocrsetting
from traceback import print_exc
from utils import somedef
class baseocr: 
    def langmap(self):
        return {}
    @property
    def langmap_(self):
        _=dict(zip(somedef.language_list_translator_inner,somedef.language_list_translator_inner))
        _.update({'cht':'zh'})
        _.update(self.langmap())
        return _
     
    @property
    def srclang(self):
        try:
            l=somedef.language_list_translator_inner[globalconfig['srclang3']]
            return self.langmap_[l] 
        except:
            return ''
    @property
    def space(self):
        if globalconfig['ocrmergelines']==False:
            space='\n'
        elif self.srclang in ['zh','ja']:
            space=''
        else:
            space=' '
        return space
    def countnum(self):
        try: 
            self.config['次数统计']=str(int(self.config['次数统计'])+1)
        except: 
            self.config['次数统计']='1'
    @property
    def config(self):
        try:
            return ocrsetting[self.typename]['args']
        except:
            return {}
    def __init__(self,typename ) :  
        self.typename=typename 
        try: 
            self.initocr() 
        except:
            print_exc()
         
    def initocr(self):
        pass
    def ocr(self,imgpath):
        raise Exception