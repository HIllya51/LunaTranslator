from utils.config import globalconfig

import os
from traceback import print_exc
class hira:
    def __init__(self) -> None: 
        hirasettingbase=globalconfig['hirasetting']
    
        mecabpath=hirasettingbase['mecab']['path']
        if os.path.exists(mecabpath):
            import fugashi 
            self.kks= fugashi.Tagger('-r nul -d "{}" -Owakati'.format(mecabpath))
             
            keys='ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ'
            vs='ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ'
            self.h2k=str.maketrans( keys,vs)
         
 
    def fy(self,text): 
         
            start=0
            result=[] 
            for node in self.kks.parseToNodeList(text): 
                l=0
                if text[start]=='\n':
                    start+=1
                while str(node) not in text[start:start+l]:
                    l+=1
                orig=text[start:start+l]
                start+=l
                try:
                    hira=node.feature.kana.translate(self.h2k)
                except:
                    hira=''
                #print(node.feature)
                result.append({'orig':orig,"hira":hira,"cixing":node.feature.pos1}) 
         
            return result
     