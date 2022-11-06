  
import functools 
from PyQt5.QtWidgets import   QWidget, QTableView,  QLabel, QVBoxLayout,QHBoxLayout

from PyQt5.QtWidgets import  QWidget,QLabel ,QLineEdit,QSpinBox,QPushButton,QTextEdit

from PyQt5.QtGui import QStandardItem, QStandardItemModel
import qtawesome 
from traceback import print_exc
from utils.config import globalconfig ,postprocessconfig,noundictconfig,transerrorfixdictconfig
from PyQt5.QtWidgets import  QWidget,QLabel  
import functools
from PyQt5.QtWidgets import QDialog ,QSpinBox,QVBoxLayout,QLineEdit,QGridLayout
from PyQt5.QtCore import QSize
from utils.config import globalconfig 
import qtawesome 
 
from gui.inputdialog import getsomepath1
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab7(self) : 
        t = QWidget()
        self.tab_widget.addTab(t,  "翻译优化")  
        lay=QGridLayout( )    
        t.setLayout(lay)  

        grids=[ 
            [(QLabel(''),10)]
        ] 
        for post in postprocessconfig:
            l=[(QLabel(postprocessconfig[post]['name'] ),3),
                self.getsimpleswitch(postprocessconfig[post],'use')]
                
            if 'args' in postprocessconfig[post]:
                l.append(self.getcolorbutton(globalconfig,'',callback= functools.partial( postconfigdialog,self,postprocessconfig[post]['args'],postprocessconfig[post]['name']+'设置'),icon='fa.gear',constcolor="#FF69B4")) 
            grids.append(l)
        
        p=QPushButton("自定义python处理" ) 

        def _openfile():
            import os
            if os.path.exists('./LunaTranslator/postprocess/post.py'):
                os.startfile( os.path.abspath('./LunaTranslator/postprocess/post.py'))
            elif os.path.exists('./postprocess/post.py'):
                os.startfile( os.path.abspath('./postprocess/post.py'))
        p.clicked.connect(lambda x:_openfile())

        grids.append([(p,5)])
        def __(x):
            globalconfig['gongxiangcishu'].__setitem__('use',x)
            self.object.loadvnrshareddict()
        grids+=[

            [(QLabel('使用专有名词翻译' ),3),
                self.getsimpleswitch(noundictconfig,'use'),
                self.getcolorbutton(globalconfig,'',callback=lambda x:  noundictconfigdialog(self,noundictconfig,'专有名词翻译设置(游戏ID 0表示全局)'),icon='fa.gear',constcolor="#FF69B4")],
            [(QLabel('使用翻译结果修正' ),3),
                self.getsimpleswitch(transerrorfixdictconfig,'use'),
                self.getcolorbutton(globalconfig,'',callback=lambda x:  noundictconfigdialog1(self,transerrorfixdictconfig,'翻译结果替换设置',['翻译','替换'],'./userconfig/transerrorfixdictconfig.json'),icon='fa.gear',constcolor="#FF69B4")],
            [(QLabel('使用VNR共享辞书' ),3),
                self.getsimpleswitch(globalconfig['gongxiangcishu'],'use',callback =lambda x:__(x)),
                self.getcolorbutton(globalconfig,'',callback=lambda x:  getsomepath1(self,'共享辞书',globalconfig['gongxiangcishu'],'path','共享辞书:',self.object.loadvnrshareddict,False,'*.xml') ,icon='fa.gear',constcolor="#FF69B4")],
            [''],[''],[''],[''],[''],
        ] 
        self.automakegrid(lay,grids)
 
def noundictconfigdialog1(object,configdict,title,label=[  '日文','翻译'],fname='./userconfig/noundictconfig.json'):
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle(title)
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
    model.setHorizontalHeaderLabels(label)
    table = QTableView(dialog)
    table.setModel(model)
    table.horizontalHeader().setStretchLastSection(True)
    #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #table.clicked.connect(self.show_info)
    button=QPushButton(dialog)
    button.setText('添加行')
    def clicked1(): 
        model.insertRow(0,[ QStandardItem(''),QStandardItem('')]) 
    button.clicked.connect(clicked1)
    button2=QPushButton(dialog)
    button2.setText('删除选中行')
    def clicked2():
        
        model.removeRow(table.currentIndex().row())
    button2.clicked.connect(clicked2)
    button3=QPushButton(dialog)
    button3.setText('保存并关闭')
    def clicked3():
        rows=model.rowCount() 
        newdict={}
        for row in range(rows):
            if model.item(row,0).text()=="":
                continue
            newdict[model.item(row,0).text()]=model.item(row,1).text()
        configdict['dict']=newdict
        with open(fname,'w',encoding='utf-8') as ff:
            import json
            ff.write(json.dumps(configdict,ensure_ascii=False,sort_keys=False, indent=4))
        dialog.close()
    button3.clicked.connect(clicked3)
    formLayout.addWidget(table)
    formLayout.addWidget(button)
    formLayout.addWidget(button2)
    formLayout.addWidget(button3)
    dialog.resize(QSize(600,400))
    dialog.show()
