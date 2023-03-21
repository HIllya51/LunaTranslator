import functools  ,os
from utils.config import globalconfig ,ocrsetting,_TRL
 
from gui.inputdialog import autoinitdialog   
 
def getocrgrid(self) :
        
          
        grids=[ ] 
        i=0
        lendict=len(list(globalconfig['ocr'].keys()))
         
        self.ocrswitchs={}
        line=[]
        for name in globalconfig['ocr']:
              
            _f=f'./Lunatranslator/ocrengines/{name}.py'
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
                _3=self.getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self,globalconfig['ocr'][name]['name'],900,items),icon='fa.gear',constcolor="#FF69B4")
                
            else:
                _3=''
            
            line+=[((globalconfig['ocr'][name]['name']),6),(self.getsimpleswitch(globalconfig['ocr'][name],'use',name=name,callback=functools.partial(self.yuitsu_switch,'ocr','ocrswitchs',name,None),pair='ocrswitchs'),1),_3 ] 
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
            
            [(("竖向OCR识别"),12),self.getsimpleswitch(globalconfig ,'verticalocr')],
            [(("合并多行识别结果"),12),self.getsimpleswitch(globalconfig ,'ocrmergelines')],
            [(("Magpie全屏时仍截取原窗口"),12),self.getsimpleswitch(globalconfig ,'ocrmagpiekeep')],
            [''],
            
            [('OCR自动化方法',8),'',(self.getsimplecombobox(_TRL(['分析图像更新','周期执行','分析图像更新+周期执行']),globalconfig,'ocr_auto_method'),12)], 
            [(("执行周期(s)"),12),(self.getspinbox(0.1,100,globalconfig,'ocr_interval',double=True,step=0.1  ),4)],  
            [(("图像稳定性阈值"),12),(self.getspinbox(0.8,1,globalconfig,'ocr_stable_sim'  ,double=True,step=0.01 ,dec=3),4),], 
            [(("图像一致性阈值"),12),(self.getspinbox(0.8,1,globalconfig,'ocr_diff_sim'  ,double=True,step=0.01 ,dec=3),4),], 

            [''],
            [(("OCR范围框颜色"),12),(self.getcolorbutton(globalconfig,'ocrrangecolor',callback=lambda  : changeocrcolorcallback(self),name='ocrrangecolor_button'),1)],
            [(("OCR范围框宽度"),12),(self.getspinbox(1,100,globalconfig,'ocrrangewidth'  ,callback=lambda x: self.object.range_ui.setstyle()  ),4)],
            [(("选取OCR范围后立即进行一次识别"),12),self.getsimpleswitch(globalconfig ,'ocrafterrangeselect')],
            [(("选取OCR范围后主动显示范围框"),12),self.getsimpleswitch(globalconfig ,'showrangeafterrangeselect')],
        ] 
        return grids
       
        
def changeocrcolorcallback(self ):
    self.ChangeTranslateColor("ocrrangecolor", self.ocrrangecolor_button) 
    self.object.range_ui.label.setStyleSheet(" border:%spx solid %s; background-color: rgba(0,0,0, 0.01)"   %(globalconfig['ocrrangewidth'],globalconfig['ocrrangecolor'] ))
 