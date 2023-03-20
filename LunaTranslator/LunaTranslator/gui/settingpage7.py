  
import functools  

from PyQt5.QtWidgets import  QDialog,QLabel ,QLineEdit,QDoubleSpinBox,QPushButton ,QTableView,   QVBoxLayout,QHBoxLayout,QHeaderView 
from PyQt5.QtCore import QSize,Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel 
from traceback import print_exc
from utils.config import globalconfig ,postprocessconfig,noundictconfig,transerrorfixdictconfig,_TR,_TRL,defaultglobalconfig 
import functools 

from gui.codeacceptdialog import codeacceptdialog  
from gui.inputdialog import getsomepath1   
from utils.utils import selectdebugfile
from utils.wrapper import Singleton
def settab7direct(self):
    self.button_noundict=self.getcolorbutton(globalconfig,'' ,callback=lambda x:  noundictconfigdialog(self,noundictconfig,'专有名词翻译设置(游戏ID 0表示全局)'),icon='fa.gear',constcolor="#FF69B4")
    self.button_fix=self.getcolorbutton(globalconfig,'',callback=lambda x:  noundictconfigdialog1(self,transerrorfixdictconfig,'翻译结果替换设置',['翻译','替换'],'./userconfig/transerrorfixdictconfig.json'),icon='fa.gear',constcolor="#FF69B4")
def setTab7(self) :  
        self.tabadd_lazy(self.tab_widget, ('文本处理'), lambda :setTab7_lazy(self)) 
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
           
            toexchangei=ii+(-1 if up else 1)
            sortlist[ii],sortlist[toexchangei]=sortlist[toexchangei],sortlist[ii] 
            for i,ww in enumerate(savelist[ii+1]):

                w1=(savelay[0].indexOf(ww))
                w2=savelay[0].indexOf(savelist[toexchangei+1][i])
                p1=savelay[0].getItemPosition(w1)
                p2=savelay[0].getItemPosition(w2) 
                savelay[0].removeWidget(ww)
                savelay[0].removeWidget(savelist[toexchangei+1][i])
                 
                savelay[0].addWidget(savelist[toexchangei+1][i],*p1)
                savelay[0].addWidget(ww,*p2)
            savelist[ii+1],savelist[toexchangei+1]=savelist[toexchangei+1],savelist[ii+1] 
        for i,post in enumerate(sortlist): 
            if post=='_11':
                config=(self.getcolorbutton(globalconfig,'',callback=lambda:selectdebugfile('./userconfig/mypost.py' ),icon='fa.gear',constcolor="#FF69B4")) 
            else:
                if post not in postprocessconfig:
                    continue
                if post=='_remove_chaos':
                    config=(self.getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self))) 
                elif 'args' in postprocessconfig[post]:
                    
                    config=(self.getcolorbutton(globalconfig,'',callback= functools.partial( postconfigdialog,self,postprocessconfig[post]['args'],postprocessconfig[post]['name']),icon='fa.gear',constcolor="#FF69B4")) 
                else:
                    config=('')
             
            button_up=(self.getcolorbutton(globalconfig,'',callback= functools.partial(changerank, post,True),icon='fa.arrow-up',constcolor="#FF69B4"))
            button_down=(self.getcolorbutton(globalconfig,'',callback= functools.partial(changerank, post,False),icon='fa.arrow-down',constcolor="#FF69B4")) 
             
            l=[((postprocessconfig[post]['name'] ),6),
                self.getsimpleswitch(postprocessconfig[post],'use'),
                config,
                button_up,
                button_down
            ]
            grids.append(l)
         
    
        grids2=[ 
            [(('使用专有名词翻译' ),6),
                self.getsimpleswitch(noundictconfig,'use'),
                self.button_noundict],
            [(('使用翻译结果修正' ),6),
                self.getsimpleswitch(transerrorfixdictconfig,'use'),
                self.button_fix],
            [(('使用VNR共享辞书' ),6),
                self.getsimpleswitch(globalconfig['gongxiangcishu'],'use',callback = self.object.loadvnrshareddict ),
                self.getcolorbutton(globalconfig,'',callback=lambda x:  getsomepath1(self,'共享辞书',globalconfig['gongxiangcishu'],'path','共享辞书',self.object.loadvnrshareddict,False,'*.xml') ,icon='fa.gear',constcolor="#FF69B4"),'','','','','',''],
            
        ]   
         
        tab=self.makesubtab_lazy(['文本预处理', '翻译优化'],[
            lambda:self.makescroll(self.makegrid(grids,True,savelist,savelay )  ) ,
            lambda:self.makescroll(self.makegrid(grids2 )  )
        ])   
        return tab
