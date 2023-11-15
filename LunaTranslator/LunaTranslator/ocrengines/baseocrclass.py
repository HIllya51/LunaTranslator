
from myutils.config import globalconfig,ocrsetting,static_data
from traceback import print_exc 
from myutils.wrapper import stripwrapper
from myutils.exceptions import ArgsEmptyExc
from myutils.utils import getproxy
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
        if ('useproxy' not in  globalconfig['ocr'][self.typename]) or globalconfig['ocr'][self.typename]['useproxy']:
            return getproxy()
        else:
            return {'https':None,'http':None}
    @property
    def srclang(self):
        try:
            l=static_data["language_list_translator_inner"][globalconfig['srclang3']]
            return self.langmap_[l] 
        except:
            return ''
    @property
    def tgtlang(self):
        try:
            l=static_data["language_list_translator_inner"][globalconfig['tgtlang3']]
            return self.langmap_[l] 
        except:
            return ''
    @property
    def space(self):
        if globalconfig['ocrmergelines']==False:
            space='\n'
        elif self.srclang in ['zh','ja','cht']:
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
            ocrsetting[self.typename]['args']['次数统计']=str(int(self.config['次数统计'])+1)
        except: 
            ocrsetting[self.typename]['args']['次数统计']='1'
        
    def checkempty(self,items):
        emptys=[]
        for item in items:
            if (self.config[item])=='':
                emptys.append(item)
        if len(emptys):
            raise ArgsEmptyExc(emptys)
            
    ############################################################
    def flatten4point(self,boxs): 
        return [[box[0][0],box[0][1],box[1][0],box[1][1],box[2][0],box[2][1],box[3][0],box[3][1]] for box in boxs]

    def common_solve_text_orientation(self,boxs,texts): 
        vertical=globalconfig['verticalocr']
        def norm48(box):
            return min([box[i*2] for i in range(len(box)//2)]),min([box[i*2+1] for i in range(len(box)//2)]),max([box[i*2] for i in range(len(box)//2)]),max([box[i*2+1] for i in range(len(box)//2)]),
        boxs=[norm48(box) if len(box)==8 else box for box in boxs]
        
        #print(list(zip(boxs,texts))) 
        
        mids=[((box[0]+box[2])/2,(box[1]+box[3])/2) for box in boxs]
        ranges=[((box[0],box[2]),(box[1],box[3])) for box in boxs] 
        juhe=[] 
        passed=[] 
        mids_idx=not vertical 
        for i in range(len(boxs)):
            ls=[i]
            if i in passed:
                continue
            for j in range(i+1,len(boxs)):
                if j in passed:
                    continue  
                
                if mids[i][mids_idx]>ranges[j][mids_idx][0] and mids[i][mids_idx]<ranges[j][mids_idx][1] \
                    and mids[j][mids_idx]>ranges[i][mids_idx][0] and mids[j][mids_idx]<ranges[i][mids_idx][1]:
                    passed.append(j)
                    ls.append(j)
            juhe.append(ls)
        
        for i in range(len(juhe)):
            juhe[i].sort(key=lambda x:mids[x][1-mids_idx]) 
        juhe.sort(key=lambda x:mids[x[0]][mids_idx],reverse=vertical)  
        lines=[] 
        for _j in juhe:  
            lines.append(' '.join([texts[_] for _ in _j])) 
        return self.space.join(lines)

    ########################################################
    def __init__(self,typename ) :  
        self.typename=typename 
        try: 
            self.initocr() 
        except Exception as e:
            raise e
    @property
    def langmap_(self):
        _=dict(zip(static_data["language_list_translator_inner"],static_data["language_list_translator_inner"]))
        _.update({'cht':'zh'})
        _.update(self.langmap())
        return _
     
    