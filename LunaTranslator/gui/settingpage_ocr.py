import functools 

from PyQt5.QtWidgets import  QWidget,QLabel, QComboBox,QDoubleSpinBox 
 
from PyQt5.QtWidgets import QWidget,QLabel,QFrame ,QPushButton,QColorDialog,QGridLayout
from PyQt5.QtGui import QColor,QFont
import functools 
import qtawesome
from utils.config import globalconfig ,ocrsetting

import importlib
from gui.inputdialog import autoinitdialog
import gui.switchbutton
import gui.attachprocessdialog  
import gui.selecthook  
def setTab6(self) :
        
          
        grids=[ ] 
        i=0
        lendict=len(list(globalconfig['ocr'].keys()))


        for name in globalconfig['ocr']:
             
            if i%3==0:
                line=[]
            
            if 'argsfile' in globalconfig['ocr'][name]:
                items=[] 
                for arg in ocrsetting[name]['args']: 
                    items.append({
                            't':'lineedit','l':arg,'d':ocrsetting[name]['args'],'k':arg
                        })
                    
                items.append({'t':'okcancel' })
                _3=self.getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self,globalconfig['ocr'][name]['name']+'设置',900,items),icon='fa.gear',constcolor="#FF69B4")
            else:
                _3=''
            
            line+=[(QLabel(globalconfig['ocr'][name]['name']),3),(self.getsimpleswitch(globalconfig['ocr'][name],'use',name=name+'_ocrswitch',callback=functools.partial(yuitsuocr,self,name)),1),_3,'']

            if i%3==2 or i==lendict-1:
                grids.append(line) 
            i+=1


        grids+=[ 
            [''],
            [''],
            [(QLabel("优化横向OCR漏字"),6),self.getsimpleswitch(globalconfig ,'ocr_hori_extend')],
            [(QLabel("使用竖排OCR(效果不佳)"),6),self.getsimpleswitch(globalconfig ,'verticalocr')],
            [(QLabel("每隔一段时间必然进行一次OCR"),6),self.getsimpleswitch(globalconfig ,'mustocr')],
            [(QLabel("OCR最长间隔时间(s)"),6),(self.getspinbox(0.1,100,globalconfig,'mustocr_interval',double=True,step=0.1  ),2)],
            [(QLabel("OCR最短间隔时间(s)"),6),(self.getspinbox(0.1,100,globalconfig,'ocrmininterval',double=True,step=0.1  ),2)],
          
        ] 
        self.yitiaolong("OCR设置",grids)
def yuitsuocr(self,name,checked): 
    
    if checked : 
        for k in globalconfig['ocr']:
            if globalconfig['ocr'][k]['use']==True:
                getattr(self,k+'_ocrswitch').setChecked(False)  
                globalconfig['ocr'][k]['use']=False
        globalconfig['ocr'][name]['use']=True
    else:
        globalconfig['ocr'][name]['use']=False  
 