@Singleton
class noundictconfigdialog1(QDialog):
    def __init__(dialog,object,configdict,title,label=[  '日文','翻译'] ,_=None) -> None:
        super().__init__(object,Qt.WindowCloseButtonHint)
            
        dialog.setWindowTitle(_TR(title))
        #dialog.setWindowModality(Qt.ApplicationModal)
        
        formLayout = QVBoxLayout(dialog)  # 配置layout
            
        model=QStandardItemModel(len(list(configdict['dict'].keys())),1 , dialog)
        row=0
        for key in  (configdict['dict']):                                   # 2
                
                item = QStandardItem( key )
                model.setItem(row, 0, item)
                item = QStandardItem(configdict['dict'][key] )
                model.setItem(row, 1, item)
                row+=1
        model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(dialog)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        button=QPushButton(dialog)
        button.setText(_TR('添加行'))
        def clicked1(): 
            model.insertRow(0,[ QStandardItem(''),QStandardItem('')]) 
        button.clicked.connect(clicked1)
        button2=QPushButton(dialog)
        button2.setText(_TR('删除选中行'))
        def clicked2():
            
            model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
        
        def clicked3(_):
            button.setFocus()
            rows=model.rowCount() 
            newdict={}
            for row in range(rows):
                if model.item(row,0).text()=="":
                    continue
                newdict[model.item(row,0).text()]=model.item(row,1).text()
            configdict['dict']=newdict 
            
        dialog.closeEvent=clicked3
        formLayout.addWidget(table)
        formLayout.addWidget(button)
        formLayout.addWidget(button2) 
        dialog.resize(QSize(600,400))
        dialog.show()
@Singleton
class noundictconfigdialog(QDialog):
    def __init__(dialog,object,configdict,title,label=['游戏ID MD5' ,'日文','翻译'] ,_=None) -> None:
        super().__init__(object,Qt.WindowCloseButtonHint)
        
        dialog.setWindowTitle(_TR(title))
        #dialog.setWindowModality(Qt.ApplicationModal)
        
        formLayout = QVBoxLayout(dialog)  # 配置layout
            
        model=QStandardItemModel(len(list(configdict['dict'].keys())),1 , dialog)
        row=0
        for key in  (configdict['dict']):                                   # 2
                if type(configdict['dict'][key])==str:
                    configdict['dict'][key]=["0",configdict['dict'][key]]
                item = QStandardItem( configdict['dict'][key][0] )
                model.setItem(row, 0, item)
                item = QStandardItem(key  )
                model.setItem(row, 1, item)
                item = QStandardItem( configdict['dict'][key][1] )
                model.setItem(row, 2, item)
                row+=1
        model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(dialog)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        button=QPushButton(dialog)
        button.setText(_TR('添加行'))
        def clicked1(): 
            try:
                md5=object.object.textsource.md5
                model.insertRow(0,[QStandardItem(md5),QStandardItem(''),QStandardItem('')]) 
            except:
                print_exc()
                model.insertRow(0,[QStandardItem('0'),QStandardItem(''),QStandardItem('')]) 
        button.clicked.connect(clicked1)
        button2=QPushButton(dialog)
        button2.setText(_TR('删除选中行'))
        def clicked2():
            
            model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
        button5=QPushButton(dialog)
        button5.setText(_TR('设置所有词条为全局词条'))
        def clicked5():
            rows=model.rowCount()  
            for row in range(rows):
                model.item(row,0).setText('0')
        button5.clicked.connect(clicked5)
        
        def clicked3(_):
            button.setFocus()
            rows=model.rowCount() 
            newdict={}
            for row in range(rows):
                if model.item(row,1).text()=="":
                    continue
                newdict[model.item(row,1).text()]=[model.item(row,0).text(),model.item(row,2).text()]
            configdict['dict']=newdict  

        dialog.closeEvent=clicked3 
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
        md5content=QLineEdit( object.object.currentmd5)
        setmd5layout.addWidget(md5content)
        button5=QPushButton()
        button5.clicked.connect(lambda x:object.object.__setitem__('currentmd5',md5content.text()))
        button5.setText(_TR('修改'))
        setmd5layout.addWidget(button5)
        
        formLayout.addLayout(setmd5layout)
        dialog.resize(QSize(600,400))
        dialog.show()
