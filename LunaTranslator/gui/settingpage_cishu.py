import functools 
from utils.config import globalconfig   
from gui.inputdialog import getsomepath1,autoinitdialog 
def setTabcishu(self) :
        
        mojiconfigitems=[{
                        't':'lineedit','l':'Moji NLT Token','d':globalconfig['hirasetting']['mojinlt'],'k':'token'
                    },
                    {'t':'okcancel' }]
        grids=[ 
                [('分词&假名分析器',10)],
                [       
                        ('内置',5),(self.getsimpleswitch(globalconfig['hirasetting']['local'],'use',name='local',callback= functools.partial(self.yuitsu_switch,'hirasetting','hiraswitchs','local',self.object.starthira),pair='hiraswitchs'),1),'','',

                        ('MeCab',5),
                        (self.getsimpleswitch(globalconfig['hirasetting']['mecab'],'use',name='mecab',callback= functools.partial(self.yuitsu_switch,'hirasetting','hiraswitchs','mecab',self.object.starthira),pair='hiraswitchs'),1),
                        self.getcolorbutton(globalconfig,'',callback=lambda  :getsomepath1(self,'mecab',globalconfig['hirasetting']['mecab'],'path' ,'mecab',lambda  :self.object.starthira(),True) ,icon='fa.gear',constcolor="#FF69B4"),'',

                        ('mojinlt',5),
                        (self.getsimpleswitch(globalconfig['hirasetting']['mojinlt'],'use',name='mojinlt',callback= functools.partial(self.yuitsu_switch,'hirasetting','hiraswitchs','mojinlt',self.object.starthira),pair='hiraswitchs'),1),
                        self.getcolorbutton(globalconfig,'',callback= functools.partial(autoinitdialog,self,  ('token设置'),900,mojiconfigitems) ,icon='fa.gear',constcolor="#FF69B4")
                ],
                [''],
                
                [''],
                [('开启点击原文查词',5),(self.getsimpleswitch(globalconfig,'usesearchword'),1),self.getcolorbutton(globalconfig,'',callback=lambda: self.object.searchwordW.showsignal.emit(),icon='fa.search',constcolor="#FF69B4")],

                [''],
                [('辞书',10)],
        ]  

        line=[]
        for i,cishu in enumerate(globalconfig['cishu']):
                if i%3==0:
                        line=[]
                line+=([
                        (globalconfig['cishu'][cishu]['name'],5),
                        self.getsimpleswitch(globalconfig['cishu'][cishu],'use',callback=functools.partial( self.object.startxiaoxueguan,cishu)),
                        self.getcolorbutton(globalconfig,'',
                                callback= functools.partial(getsomepath1,self,globalconfig['cishu'][cishu]['name'],globalconfig['cishu'][cishu],'path' ,globalconfig['cishu'][cishu]['name'],functools.partial(self.object.startxiaoxueguan,cishu),globalconfig['cishu'][cishu]['isdir'],globalconfig['cishu'][cishu]['filter']) ,icon='fa.gear',constcolor="#FF69B4") 
                                if 'path' in globalconfig['cishu'][cishu] else '' 
                         
                ])
                
                if i%3==2 or i==len(globalconfig['cishu']) : 
                        grids.append(line)
                else:
                        line+=['']
        
   
        self.yitiaolong("辞书设置",grids)