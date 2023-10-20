import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QHeaderView,QComboBox,QFormLayout,QDoubleSpinBox,QSpinBox,QHBoxLayout,QLineEdit,QFileDialog,QPushButton,QLabel,QTableView,QVBoxLayout
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QStandardItem, QStandardItemModel 

from PyQt5.QtGui import QColor 
import qtawesome,importlib
from myutils.config import globalconfig ,_TR,_TRL
from gui.usefulwidget import MySwitch ,selectcolor
from myutils.utils import makehtml
from myutils.wrapper import Singleton
@Singleton
class autoinitdialog(QDialog):
    def __init__(dialog, parent,title,width,lines,_=None  ) -> None:
        super().__init__(parent,  Qt.WindowCloseButtonHint)
    
        dialog.setWindowTitle(_TR(title))
        dialog.resize(QSize(width,10))
        formLayout = QFormLayout()
        dialog.setLayout(formLayout)
        regist=[]
        def save(callback=None):
            for l in regist:
                l[0][l[1]]=l[2]() 
            dialog.close()
            if callback:
                callback()
        def openfiledirectory(multi,edit,isdir,filter1='*.*'):
            if isdir:
                f=QFileDialog.getExistingDirectory(directory= edit.text())
                res=f
            else:
                if multi:
                    f=QFileDialog.getOpenFileNames(directory= edit.text(),filter=filter1)
                    res='|'.join(f[0])
                else:
                    f=QFileDialog.getOpenFileName(directory= edit.text(),filter=filter1)
                    res=f[0]
                
            if res!='':
                edit.setText(res)
        for line in lines:
            if 'type' in line:
                line['t']=line['type']
            if 'd' in line:
                dd=line['d']
            if 'k' in line:
                key=line['k'] 
            if line['t']=='label':
                
                if 'islink' in line and line['islink']:
                    lineW=QLabel(makehtml(dd[key]))
                    lineW.setOpenExternalLinks(True)
                else:
                    lineW=QLabel(_TR(dd[key])) 
            elif line['t']=='combo':
                lineW=QComboBox()
                if 'list_function' in line:
                    try:
                        func=getattr(importlib.import_module(line['list_function'][0]),line['list_function'][1])
                        items=func()
                    except:
                        items=[]
                else:
                    items=line['list']
                lineW.addItems(_TRL(items))
                lineW.setCurrentIndex(dd[key])
                lineW.currentIndexChanged.connect(functools.partial(dd.__setitem__,key)) 
            elif line['t']=='okcancel':
                lineW = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)  
                lineW.rejected.connect(dialog.close)
                lineW.accepted.connect(functools.partial(save,None if 'callback' not in line else line['callback']))

                lineW.button(QDialogButtonBox.Ok).setText(_TR('确定'))
                lineW.button(QDialogButtonBox.Cancel).setText(_TR('取消'))
            elif line['t']=='lineedit':  
                lineW=QLineEdit(dd[key])
                regist.append([dd,key,lineW.text])   
            elif line['t']=='file': 
                e=QLineEdit(dd[key])
                regist.append([dd,key,e.text])  
                bu=QPushButton(_TR('选择'+('文件夹' if line['dir'] else '文件')  ))
                bu.clicked.connect(functools.partial(openfiledirectory,line.get('multi',False), e,line['dir'],'' if line['dir'] else line['filter']  ))
                lineW=QHBoxLayout()
                lineW.addWidget(e)
                lineW.addWidget(bu) 
            elif line['t']=='switch':
                lineW=MySwitch(parent.rate,sign=dd[key])
                regist.append([dd,key,lineW.isChecked])   
            elif line['t']=='spin':
                lineW=QDoubleSpinBox()
                lineW.setMinimum(0 if 'min' not in line else line['min'])
                lineW.setMaximum(100 if 'max' not in line else line['max'])
                lineW.setSingleStep(0.1 if 'step' not in line  else line['step'])
                lineW.setValue(dd[key])
                lineW.valueChanged.connect(functools.partial(dd.__setitem__,key))
                
            elif line['t']=='intspin':
                lineW=QSpinBox()
                lineW.setMinimum(0 if 'min' not in line else line['min'])
                lineW.setMaximum(100 if 'max' not in line else line['max'])
                lineW.setSingleStep(1 if 'step' not in line  else line['step'])
                lineW.setValue(dd[key])
                lineW.valueChanged.connect(functools.partial(dd.__setitem__,key))
            if 'l' in line:
                formLayout.addRow(_TR(line['l']),lineW)  
            else:
                formLayout.addRow( lineW)  
        dialog.show()
 
def getsomepath1(parent,title,d,k,label,callback=None,isdir=False,filter1="*.db"):
    autoinitdialog(parent,title,900,[ 
                                {'t':'file','l':label,'d':d,'k':k,'dir':isdir,'filter':filter1}, 
                                {'t':'okcancel','callback':callback},
                                ])


@Singleton
class multicolorset(QDialog):
    def __init__(self, parent ) -> None:
        super().__init__(parent,Qt.WindowCloseButtonHint )
        self.setWindowTitle(_TR("颜色设置") )
        self.resize(QSize(300,10))
        formLayout = QFormLayout(self)  # 配置layout 
        _hori=QHBoxLayout()
        l=QLabel(_TR("透明度"))
        _hori.addWidget(l)
        _s=QSpinBox()
        _s.setValue(globalconfig['showcixing_touming'])
        _s.setMinimum(1)
        _s.setMaximum(100)
        _hori.addWidget(_s)
        formLayout.addRow(_hori)
        _s.valueChanged.connect(lambda x:globalconfig.__setitem__('showcixing_touming',x))
        hori=QHBoxLayout()
        hori.addWidget(QLabel(_TR("词性")))
        hori.addWidget(QLabel(_TR("是否显示")))
        hori.addWidget(QLabel(_TR("颜色")))
        for k in globalconfig['cixingcolor']:
            hori=QHBoxLayout()
            
            l=QLabel(_TR(k)) 
            
            hori.addWidget(l)
            
            b=MySwitch(parent.rate,sign=globalconfig['cixingcolorshow'][k] ) 
            b.clicked.connect(functools.partial(globalconfig['cixingcolorshow'].__setitem__,k))
            
        

            p=QPushButton(qtawesome.icon("fa.paint-brush", color=globalconfig['cixingcolor'][k]), "" )
            
            p.setIconSize(QSize(20*parent.rate,20*parent.rate))
            
            p.setStyleSheet("background: transparent;")
            p.clicked.connect(functools.partial(selectcolor,self,globalconfig['cixingcolor'],k,p))
            hori.addWidget(b)
            hori.addWidget(p)
            
            formLayout.addRow(hori) 
        self.show() 

@Singleton
class postconfigdialog(QDialog):
    def __init__(dialog, parent,configdict,title,_=None) -> None:
        super().__init__(parent,Qt.WindowCloseButtonHint)
    
        dialog.setWindowTitle(_TR(title))
        #dialog.setWindowModality(Qt.ApplicationModal)
        
        formLayout = QVBoxLayout(dialog)  # 配置layout
        
        key=list(configdict.keys())[0]
        lb=QLabel(dialog)
        lb.setText(_TR(key) )
        formLayout.addWidget(lb) 
        if type(configdict[key]) in (float,int): 
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
    