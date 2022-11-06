 
from PyQt5.QtWidgets import QWidget,QLabel,QStyle ,QPushButton,QGridLayout,QSpinBox,QComboBox,QScrollArea,QLineEdit,QApplication
from PyQt5.QtGui import QColor 
from PyQt5.QtCore import Qt 
import functools
from utils.config import globalconfig ,translatorsetting
import os
import qtawesome,sys

import gui.switchbutton
import gui.attachprocessdialog  
from traceback import print_exc
import gui.selecthook 
import time
import importlib
import socket
from gui.inputdialog import autoinitdialog
def fanyiselect(self, who,checked ):
            if checked : 
                globalconfig['fanyi'][who]['use']=True
                self.object.prepare(who) 
            else:
                globalconfig['fanyi'][who]['use']=False 
def initsome11(self,l,label,grids): 
    grids.append(
        [(QLabel(label),4)]
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
        
        
        if 'argsfile' in globalconfig['fanyi'][fanyi]:
             
            items=[] 
            for arg in translatorsetting[fanyi]['args']: 
                items.append({
                        't':'lineedit','l':arg,'d':translatorsetting[fanyi]['args'],'k':arg
                    })
                if arg=='json文件' or arg=='sqlite文件':
                    items[-1].update({
                        't':'file',
                        'dir':False,
                        'filter':"*.json" if arg=='json文件' else "*.sqlite"
                    }) 
                elif arg=='路径':
                    items[-1].update({
                        't':'file',
                        'dir':True 
                    }) 
            items.append({'t':'okcancel' })
            last=self.getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self,globalconfig['fanyi'][fanyi]['name']+'设置',900,items),icon='fa.gear',constcolor="#FF69B4")
        else:
            last=''
        line+=[(QLabel(globalconfig['fanyi'][fanyi]['name']),4),
        self.getsimpleswitch(globalconfig['fanyi'][fanyi],'use',callback=functools.partial( fanyiselect,self,fanyi)),
        self.getcolorbutton(globalconfig['fanyi'][fanyi],'color',name="fanyicolor_"+fanyi,callback=functools.partial(self.ChangeTranslateColor,fanyi,None,self,"fanyicolor_"+fanyi)),last ] 


        if i%3==0 or i==len(l):
            grids.append(line)
        else:
            line+=['']
def initfanyiswitchs_auto11(self,grids):  
        lixians=set(('jb7','dreye','kingsoft'))
        alls=set(globalconfig['fanyi'].keys())
        mt=set(('rengong','premt'))
        online=alls-lixians-mt

        mianfei=set()
        for _ in online:
            if 'argsfile' not in globalconfig['fanyi'][_]:
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
        _setproxy(globalconfig['useproxy'])

        proxy=QLineEdit(globalconfig['proxy'])
        btn=QPushButton('确定' )
        def __resetproxy(x):
            globalconfig.__setitem__('proxy',l.text())
            if globalconfig['useproxy']:
                os.environ['https_proxy']=globalconfig['proxy'] 
                os.environ['http_proxy']=globalconfig['proxy'] 
        btn.clicked.connect(lambda x: __resetproxy())
        
  

        grids=[
            [
                (QLabel("是否显示翻译器名称"),4),(self.getsimpleswitch(globalconfig  ,'showfanyisource'),1),'','','',
                (QLabel("源语言"),4),(self.getsimplecombobox(['日文','英文'],globalconfig,'srclang'),3),'',
                (QLabel("目标语言"),4),(self.getsimplecombobox(['中文','英文'],globalconfig,'tgtlang'),3) ,
            ],
            [
                (QLabel("最短翻译字数"),4),(self.getspinbox(0,500,globalconfig,'minlength'),3),'',
                (QLabel("最长翻译字数"),4),(self.getspinbox(0,500,globalconfig,'maxlength'),3),'',
                (QLabel("在线翻译超时(s)"),4),(self.getspinbox(1,20,globalconfig,'translatortimeout',callback=lambda x:__timeout(x)),3),

            ],
            [
                (QLabel("预翻译采用模糊匹配"),4),(self.getsimpleswitch(globalconfig  ,'premtsimiuse'),1),'','','',
                (QLabel("模糊匹配相似度限制"),5),(self.getspinbox(0,500,globalconfig,'premtsimi'),2),'', 
            ],[
                (QLabel("使用代理(ip:port)"),4),(self.getsimpleswitch(globalconfig  ,'useproxy',callback=lambda x: _setproxy(x)),1),
                (proxy,6),(btn,2),'','','', 
            ],
            ['']
        ] 
        initfanyiswitchs_auto11(self,grids)
         
        self.yitiaolong("翻译设置",grids)