def noundictconfigdialog(object,configdict,title,label=['游戏ID MD5' ,'日文','翻译'],fname='./userconfig/noundictconfig.json'):
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle(title)
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
    model.setHorizontalHeaderLabels(label)
    table = QTableView(dialog)
    table.setModel(model)
    table.horizontalHeader().setStretchLastSection(True)
    #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #table.clicked.connect(self.show_info)
    button=QPushButton(dialog)
    button.setText('添加行')
    def clicked1(): 
        try:
            md5=object.object.textsource.md5
            model.insertRow(0,[QStandardItem(md5),QStandardItem(''),QStandardItem('')]) 
        except:
            print_exc()
            model.insertRow(0,[QStandardItem('0'),QStandardItem(''),QStandardItem('')]) 
    button.clicked.connect(clicked1)
    button2=QPushButton(dialog)
    button2.setText('删除选中行')
    def clicked2():
        
        model.removeRow(table.currentIndex().row())
    button2.clicked.connect(clicked2)
    button5=QPushButton(dialog)
    button5.setText('设置所有词条为全局词条')
    def clicked5():
        rows=model.rowCount()  
        for row in range(rows):
            model.item(row,0).setText('0')
    button5.clicked.connect(clicked5)
    button3=QPushButton(dialog)
    button3.setText('保存并关闭')
    def clicked3():
        rows=model.rowCount() 
        newdict={}
        for row in range(rows):
            if model.item(row,1).text()=="":
                continue
            newdict[model.item(row,1).text()]=[model.item(row,0).text(),model.item(row,2).text()]
        configdict['dict']=newdict
        with open(fname,'w',encoding='utf-8') as ff:
            import json
            ff.write(json.dumps(configdict,ensure_ascii=False,sort_keys=False, indent=4))
        dialog.close()
    button3.clicked.connect(clicked3)
    search=QHBoxLayout()
    searchcontent=QLineEdit()
    search.addWidget(searchcontent)
    button4=QPushButton()
    button4.setText('搜索')
    def clicked4():
        text=searchcontent.text()
         
        rows=model.rowCount() 
        cols=model.columnCount()
        for row in range(rows):
            ishide=True
            for c in range(cols):
                if text in model.item(row,c).text():
                    table.showRow(row)
                    ishide=False
                    break
            if ishide :
                table.hideRow(row)

             
    button4.clicked.connect(clicked4)
    search.addWidget(button4)
    
    formLayout.addWidget(table)
    formLayout.addLayout(search)
    formLayout.addWidget(button)
    formLayout.addWidget(button2)
    formLayout.addWidget(button5)
    formLayout.addWidget(button3)
    
    dialog.resize(QSize(600,400))
    dialog.show()
  
def postconfigdialog(object,configdict,title):
    dialog = QDialog(object)  # 自定义一个dialog
    dialog.setWindowTitle(title)
    #dialog.setWindowModality(Qt.ApplicationModal)
    
    formLayout = QVBoxLayout(dialog)  # 配置layout
     
    key=list(configdict.keys())[0]
    lb=QLabel(dialog)
    lb.setText(key) 
    formLayout.addWidget(lb) 
    if type(configdict[key])==type(1): 
        spin=QSpinBox(dialog)
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
        model.setHorizontalHeaderLabels([ '原文内容','替换为'])
        table = QTableView(dialog)
        table.setModel(model)
        table.setWordWrap(False) 
        table.horizontalHeader().setStretchLastSection(True)
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        button=QPushButton(dialog)
        button.setText('添加行')
        def clicked1(): 
            model.insertRow(0,[QStandardItem(''),QStandardItem('')])   
        button.clicked.connect(clicked1)
        button2=QPushButton(dialog)
        button2.setText('删除选中行')
        def clicked2():
            
            model.removeRow(table.currentIndex().row())
        button2.clicked.connect(clicked2)
        button3=QPushButton(dialog)
        button3.setText('保存并关闭')
        def clicked3():
            rows=model.rowCount() 
            newdict={}
            for row in range(rows):
                if model.item(row,0).text()=="":
                    continue
                newdict[(model.item(row,0).text())]=(model.item(row,1).text())
            configdict[key]=newdict
            dialog.close()
        button3.clicked.connect(clicked3)
        formLayout.addWidget(table)
        formLayout.addWidget(button)
        formLayout.addWidget(button2)
        formLayout.addWidget(button3)
        dialog.resize(QSize(600,400))
    dialog.show()
 