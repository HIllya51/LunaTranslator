 
import functools,os,shutil,windows,json
from PyQt5.QtGui import  QFont,QStandardItem,QStandardItemModel
from PyQt5.QtCore import Qt,QSize
from traceback import print_exc
from PyQt5.QtWidgets import  QFontComboBox,QDialog,QLabel,QComboBox,QPushButton,QFileDialog,QFormLayout,QDialogButtonBox,QHeaderView,QHBoxLayout,QLineEdit
from gui.pretransfile import sqlite2json2
from gui.settingpage_ocr import getocrgrid  
from myutils.config import globalconfig ,_TR,_TRL,savehook_new_data,savehook_new_list
from gui.dialog_savedgame import dialog_savedgame 
import threading,gobject,requests,datetime,zipfile
from gui.inputdialog import autoinitdialog,regexedit
from gui.usefulwidget import getsimplecombobox,getspinbox,getcolorbutton,yuitsu_switch,getsimpleswitch,Singleton,getQMessageBox
from gui.codeacceptdialog import codeacceptdialog   
from textsource.fridahook import fridahook
from myutils.utils import loadfridascriptslist,checkifnewgame,makehtml,getfilemd5
from myutils.proxy import getproxy
def gethookgrid(self) :
 
        grids=[
                [('获取最新提取器核心&错误反馈&游戏支持',8),(makehtml("https://github.com/HIllya51/LunaHook"),8,"link")],
                [],
                [('选择游戏',5),self.selectbutton,('',5)],
                [('选择文本',5),self.selecthookbutton],
                [],
                [('检测到游戏时自动开始',5),(getsimpleswitch(globalconfig,'autostarthook'),1)],
                
                [('已保存游戏',5),(getcolorbutton(globalconfig,'',icon='fa.gamepad',constcolor="#FF69B4",callback=lambda:dialog_savedgame(self)),1)],
                [],
                [('过滤反复刷新的句子',5),(getsimpleswitch(globalconfig,'direct_filterrepeat'),1)],
                [('刷新延迟(ms)',5),(getspinbox(0,10000,globalconfig,'textthreaddelay',callback=lambda x:gobject.baseobject.textsource.setsettings()),3)],
                [('文本缓冲区长度',5),(getspinbox(0,10000,globalconfig,'flushbuffersize',callback=lambda x:gobject.baseobject.textsource.setsettings()),3)],
                [('过滤包含乱码的文本行',5),(getsimpleswitch(globalconfig,'filter_chaos_code'),1),(getcolorbutton(globalconfig,'',icon='fa.gear',constcolor="#FF69B4",callback=lambda:codeacceptdialog(self)),1)],
                [],
                [('区分人名和文本',5),getsimpleswitch(globalconfig,'allow_set_text_name')],
                [('使用YAPI注入',5),getsimpleswitch(globalconfig,'use_yapi')],
        ]
         
        return grids
updatelock=threading.Lock()
def updatescripts( self):
        if globalconfig['fridahook']['autoupdate']==False:return
        if updatelock.locked():return
        updatelock.acquire()
        if (os.path.exists(os.path.join(globalconfig['fridahook']['path'],'runtime/x86/frida')) or os.path.exists(os.path.join(globalconfig['fridahook']['path'],'runtime/x64/frida')))==False:return
        info_url='https://api.github.com/repos/0xDC00/scripts'
        scripts_url = f'https://api.github.com/repos/0xDC00/scripts/zipball'
        updated_at = requests.get(info_url ,proxies=getproxy()).json()['pushed_at']
        updatetimef=os.path.join(globalconfig['fridahook']['path'],'updatetime.txt')
        savezip=os.path.join(globalconfig['fridahook']['path'],'latest.zip')
        scriptspath=os.path.join(globalconfig['fridahook']['path'],'scripts')
        timefmt=lambda s:datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        dt = timefmt(updated_at ) 
        #print(updated_at,dt)
        try:
            with open(updatetimef,'r') as ff:
                time=ff.read()
            if timefmt(time)<dt:
                need=True
            else:
                need=False
        except:
            need=True
            print_exc()
        #print(need)
        try:
            if need:
                response = requests.get(scripts_url ,proxies=getproxy()).content
                with open(savezip,'wb') as ff:
                    ff.write(response)
                zipf=(zipfile.ZipFile(savezip))
                zipf.extractall(globalconfig['fridahook']['path'])
                try:    
                        shutil.rmtree(scriptspath)
                except:
                       pass
                os.rename(os.path.join( globalconfig['fridahook']['path'],zipf.namelist()[0]),scriptspath)
               
                with open(updatetimef,'w') as ff:
                    ff.write(updated_at)
                flashcombo(self,0)
        except:
            print_exc()
        updatelock.release()
