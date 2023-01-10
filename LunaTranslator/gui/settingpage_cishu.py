import functools 
from utils.config import globalconfig 
import functools

from traceback import print_exc
import gui.selecthook  
from gui.inputdialog import getsomepath1,autoinitdialog
def hirachange(self,who,checked):   
     
    if checked : 
         
        for k in self.hiraswitchs: 
                
                if globalconfig['hirasetting'][k]['use']==True:
                     
                    self.hiraswitchs[k].setChecked(False) 
                    globalconfig['hirasetting'][k]['use']=False
        globalconfig['hirasetting'][who]['use']=True
    else:
        globalconfig['hirasetting'][who]['use']=False  
         
    
    if checked : 
        try:
                self.object.starthira()  
        except:
                print_exc()
def setTabcishu(self) :
        
        mojiconfigitems=[{
                        't':'lineedit','l':'Moji NLT Token','d':globalconfig['hirasetting']['mojinlt'],'k':'token'
                    },
                    {'t':'okcancel' }]
        grids=[ 
                [('分词&假名分析器',10)],
                [       
                        ('内置',4),(self.getsimpleswitch(globalconfig['hirasetting']['local'],'use',name='localhiraswitch',callback= functools.partial(hirachange,self,'local')),1),'',

                        ('MeCab',4),
                        (self.getsimpleswitch(globalconfig['hirasetting']['mecab'],'use',name='mecabhiraswitch',callback= functools.partial(hirachange,self,'mecab')),1),
                        self.getcolorbutton(globalconfig,'',callback=lambda  :getsomepath1(self,'mecab',globalconfig['hirasetting']['mecab'],'path' ,'mecab',lambda  :self.object.starthira(),True) ,icon='fa.gear',constcolor="#FF69B4"),'',

                        ('mojinlt',4),
                        (self.getsimpleswitch(globalconfig['hirasetting']['mojinlt'],'use',name='mojinlthiraswitch',callback= functools.partial(hirachange,self,'mojinlt')),1),
                        self.getcolorbutton(globalconfig,'',callback= functools.partial(autoinitdialog,self,  ('token设置'),900,mojiconfigitems) ,icon='fa.gear',constcolor="#FF69B4")
                ],
                [''],
                
                [''],
                [('开启快捷查词(点击原文可查词)',10),(self.getsimpleswitch(globalconfig,'usesearchword'),1),self.getcolorbutton(globalconfig,'',callback=self.object.translation_ui.searchwordW.show,icon='fa.search',constcolor="#FF69B4")],

                [''],
                [('辞书',10)],
        ]
        self.hiraswitchs={'local':self.localhiraswitch,
                            'mecab':self.mecabhiraswitch, 
                            'mojinlt':self.mojinlthiraswitch }
        def cishuselect(self, who,checked ): 
            globalconfig['cishu'][who]['use']=checked 
            self.object.startxiaoxueguan(who) 
        for cishu in globalconfig['cishu']:
                grids.append([
                        (globalconfig['cishu'][cishu]['name'],10),
                        self.getsimpleswitch(globalconfig['cishu'][cishu],'use',callback=functools.partial( cishuselect,self,cishu)),
                        self.getcolorbutton(globalconfig,'',
                                callback= functools.partial(getsomepath1,self,globalconfig['cishu'][cishu]['name'],globalconfig['cishu'][cishu],'path' ,globalconfig['cishu'][cishu]['name'],functools.partial(self.object.startxiaoxueguan,cishu),globalconfig['cishu'][cishu]['isdir'],globalconfig['cishu'][cishu]['filter']) ,icon='fa.gear',constcolor="#FF69B4") 
                                if 'path' in globalconfig['cishu'][cishu] else ''
                ])
                 
        
   
        self.yitiaolong("辞书设置",grids)