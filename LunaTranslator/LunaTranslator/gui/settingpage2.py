 
from PyQt5.QtWidgets import QPushButton  ,QWidget,QVBoxLayout
import functools 
from utils.config import globalconfig ,translatorsetting 
 
from gui.pretransfile import sqlite2json
from utils.config import globalconfig ,_TR,_TRL
from utils.utils import selectdebugfile
import os
from utils import somedef
from gui.inputdialog import autoinitdialog 
def initsome11(self,l,label=None): 
    grids=[]
    if label:
        grids.append(
            [(label,8)]
        )
    i=0
    bad=0
    for fanyi in globalconfig['fanyi']:
        if i%3==0:
            line=[]
        if fanyi not in l:
            continue
        
        _f=f'./Lunatranslator/translator/{fanyi}.py'
        if os.path.exists(_f)==False: 
            bad+=1 
            continue 
        i+=1
        
        if fanyi in translatorsetting :
            
            items=[] 
            for arg in translatorsetting[fanyi]['args']: 
                items.append({
                        'l':arg,'d':translatorsetting[fanyi]['args'],'k':arg
                    })
                if 'argstype' in translatorsetting[fanyi] and arg in translatorsetting[fanyi]['argstype']:
                   
                    items[-1].update(translatorsetting[fanyi]['argstype'][arg]) 
                else:
                    items[-1].update(
                        {'t':'lineedit'}
                    )
            items.append({'t':'okcancel' })
            last=self.getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self, (globalconfig['fanyi'][fanyi]['name']),900,items),icon='fa.gear',constcolor="#FF69B4")
        elif fanyi=='selfbuild': 
            last=self.getcolorbutton(globalconfig,'',callback=lambda:selectdebugfile('translator/selfbuild.py' ),icon='fa.gear',constcolor="#FF69B4")
        else:
            last=''
        line+=[(globalconfig['fanyi'][fanyi]['name'],6),
        self.getsimpleswitch(globalconfig['fanyi'][fanyi],'use',callback=functools.partial( self.object.prepare ,fanyi)),
        self.getcolorbutton(globalconfig['fanyi'][fanyi],'color',name="fanyicolor_"+fanyi,callback=functools.partial(self.ChangeTranslateColor,fanyi,None,self,"fanyicolor_"+fanyi)),last ] 


        if i%3==0 or i==len(l)-bad:
            grids.append(line)
        else:
            line+=['']

    return grids
def setTabTwo(self) : 
    self.tabadd_lazy(self.tab_widget, ('翻译设置'), lambda :setTabTwo_lazy(self)) 
def setTabTwo_lazy(self) :
         
         
        bt = QPushButton(_TR("导出翻译记录为json文件")  ) 
        bt.clicked.connect(lambda x:sqlite2json(self)) 
    


        grids=[[
                ("最短翻译字数",8),(self.getspinbox(0,500,globalconfig,'minlength'),3),'',
                ("最长翻译字数",8),(self.getspinbox(0,500,globalconfig,'maxlength'),3)  ,('',7)],
                [
                ("在线翻译等待时间(s)",8),(self.getspinbox(1,20,globalconfig,'translatortimeout',step=0.1,double=True ),3),'',
                 ("翻译请求间隔(s)",8),(self.getspinbox(0,10,globalconfig,'transtimeinternal',step=0.1,double=True),3) ,
            ],
        ] 
 
        pretransgrid=[
            [
                ("预翻译采用模糊匹配",8),(self.getsimpleswitch(globalconfig  ,'premtsimiuse'),1),'',
                ("模糊匹配相似度",8),(self.getspinbox(0,500,globalconfig,'premtsimi'),3) , 
            ],[ 
                 (bt,12) ,
            ],['']
        ]

        lixians=set(somedef.fanyi_offline)
        alls=set(globalconfig['fanyi'].keys())
        mt=set(somedef.fanyi_pre)
        online=alls-lixians-mt 
        mianfei=set()
        for _ in online:
            if _ not in translatorsetting : 
                mianfei.add(_) 
        shoufei=online-mianfei  
        offlinegrid=initsome11(self, lixians)   
        onlinegrid=initsome11(self, mianfei ) 
        online_reg_grid=initsome11(self, shoufei) 
        pretransgrid+=initsome11(self,mt )   
        tab=self.makesubtab_lazy(['在线翻译','注册在线翻译','离线翻译','预翻译'],[
            lambda:self.makescroll( self.makegrid(onlinegrid )   ),
            lambda:self.makescroll( self.makegrid(online_reg_grid )   ),
            lambda:self.makescroll( self.makegrid(offlinegrid )   ),
            lambda:self.makescroll( self.makegrid(pretransgrid )   ),
        ]) 

        gridlayoutwidget=self.makegrid(grids )    
        return self.makevbox([gridlayoutwidget,tab])