def flashcombo(self,update=1):
        self.fridascripts=loadfridascriptslist(globalconfig['fridahook']['path'],self.Scriptscombo)
        if update:
                threading.Thread(target=updatescripts,args=(self,)).start()
def getfridahookgrid(self) :
        
        
        _items=[
            {'t':'file','dir':True, 'l':'FridaHook_路径','d':globalconfig['fridahook'],'k':'path'},
            {'t':'okcancel','callback':functools.partial(flashcombo,self,1)},
        ]
        attachbutton=QPushButton('Attach')
        execbutton=QPushButton('Spawn')
        def execclicked():
                
                f=QFileDialog.getOpenFileName(filter='*.exe')
                pname=f[0]
                if pname!='':
                        pname=pname.replace('/','\\')
                        checkifnewgame(pname) 
                        yuitsu_switch(gobject.baseobject.settin_ui,globalconfig['sourcestatus2'],'sourceswitchs','fridahook',None ,True) 
                        gobject.baseobject.starttextsource(use='fridahook',checked=True)
                        try:
                                gobject.baseobject.textsource=fridahook(1,self.fridascripts[self.Scriptscombo.currentIndex()],pname)
                        except:
                                print_exc()
        
        execbutton.clicked.connect(execclicked)
        attachbutton.clicked.connect(gobject.baseobject.AttachProcessDialog.showsignal.emit)
        grids=[
                
                [('FridaHook_路径',3),(getcolorbutton(globalconfig,'',callback=functools.partial(autoinitdialog,self, 'FridaHook_路径',800,_items),icon='fa.gear',constcolor="#FF69B4"))],
                [('下载',3),(makehtml("https://github.com/HIllya51/RESOURCES/releases/download/dictionary/FridaHook.zip",True),3,'link')],
                [],

                [('Scripts',3),(self.Scriptscombo,10)],
                [(attachbutton,3),(execbutton,3)] ,
                [],
                [('autoupdate',3),getsimpleswitch( globalconfig['fridahook'],'autoupdate' )],
                [],
                
                
                [('latest scripts',3),(makehtml("https://github.com/0xDC00/scripts"),6,'link')],
                [('capable emulator',3),(makehtml("https://github.com/koukdw/emulators/releases"),6,"link")]
        ]
         
        return grids

def doexportchspatch(exe,realgame):
        
        b=windows.GetBinaryType(exe) 
        is64=(b==6)
        arch=['32','64'][is64]
        
        dllhook=os.path.abspath('./files/plugins/LunaHook/LunaHook{}.dll'.format(arch))
        dllhost=os.path.abspath('./files/plugins/LunaHook/LunaHost{}.dll'.format(arch,arch))
        runner=os.path.abspath('./files/plugins/shareddllproxy{}.exe'.format(arch))

        windows.CopyFile(dllhook,os.path.join(os.path.dirname(exe),os.path.basename(dllhook)),False)
        windows.CopyFile(dllhost,os.path.join(os.path.dirname(exe),os.path.basename(dllhost)),False)
        windows.CopyFile(runner,os.path.join(os.path.dirname(exe),'LunaPatch.exe'),False)

        embedconfig={
              'translation_file':'translation.json',
              'target_exe':os.path.basename(exe),
              'target_exe2':os.path.basename(realgame),
              'startup_argument':None,
              'inject_timeout':1000,
              'embedhook':savehook_new_data[realgame]['embedablehook'],
              'embedsettings':{
                    'font':globalconfig['embedded']['changefont_font'] if globalconfig['embedded']['changefont'] else '',
                    'insertspace_policy':globalconfig['embedded']['insertspace_policy'],
                    'keeprawtext':globalconfig['embedded']['keeprawtext']
              }
        }
        with open(os.path.join(os.path.dirname(exe),'LunaPatch.json'),'w',encoding='utf8') as ff:
              ff.write(json.dumps(embedconfig,ensure_ascii=False,indent=4))
