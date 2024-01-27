  
import functools  

from PyQt5.QtWidgets import  QDialog,QLabel ,QLineEdit,QSpinBox,QPushButton ,QTableView,   QVBoxLayout,QHBoxLayout,QHeaderView ,QTextEdit,QHBoxLayout,QWidget,QMenu,QAction
from PyQt5.QtCore import QSize,Qt,pyqtSignal,QPoint
from PyQt5.QtGui import QCloseEvent, QStandardItem, QStandardItemModel 
from traceback import print_exc
from myutils.config import globalconfig ,postprocessconfig,noundictconfig,transerrorfixdictconfig,_TR,_TRL,defaultglobalconfig 
import functools ,gobject
from gui.usefulwidget import getcolorbutton,getsimpleswitch
from gui.codeacceptdialog import codeacceptdialog  
from gui.inputdialog import getsomepath1  ,postconfigdialog 
from myutils.utils import selectdebugfile
from myutils.wrapper import Singleton
from myutils.config import   savehook_new_list,savehook_new_data
import copy
from myutils.post import POSTSOLVE
def savegameprocesstext():
    try:
        try:
            with open('./userconfig/mypost.py','r',encoding='utf8') as ff:
                _mypost=ff.read()
            with open('./userconfig/posts/{}.py'.format(gobject.baseobject.textsource.uuname),'w',encoding='utf8') as ff:
                ff.write(_mypost)
        except:
            _mypost=None
        ranklist=[]
        postargs={}
        for postitem in globalconfig['postprocess_rank']:
            if postitem not in postprocessconfig:continue
            if postprocessconfig[postitem]['use']:
                ranklist.append(postitem)
                postargs[postitem]=copy.deepcopy(postprocessconfig[postitem])
        exepath=gobject.baseobject.textsource.pname
        savehook_new_data[exepath]['save_text_process_info']={
            'postprocessconfig':postargs,
            'rank':ranklist,
            'mypost':gobject.baseobject.textsource.uuname
        }
        if savehook_new_data[exepath]['use_saved_text_process']==False:
            savehook_new_data[exepath]['use_saved_text_process']=True
    except:
        print_exc()
def settab7direct(self):
    self.comparelayout=getcomparelayout(self)
    self.button_noundict=getcolorbutton(globalconfig,'' ,callback=lambda x:  noundictconfigdialog(self,noundictconfig,'专有名词翻译设置(游戏ID 0表示全局)'),icon='fa.gear',constcolor="#FF69B4")
    self.button_fix=getcolorbutton(globalconfig,'',callback=lambda x:  noundictconfigdialog1(self,transerrorfixdictconfig,'翻译结果替换设置',['翻译','替换'],'./userconfig/transerrorfixdictconfig.json'),icon='fa.gear',constcolor="#FF69B4")
def setTab7(self) :  
        self.tabadd_lazy(self.tab_widget, ('文本处理'), lambda :setTab7_lazy(self)) 
def getcomparelayout(self):
    
    layout=QHBoxLayout()
    fromtext=QTextEdit()
    totext=QTextEdit()
    solvebutton=getcolorbutton(globalconfig,'',callback=lambda :totext.setPlainText(POSTSOLVE(fromtext.toPlainText())),icon='fa.chevron-right',constcolor="#FF69B4")
    
    layout.addWidget(fromtext)
    layout.addWidget(solvebutton) 
    layout.addWidget(totext)
    w=QWidget()
    w.setLayout(layout)
    
    def _(s):
        fromtext.setPlainText(s)
        totext.setPlainText(POSTSOLVE(fromtext.toPlainText()))
    self.showandsolvesig.connect(_)
    return w
