import functools ,os
from utils.config import globalconfig   
from gui.inputdialog import getsomepath1,autoinitdialog 

def setTabcishu(self) : 
    self.tabadd_lazy(self.tab_widget, ('辞书设置'), lambda :setTabcishu_l(self)) 


def gethiragrid(self) :
        
          
        grids=[ ] 
        i=0 
        self.ocrswitchs={}
        line=[]
        for name in globalconfig['hirasetting']:
              
            _f=f'./LunaTranslator/hiraparse/{name}.py'
            if os.path.exists(_f)==False:  
                continue 
            
            line+=[
                 ((globalconfig['hirasetting'][name]['name']),5),
                 self.getsimpleswitch(globalconfig['hirasetting'][name],'use',name=name,callback=functools.partial(self.yuitsu_switch,'hirasetting','hiraswitchs',name,self.object.starthira),pair='hiraswitchs'), 
                 
                 ] 
            if 'path' in globalconfig['hirasetting'][name]:
                 line+=[self.getcolorbutton(globalconfig,'',callback=functools.partial(getsomepath1,self,globalconfig['hirasetting'][name]['name'],globalconfig['hirasetting'][name], 'path',globalconfig['hirasetting'][name]['name'],self.object.starthira,True),icon='fa.gear',constcolor="#FF69B4")]
            elif 'token' in globalconfig['hirasetting'][name] and 'token_name' in globalconfig['hirasetting'][name]:
                items=[{
                        't':'lineedit','l': globalconfig['hirasetting'][name]['token_name'],'d':globalconfig['hirasetting'][name],'k':'token'
                    },
                    {'t':'okcancel' }]
                line+=[self.getcolorbutton(globalconfig,'',callback= functools.partial(autoinitdialog,self,  globalconfig['hirasetting'][name]['name'],900,items) ,icon='fa.gear',constcolor="#FF69B4")]
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
                
                if i%3==2 or i==len(globalconfig['cishu']) -1: 
                        grids.append(line)
                else:
                        line+=['']
        
        gridlayoutwidget=self.makegrid(grids )  
        gridlayoutwidget=self.makescroll( gridlayoutwidget  )
        
        return gridlayoutwidget