def getunknowgameexe(self): 
     

    dialog = QDialog(self,Qt.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle(_TR("选择游戏"))
    dialog.resize(QSize(800,10))
    formLayout = QFormLayout(dialog) 
    dialog.setLayout(formLayout)

    combo=QComboBox()
    combo.addItems([savehook_new_data[_]['title'] for _ in savehook_new_list])

    formLayout.addRow(_TR("选择游戏"),combo) 
     
    button = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel) 
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)
    button.accepted.connect(dialog.accept)
    button.button(QDialogButtonBox.Ok).setText(_TR('确定'))
    button.button(QDialogButtonBox.Cancel).setText(_TR('取消'))
    if(dialog.exec()):
        return savehook_new_list[combo.currentIndex()]
def exportchspatch(self):
        realgame=getunknowgameexe(self)
        if realgame is None:return
        exe=realgame
        if exe.lower().endswith('.exe')==False:
                f=QFileDialog.getOpenFileName(self,caption= _TR("选择EXE文件"),filter='*.exe')
                exe=f[0]
                if exe=='':return
                exe=exe.replace('/','\\')
        doexportchspatch(exe,realgame)
        md5=getfilemd5(exe)
        name= os.path.basename(exe).replace('.'+os.path.basename(exe).split('.')[-1],'') 
        sqlfname_all='./translation_record/'+name+'_'+md5+'.sqlite'
        if os.path.exists(sqlfname_all)==False:
                f=QFileDialog.getOpenFileName(self,caption=_TR("选择预翻译文件"), directory='./translation_record/',filter='*.sqlite')
                sqlfname_all=f[0]
        if os.path.exists(sqlfname_all):
                sqlite2json2(self,sqlfname_all,os.path.join(os.path.dirname(exe),'translation.json'),existsmerge=True)
        else:
                with open(os.path.join(os.path.dirname(exe),'translation.json'),'w') as ff:
                      ff.write("{}")
def gethookembedgrid(self) :   
        self.gamefont_comboBox = QFontComboBox( ) 
        def callback(x):
                globalconfig['embedded'].__setitem__('changefont_font',x)
                try:
                        gobject.baseobject.textsource.flashembedsettings()
                except:
                        pass
        self.gamefont_comboBox.activated[str].connect(callback)   
        self.gamefont_comboBox.setCurrentFont(QFont(globalconfig['embedded']['changefont_font']))  
        grids=[
                 
                [('导出翻译补丁',5),getcolorbutton(globalconfig,'',callback=lambda x:exportchspatch(self),icon='fa.gear',constcolor="#FF69B4")],
                [],
                [('保留原文',5),(getsimpleswitch( globalconfig['embedded'],'keeprawtext',callback=lambda _:gobject.baseobject.textsource.flashembedsettings())  ,1) ],
                 
                [('翻译等待时间(s)',5),'',(getspinbox(0,30,globalconfig['embedded'],'timeout_translate',double=True,step=0.1,callback=lambda x:gobject.baseobject.textsource.flashembedsettings()),3) ],
                [('使用最快翻译而非指定翻译器',5),(getsimpleswitch( globalconfig['embedded'] ,'as_fast_as_posible'),1) ],
                [('内嵌的翻译器',5),'',(getsimplecombobox(_TRL([globalconfig['fanyi'][x]['name'] for x in globalconfig['fanyi']]),globalconfig['embedded'],'translator'),5) ],
                [('将汉字转换成繁体/日式汉字',5),(getsimpleswitch( globalconfig['embedded'] ,'trans_kanji'),1) ],
                [('在重叠显示的字间插入空格',5),'',(getsimplecombobox(_TRL(['不插入空格','每个字后插入空格','仅在无法编码的字后插入']),globalconfig['embedded'],'insertspace_policy',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),5) ],
                [('修改游戏字体',5),(getsimpleswitch( globalconfig['embedded'] ,'changefont',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),1), (self.gamefont_comboBox,5)],
                [],
                [('内嵌安全性检查',5),getsimpleswitch(globalconfig['embedded'],'safecheck_use' ),getcolorbutton(globalconfig,'',callback=lambda x:regexedit(self,globalconfig['embedded']['safecheckregexs']),icon='fa.gear',constcolor="#FF69B4")]
                #[('修改字体字符集',5),(getsimpleswitch( globalconfig['embedded'] ,'changecharset',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),1) ,(getsimplecombobox(_TRL(static_data["charsetmapshow"]),globalconfig['embedded'],'changecharset_charset',callback=lambda _:gobject.baseobject.textsource.flashembedsettings()),5)],

        ]
        
        return grids
        
