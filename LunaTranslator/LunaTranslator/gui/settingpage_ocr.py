import functools  ,os
from myutils.config import globalconfig ,ocrsetting,_TRL,ocrerrorfix
from gui.usefulwidget import getsimplecombobox,getspinbox,getcolorbutton,yuitsu_switch,getsimpleswitch,selectcolor
from gui.inputdialog import autoinitdialog   ,postconfigdialog
import gobject
def getocrgrid(self) :
        
          
        grids=[ ] 
        i=0
        lendict=len(list(globalconfig['ocr'].keys()))
         
        self.ocrswitchs={}
        line=[]
        for name in globalconfig['ocr']:
              
            _f='./Lunatranslator/ocrengines/{}.py'.format(name)
            if os.path.exists(_f)==False:  
                continue 
            if name in ocrsetting:
                items=[] 
                for arg in ocrsetting[name]['args']: 
                    items.append({
                        'l':arg,'d':ocrsetting[name]['args'],'k':arg
                    })
                    if 'argstype' in ocrsetting[name] and arg in ocrsetting[name]['argstype']:
                    
                        items[-1].update(ocrsetting[name]['argstype'][arg]) 
                    else:
                        items[-1].update(
                            {'t':'lineedit'}
                        )
                items.append({'t':'okcancel' })
                _3=getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self,globalconfig['ocr'][name]['name'],900,items),icon='fa.gear',constcolor="#FF69B4")
                
            else:
                _3=''
            
            line+=[((globalconfig['ocr'][name]['name']),6),(getsimpleswitch(globalconfig['ocr'][name],'use',name=name,parent=self,callback=functools.partial(yuitsu_switch,self,globalconfig['ocr'],'ocrswitchs',name,None),pair='ocrswitchs'),1),_3 ] 
            if i%3==2  :
                grids.append(line) 
                line=[]
            else:
                 line+=['']
            i+=1
        if len(line):
             grids.append(line)

        grids+=[  
            [''],
            
            [(("竖向OCR识别"),12),getsimpleswitch(globalconfig ,'verticalocr')],
            [(("合并多行识别结果"),12),getsimpleswitch(globalconfig ,'ocrmergelines')],
            [''],
            [('OCR预处理方法',8), (getsimplecombobox(_TRL(['不处理','灰度化','阈值二值化','OTSU二值化']),globalconfig,'ocr_presolve_method'),12),''], 
            [('查看处理效果',6),getcolorbutton(globalconfig,'',icon='fa.picture-o',constcolor="#FF69B4",callback=gobject.baseobject.showocrimage.showsignal.emit),'',(("二值化阈值"),8),(getspinbox(0,255,globalconfig,'binary_thresh'  ),4)], 
            [''],
            [('OCR自动化方法',8), (getsimplecombobox(_TRL(['分析图像更新','周期执行','分析图像更新+周期执行']),globalconfig,'ocr_auto_method'),12)], 
            [(("执行周期(s)"),8),(getspinbox(0.1,100,globalconfig,'ocr_interval',double=True,step=0.1  ),4)],  
            [(("图像稳定性阈值"),8),(getspinbox(0,1,globalconfig,'ocr_stable_sim'  ,double=True,step=0.01 ,dec=3),4),(self.threshold1label,4)], 
            [(("图像一致性阈值"),8),(getspinbox(0,1,globalconfig,'ocr_diff_sim'  ,double=True,step=0.01 ,dec=3),4),(self.threshold2label,4)], 

            [''],
            [(("OCR范围框颜色"),12),(getcolorbutton(globalconfig,'ocrrangecolor',callback=lambda  : selectcolor(self,globalconfig,'ocrrangecolor',self.ocrrangecolor_button,callback=lambda :gobject.baseobject.textsource.setstyle()),name='ocrrangecolor_button',parent=self),1)],
            [(("OCR范围框宽度"),12),(getspinbox(1,100,globalconfig,'ocrrangewidth'  ,callback=lambda x: gobject.baseobject.textsource.setstyle()  ),4)],
            [(("选取OCR范围后立即进行一次识别"),12),getsimpleswitch(globalconfig ,'ocrafterrangeselect')],
            [(("选取OCR范围后显示范围框"),12),getsimpleswitch(globalconfig ,'showrangeafterrangeselect')],
            [(("OCR识别易错内容修正"),12),getsimpleswitch(ocrerrorfix ,'use'),getcolorbutton(globalconfig,'',callback= functools.partial( postconfigdialog,self,ocrerrorfix['args'],'OCR识别易错内容修正'),icon='fa.gear',constcolor="#FF69B4")],
        ] 
        return grids
       
         