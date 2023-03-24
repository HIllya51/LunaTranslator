import functools
from PyQt5.QtWidgets import QDialogButtonBox,QDialog,QComboBox,QFormLayout,QDoubleSpinBox,QSpinBox,QHBoxLayout,QLineEdit,QFileDialog,QPushButton,QLabel,QColorDialog
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QColor 
import qtawesome
from utils.config import globalconfig ,_TR,_TRL
from gui.usefulwidget import MySwitch 
from utils.utils import makehtml
from utils.wrapper import Singleton
@Singleton
class autoinitdialog(QDialog):
    def __init__(dialog, object,title,width,lines,_=None  ) -> None:
        super().__init__(object,  Qt.WindowCloseButtonHint)
    
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
        def openfiledirectory(edit,isdir,filter1='*.*'):
            if isdir:
                f=QFileDialog.getExistingDirectory(directory= edit.text())
                res=f
            else:
                f=QFileDialog.getOpenFileName(directory= edit.text(),filter=filter1)
                res=f[0]
            if res!='':
                edit.setText(res)
        for line in lines:
            if 'type' in line:
                line['t']=line['type']
            if line['t']=='label':
                dd=line['d']
                key=line['k'] 
                
                if 'islink' in line and line['islink']:
                    e=QLabel(makehtml(dd[key]))
                    e.setOpenExternalLinks(True)
                else:
                    e=QLabel(_TR(dd[key]))
                formLayout.addRow((_TR(line['l'])),e)
            
            elif line['t']=='okcancel':
                button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel) 
                formLayout.addRow(button)
                button.rejected.connect(dialog.close)
                button.accepted.connect(functools.partial(save,None if 'callback' not in line else line['callback']))

                button.button(QDialogButtonBox.Ok).setText(_TR('确定'))
                button.button(QDialogButtonBox.Cancel).setText(_TR('取消'))
            elif line['t']=='lineedit':   
                dd=line['d']
                key=line['k'] 
                e=QLineEdit(dd[key])
                regist.append([dd,key,e.text])  
                formLayout.addRow((_TR(line['l'])),e)
            elif line['t']=='file': 
                dd=line['d']
                key=line['k'] 
                e=QLineEdit(dd[key])
                regist.append([dd,key,e.text])  
                bu=QPushButton(_TR('选择'+('文件夹' if line['dir'] else '文件')  ))
                bu.clicked.connect(functools.partial(openfiledirectory,e,line['dir'],'' if line['dir'] else line['filter']  ))
                hori=QHBoxLayout()
                hori.addWidget(e)
                hori.addWidget(bu)
                formLayout.addRow((_TR(line['l'])),hori)
             
            elif line['t']=='spin':
                dd=line['d']
                key=line['k'] 
                spin=QDoubleSpinBox()
                spin.setMinimum(0 if 'min' not in line else line['min'])
                spin.setMaximum(100 if 'max' not in line else line['max'])
                spin.setSingleStep(0.1 if 'step' not in line  else line['step'])
                spin.setValue(dd[key])
                spin.valueChanged.connect(functools.partial(dd.__setitem__,key))
                
                formLayout.addRow(_TR(line['l']),spin)  
            elif line['t']=='intspin':
                dd=line['d']
                key=line['k'] 
                spin=QSpinBox()
                spin.setMinimum(0 if 'min' not in line else line['min'])
                spin.setMaximum(100 if 'max' not in line else line['max'])
                spin.setSingleStep(1 if 'step' not in line  else line['step'])
                spin.setValue(dd[key])
                spin.valueChanged.connect(functools.partial(dd.__setitem__,key))
                
                formLayout.addRow(_TR(line['l']),spin)  
        dialog.show()
 
def getsomepath1(object,title,d,k,label,callback=None,isdir=False,filter1="*.db"):
    autoinitdialog(object,title,900,[ 
                                {'t':'file','l':label,'d':d,'k':k,'dir':isdir,'filter':filter1}, 
                                {'t':'okcancel','callback':callback},
                                ])

def ChangeTranslateColor(self,button,item) :
        color = QColorDialog.getColor(QColor(globalconfig['cixingcolor'][item]), self, item)
        
    
        button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
        globalconfig['cixingcolor'][item]=color.name() 

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
            p.clicked.connect(functools.partial(ChangeTranslateColor,self,p,k))
            hori.addWidget(b)
            hori.addWidget(p)
            
            formLayout.addRow(hori) 
        self.show() 
        