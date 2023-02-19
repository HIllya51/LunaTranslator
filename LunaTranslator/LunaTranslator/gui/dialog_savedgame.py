  
import functools,win32api 
from PyQt5.QtWidgets import  QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog ,QGridLayout
import functools 
from traceback import print_exc 
from PyQt5.QtWidgets import    QHBoxLayout, QTableView, QAbstractItemView, QLabel, QVBoxLayout
import qtawesome 

from PyQt5.QtGui import QStandardItem, QStandardItemModel  
from PyQt5.QtGui import QColor,QFont,QPixmap,QIcon 
from PyQt5.QtCore import Qt,QSize  
from utils.config import   savehook_new_list,savehook_new_data
from utils.getpidlist import getExeIcon 
from utils.le3264 import le3264run  
from utils.config import _TR,_TRL
import os
import win32con,win32api  
from utils.wrapper import Singleton_close
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
                
        def selectexe(self,item:QStandardItem ):
                f=QFileDialog.getOpenFileName(directory=item.savetext )
                res=f[0]
                if res!='':
                        res=res.replace('/','\\')
                        savehook_new_list[savehook_new_list.index(item.savetext)]=res 
                        savehook_new_data[res]=savehook_new_data[item.savetext] 
                        item.savetext=res   
                        self.table.setIndexWidget(self.model.index(self.model.indexFromItem(item).row(), 1),self.object.getcolorbutton('','',functools.partial(self._opendir,res),qicon=getExeIcon(res) ))
                
        def clicked2(self): 
                try: 
                        savehook_new_list.pop(self.table.currentIndex().row())
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
                        savehook_new_list.insert(0,res) 
                        self.newline(0,res)
                        self.table.setCurrentIndex(self.model.index(0,0))
                        
        def clicked(self): 
                try: 
                    game=self.model.item(self.table.currentIndex().row(),2).savetext 
                    if os.path.exists(game):
                        #subprocess.Popen(model.item(table.currentIndex().row(),1).text())  
                        if savehook_new_data[game]['leuse'] :
                                le3264run(game)
                        else:
                                win32api.ShellExecute(None, "open", game, "", os.path.dirname(game), win32con.SW_SHOW) 
                        savehook_new_list.insert(0,savehook_new_list.pop(self.table.currentIndex().row())) 
                        self.close() 
                except:
                        print_exc()
        def _opendir(self,k):
                try:
                        os.startfile(os.path.dirname(k))
                except:
                        pass
        def newline(self,row,k): 
                keyitem=QStandardItem()
                keyitem.savetext=k
                k=k.replace('/','\\')
                 
                if k not in savehook_new_data:
                        savehook_new_data[k]={'leuse':True,'title':os.path.basename(os.path.dirname(k))+'/'+ os.path.basename(k),'hook':[] } 
                        print(k,savehook_new_data[k])
                self.model.insertRow(row,[QStandardItem( ),QStandardItem( ),keyitem,QStandardItem( (savehook_new_data[k]['title'] ) )])  
                self.table.setIndexWidget(self.model.index(row, 0),self.object.getsimpleswitch(savehook_new_data[k],'leuse'))
                self.table.setIndexWidget(self.model.index(row, 1),self.object.getcolorbutton('','',functools.partial(self._opendir,k),qicon=getExeIcon(k) ))
                
                self.table.setIndexWidget(self.model.index(row, 2),self.object.getcolorbutton('','',functools.partial(self.selectexe,keyitem),icon='fa.gear',constcolor="#FF69B4")) 
        def __init__(self, object ) -> None:
                # if dialog_savedgame._sigleton :
                #         return
                # dialog_savedgame._sigleton=True 
                super().__init__(object, Qt.WindowCloseButtonHint)
                self.setWindowTitle(_TR('已保存游戏'))
                self.object=object
                formLayout = QVBoxLayout(self)  # 
                model=QStandardItemModel(   )
                model.setHorizontalHeaderLabels(_TRL(['转区','','路径', '游戏']))#,'HOOK'])
         
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