def setTabclip(self) :
          
        grids=[
            [
                ('提取的文本自动复制到剪贴板',5),(getsimpleswitch(globalconfig ,'outputtopasteboard' ),1),('',3)
                
            ],
            [('排除复制自翻译器的文本',5),(getsimpleswitch(globalconfig ,'excule_from_self' ),1), ], 
            
        ]
        return grids


def setTabOne_direct(self) :  
        
        self.tab1grids=[
                [ ('选择文本输入源',8)],
                
                [
                        ('剪贴板',3),(getsimpleswitch(globalconfig['sourcestatus2']['copy'],'use',name='copy',parent=self,callback= functools.partial(yuitsu_switch,self, globalconfig['sourcestatus2'],'sourceswitchs','copy',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'',
                        ('OCR',3),(getsimpleswitch(globalconfig['sourcestatus2']['ocr'],'use',name='ocr',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus2'],'sourceswitchs','ocr',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),'', 
                       
                ], 
                [
                         ('HOOK',3),(getsimpleswitch(globalconfig['sourcestatus2']['texthook'],'use',name='texthook',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus2'],'sourceswitchs','texthook',gobject.baseobject.starttextsource),pair='sourceswitchs'),1), '',
                         ('FridaScripts',3),(getsimpleswitch(globalconfig['sourcestatus2']['fridahook'],'use',name='fridahook',parent=self,callback= functools.partial(yuitsu_switch,self,globalconfig['sourcestatus2'],'sourceswitchs','fridahook',gobject.baseobject.starttextsource),pair='sourceswitchs'),1),

                     
                ] ,
        ]  

        getcolorbutton(globalconfig ,'',name='selectbutton',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit())
        getcolorbutton(globalconfig ,'',name='selectbuttonembed',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda :gobject.baseobject.AttachProcessDialog.showsignal.emit())
        getcolorbutton(globalconfig ,'',name='selecthookbutton',parent=self,icon='fa.gear',constcolor="#FF69B4",callback=lambda  : gobject.baseobject.hookselectdialog.showsignal.emit() )
        self.clicksourcesignal.connect(lambda k: getattr(self,'sourceswitchs')[k].click())


        self.threshold1label=QLabel()
        self.threshold2label=QLabel()

        self.Scriptscombo=QComboBox() 
        flashcombo(self,1)
def setTabOne(self) :  
        self.tabadd_lazy(self.tab_widget, ('文本输入'), lambda :setTabOne_lazy(self)) 

def setTabOne_lazy(self) : 
        
         
         
        tab=self.makesubtab_lazy(['HOOK设置','OCR设置','剪贴板','内嵌翻译','FridaScripts'],
                                [       
                                        lambda:self.makescroll(self.makegrid(gethookgrid(self))),
                                        lambda:self.makescroll(self.makegrid(getocrgrid(self))),
                                        lambda:self.makescroll(self.makegrid(setTabclip(self))),
                                        lambda:self.makescroll(self.makegrid(gethookembedgrid(self) )),
                                        lambda:self.makescroll(self.makegrid(getfridahookgrid(self) ))
                                ]) 

        gridlayoutwidget=self.makegrid(self.tab1grids )    
        return self.makevbox([gridlayoutwidget,tab]) 