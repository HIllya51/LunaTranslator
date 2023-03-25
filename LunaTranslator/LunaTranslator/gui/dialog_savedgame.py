  
import functools 
from PyQt5.QtWidgets import  QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog ,QLineEdit
import functools,threading
from traceback import print_exc 
from PyQt5.QtWidgets import    QHBoxLayout, QTableView, QAbstractItemView, QLabel, QVBoxLayout
import win32utils 

from PyQt5.QtGui import QStandardItem, QStandardItemModel   
from PyQt5.QtCore import Qt,QSize  
from utils.config import   savehook_new_list,savehook_new_data
from utils.hwnd import getExeIcon 
from utils.utils import le3264run  
from utils.config import _TR,_TRL,globalconfig
import os
import win32con,win32utils
from utils import somedef
from utils.wrapper import Singleton_close,Singleton
from utils.config import checkifnewgame
def opendir( k):
                try:
                        os.startfile(os.path.dirname(k))
                except:
                        pass
@Singleton
class dialog_setting_game(QDialog):
        def selectexe(self,item:QStandardItem ):
                f=QFileDialog.getOpenFileName(directory=self.exepath )
                res=f[0]
                if res!='':
                        
                        res=res.replace('/','\\')
                        savehook_new_list[savehook_new_list.index(self.exepath)]=res 
                        savehook_new_data[res]=savehook_new_data[self.exepath] 
                        _icon=getExeIcon(res)
                        try:
                                item.savetext=res   
                                self.table.setIndexWidget(self.model.index(self.model.indexFromItem(item).row(), 1),self.object.getcolorbutton('','',functools.partial( opendir,res),qicon=_icon ))
                        except:
                                pass
                        self.setWindowIcon(_icon)
                        self.lujing.setText(res)
                        self.exepath=res
        def __init__(self, parent,exepath, item=None,settingui=None) -> None:
                super().__init__(parent, Qt.WindowCloseButtonHint )
                checkifnewgame(exepath)
                formLayout = QVBoxLayout(self)  # 配置layout
                if settingui:
                        self.object=settingui
                else:
                        self.object=parent.object
                
                self.item=item
                self.exepath=exepath
                lujing=QHBoxLayout()
                editpath=QLineEdit(exepath)
                editpath.setReadOnly(True)
                if item:
                        self.table=parent.table
                        self.model=parent.model
                        editpath.textEdited.connect(lambda _:item.__setitem__('savetext',_)) 
                lujing.addWidget(QLabel(_TR("修改路径")))
                lujing.addWidget(editpath)
                lujing.addWidget(self.object.getcolorbutton('','',functools.partial(self.selectexe,item),icon='fa.gear',constcolor="#FF69B4"))
                self.lujing=editpath
                self.setWindowTitle(savehook_new_data[exepath]['title'])
                self.resize(QSize(600,200))
                self.setWindowIcon(getExeIcon(exepath))
                formLayout.addLayout(lujing)
                
                try:
                        b=win32utils.GetBinaryType(exepath)
                        if b==0: 
                                lrelay=QHBoxLayout()
                                lrelay.addWidget(QLabel(_TR("使用Locale_Remulator转区")))
                                
                                lrelay.addWidget(self.object.getsimpleswitch(savehook_new_data[exepath],'alwaysuselr'))
                                formLayout.addLayout(lrelay)
                except:
                        pass
                autochangestatus=QHBoxLayout()
                autochangestatus.addWidget(QLabel(_TR("自动切换到模式"))) 
                autochangestatus.addWidget(self.object.getsimplecombobox(_TRL(['不切换','HOOK','HOOK_内嵌','剪贴板','OCR']),savehook_new_data[exepath],'onloadautochangemode'))
                formLayout.addLayout(autochangestatus)
                
                remove_useless_hook_layout=QHBoxLayout()
                remove_useless_hook_layout.addWidget(QLabel(_TR('移除非选定HOOK')))
                remove_useless_hook_layout.addWidget(self.object.getsimpleswitch(savehook_new_data[exepath],'remove_useless_hook'))
                formLayout.addLayout(remove_useless_hook_layout)


                cp_layout=QHBoxLayout()
                cp_layout.addWidget(QLabel(_TR('代码页')))
                cp_layout.addWidget(self.object.getsimplecombobox(_TRL(somedef.codepage_display),savehook_new_data[exepath],'codepage_index' ,lambda x: self.object.object.textsource.setcodepage()))
                formLayout.addLayout(cp_layout)
                

                model=QStandardItemModel(   )
                model.setHorizontalHeaderLabels(_TRL(['删除','特殊码',]))#,'HOOK'])
         
                self.hcmodel=model
                
                table = QTableView( )
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                table.horizontalHeader().setStretchLastSection(True)
                #table.setEditTriggers(QAbstractItemView.NoEditTriggers);
                table.setSelectionBehavior(QAbstractItemView.SelectRows)
                table.setSelectionMode( (QAbstractItemView.SingleSelection)      )
                table.setWordWrap(False) 
                table.setModel(model) 
                self.hctable=table

                for row,k in enumerate(savehook_new_data[exepath]['needinserthookcode']):                                   # 2
                        self.newline(row,k)  
                 
                formLayout.addWidget(self.hctable) 

                ttsonname=QHBoxLayout()
                ttsonname.addWidget(QLabel(_TR("自动朗读仅当名字为指定名字时才执行"))) 
                
                ttsonname.addWidget(self.object.getsimpleswitch(savehook_new_data[exepath],'ttsonname')) 
                formLayout.addLayout(ttsonname)
                ttsname=QHBoxLayout()
                editname=QLineEdit('|'.join(savehook_new_data[exepath]['ttsusename']))
                editname.textEdited.connect(lambda t:savehook_new_data[exepath].__setitem__('ttsusename',t.split('|')))
                ttsname.addWidget(QLabel(_TR('指定朗读的名字(以|分隔多个,以"None"表示没有名字)'))) 
                ttsname.addWidget(editname)
                formLayout.addLayout(ttsname)
                self.show()
        def clicked2(self):
                try: 
                        savehook_new_data[self.exepath]['needinserthookcode'].pop(self.hctable.currentIndex().row()) 
                        self.hcmodel.removeRow(self.hctable.currentIndex().row())
                except:
                        pass
        
        def newline(self,row,k):  
                 
                self.hcmodel.insertRow(row,[QStandardItem( ),QStandardItem(k)])  
                    
                self.hctable.setIndexWidget(self.hcmodel.index(row, 0),self.object.getcolorbutton('','',self.clicked2,icon='fa.times',constcolor="#FF69B4")) 
