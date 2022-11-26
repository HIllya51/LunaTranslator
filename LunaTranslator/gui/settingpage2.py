 
from PyQt5.QtWidgets import QWidget,QLabel,QStyle ,QPushButton,QGridLayout,QSpinBox,QComboBox,QScrollArea,QLineEdit,QApplication,QFileDialog
from PyQt5.QtGui import QColor 
from PyQt5.QtCore import Qt 
import functools,sqlite3
from utils.config import globalconfig ,translatorsetting
import os,json
from traceback import print_exc

from utils.config import globalconfig ,_TR,_TRL
import time
import importlib
import socket
from gui.inputdialog import autoinitdialog
def fanyiselect(self, who,checked ):
            if checked :  
                self.object.prepare(who)  
            globalconfig['fanyi'][who]['use']=checked 
            
            
def initsome11(self,l,label,grids): 
    grids.append(
        [(label,4)]
    )
    i=0
    for fanyi in globalconfig['fanyi']:
        if i%3==0:
            line=[]
        if fanyi not in l:
            continue
        i+=1
        try:
            importlib.import_module('translator.'+fanyi)
        except:
            print_exc()
            continue
        
        
        if fanyi in translatorsetting :
            fileselect={
                'json文件':{'dir':False,'filter':'*.json'},
                'sqlite文件':{'dir':False,'filter':'*.sqlite'},
                'xml文件':{'dir':False,'filter':'*.xml'},
                'txt文件':{'dir':False,'filter':'*.txt'},
                'xml目录':{'dir':True,'filter':''},
            }
            items=[] 
            for arg in translatorsetting[fanyi]['args']: 
                items.append({
                        't':'lineedit','l':arg,'d':translatorsetting[fanyi]['args'],'k':arg
                    })
                if arg in fileselect:
                    items[-1].update({
                        't':'file',
                        'dir':fileselect[arg]['dir'],
                        'filter':fileselect[arg]['filter']
                    }) 
                elif arg=='路径':
                    items[-1].update({
                        't':'file',
                        'dir':True 
                    }) 
            items.append({'t':'okcancel' })
            last=self.getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self, (globalconfig['fanyi'][fanyi]['name'])+ ('设置'),900,items),icon='fa.gear',constcolor="#FF69B4")
        else:
            last=''
        line+=[(globalconfig['fanyi'][fanyi]['name'],6),
        self.getsimpleswitch(globalconfig['fanyi'][fanyi],'use',callback=functools.partial( fanyiselect,self,fanyi)),
        self.getcolorbutton(globalconfig['fanyi'][fanyi],'color',name="fanyicolor_"+fanyi,callback=functools.partial(self.ChangeTranslateColor,fanyi,None,self,"fanyicolor_"+fanyi)),last ] 


        if i%3==0 or i==len(l):
            grids.append(line)
        else:
            line+=['']
def initfanyiswitchs_auto11(self,grids):  
        lixians=set(('jb7','dreye','kingsoft'))
        alls=set(globalconfig['fanyi'].keys())
        mt=set(('rengong','premt','rengong_vnr','rengong_msk'))
        online=alls-lixians-mt

        mianfei=set()
        for _ in online:
            if _ not in translatorsetting : 
                mianfei.add(_)
        
        shoufei=online-mianfei 
 
        initsome11(self, lixians,'离线翻译',grids)  
        grids.append([''])
        initsome11(self, mianfei,'在线翻译',grids)
        grids.append([''])
        initsome11(self, shoufei,'注册在线翻译',grids)
        grids.append([''])
        initsome11(self,mt,'预翻译',grids) 
