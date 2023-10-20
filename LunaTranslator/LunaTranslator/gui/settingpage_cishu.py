import functools ,os
from myutils.config import globalconfig   
from gui.inputdialog import getsomepath1,autoinitdialog 
from gui.usefulwidget import getcolorbutton,yuitsu_switch,getsimpleswitch
import gobject
def setTabcishu(self) : 
    self.tabadd_lazy(self.tab_widget, ('辞书设置'), lambda :setTabcishu_l(self)) 


def gethiragrid(self) :
        
          
        grids=[ ] 
        i=0 
        self.ocrswitchs={}
        line=[]
        for name in globalconfig['hirasetting']:
              
            _f='./LunaTranslator/hiraparse/{}.py'.format(name)
            if os.path.exists(_f)==False:  
                continue 
            
            line+=[
                 ((globalconfig['hirasetting'][name]['name']),5),
                 getsimpleswitch(globalconfig['hirasetting'][name],'use',parent=self,name=name,callback=functools.partial(yuitsu_switch,self,globalconfig['hirasetting'],'hiraswitchs',name,gobject.baseobject.starthira),pair='hiraswitchs'), 
                 
                 ] 
            if 'path' in globalconfig['hirasetting'][name]:
                 line+=[getcolorbutton(globalconfig,'',callback=functools.partial(getsomepath1,self,globalconfig['hirasetting'][name]['name'],globalconfig['hirasetting'][name], 'path',globalconfig['hirasetting'][name]['name'],gobject.baseobject.starthira,True),icon='fa.gear',constcolor="#FF69B4")]
            elif 'token' in globalconfig['hirasetting'][name] and 'token_name' in globalconfig['hirasetting'][name]:
                items=[{
                        't':'lineedit','l': globalconfig['hirasetting'][name]['token_name'],'d':globalconfig['hirasetting'][name],'k':'token'
                    },
                    {'t':'okcancel' }]
                line+=[getcolorbutton(globalconfig,'',callback= functools.partial(autoinitdialog,self,  globalconfig['hirasetting'][name]['name'],900,items) ,icon='fa.gear',constcolor="#FF69B4")]
            else:
                  line+=['']
            if i%3==2  :
                grids.append(line) 
                line=[]
            else:
                line+=['']
            i+=1
        if len(line):
             grids.append(line) 
        return grids
def setTabcishu_l(self) :
        
        grids=[ 
                [('分词&假名分析器',10)],
        ]+gethiragrid(self)+ [
                [''],
                [''],
                [('点击单词查词',5),(getsimpleswitch(globalconfig,'usesearchword'),1),getcolorbutton(globalconfig,'',callback=lambda: gobject.baseobject.searchwordW.showsignal.emit(),icon='fa.search',constcolor="#FF69B4"),'',
                 ('点击单词复制',5),(getsimpleswitch(globalconfig,'usecopyword'),1),],

                [''],
                [('辞书',10)],
        ]  

        line=[]
        for i,cishu in enumerate(globalconfig['cishu']): 
                if i%3==0:
                        line=[]
                line+=([
                        (globalconfig['cishu'][cishu]['name'],5),
                        getsimpleswitch(globalconfig['cishu'][cishu],'use',callback=functools.partial( gobject.baseobject.startxiaoxueguan,cishu)),
                        getcolorbutton(globalconfig,'',
                                callback= functools.partial(getsomepath1,self,globalconfig['cishu'][cishu]['name'],globalconfig['cishu'][cishu],'path' ,globalconfig['cishu'][cishu]['name'],functools.partial(gobject.baseobject.startxiaoxueguan,cishu),globalconfig['cishu'][cishu]['isdir'],globalconfig['cishu'][cishu]['filter']) ,icon='fa.gear',constcolor="#FF69B4") 
                                if 'path' in globalconfig['cishu'][cishu] else '' 
                         
                ])
                
                if i%3==2 or i==len(globalconfig['cishu']) -1: 
                        grids.append(line)
                else:
                        line+=['']
        
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        
        return gridlayoutwidget