def setTab7_lazy(self) :   
        grids=[
            [('预处理方法',6),'','',('调整执行顺序',6)]
        ] 
        if set(postprocessconfig.keys())!=set(globalconfig['postprocess_rank']):
            globalconfig['postprocess_rank']=list(postprocessconfig.keys())
        sortlist=globalconfig['postprocess_rank']
        savelist=[]
        savelay=[] 
        def changerank( item,up):

            ii=sortlist.index(item)
            if up and ii==0:
                return
            if up==False and ii==len(sortlist)-1:
                return
            headoffset=1
            toexchangei=ii+(-1 if up else 1)
            sortlist[ii],sortlist[toexchangei]=sortlist[toexchangei],sortlist[ii] 
            for i,ww in enumerate(savelist[ii+headoffset]):

                w1=(savelay[0].indexOf(ww))
                w2=savelay[0].indexOf(savelist[toexchangei+headoffset][i])
                p1=savelay[0].getItemPosition(w1)
                p2=savelay[0].getItemPosition(w2) 
                savelay[0].removeWidget(ww)
                savelay[0].removeWidget(savelist[toexchangei+headoffset][i])
                 
                savelay[0].addWidget(savelist[toexchangei+headoffset][i],*p1)
                savelay[0].addWidget(ww,*p2)
            savelist[ii+headoffset],savelist[toexchangei+headoffset]=savelist[toexchangei+headoffset],savelist[ii+headoffset] 
        for i,post in enumerate(sortlist): 
            if post=='_11':
                config=(getcolorbutton(globalconfig,'',callback=lambda:selectdebugfile('./userconfig/mypost.py' ),icon='fa.gear',constcolor="#FF69B4")) 
            else:
                if post not in postprocessconfig:
                    continue
                if post=='_remove_chaos':
                    config=(getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self))) 
                elif 'args' in postprocessconfig[post]:
                    
                    config=(getcolorbutton(globalconfig,'',callback= functools.partial( postconfigdialog,self,postprocessconfig[post]['args'],postprocessconfig[post]['name']),icon='fa.gear',constcolor="#FF69B4")) 
                else:
                    config=('')
             
            button_up=(getcolorbutton(globalconfig,'',callback= functools.partial(changerank, post,True),icon='fa.arrow-up',constcolor="#FF69B4"))
            button_down=(getcolorbutton(globalconfig,'',callback= functools.partial(changerank, post,False),icon='fa.arrow-down',constcolor="#FF69B4")) 
             
            l=[((postprocessconfig[post]['name'] ),6),
                getsimpleswitch(postprocessconfig[post],'use'),
                config,
                button_up,
                button_down
            ]
            grids.append(l)
         
    
        grids2=[ 
            [(('使用专有名词翻译' ),6),
                getsimpleswitch(noundictconfig,'use'),
                self.button_noundict],
            [(('使用翻译结果修正' ),6),
                getsimpleswitch(transerrorfixdictconfig,'use'),
                self.button_fix],
            [(('使用VNR共享辞书' ),6),
                getsimpleswitch(globalconfig['gongxiangcishu'],'use',callback = gobject.baseobject.loadvnrshareddict ),
                getcolorbutton(globalconfig,'',callback=lambda x:  getsomepath1(self,'共享辞书',globalconfig['gongxiangcishu'],'path','共享辞书',gobject.baseobject.loadvnrshareddict,False,'*.xml') ,icon='fa.gear',constcolor="#FF69B4"),'','','','','',''],
            
        ]   
        def __():
            _w=self.makescroll(self.makegrid(grids,True,savelist,savelay )  ) 
            _w.setContextMenuPolicy(Qt.CustomContextMenu)
            def showmenu(p:QPoint):  
                        
                try:  
                    gobject.baseobject.textsource.pname  #检查是否为texthook
                        
                    menu=QMenu(_w)  
                    save=QAction(_TR("保存当前游戏的文本处理流程")) 
                    menu.addAction(save)
                    action=menu.exec(_w.cursor().pos())
                    if action==save:
                        savegameprocesstext()
                except:
                    pass
        
            _w.customContextMenuRequested.connect(showmenu  )
            return _w
        tab=self.makesubtab_lazy(['文本预处理', '翻译优化'],[
            lambda:__(),
            lambda:self.makescroll(self.makegrid(grids2 )  )
        ])   
  
        return self.makevbox([tab,self.comparelayout ]) 

@Singleton
class noundictconfigdialog1(QDialog):
    def __init__(self,parent,configdict,title,label=[  '原文','翻译'] ,_=None) -> None:
        super().__init__(parent,Qt.WindowCloseButtonHint)
            
        self.setWindowTitle(_TR(title))
        #self.setWindowModality(Qt.ApplicationModal)
        
        formLayout = QVBoxLayout(self)  # 配置layout
            
        model=QStandardItemModel(len(list(configdict['dict'].keys())),1 , self)
        row=0
        for key in  (configdict['dict']):                                   # 2
                
                item = QStandardItem( key )
                model.setItem(row, 0, item)
                item = QStandardItem(configdict['dict'][key] )
                model.setItem(row, 1, item)
                row+=1
        model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(self)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)

        search=QHBoxLayout()
        searchcontent=QLineEdit()
        search.addWidget(searchcontent)
        button4=QPushButton()
        button4.setText(_TR('搜索'))
        def clicked4():
            text=searchcontent.text()
            
            rows=model.rowCount() 
            cols=model.columnCount()
            for row in range(rows):
                ishide=True
                for c in range(cols):
                    if text in model.item(row,c).text(): 
                        ishide=False
                        break 
                table.setRowHidden(row,ishide)

                
        button4.clicked.connect(clicked4)
        search.addWidget(button4)
         

        button=QPushButton(self)
        button.setText(_TR('添加行'))
        def clicked1(): 
            model.insertRow(0,[ QStandardItem(''),QStandardItem('')]) 
        button.clicked.connect(clicked1)
        button2=QPushButton(self)
        button2.setText(_TR('删除选中行'))
        def clicked2():
            
            model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
        self.button=button
        self.model=model
        self.configdict=configdict
        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)
        formLayout.addWidget(button2) 
        self.resize(QSize(600,400))
        self.show()
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        rows=self.model.rowCount() 
        newdict={}
        for row in range(rows):
            if self.model.item(row,0).text()=="":
                continue
            newdict[self.model.item(row,0).text()]=self.model.item(row,1).text()
        self.configdict['dict']=newdict 