def setTabTwo(self) :
        def __timeout(x):
    
            globalconfig.__setitem__('translatortimeout',x)
            socket.setdefaulttimeout(globalconfig['translatortimeout'])

        def _setproxy(x):
            globalconfig.__setitem__('useproxy',x)
            if x:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
            else:
                os.environ['https_proxy']='' 
                os.environ['http_proxy']=''
        #_setproxy(globalconfig['useproxy'])
        if globalconfig['useproxy']:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
        proxy=QLineEdit(globalconfig['proxy'])
        btn=QPushButton(_TR('确定' ))
        def __resetproxy(x):
            globalconfig.__setitem__('proxy',proxy.text())
            if globalconfig['useproxy']:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
        btn.clicked.connect(lambda x: __resetproxy(x))
        transkirokuuse =QComboBox( )  
        transkirokuuse.addItems(_TRL([globalconfig['fanyi'][k]['name'] for k  in globalconfig['fanyi']]))
        transkirokuuse.setCurrentIndex(list(globalconfig['fanyi'].keys()).index(globalconfig['transkirokuuse']))
       
        def changerengong(x):
            globalconfig.__setitem__('transkirokuuse',list(globalconfig['fanyi'].keys())[x])
            self.object.translation_ui.startTranslater()
        transkirokuuse.currentIndexChanged.connect(changerengong)
        self.transkirokuuse=transkirokuuse
        bt = QPushButton(_TR("导出sqlite文件为json文件")  )

        def _sqlite2json():
                f=QFileDialog.getOpenFileName(filter="*.sqlite")
                if f[0]!='' :
                        try:
                                sql=sqlite3.connect(f[0],check_same_thread=False)
                                ret=sql.execute(f'SELECT * FROM artificialtrans  ').fetchall()
                                js={}
                                transkirokuuse=list(globalconfig['fanyi'].keys())[globalconfig['transkirokuuse']]
                                for _aret  in ret:
                                    if len(_aret)==4:
                                        #旧版兼容
                                         
                                        _id,source,mt,ut=_aret
                                        js[source]={'userTrans':ut,'machineTrans':mt}
                                    elif len(_aret)==3: 
                                        _id,source,mt =_aret
                                        js[source]={'userTrans':'','machineTrans':''}
                                        mtjs=json.loads(mt)
                                        for _i,_t in enumerate(mtjs):
                                            if  _i==0 or _t==transkirokuuse:
                                                js[source]['machineTrans']=mtjs[_t]
                                                
                                            js[source]['inferrence_'+str(_i)]=mtjs[_t]
                                            js[source]['api_'+str(_i)]=_t
                                with open(os.path.join(os.path.dirname(f[0]), os.path.basename(f[0]).replace('.'+os.path.basename(f[0]).split('.')[-1],'.json')),'w',encoding='utf8') as ff:
                                        ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
                        except:
                                print_exc()
        bt.clicked.connect(lambda x:_sqlite2json()) 
 
  

        grids=[
            [
                ("是否显示翻译器名称",6),(self.getsimpleswitch(globalconfig  ,'showfanyisource'),1),'','','',
                ("源语言",6),(self.getsimplecombobox(_TRL(['日文','英文']),globalconfig,'srclang'),3),'',
                ("目标语言",6),(self.getsimplecombobox(_TRL(['中文','英文']),globalconfig,'tgtlang'),3) ,
            ],
            [
                ("最短翻译字数",6),(self.getspinbox(0,500,globalconfig,'minlength'),3),'',
                ("最长翻译字数",6),(self.getspinbox(0,500,globalconfig,'maxlength'),3),],
            [
                ("在线翻译超时(s)",6),(self.getspinbox(1,20,globalconfig,'translatortimeout',step=0.1,double=True,callback=lambda x:__timeout(x)),3),'',
                 ("翻译请求间隔(s)",6),(self.getspinbox(0,10,globalconfig,'transtimeinternal',step=0.1,double=True),3),''
                 ("TXT读取间隔(s)",6),(self.getspinbox(0,10,globalconfig,'txtreadlineinterval',step=0.1,double=True),3),
            ],
            [
                ("预翻译采用模糊匹配",6),(self.getsimpleswitch(globalconfig  ,'premtsimiuse'),1),'','','',
                ("模糊匹配相似度限制",6),(self.getspinbox(0,500,globalconfig,'premtsimi'),3),'', 
            ],[
                ("使用代理(ip:port)",6),(self.getsimpleswitch(globalconfig  ,'useproxy',callback=lambda x: _setproxy(x)),1),'',
                (proxy,8),(btn,3),  
            ],
            
                [('录制翻译文件',6),(self.getsimpleswitch(globalconfig,'transkiroku'),1),'',
                 ('导出的第一翻译源',6),(transkirokuuse,6),
                 
                 (bt,8) ,
                 ],
            ['']
        ] 
        initfanyiswitchs_auto11(self,grids)
         
        self.yitiaolong("翻译设置",grids)