@Singleton_close
class dialog_savedgame(QDialog):
        #_sigleton=False
        def closeEvent( self, a0  ) -> None:
                
                self.button.setFocus()
                rows=self.model.rowCount() 
                 
                for row in range(rows):  
                        savehook_new_data[self.model.item(row,2).savetext]['title']=self.model.item(row,3).text()
               # dialog_savedgame._sigleton=False
                return QDialog().closeEvent(a0)
                
        
        def showsettingdialog(self,k,item):
                dialog_setting_game(self,k,item) 
        def clicked2(self): 
                try: 
                        key=savehook_new_list.pop(self.table.currentIndex().row())
                        if key in savehook_new_data:
                                savehook_new_data.pop(key)
                        self.model.removeRow(self.table.currentIndex().row())
                except:
                        pass
        def clicked3(self): 
                
                f=QFileDialog.getOpenFileName(directory='' )
                res=f[0]
                if res!='':
                        row=0#model.rowCount() 
                        res=res.replace('/','\\')
                        if res in savehook_new_list: 
                                return
                        
                        self.newline(0,res)
                        self.table.setCurrentIndex(self.model.index(0,0))
                        
        def clicked(self): 
                try: 
                    
                    game=self.model.item(self.table.currentIndex().row(),2).savetext 

                

                    if os.path.exists(game):

                        if 'onloadautochangemode' in savehook_new_data[game]:
                                mode=savehook_new_data[game]['onloadautochangemode']
                                if mode==0:
                                        pass
                                else:
                                        _={
                                        1:'textractor',
                                        2:'embedded',
                                        3:'copy',
                                        4:'ocr'
                                        } 
                                        if globalconfig['sourcestatus'][_[mode]]['use']==False:
                                                globalconfig['sourcestatus'][_[mode]]['use']=True
                                                
                                                self.object.yuitsu_switch('sourcestatus','sourceswitchs',_[mode],None ,True) 
                                                self.object.object.starttextsource(use=_[mode],checked=True,waitforautoinit=True)
                        
                        savehook_new_list.insert(0,savehook_new_list.pop(self.table.currentIndex().row())) 
                        self.close() 
                        if savehook_new_data[game]['leuse'] :
                                le3264run(game,savehook_new_data[game]['alwaysuselr'])
                        else:
                                win32utils.ShellExecute(None, "open", game, "", os.path.dirname(game), win32con.SW_SHOW) 
                except:
                        print_exc()
        
        def newline(self,row,k): 
                keyitem=QStandardItem()
                keyitem.savetext=k
                k=k.replace('/','\\')
                checkifnewgame(k)
                self.model.insertRow(row,[QStandardItem( ),QStandardItem( ),keyitem,QStandardItem( (savehook_new_data[k]['title'] ) )])  
                self.table.setIndexWidget(self.model.index(row, 0),self.object.getsimpleswitch(savehook_new_data[k],'leuse'))
                self.table.setIndexWidget(self.model.index(row, 1),self.object.getcolorbutton('','',functools.partial( opendir,k),qicon=getExeIcon(k) ))
                
                # self.table.setIndexWidget(self.model.index(row, 2),self.object.getcolorbutton('','',functools.partial(self.selectexe,keyitem),icon='fa.gear',constcolor="#FF69B4")) 
                self.table.setIndexWidget(self.model.index(row, 2),self.object.getcolorbutton('','',functools.partial(self.showsettingdialog,k,keyitem ),icon='fa.gear',constcolor="#FF69B4")) 
        def __init__(self, object ) -> None:
                # if dialog_savedgame._sigleton :
                #         return
                # dialog_savedgame._sigleton=True 
                super().__init__(object, Qt.WindowCloseButtonHint)
                self.setWindowTitle(_TR('已保存游戏'))
                self.object=object
                formLayout = QVBoxLayout(self)  # 
                model=QStandardItemModel(   )
                model.setHorizontalHeaderLabels(_TRL(['转区','','设置', '游戏']))#,'HOOK'])
         
                self.model=model
                
                table = QTableView( )
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                table.horizontalHeader().setStretchLastSection(True)
                #table.setEditTriggers(QAbstractItemView.NoEditTriggers);
                table.setSelectionBehavior(QAbstractItemView.SelectRows)
                table.setSelectionMode( (QAbstractItemView.SingleSelection)      )
                table.setWordWrap(False) 
                table.setModel(model) 
                self.table=table 
                for row,k in enumerate(savehook_new_list):                                   # 2
                        self.newline(row,k) 
                button=QPushButton( )
                button.setText(_TR('开始游戏'))
                self.button=button
                button.clicked.connect(self.clicked)
                button3=QPushButton( )
                button3.setText(_TR('添加游戏'))

                        
                button3.clicked.connect(self.clicked3)
                button2=QPushButton( )
                button2.setText(_TR('删除游戏'))
                
                button2.clicked.connect(self.clicked2)
                
                formLayout.addWidget(table) 
                formLayout.addWidget(button) 
                formLayout.addWidget(button3) 
                formLayout.addWidget(button2) 
                self.resize(QSize(800,400))
                self.show() 

