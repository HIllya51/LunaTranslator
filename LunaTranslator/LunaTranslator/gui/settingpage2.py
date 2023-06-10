 
from PyQt5.QtWidgets import QPushButton  ,QWidget,QVBoxLayout,QLabel
import functools 
from myutils.config import globalconfig ,translatorsetting 
 
from myutils.subproc import subproc_w
from gui.pretransfile import sqlite2json
from myutils.config import globalconfig ,_TR,_TRL,static_data
from myutils.utils import selectdebugfile,splittranslatortypes,checkportavailable
import os ,time,requests,threading
from gui.inputdialog import autoinitdialog 

import time,hashlib
def hashtext(a): 
    return hashlib.md5(a.encode('utf8')).hexdigest()
def initsome11(self,l,label=None): 
    grids=[]
    if label:
        grids.append(
            [(label,8)]
        )
    i=0 
    line=[]
    for fanyi in globalconfig['fanyi']:
        
        if fanyi not in l:
            continue
 
        _f='./Lunatranslator/translator/{}.py'.format(fanyi)
        if fanyi!='selfbuild' and os.path.exists(_f)==False :  
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
            last=self.getcolorbutton(globalconfig,'',callback=lambda:selectdebugfile('./userconfig/selfbuild.py' ),icon='fa.gear',constcolor="#FF69B4")
        else:
            last=''
        line+=[(globalconfig['fanyi'][fanyi]['name'],6),
        self.getsimpleswitch(globalconfig['fanyi'][fanyi],'use',callback=functools.partial( self.object.prepare ,fanyi)),
        self.getcolorbutton(globalconfig['fanyi'][fanyi],'color',name="fanyicolor_"+fanyi,callback=functools.partial(self.ChangeTranslateColor,fanyi,None,self,"fanyicolor_"+fanyi)),last ] 
 
        if i%3==0  :
            grids.append(line)
            line=[]
        else:
            line+=['']
    if len(line) :
        grids.append(line)
    return grids
def setTabTwo(self) : 
    self.tabadd_lazy(self.tab_widget, ('翻译设置'), lambda :setTabTwo_lazy(self)) 
def settab2d(self):
    self.statuslabel=QLabel()
    def checkconnected(): 
        lixians,pre,mianfei,develop,shoufei=splittranslatortypes()
        while True:
            port=globalconfig['debugport']
            try:
                requests.get('http://127.0.0.1:{}/json/list'.format(port)).json()
                self.statuslabel.setText(_TR("连接成功"))
            except:
                if (checkportavailable(port)):
                    self.statuslabel.setText(_TR("连接失败"))
                    needstart=any([globalconfig['fanyi'][dev]['use'] for dev in develop])
                    if needstart:
                        _path=globalconfig['chromepath']
                    
                        call="\"%s\" --disable-extensions --remote-allow-origins=* --disable-gpu --no-first-run --remote-debugging-port=%d --user-data-dir=\"%s\"" %(_path ,port,os.path.abspath('./chrome_cache/'+hashtext(_path))) 
                        print(call)
                        self.engine=subproc_w(call) 
                else:
                    self.statuslabel.setText(_TR("端口冲突"))
            time.sleep(1)
    threading.Thread(target=checkconnected).start()
def setTabTwo_lazy(self) :
         
         
        bt = QPushButton(_TR("导出翻译记录为json文件")  ) 
        bt.clicked.connect(lambda x:sqlite2json(self)) 
    

         
        _fuzainum=self.getspinbox(1,99999,globalconfig,'loadbalance_oncenum',step=1)
        _fuzainum.setEnabled(globalconfig['loadbalance'])
        grids=[[
                ("最短翻译字数",8),(self.getspinbox(0,9999,globalconfig,'minlength'),2),'',
                ("最长翻译字数",8),(self.getspinbox(0,9999,globalconfig,'maxlength'),2) ,'',
        ],
                
            [
                ("使用持久化翻译缓存",8),(self.getsimpleswitch(globalconfig,'uselongtermcache')),'','',
                ('显示错误信息',8),(self.getsimpleswitch(globalconfig  ,'showtranexception'),1),'','',
                ('翻译请求间隔(s)',8),(self.getspinbox(0,9999,globalconfig,'requestinterval',step=0.1,double=True),2)
            ],
            [
                ("均衡负载",8),(self.getsimpleswitch(globalconfig,'loadbalance',callback=lambda x:_fuzainum.setEnabled(x))),'','',
                ("单次负载个数",8),(_fuzainum,2) ,
            ]

        ] 
        online_reg_grid=[
            [("若有多个api key，用|将每个key连接后填入，即可轮流使用",24)]
        ]
        pretransgrid=[
            [
                ("预翻译采用模糊匹配",8),(self.getsimpleswitch(globalconfig  ,'premtsimiuse'),1),'',
                ("模糊匹配相似度",8),(self.getspinbox(0,500,globalconfig,'premtsimi'),3) , 
            ],[ 
                 (bt,12) ,
            ],['']
        ] 
        _items=[
            {'t':'file','dir':False,'filter':'*.exe','l':'chrome路径','d':globalconfig,'k':'chromepath'},
            {'t':'okcancel' },
        ]

        developgrid=[
            [('chrome路径',8),(self.getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self, 'chrome路径',900,_items),icon='fa.gear',constcolor="#FF69B4"))],
            [("端口号",8),(self.getspinbox(0,65535,globalconfig,'debugport'),3) ,],
            [(self.statuslabel,16)],
            ['']
        ]
        lixians,pre,mianfei,develop,shoufei=splittranslatortypes()
        
        offlinegrid=initsome11(self, lixians) 
        onlinegrid=initsome11(self, mianfei ) 
        developgrid+=initsome11(self, develop ) 
        online_reg_grid+=initsome11(self, shoufei) 
        pretransgrid+=initsome11(self,pre )   
        tab=self.makesubtab_lazy(['在线翻译','develop','注册在线翻译','离线翻译','预翻译'],[
            lambda:self.makescroll( self.makegrid(onlinegrid )   ),
            lambda:self.makescroll( self.makegrid(developgrid )   ),
            lambda:self.makescroll( self.makegrid(online_reg_grid )   ),
            lambda:self.makescroll( self.makegrid(offlinegrid )   ),
            lambda:self.makescroll( self.makegrid(pretransgrid )   ),
        ]) 

        gridlayoutwidget=self.makegrid(grids )    
        return self.makevbox([gridlayoutwidget,tab])