@Singleton
class noundictconfigdialog(QDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        rows=self.model.rowCount() 
        newdict={}
        for row in range(rows):
            if self.model.item(row,1).text()=="":
                continue
            if self.model.item(row,1).text() not in newdict:
                newdict[self.model.item(row,1).text()]=[self.model.item(row,0).text(),self.model.item(row,2).text()]
            else:
                newdict[self.model.item(row,1).text()]+=[self.model.item(row,0).text(),self.model.item(row,2).text()]
        self.configdict['dict']=newdict  
    def __init__(self,parent,configdict,title,label=['游戏ID MD5' ,'原文','翻译'] ,_=None) -> None:
        super().__init__(parent,Qt.WindowCloseButtonHint)
        
        self.setWindowTitle(_TR(title))
        #self.setWindowModality(Qt.ApplicationModal)
        
        formLayout = QVBoxLayout(self)  # 配置layout
            
        model=QStandardItemModel(len(list(configdict['dict'].keys())),1 , self)
        row=0
        for key in  (configdict['dict']):                                   # 2
                if type(configdict['dict'][key])==str:
                    configdict['dict'][key]=["0",configdict['dict'][key]]
                 
                for i in range(len( configdict['dict'][key])//2):
                    item = QStandardItem( configdict['dict'][key][i*2] )
                    model.setItem(row, 0, item)
                    item = QStandardItem(key  )
                    model.setItem(row, 1, item)
                    item = QStandardItem( configdict['dict'][key][1+i*2] )
                    model.setItem(row, 2, item)
                    row+=1
        model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(self)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        button=QPushButton(self)
        button.setText(_TR('添加行'))
        def clicked1(): 
            try:
                md5=gobject.baseobject.currentmd5
                model.insertRow(0,[QStandardItem(md5),QStandardItem(''),QStandardItem('')]) 
            except:
                print_exc()
                model.insertRow(0,[QStandardItem('0'),QStandardItem(''),QStandardItem('')]) 
        button.clicked.connect(clicked1)
        button2=QPushButton(self)
        button2.setText(_TR('删除选中行'))
        def clicked2():
            
            model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
        button5=QPushButton(self)
        button5.setText(_TR('设置所有词条为全局词条'))
        def clicked5():
            rows=model.rowCount()  
            for row in range(rows):
                model.item(row,0).setText('0')
        button5.clicked.connect(clicked5)
        
        search=QHBoxLayout()
        searchcontent=QLineEdit()
        search.addWidget(searchcontent)
        button4=QPushButton()
        button4.setText(_TR('搜索'))
        def clicked4():
            text=searchcontent.text()
            
            rows=model.rowCount() 
            cols=model.columnCount()
            for row in range(rows):
                ishide=True
                for c in range(cols):
                    if text in model.item(row,c).text(): 
                        ishide=False
                        break 
                table.setRowHidden(row,ishide)

                
        button4.clicked.connect(clicked4)
        search.addWidget(button4)
        
        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)
        formLayout.addWidget(button2)
        formLayout.addWidget(button5) 
        setmd5layout=QHBoxLayout()
        setmd5layout.addWidget(QLabel(_TR("当前MD5")))
        md5content=QLineEdit( gobject.baseobject.currentmd5)
        setmd5layout.addWidget(md5content)
        button5=QPushButton()
        button5.clicked.connect(lambda x:gobject.baseobject.__setattr__('currentmd5',md5content.text()))
        button5.setText(_TR('修改'))
        setmd5layout.addWidget(button5)
        self.button=button
        self.model=model
        self.configdict=configdict
        formLayout.addLayout(setmd5layout)
        self.resize(QSize(600,400))
        self.show()
