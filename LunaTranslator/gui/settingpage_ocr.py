import functools 

from PyQt5.QtWidgets import  QWidget, QComboBox,QDoubleSpinBox 
 
from PyQt5.QtWidgets import QWidget,QFrame ,QPushButton,QColorDialog,QGridLayout
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
            
            if name in ocrsetting:
                items=[] 
                for arg in ocrsetting[name]['args']: 
                    items.append({
                            't':'lineedit','l':arg,'d':ocrsetting[name]['args'],'k':arg
                        })
                    
                items.append({'t':'okcancel' })
                _3=self.getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self,globalconfig['ocr'][name]['name']+'设置',900,items),icon='fa.gear',constcolor="#FF69B4")
            else:
                _3=''
            
            line+=[((globalconfig['ocr'][name]['name']),6),(self.getsimpleswitch(globalconfig['ocr'][name],'use',name=name+'_ocrswitch',callback=functools.partial(yuitsuocr,self,name)),1),_3,'']

            if i%3==2 or i==lendict-1:
                grids.append(line) 
            i+=1


        grids+=[ 
            [''],
            [''],
            
            [(("百度OCR使用竖排OCR"),9),self.getsimpleswitch(globalconfig ,'verticalocr')],
            [(("合并多行识别结果"),9),self.getsimpleswitch(globalconfig ,'ocrmergelines')],
            [''],
           # [(("优化横向OCR漏字"),6),self.getsimpleswitch(globalconfig ,'ocr_hori_extend')],
         #   [(("使用竖排OCR(效果不佳)"),6),self.getsimpleswitch(globalconfig ,'verticalocr')],
         
            [(("选取OCR范围后立即进行一次识别"),9),self.getsimpleswitch(globalconfig ,'ocrafterrangeselect')],
            [(("选取OCR范围后主动显示范围框"),9),self.getsimpleswitch(globalconfig ,'showrangeafterrangeselect')],
            [''],
            [(("每隔一段时间必然进行一次OCR"),9),self.getsimpleswitch(globalconfig ,'mustocr')],
            [(("OCR最长间隔时间(s)"),9),(self.getspinbox(0.1,100,globalconfig,'mustocr_interval',double=True,step=0.1  ),2)],
            [(("OCR最短间隔时间(s)"),9),(self.getspinbox(0.1,100,globalconfig,'ocrmininterval',double=True,step=0.1  ),2)],
            [(("OCR范围框颜色"),9),(self.getcolorbutton(globalconfig,'ocrrangecolor',callback=lambda  : changeocrcolorcallback(self),name='ocrrangecolor_button'),1)],
            [(("OCR范围框宽度"),9),(self.getspinbox(1,100,globalconfig,'ocrrangewidth'  ,callback=lambda x: changeocrwidthcallback(self,x) ),2)],
            [''],
            [(("OCR区域稳定性阈值"),9),(self.getspinbox(0.8,1,globalconfig,'ocr_stable_sim'  ,double=True,step=0.01 ,dec=3),2),],
             [("判断区域内图片是否稳定，值越高要求区域内变化越小，若稳定性较低则暂时先不ocr",25)], 
            [(("OCR前次区分度阈值"),9),(self.getspinbox(0.8,1,globalconfig,'ocr_diff_sim'  ,double=True,step=0.01 ,dec=3),2),],
            [("图像稳定后判断当前图片和上次ocr图片是否一致，如果一致性过高则不ocr",25)],
        ] 
        self.yitiaolong("OCR设置",grids)
def changeocrcolorcallback(self ):
    self.ChangeTranslateColor("ocrrangecolor", self.ocrrangecolor_button) 
    self.object.range_ui.label.setStyleSheet(" border:%spx solid %s; background-color: rgba(0,0,0, 0.01)"   %(globalconfig['ocrrangewidth'],globalconfig['ocrrangecolor'] ))
def changeocrwidthcallback(self,x):
    globalconfig.__setitem__('ocrrangewidth',x)
    self.object.range_ui.label.setStyleSheet(" border:%spx solid %s; background-color: rgba(0,0,0, 0.01)"   %(globalconfig['ocrrangewidth'],globalconfig['ocrrangecolor'] ))
def yuitsuocr(self,name,checked): 
    
    if checked : 
        for k in globalconfig['ocr']:
            if globalconfig['ocr'][k]['use']==True:
                getattr(self,k+'_ocrswitch').setChecked(False)  
                globalconfig['ocr'][k]['use']=False
        globalconfig['ocr'][name]['use']=True
    else:
        globalconfig['ocr'][name]['use']=False  
 