@Singleton
class postconfigdialog(QDialog):
    def __init__(dialog, object,configdict,title,_=None) -> None:
        super().__init__(object,Qt.WindowCloseButtonHint)
    
        dialog.setWindowTitle(_TR(title))
        #dialog.setWindowModality(Qt.ApplicationModal)
        
        formLayout = QVBoxLayout(dialog)  # 配置layout
        
        key=list(configdict.keys())[0]
        lb=QLabel(dialog)
        lb.setText(_TR(key) )
        formLayout.addWidget(lb) 
        if type(configdict[key])==type(1): 
            spin=QDoubleSpinBox(dialog)
            spin.setMinimum(1)
            spin.setMaximum(100)
            spin.setValue(configdict[key])
            spin.valueChanged.connect(lambda x:configdict.__setitem__(key,x))
            formLayout.addWidget(spin)
            dialog.resize(QSize(600,1))
        
        elif type(configdict[key])==type({}): 
            # lines=QTextEdit(dialog)
            # lines.setPlainText('\n'.join(configdict[key]))
            # lines.textChanged.connect(lambda   :configdict.__setitem__(key,lines.toPlainText().split('\n')))
            # formLayout.addWidget(lines)
            model=QStandardItemModel(len(configdict[key]),1 , dialog)
            row=0
            
            for key1  in  ( (configdict[key])):                                   # 2
                
                    item = QStandardItem(key1)
                    model.setItem(row, 0, item)
                    
                    item = QStandardItem(configdict[key][key1])
                    model.setItem(row, 1, item)
                    row+=1
            model.setHorizontalHeaderLabels(_TRL([ '原文内容','替换为']))
            table = QTableView(dialog)
            table.setModel(model)
            table.setWordWrap(False) 
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
            #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            #table.clicked.connect(self.show_info)
            button=QPushButton(dialog)
            button.setText(_TR('添加行'))
            def clicked1(): 
                model.insertRow(0,[QStandardItem(''),QStandardItem('')])   
            button.clicked.connect(clicked1)
            button2=QPushButton(dialog)
            button2.setText(_TR('删除选中行'))
            def clicked2():
                
                model.removeRow(table.currentIndex().row())
            button2.clicked.connect(clicked2)
        
            def clicked3(_):
                button.setFocus()
                rows=model.rowCount() 
                newdict={}
                for row in range(rows):
                    if model.item(row,0).text()=="":
                        continue
                    newdict[(model.item(row,0).text())]=(model.item(row,1).text())
                configdict[key]=newdict 
            dialog.closeEvent=(clicked3)
            formLayout.addWidget(table)
            formLayout.addWidget(button)
            formLayout.addWidget(button2) 
            dialog.resize(QSize(600,400))
        dialog.show()
    