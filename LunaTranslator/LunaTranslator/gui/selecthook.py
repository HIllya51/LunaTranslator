import functools,json
from traceback import print_exc 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy,QWidget,QHBoxLayout,QDialog,QAction,QVBoxLayout,QMenu,QPlainTextEdit,QTabWidget,QComboBox,QLineEdit,QPushButton,QTableView,QAbstractItemView,QRadioButton,QButtonGroup,QHeaderView,QCheckBox,QSpinBox,QFormLayout ,QLabel
from myutils.config import savehook_new_list,savehook_new_data,static_data
from PyQt5.QtGui import QStandardItem, QStandardItemModel 
from PyQt5.QtGui import QFont,QTextCursor
from PyQt5.QtCore import Qt,pyqtSignal,QSize,QModelIndex,QPoint
import qtawesome
import subprocess
import winsharedutils
import os,time 
import gobject
import binascii 
from myutils.subproc import subproc_w
from myutils.config import globalconfig ,_TR,_TRL
from collections import OrderedDict
from gui.usefulwidget import closeashidewindow,getQMessageBox,dialog_showinfo,getsimplecombobox,getsimpleswitch,getcolorbutton,textbrowappendandmovetoend
from myutils.utils import checkchaos ,checkifnewgame
from gui.dialog_savedgame import dialog_setting_game
def getformlayoutw(w=None,cls=QFormLayout,hide=False):
    if w is None:
        _w=QWidget()
    else:
        _w=w
    _l=cls()
    if hide:
        _w.hide()
    _l.setContentsMargins(0,0,0,0)
    _w.setLayout(_l)
    return _w,_l
class QButtonGroup_switch_widegt(QWidget):
    selectidx=pyqtSignal(int)
    def __init__(self,p,text=None) -> None:
        super().__init__()
        self._parent=p
        _,self.mainlayout=getformlayoutw(self,QVBoxLayout) 
        self.selectlayout=QHBoxLayout() 
        self.selectlayout.setContentsMargins(0,0,0,0) 
        if text is not None:
            self.mainlayout.addWidget(QLabel(text))
        self.mainlayout.addLayout(self.selectlayout)
        self.selectGroup=QButtonGroup()
        self.wlist=[]
        self.selectGroup.buttonClicked.connect(self.selectmodelf)
    def idx(self):
        return self.selectGroup.checkedId()
    def selectmodelf(self,idx):
        idx=self.idx()
        self.selectidx.emit(idx)
        for _ in range(len(self.wlist)):
            if _!=idx:
                self.wlist[_].hide() 
                self._parent.resize(self._parent.width(),1)
        self.wlist[idx].show()
        self._parent.resize(self._parent.width(),1)
    def addW(self,text,widget):
        self.mainlayout.addWidget(widget)
        btn=QRadioButton(text)
        self.selectGroup.addButton(btn,len(self.wlist))
        self.selectlayout.addWidget(btn)
        if len(self.wlist)==0:
            btn.setChecked(True)
        else:
            widget.hide()
        self.wlist.append(widget)
def listprocessm():
    cachefname=os.path.abspath('./cache/{}.txt'.format(time.time())) 
    arch='64' if gobject.baseobject.textsource.is64bit else '32'
    exe=os.path.abspath('./files/plugins/shareddllproxy{}.exe'.format(arch)) 
    pid=' '.join([str(_) for _ in gobject.baseobject.textsource.pids])
    subprocess.run('"{}"  listpm "{}" {}'.format(exe,cachefname,pid)) 
    
    with open(cachefname,'r',encoding='utf-16-le') as ff:
        readf=(ff.read())
    
    os.remove(cachefname)
    _list=readf.split('\n')[:-1]
    if len(_list)==0:return []

    ret=[]
    hasprogram='c:\\program files' in _list[0].lower() 
    for name_ in _list:
        name=name_.lower()
        if ':\\windows\\'  in name   or '\\microsoft\\'  in name or '\\windowsapps\\'  in name:
            continue 
        if hasprogram==False and 'c:\\program files' in name:
            continue
        fn=name_.split('\\')[-1]
        if fn in ret:
            continue
        if fn.lower() in ['lunahook32.dll','lunahook64.dll']:
            continue
        ret.append(fn)
    return ret
