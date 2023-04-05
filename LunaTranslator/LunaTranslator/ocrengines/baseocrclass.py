
from utils.config import globalconfig,ocrsetting
from traceback import print_exc
from utils import somedef
from utils.wrapper import stripwrapper
from utils.exceptions import ArgsEmptyExc
from utils.utils import getproxy
class baseocr: 
    def langmap(self):
        return {}
    def initocr(self):
        pass
    def ocr(self,imgpath):
        raise Exception 
    def end(self):
        pass
    ############################################################
    @property
    def proxy(self):
        return getproxy()
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
    @property
    def config(self):
        try:
            return stripwrapper(ocrsetting[self.typename]['args'])
        except:
            return {}
    def countnum(self):
        try: 
            self.config['次数统计']=str(int(self.config['次数统计'])+1)
        except: 
            self.config['次数统计']='1'
    def checkempty(self,items):
        emptys=[]
        for item in items:
            if (self.config[item])=='':
                emptys.append(item)
        if len(emptys):
            raise ArgsEmptyExc(emptys)
            
    ############################################################
    def __init__(self,typename ) :  
        self.typename=typename 
        try: 
            self.initocr() 
        except Exception as e:
            raise e
    @property
    def langmap_(self):
        _=dict(zip(somedef.language_list_translator_inner,somedef.language_list_translator_inner))
        _.update({'cht':'zh'})
        _.update(self.langmap())
        return _
     
    