class searchhookparam(QDialog):
    def safehex(self,string,default):
        try:
            return int(string.replace(" ", "").replace("0x", ""),16)
        except:
            return default
    def searchstart(self):
        idx=self.searchmethod.idx()
        usestruct=gobject.baseobject.textsource.defaultsp()
        if idx==0:
            usestruct.length=0
            usestruct.codepage=static_data["codepage_real"][self.codepagesave['spcp']]
            #sp = spUser.length == 0 ? spDefault : spUser;
        elif idx==1:  #0默认
            #usestruct.codepage=self.codepage.value()
            usestruct.codepage=static_data["codepage_real"][self.codepagesave['spcp']]
            usestruct.text=self.searchtext.text()
            if len(usestruct.text)<4:
                getQMessageBox(self,"警告","搜索文本过短！",True)
                return
        elif idx==2:
            dumpvalues={}
            for k,widget in self.regists.items():
                if type(widget)==QLineEdit:
                    dumpvalues[k]=(widget.text())
                if type(widget)==QSpinBox:
                    dumpvalues[k]=(widget.value())
            pattern=dumpvalues['pattern']
            if('.' in pattern):
                usestruct.length=1
                usestruct.exportModule=pattern[:120]
            else:
                try:  
                    bs=bytes.fromhex(pattern.replace(" ", "").replace("0x", "").replace('??','11'))
                    usestruct.pattern=bs[:30]
                    usestruct.length=len(bs)
                except:pass 
            usestruct.boundaryModule=dumpvalues['module'][:120]
            usestruct.address_method=self.search_addr_range.idx()
            usestruct.search_method=self.search_method.idx()
            if self.search_addr_range.idx()==0:
                usestruct.minAddress=self.safehex(dumpvalues['startaddr'], usestruct.minAddress)
                usestruct.maxAddress=self.safehex(dumpvalues['stopaddr'], usestruct.maxAddress)
            else:
                usestruct.minAddress=self.safehex(dumpvalues['offstartaddr'], usestruct.minAddress)
                usestruct.maxAddress=self.safehex(dumpvalues['offstopaddr'], usestruct.maxAddress)
            usestruct.padding=0#self.safehex(dumpvalues[4], usestruct.padding)
            usestruct.offset=dumpvalues['offset']
            usestruct.codepage=static_data["codepage_real"][self.codepagesave['spcp']]#dumpvalues[6]
            usestruct.searchTime=dumpvalues['time']*1000#dumpvalues[7]
            usestruct.maxRecords=dumpvalues['maxrecords']#dumpvalues[8]
        gobject.baseobject.textsource.findhook(usestruct)
        if idx!=1:
            self.parent().findhookchecked()
        self.close()
     
    def hex2str(self,h):
        byte_data = h
        hex_str = binascii.hexlify(byte_data).decode() 
        space_hex_str = ' '.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])
        return space_hex_str
    def __init__(self, parent ) -> None:
        super().__init__(parent, Qt.WindowCloseButtonHint )
        self.setWindowTitle(_TR("搜索设置"))
        mainlayout=QVBoxLayout()
        checks=QButtonGroup_switch_widegt(self)
        self.searchmethod=checks
        self.setLayout(mainlayout)
        
        layout1=QHBoxLayout()
        layout1.addWidget(QLabel(_TR("代码页")))
        self.codepagesave={'spcp':savehook_new_data[gobject.baseobject.textsource.pname]['codepage_index']}
        layout1.addWidget( getsimplecombobox(_TRL(static_data['codepage_display']),self.codepagesave,'spcp' ))
        
        mainlayout.addLayout(layout1) 

        usestruct=gobject.baseobject.textsource.defaultsp() 
        w1,self.layoutseatchtext=getformlayoutw(hide=True)
        
        self.searchtext=QLineEdit()
        # self.codepage=QSpinBox()
        # self.codepage.setMaximum(100000)
        # self.codepage.setValue(usestruct.codepage)
        self.layoutseatchtext.addRow(_TR("文本"), self.searchtext)        
 
        w2,self.layoutsettings=getformlayoutw(hide=True)
        _=QWidget()
        self.wlist=[_,w1,w2]

        self.regists={}
        def autoaddline(reg, _vis,_val,_type,uselayout=self.layoutsettings,getlistcall=None):
            if _type==0:
                line=QLineEdit(_val) 
                regwid=addwid=line
            elif _type==1:
                sp=QSpinBox()
                sp.setMaximum(10000000)
                sp.setValue(_val) 
                regwid=addwid=sp
            elif _type==2:
                line=QLineEdit(_val) 
                line._idx=0
                try:
                    _list=getlistcall()
                except:
                    _list=[]
                if len(_list)==0:
                    regwid=addwid=line
                else:
                    combo=QComboBox( )  
                    combo.addItems(_list)
                    def __(_line,__list,idx):
                        _line.setText(__list[idx])
                    combo.currentIndexChanged.connect(functools.partial(__,line,_list) )
                    def switch(_1,_2):
                        _1._idx+=1
                        _1.setVisible(_1._idx%2==0)
                        _2.setVisible(_1._idx%2==1) 
                    btn=getcolorbutton('','',functools.partial(switch,line,combo),icon='fa.edit',constcolor="#FF69B4")
                    btn.click() 
                    _w,_l=getformlayoutw(cls=QHBoxLayout) 
                    _l.addWidget(line)
                    _l.addWidget(combo)
                    _l.addWidget(btn)
                    addwid=_w
                    regwid=line
            uselayout.addRow(_TR(_vis),addwid)
            self.regists[reg]=(regwid)
        
        self.search_addr_range=QButtonGroup_switch_widegt(self)
        self.layoutsettings.addRow(_TR("搜索范围"),self.search_addr_range)
        absaddrw,absaddrl=getformlayoutw() 
        offaddrw,offaddrl=getformlayoutw()  
        self.search_addr_range.addW("绝对地址",absaddrw)
        self.search_addr_range.addW("相对地址",offaddrw)
        autoaddline('startaddr','起始地址(hex)',hex(usestruct.minAddress)[2:],0,uselayout=absaddrl)
        autoaddline('stopaddr','结束地址(hex)',hex(usestruct.maxAddress)[2:],0,uselayout=absaddrl)
        
        autoaddline('module','指定模块',usestruct.boundaryModule,2,uselayout=offaddrl,getlistcall=listprocessm)
        autoaddline('offstartaddr','起始地址(hex)',hex(usestruct.minAddress)[2:],0,uselayout=offaddrl)
        autoaddline('offstopaddr','结束地址(hex)',hex(usestruct.maxAddress)[2:],0,uselayout=offaddrl)
        
        self.search_method=QButtonGroup_switch_widegt(self)
        self.layoutsettings.addRow(_TR("搜索方式"),self.search_method)
        
        
        patternW,patternWl=getformlayoutw() 
        #presetW,presetWl=getformlayoutw()  
        self.search_method.addW("特征匹配",patternW)
        self.search_method.addW("函数对齐",QLabel())
        self.search_method.addW("函数调用",QLabel())

        autoaddline('pattern','搜索匹配的特征(hex)',self.hex2str(usestruct.pattern),0,uselayout=patternWl)
        autoaddline('offset','相对特征地址的偏移',usestruct.offset,1,uselayout=patternWl)

        autoaddline('time','搜索持续时间(s)',usestruct.searchTime//1000,1)
        autoaddline('maxrecords','搜索结果数上限',usestruct.maxRecords,1)  

        checks.addW(_TR("默认搜索"),_)
        checks.addW(_TR("文本搜索"),w1)
        checks.addW(_TR("自定义搜索"),w2)
        mainlayout.addWidget(checks)
        btn=QPushButton(_TR("开始搜索"))
        btn.clicked.connect(self.searchstart)
        mainlayout.addWidget(btn)
        self.show()
class hookselect(closeashidewindow):
    addnewhooksignal=pyqtSignal(tuple,bool,list)
    getnewsentencesignal=pyqtSignal(str)
    sysmessagesignal=pyqtSignal(str)
    changeprocessclearsignal=pyqtSignal()
    removehooksignal=pyqtSignal(tuple)
    getfoundhooksignal=pyqtSignal(dict)
    update_item_new_line=pyqtSignal(tuple,str)  
    def __init__(self,parent):
        super(hookselect, self).__init__(parent,globalconfig,'selecthookgeo')  
        self.setupUi( )
        
        self.changeprocessclearsignal.connect(self.changeprocessclear)
        self.removehooksignal.connect(self.removehook)
        self.addnewhooksignal.connect(self.addnewhook)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.sysmessagesignal.connect(self.sysmessage)
        self.update_item_new_line.connect(self.update_item_new_line_function)
        self.getfoundhooksignal.connect(self.getfoundhook)
        self.setWindowTitle(_TR('选择文本'))
     
        
    def update_item_new_line_function(self,hook,output): 
        if hook not in self.save:return
        row=self.save.index(hook)
        output=output[:200].replace('\n','') 
        colidx=2+(gobject.baseobject.textsource.allow_set_text_name)
        self.ttCombomodelmodel.item(row,colidx).setText(output) 
    def removehook(self,key):
        if key not in self.save:return
        self.ttCombomodelmodel.removeRow(self.save.index(key))
        self.selectionbutton.pop(self.save.index(key))
        self.save.remove(key)

    def changeprocessclear(self):
        #self.ttCombo.clear() 
        self.ttCombomodelmodel.clear()
        self.save=[]
        self.at1=1
        self.textOutput.clear()
        self.selectionbutton=[] 
        self.typecombo=[] 
        self.allres=OrderedDict() 
        self.hidesearchhookbuttons()
    def addnewhook(self,ss ,select,textthread):
        hc,hn,tp=textthread
        if len(self.save)==0:
            if gobject.baseobject.textsource.allow_set_text_name:
                self.ttCombomodelmodel.setHorizontalHeaderLabels(_TRL(['显示','类型','HOOK','文本']))
            
                self.tttable.horizontalHeader().setSectionResizeMode(2,QHeaderView.Interactive)
                self.tttable.horizontalHeader().setSectionResizeMode(3,QHeaderView.Interactive)
            
                self.tttable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
                self.tttable.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
            else:
                self.ttCombomodelmodel.setHorizontalHeaderLabels(_TRL(['选择','HOOK','文本']))
            
                self.tttable.horizontalHeader().setSectionResizeMode(1,QHeaderView.Interactive)
                self.tttable.horizontalHeader().setSectionResizeMode(2,QHeaderView.Interactive)
            
                self.tttable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        
        
        
        
        
        if(ss[-1][0]=='E'):
            self.selectionbutton.insert(0,getsimpleswitch({1:False},1,callback=functools.partial(self.accept,ss))) 
            self.save.insert(0,ss)
            rown=0 
        else: 
            self.save.append(ss ) 
            rown=self.ttCombomodelmodel.rowCount()
            self.selectionbutton.append(getsimpleswitch({1:False},1,callback=functools.partial(self.accept,ss))) 
        if gobject.baseobject.textsource.allow_set_text_name:
            for jskey in savehook_new_data[gobject.baseobject.textsource.pname]['hooktypeasname']:
                if savehook_new_data[gobject.baseobject.textsource.pname]['hooktypeasname'][jskey]==0:continue
                if gobject.baseobject.textsource.match_compatibility(json.loads(jskey),ss):
                    gobject.baseobject.textsource.hooktypecollecter[ss]=1
            self.typecombo.insert(rown,getsimplecombobox(_TRL(['文本','人名']),gobject.baseobject.textsource.hooktypecollecter,ss,callback=functools.partial(savehook_new_data[gobject.baseobject.textsource.pname]['hooktypeasname'].__setitem__,json.dumps(ss))))
            self.ttCombomodelmodel.insertRow(rown,[QStandardItem(),QStandardItem(),QStandardItem('%s %s %x:%x' %(ss[-2],ss[-1],ss[-3],ss[-4])),QStandardItem()])  
            self.tttable.setIndexWidget(self.ttCombomodelmodel.index(rown,1),self.typecombo[rown])
        else:
            self.ttCombomodelmodel.insertRow(rown,[QStandardItem(),QStandardItem('%s %s %x:%x' %(ss[-2],ss[-1],ss[-3],ss[-4])),QStandardItem()])  
                    
        
        if select:self.selectionbutton[rown].click()
        self.tttable.setIndexWidget(self.ttCombomodelmodel.index(rown,0),self.selectionbutton[rown])
        if(ss[-1][0]=='E'):
            embedw,hlay=getformlayoutw(cls=QHBoxLayout)
            label=QLabel()
            hlay.addWidget(label)
            label.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
            checkbtn=QPushButton()
            checkbtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            def _t(tp):
                _isusing=gobject.baseobject.textsource.checkisusingembed(tp.addr,tp.ctx,tp.ctx2)
                if _isusing:
                    _text='取消内嵌翻译'
                    checkifnewgame(gobject.baseobject.textsource.pname)
                        

                    if(ss[-2][:8]=='UserHook'): 
                        needinserthookcode= savehook_new_data[gobject.baseobject.textsource.pname]['needinserthookcode']  
                        needinserthookcode=list(set(needinserthookcode+[ss[-1]]))
                        savehook_new_data[gobject.baseobject.textsource.pname].update({  'needinserthookcode':needinserthookcode } )
                    else:
                        pass
                else:
                    _text="使用内嵌翻译"
                checkbtn.setText('【'+_TR(_text)+'】') 
                return _isusing
            _t(tp) 
            def _c(hc,tp,_):
                gobject.baseobject.textsource.useembed(tp.addr,tp.ctx,tp.ctx2,not _t(tp))
                _use=_t(tp)
                if _use:
                    savehook_new_data[gobject.baseobject.textsource.pname]['embedablehook'].append([hc,tp.addr,tp.ctx,tp.ctx2])
                else:
                    save=[]
                    for _ in savehook_new_data[gobject.baseobject.textsource.pname]['embedablehook']:
                        hc,ad,c1,c2=_
                        if(hc,ad,c1,c2)==(hc,tp.addr,tp.ctx,tp.ctx2):
                            save.append(_)
                    for _ in save:
                        savehook_new_data[gobject.baseobject.textsource.pname]['embedablehook'].remove(_)
            checkbtn.clicked.connect(functools.partial(_c,hc,tp))
            hlay.addWidget(checkbtn)
            colidx=2+(gobject.baseobject.textsource.allow_set_text_name)
            self.tttable.setIndexWidget(self.ttCombomodelmodel.index(rown,colidx),embedw)
        

    def setupUi(self  ):
        
        self.widget = QWidget() 
        self.setWindowIcon(qtawesome.icon("fa.gear" ))
        self.hboxlayout = QHBoxLayout()  
        self.widget.setLayout(self.hboxlayout)
        self.vboxlayout = QVBoxLayout()    
        self.ttCombomodelmodel=QStandardItemModel()  
        
        
        self.tttable = QTableView()
        self.tttable .setModel(self.ttCombomodelmodel)
        #self.tttable .horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.tttable .horizontalHeader().setStretchLastSection(True) 
        self.tttable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tttable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tttable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tttable.doubleClicked.connect(self.table1doubleclicked)
        self.tttable.clicked.connect(self.ViewThread)
        #self.tttable.setFont(font)
        self.vboxlayout.addWidget(self.tttable)
        #table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #table.clicked.connect(self.show_info)
        
        self.tttable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tttable.customContextMenuRequested.connect(self.showmenu  )
        
        #self.ttCombo.setMaxVisibleItems(50) 
        
        self.userhooklayout = QHBoxLayout() 
        self.vboxlayout.addLayout(self.userhooklayout)
        self.userhook=QLineEdit() 
        self.userhooklayout.addWidget(self.userhook)
        self.userhookinsert=QPushButton(_TR("插入特殊码")) 
        self.userhookinsert.clicked.connect(self.inserthook)
        self.userhooklayout.addWidget(self.userhookinsert)

        self.userhookinsert=QPushButton(icon=qtawesome.icon('fa.question')) 
        self.userhookinsert.clicked.connect(lambda:dialog_showinfo(self,'CODE',static_data['hcodeintroduction']))
        self.userhooklayout.addWidget(self.userhookinsert)

        self.userhookfind=QPushButton(_TR("搜索特殊码")) 
        self.userhookfind.clicked.connect(self.findhook)
        self.userhooklayout.addWidget(self.userhookfind)
         
        self.opensolvetextb=QPushButton(_TR("文本处理")) 
        self.opensolvetextb.clicked.connect(self.opensolvetext)
        self.userhooklayout.addWidget(QLabel("      "))
        self.userhooklayout.addWidget(self.opensolvetextb)

        
        self.settingbtn=QPushButton(_TR("游戏设置")) 
        self.settingbtn.clicked.connect(self.opengamesetting)
        self.userhooklayout.addWidget(self.settingbtn)

        #################
        self.searchtextlayout = QHBoxLayout() 
        self.vboxlayout.addLayout(self.searchtextlayout)
        self.searchtext=QLineEdit() 
        self.searchtextlayout.addWidget(self.searchtext)
        self.searchtextbutton=QPushButton(_TR("搜索包含文本的条目"))
         
        self.searchtextbutton.clicked.connect(self.searchtextfunc)
        self.searchtextlayout.addWidget(self.searchtextbutton)
        ###################
        self.ttCombomodelmodel2=QStandardItemModel(self) 
        #self.ttCombomodelmodel.setColumnCount(2)
        self.ttCombomodelmodel2.setHorizontalHeaderLabels(_TRL([ 'HOOK','文本']))
        
        
        self.tttable2 = QTableView(self)
        self.tttable2 .setModel(self.ttCombomodelmodel2)
        #self.tttable2 .horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 
        self.tttable2.horizontalHeader().setStretchLastSection(True) 
        self.tttable2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tttable2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tttable2.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        self.tttable2.clicked.connect(self.ViewThread2) 
         
        self.vboxlayout.addWidget(self.tttable2)
        self.searchtextlayout2 = QHBoxLayout()   
        self.vboxlayout.addLayout(self.searchtextlayout2)
        self.searchtext2=QLineEdit() 
        self.searchtextlayout2.addWidget(self.searchtext2)
        self.searchtextbutton2=QPushButton(_TR("搜索包含文本的条目"))
        self.checkfilt_notcontrol=QCheckBox(_TR("过滤控制字符"))
        self.checkfilt_notascii=QCheckBox(_TR("过滤纯英文")) 
        self.checkfilt_notshiftjis=QCheckBox(_TR("过滤乱码文本"))  
        self.checkfilt_notcontrol.setChecked(True)
        self.checkfilt_notascii.setChecked(True) 
        self.checkfilt_notshiftjis.setChecked(True)  
        self.searchtextlayout2.addWidget(self.checkfilt_notcontrol)
        self.searchtextlayout2.addWidget(self.checkfilt_notascii)  
        self.searchtextlayout2.addWidget(self.checkfilt_notshiftjis)   
        self.searchtextbutton2.clicked.connect(self.searchtextfunc2)
        self.searchtextlayout2.addWidget(self.searchtextbutton2) 


        
        self.textOutput = QPlainTextEdit()
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True) 


        self.sysOutput = QPlainTextEdit()
        self.sysOutput.setUndoRedoEnabled(False)
        self.sysOutput.setReadOnly(True) 

        self.tabwidget=QTabWidget()
        self.tabwidget.setTabPosition(QTabWidget.East)
        self.tabwidget.addTab(self.textOutput,_TR("文本"))
        self.tabwidget.addTab(self.sysOutput,_TR("系统"))

        self.vboxlayout.addWidget(self.tabwidget)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setCentralWidget(self.widget)
         
        
        self.changeprocessclear()
    def showmenu(self,p:QPoint):  
        menu=QMenu(self.tttable ) 
        remove=QAction(_TR("移除"))  
        copy=QAction(_TR("复制特殊码") ) 
        menu.addAction(remove)  
        menu.addAction(copy)
        action=menu.exec(self.tttable.cursor().pos())
        
        r=self.tttable.currentIndex().row() 
        if r<0:return 
        hook=self.save[r] 
        if action==remove:
            pid=hook[0]
            addr=hook[1]
            gobject.baseobject.textsource.removehook(pid,addr)
         
        elif action==copy :
            copyhook=hook[-1]
            if copyhook[0]=='E':
                copyhook=copyhook[copyhook.find('H'):]
            winsharedutils.clipboard_set(copyhook)
             
    def opensolvetext(self):
        gobject.baseobject.settin_ui.opensolvetextsig.emit()
    def opengamesetting(self):
        try:
            dialog_setting_game(self,gobject.baseobject.textsource.pname) 
        except:
            print_exc()
    def gethide(self,res ):
        hide=False
        
        if self.checkfilt_notascii.isChecked():
            try:
                res.encode('ascii')
                hide=True
            except:
                pass
        if self.checkfilt_notshiftjis.isChecked():
            if checkchaos(res):
                hide=True
             
        if self.checkfilt_notcontrol.isChecked():
            lres=list(res)
            
            for r in lres:
                _ord=ord(r)
                if _ord<0x20 or (_ord>0x80 and _ord<0xa0):

                    hide=True
                    break
        
        return hide
    def searchtextfunc2(self):
        searchtext=self.searchtext2.text() 
        
        for index in range(len(self.allres)):   
            _index=len(self.allres)-1-index
            
            resbatch=self.allres[list(self.allres.keys())[_index]] 
             
            hide=all([ (searchtext not in res) or self.gethide(res ) for res in resbatch]) 
            self.tttable2.setRowHidden(_index,hide)  
            
    def searchtextfunc(self):
        searchtext=self.searchtext.text() 
 
        #self.ttCombomodelmodel.blockSignals(True)
        try:
            for index,key in enumerate(gobject.baseobject.textsource.hookdatacollecter):   
                ishide=True  
                for i in range(min(len(gobject.baseobject.textsource.hookdatacollecter[key]),20)):
                    
                    if searchtext  in [_.replace('\n','') for _ in gobject.baseobject.textsource.hookdatacollecter[key][-i:]]:
                        ishide=False
                        break
                self.tttable.setRowHidden(index,ishide) 
        except:
            pass
        #self.ttCombomodelmodel.blockSignals(False)  
            #self.ttCombo.setItemData(index,'',Qt.UserRole-(1 if ishide else 0))
            #self.ttCombo.setRowHidden(index,ishide)
    def inserthook(self): 
        hookcode=self.userhook.text()
        if len(hookcode)==0:
            return 
        
        if  gobject.baseobject.textsource:
            print(hookcode)
            gobject.baseobject.textsource.inserthook(hookcode)
            self.tabwidget.setCurrentIndex(1)
        else:
            self.getnewsentence(_TR('！未选定进程！'))
    def hidesearchhookbuttons(self,hide=True):
         
        self.tttable2.setHidden(hide)
        self.searchtextbutton2.setHidden(hide)
        self.searchtext2.setHidden(hide)
        self.checkfilt_notcontrol.setHidden(hide)
        self.checkfilt_notascii.setHidden(hide)
        self.checkfilt_notshiftjis.setHidden(hide) 
    def findhook(self): 
        if gobject.baseobject.textsource is None:return 
        if globalconfig['sourcestatus2']['texthook']['use']==False:
            return 
        getQMessageBox(self,"警告","该功能可能会导致游戏崩溃！",True,True,lambda:searchhookparam(self))
    def findhookchecked(self):  
            if  gobject.baseobject.textsource:  
                self.allres.clear()
                self.ttCombomodelmodel2.clear()
                self.ttCombomodelmodel2.setHorizontalHeaderLabels(_TRL([ 'HOOK','文本']))
                self.hidesearchhookbuttons() 
            else:
                self.getnewsentence(_TR('！未选定进程！'))
    def getfoundhook(self,hooks):
       
        searchtext=self.searchtext2.text() 
          
        for hookcode in hooks:
            string=hooks[hookcode][-1]
            if hookcode not in self.allres:
                self.allres[hookcode]=hooks[hookcode].copy()
                self.ttCombomodelmodel2.insertRow(self.ttCombomodelmodel2.rowCount(),[QStandardItem(hookcode),QStandardItem(string[:100])])  
            else:
                self.allres[hookcode]+=hooks[hookcode].copy() 
                self.ttCombomodelmodel2.setItem(list(self.allres.keys()).index(hookcode),1,QStandardItem(string[:100]))  
              
            resbatch=self.allres[hookcode] 
            hide=all([ (searchtext not in res) or self.gethide(res ) for res in resbatch])
            self.tttable2.setRowHidden(list(self.allres.keys()).index(hookcode),hide)  
        if len(hooks)==0:return 
        self.hidesearchhookbuttons(False) 
    def accept(self,key,select):
        try: 
            
            gobject.baseobject.textsource.lock.acquire()


            checkifnewgame(gobject.baseobject.textsource.pname)
            if key in gobject.baseobject.textsource.selectedhook:
                gobject.baseobject.textsource.selectedhook.remove(key)

            if select :
                gobject.baseobject.textsource.selectedhook.append(key)

                print(key)
                if(key[-2][:8]=='UserHook'): 
                    needinserthookcode= savehook_new_data[gobject.baseobject.textsource.pname]['needinserthookcode']  
                    needinserthookcode=list(set(needinserthookcode+[key[-1]]))
                    
                    savehook_new_data[gobject.baseobject.textsource.pname].update({  'needinserthookcode':needinserthookcode } )
            else:
                pass
             
            savehook_new_data[gobject.baseobject.textsource.pname].update({ 'hook':gobject.baseobject.textsource.selectedhook } )
            gobject.baseobject.textsource.lock.release()
        except:
            print_exc() 
    def showEvent(self,e):   
        gobject.baseobject.AttachProcessDialog.realshowhide.emit(False)
        try:  
            for i in range(len(self.save)):  
                if self.save[i] in gobject.baseobject.textsource.selectedhook: 
                    self.tttable.setCurrentIndex(self.ttCombomodelmodel.index(i,0)) 
                    break
        except:
            print_exc() 
    def get_time_stamp(self):
        ct = time.time()
        local_time = time.localtime(ct)
        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        data_secs = (ct - int(ct)) * 1000
        time_stamp = "%s.%03d" % (data_head, data_secs)
        return (time_stamp)
         
    def sysmessage(self,sentence):
          
        textbrowappendandmovetoend(self.sysOutput,self.get_time_stamp()+" "+sentence) 
    
    def getnewsentence(self,sentence):
        if self.at1==2:
            return 
          
        textbrowappendandmovetoend(self.textOutput,sentence) 
 
    def ViewThread2(self, index:QModelIndex):   
        self.tabwidget.setCurrentIndex(0)  
        self.at1=2
        key=list(self.allres.keys())[index.row()]
        self.userhook.setText(key)
        self.textOutput. setPlainText('\n'.join(self.allres[key] )) 
    def ViewThread(self, index:QModelIndex): 
        self.tabwidget.setCurrentIndex(0)   
        self.at1=1 
        try:
            #print(gobject.baseobject.textsource)
            gobject.baseobject.textsource.selectinghook=self.save[index.row()]
            
            self.textOutput. setPlainText('\n'.join(gobject.baseobject.textsource.hookdatacollecter[self.save[index.row()]]))
            self.textOutput. moveCursor(QTextCursor.End)

        except:
            print_exc()
    def table1doubleclicked(self,index:QModelIndex): 
            self.selectionbutton[index.row()].click()