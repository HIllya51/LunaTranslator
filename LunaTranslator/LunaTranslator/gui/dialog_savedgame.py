  
import functools ,time
from PyQt5.QtWidgets import  QPushButton,QDialog,QVBoxLayout ,QHeaderView,QFileDialog ,QLineEdit,QFormLayout
import functools,threading
from traceback import print_exc 
from PyQt5.QtWidgets import    QHBoxLayout, QTableView, QAbstractItemView, QLabel, QVBoxLayout,QSpacerItem,QTabWidget,QComboBox
import importlib
import windows
from PyQt5.QtCore import QPoint, QRect, QSize, Qt,pyqtSignal,QCoreApplication
import os,hashlib
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import   QApplication, QLayout, QSizePolicy, QWidget, QGridLayout ,QMenu,QAction,QTabBar
from PyQt5.QtGui import QIntValidator, QColor,QResizeEvent,QIcon,QPixmap
from PyQt5.QtCore import Qt 
from gui.usefulwidget import getsimplecombobox,getspinbox,getcolorbutton,getsimpleswitch,getspinbox,selectcolor
from PyQt5.QtCore import QPoint, QRect, QSize, Qt,pyqtSignal
import os   
from textsource.fridahook import fridahook
from myutils.hwnd import showintab
from PyQt5.QtGui import QStandardItem, QStandardItemModel   
from PyQt5.QtCore import Qt,QSize  
from myutils.config import   savehook_new_list,savehook_new_data
from myutils.hwnd import getExeIcon  
import gobject
from myutils.config import _TR,_TRL,globalconfig,static_data 
import winsharedutils
from myutils.wrapper import Singleton_close,Singleton,threader
from myutils.utils import checkifnewgame ,loadfridascriptslist
from myutils.proxy import getproxy
from gui.usefulwidget import yuitsu_switch,saveposwindow,getboxlayout
from myutils.vndb import parsehtmlmethod
from webview import Webview
class ItemWidget(QWidget):
  focuschanged=pyqtSignal(bool,str)
  doubleclicked=pyqtSignal(str)
  def focusInEvent(self, ev ) -> None: 
        self.bottommask.setStyleSheet('QLabel { background-color: '+globalconfig['dialog_savegame_layout']['onselectcolor']+'; }') 
        self.focuschanged.emit(True,self.exe)
  def focusOutEvent(self, event):
        self.bottommask.setStyleSheet('QLabel { background-color: rgba(255,255,255, 0); }')
        self.focuschanged.emit(False,self.exe)
  def mouseDoubleClickEvent(self,e):
        self.doubleclicked.emit(self.exe)
  def resizeEvent(self, a0: QResizeEvent) -> None:
    self.bottommask.resize(a0.size()) 
    self.maskshowfileexists.resize(a0.size()) 
  def settitle(self,text):
        self._lb.setText(text)
  def setimg(self,pixmap):
        self._img.setimg(pixmap)
  def connectexepath(self,exe):
        self.exe=exe
        self.latershowfileexits(exe)
  @threader      
  def latershowfileexits(self,exe):
        if os.path.exists(exe):
                self.maskshowfileexists.setStyleSheet('QLabel { background-color: rgba(255,255,255, 0); }')
        else:
                self.maskshowfileexists.setStyleSheet('QLabel { background-color: '+globalconfig['dialog_savegame_layout']['onfilenoexistscolor']+'; }') 
  def __init__(self,pixmap,file) -> None:
    super().__init__()  
    self.itemw=globalconfig['dialog_savegame_layout']['itemw']
    self.itemh=globalconfig['dialog_savegame_layout']['itemh'] 
    self.imgw=globalconfig['dialog_savegame_layout']['imgw']
    self.imgh=globalconfig['dialog_savegame_layout']['imgh']
    margin=(self.itemw-self.imgw)//2#globalconfig['dialog_savegame_layout']['margin']
    self.setFixedSize(QSize(self.itemw,self.itemh)) 
    self.setFocusPolicy(Qt.StrongFocus)   
    self.maskshowfileexists=QLabel(self)  
    self.bottommask=QLabel(self)  
    layout=QVBoxLayout()
    layout.setContentsMargins(margin,0,margin,0)
    self._img=IMGWidget(self.imgw,self.imgh,pixmap)
    layout.addWidget(self._img)

    self._lb=QLabel(file)
    self._lb.setWordWrap(True)
    layout.addWidget(self._lb)
    self.setLayout(layout) 
class IMGWidget(QWidget):
  
  def adaptsize(self,size:QSize):
    h,w=size.height(),size.width()
    if h< self.imgmaxheigth and w<self.imgmaxwidth:
        return size
    r = float(w) / h
    max_r = float(self.imgmaxwidth) / self.imgmaxheigth
    if r > max_r:
        new_w = self.imgmaxwidth
        new_h = int(new_w / r)
    else:
        new_h = self.imgmaxheigth
        new_w = int(new_h * r)
    return QSize(new_w,new_h)
  @threader
  def setimg(self,pixmap):
        if type(pixmap)!=QPixmap: 
              pixmap=pixmap() 
        self.label.setPixmap(pixmap)
        self.label.setFixedSize(self.adaptsize(pixmap.size()))
  def __init__(self,w,h,pixmap) -> None:
    super().__init__() 
    self.imgmaxwidth=w
    self.imgmaxheigth=h
    self.setFixedSize(QSize(self.imgmaxwidth,self.imgmaxheigth)) 
    layout=QGridLayout()
    layout.setContentsMargins(0,0,0,0) 
    self.label = QLabel()
    self.label.setScaledContents(True) 
    
    self.setimg(pixmap)  
    layout.addWidget(self.label) 
    
    self.setLayout(layout) 
 

class ScrollFlow(QWidget):
  def resizeEvent(self, a0 ) -> None:
    self.qscrollarea.resize(self.size())
    return super().resizeEvent(a0)
  def __init__(self): 
    super(ScrollFlow, self).__init__() 
    
    self.listWidget = QtWidgets.QListWidget(self)
    #self.listWidget.setFixedWidth(600) 
    
    self.l = FlowLayout() 
     
    self.listWidget.setLayout(self.l)
 
    self.qscrollarea = QtWidgets.QScrollArea(self) 
    self.qscrollarea.setWidgetResizable(True)
    self.qscrollarea.setWidget(self.listWidget) 
  def addwidget(self,wid):
    self.l.addWidget(wid) 
  def removeidx(self,index):
    _=self.l.takeAt(index)
    _.widget().hide()
class FlowLayout(QLayout): 
  heightChanged = pyqtSignal(int)
 
  def __init__(self, parent=None, margin=0, spacing=-1):
    super().__init__(parent)
    if parent is not None:
      self.setContentsMargins(margin, margin, margin, margin)
    self.setSpacing(spacing)
 
    self._item_list = []
 
  def __del__(self):
    while self.count():
      self.takeAt(0)
 
  def addItem(self, item): # pylint: disable=invalid-name
    self._item_list.append(item)
 
  def addSpacing(self, size): # pylint: disable=invalid-name
    self.addItem(QSpacerItem(size, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
 
  def count(self):
    return len(self._item_list)
 
  def itemAt(self, index): # pylint: disable=invalid-name
    if 0 <= index < len(self._item_list):
      return self._item_list[index]
    return None
 
  def takeAt(self, index): # pylint: disable=invalid-name
    if 0 <= index < len(self._item_list):
      return self._item_list.pop(index)
    return None
 
  def expandingDirections(self): # pylint: disable=invalid-name,no-self-use
    return Qt.Orientations(Qt.Orientation(0))
 
  def hasHeightForWidth(self): # pylint: disable=invalid-name,no-self-use
    return True
 
  def heightForWidth(self, width): # pylint: disable=invalid-name
    height = self._do_layout(QRect(0, 0, width, 0), True)
    return height
 
  def setGeometry(self, rect): # pylint: disable=invalid-name
    super().setGeometry(rect)
    self._do_layout(rect, False)
 
  def sizeHint(self): # pylint: disable=invalid-name
    return self.minimumSize()
 
  def minimumSize(self): # pylint: disable=invalid-name
    size = QSize()
 
    for item in self._item_list:
      minsize = item.minimumSize()
      extent = item.geometry().bottomRight()
      size = size.expandedTo(QSize(minsize.width(), extent.y()))
 
    margin = self.contentsMargins().left()
    size += QSize(2 * margin, 2 * margin)
    return size
 
  def _do_layout(self, rect, test_only=False):
    m = self.contentsMargins()
    effective_rect = rect.adjusted(+m.left(), +m.top(), -m.right(), -m.bottom())
    x = effective_rect.x()
    y = effective_rect.y()
    line_height = 0
 
    for item in self._item_list:
      wid = item.widget()
 
      space_x = self.spacing()
      space_y = self.spacing()
      if wid is not None:
        space_x += wid.style().layoutSpacing(
          QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
        space_y += wid.style().layoutSpacing(
          QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
 
      next_x = x + item.sizeHint().width() + space_x
      if next_x - space_x > effective_rect.right() and line_height > 0:
        x = effective_rect.x()
        y = y + line_height + space_y
        next_x = x + item.sizeHint().width() + space_x
        line_height = 0
 
      if not test_only:
        item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
 
      x = next_x
      line_height = max(line_height, item.sizeHint().height())
 
    new_height = y + line_height - rect.y()
    self.heightChanged.emit(new_height)
    return new_height


def opendir( k):
                try:
                        os.startfile(os.path.dirname(k))
                except:
                        pass
class CustomTabBar(QTabBar):
    lastclick=pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index == self.count() - 1 and event.button() == Qt.LeftButton:
            self.lastclick.emit()
        else:
            super().mousePressEvent(event)
@Singleton
class browserdialog(QDialog):
         
        def parsehtml(self,exepath):
                try:
                        newpath=parsehtmlmethod(savehook_new_data[exepath]['vid'],savehook_new_data[exepath]['infopath'])   
                except:
                        print_exc()
                        newpath=savehook_new_data[exepath]['infopath']
                if newpath[:4].lower()!='http':
                      newpath=os.path.abspath(newpath)
                return newpath
        def resizeEvent(self, a0: QResizeEvent) -> None:
              self.nettab.resize(a0.size().width(),self.nettab.height())
              if self.webviewv==0:
                    self.browser.resize(0,self.nettab.height(),a0.size().width(),a0.size().height()-self.nettab.height())
              elif self.webviewv==1:  
                      self.browser.set_geo(0,self.nettab.height(),a0.size().width(),a0.size().height()-self.nettab.height())
        def __init__(self, parent,exepath ) -> None:
                super().__init__(parent, Qt.WindowMinMaxButtonsHint|Qt.WindowCloseButtonHint)
                self.exepath=exepath
                self.webviewv=globalconfig['usewebview']
                self.resize(1300,800)
                if self.webviewv==0:
                        self.browser= winsharedutils.HTMLBrowser(int(self.winId()))
                elif self.webviewv==1:
                      self.browser=Webview(0,int(self.winId()))
                self.setWindowTitle(savehook_new_data[exepath]['title'])
                self.nettab=QTabWidget(self)
                self.nettab.setFixedHeight(self.nettab.tabBar().height()+10)
                tabBar = CustomTabBar(self)
                self.nettab.setTabBar(tabBar)
                tabBar.lastclick.connect(self.lastclicked)
                #self.nettab.setSizePolicy( QSizePolicy.Preferred,QSizePolicy.Fixed)
                self.nettab.addTab(QWidget(),"vndb")
                for lnk in savehook_new_data[self.exepath]['relationlinks']:
                      self.nettab.addTab(QWidget(),lnk[0])
                self.nettab.addTab(QWidget(),"+")
                self.nettab.currentChanged.connect(self.changetab)
                self.nettab.setContextMenuPolicy(Qt.CustomContextMenu)
                self.nettab.customContextMenuRequested.connect(self.showmenu) 
                self.changetab(0)
                #vbox.addWidget(self.nettab)
                #vbox.addWidget(qww)
                
                self.show()
        def showmenu(self,p):  
                tab_index = self.nettab.tabBar().tabAt(p)
                if tab_index ==0 or tab_index==self.nettab.count()-1:
                      return
                menu=QMenu(self ) 
                shanchu=QAction(_TR("删除"))  
                cache=QAction(_TR("缓存"))  
                menu.addAction(cache) 
                menu.addAction(shanchu) 
                action=menu.exec(self.mapToGlobal(p))
                if action==shanchu:
                        self.nettab.setCurrentIndex(0)
                        self.nettab.removeTab(tab_index)
                        savehook_new_data[self.exepath]['relationlinks'].pop(tab_index-1)
                elif action==cache:
                      def cachehtml(exepath,idx):
                                url=savehook_new_data[exepath]['relationlinks'][idx][1]
                                import requests

                                headers = {
                                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                                'accept-language': 'zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7',
                                'cache-control': 'no-cache',
                                'pragma': 'no-cache',
                                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                                'sec-ch-ua-mobile': '?0',
                                'sec-ch-ua-platform': '"Windows"',
                                'sec-fetch-dest': 'document',
                                'sec-fetch-mode': 'navigate',
                                'sec-fetch-site': 'same-origin',
                                'sec-fetch-user': '?1',
                                'upgrade-insecure-requests': '1',
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                }

                                response = requests.get(url, headers=headers,proxies=getproxy())
                                os.makedirs('./cache/cachehtml',exist_ok=True)
                                fn='./cache/cachehtml/'+hashlib.md5(url.encode('utf8')).hexdigest()+'.html'
                                with open(fn,'w',encoding='utf8') as ff:
                                      ff.write(response.text.replace('<HEAD>','<HEAD><base href="{}">'.format(url)).replace('<head>','<head><base href="{}">'.format(url)))
                                for i in range(len(savehook_new_data[exepath]['relationlinks'])):
                                        if url==savehook_new_data[exepath]['relationlinks'][i][1]:
                                              if len(savehook_new_data[exepath]['relationlinks'][i])==3:
                                                    savehook_new_data[exepath]['relationlinks'][i][2]=fn
                                              else:
                                                      savehook_new_data[exepath]['relationlinks'][i].append(fn)
                      threading.Thread(target=cachehtml,args=(self.exepath,tab_index-1)).start()
        def lastclicked(self):
                def callback(texts):
                            if len(texts[0].strip()) and len(texts[1].strip()):
                                  savehook_new_data[self.exepath]['relationlinks'].append(texts)
                                  self.nettab.insertTab(self.nettab.count()-1,QWidget(),texts[0])
                gobject.baseobject.Prompt.call.emit(_TR('添加关联页面'),_TR('页面类型_页面链接'),[['vndb/2df/...'],'about:blank'],[callback])
        def changetab(self,idx):
                if idx==0:
                        try:
                                self.browser.navigate((self.parsehtml( self.exepath)))
                        except:
                              self.browser.navigate('about:blank')
                else:
                      lnks=savehook_new_data[self.exepath]['relationlinks'][idx-1]
                      if len(lnks)==3 and os.path.exists(lnks[2]):
                            link=os.path.abspath(lnks[2])
                      else:
                            link=lnks[1]  
                      print(link)      
                      self.browser.navigate(link)
@Singleton
class dialog_setting_game(QDialog):
        def selectexe(self ):
                f=QFileDialog.getOpenFileName(directory=self.exepath )
                res=f[0]
                if res!='':
                        
                        res=res.replace('/','\\')
                        if res in savehook_new_list: 
                                return
                        savehook_new_list[savehook_new_list.index(self.exepath)]=res 
                        savehook_new_data[res]=savehook_new_data[self.exepath] 
                        savehook_new_data.pop(self.exepath)
                        _icon=getExeIcon(res,cache=True)
                        if self.item:
                                self.item.savetext=res   
                                self.table.setIndexWidget(self.model.index(self.model.indexFromItem(self.item).row(), 1),getcolorbutton('','',functools.partial( opendir,res),qicon=_icon ))
                        if self.gametitleitme:
                              if savehook_new_data[res]['imagepath'] is None:
                                      self.gametitleitme.setimg(getExeIcon(res,False,cache=True))
                              self.gametitleitme.connectexepath(res) 
                         
                        self.setWindowIcon(_icon)
                        self.editpath.setText(res)
                        self.exepath=res 
                
        def __init__(self, parent,exepath, item=None,type=1,gametitleitme=None) -> None:
                super().__init__(parent, Qt.WindowCloseButtonHint )
                checkifnewgame(exepath)
                formLayout = QVBoxLayout(self)  # 配置layout
                 
                self.item=item 
                self.exepath=exepath 
                self.gametitleitme=gametitleitme
                if type==2:
                        titleedit=QLineEdit(savehook_new_data[exepath]['title'])
                        def _titlechange(x):
                                savehook_new_data[exepath]['title']=x
                                savehook_new_data[exepath]['searchnoresulttime']=0
                                self.setWindowTitle(x)
                                gametitleitme.settitle(x)
                        titleedit.textChanged.connect(_titlechange)
                        formLayout.addLayout(getboxlayout([QLabel(_TR("标题")),titleedit]))

                       
                        imgpath=QLineEdit(savehook_new_data[exepath]['imagepath'])
                        imgpath.setReadOnly(True) 
                        def selectimg(  ):
                                f=QFileDialog.getOpenFileName(directory=savehook_new_data[exepath]['imagepath'])
                                res=f[0]
                                if res!='':
                                        
                                        _pixmap=QPixmap(res)
                                        if _pixmap.isNull()==False:
                                                savehook_new_data[exepath]['imagepath']=res
                                                imgpath.setText(res)
                                                gametitleitme.setimg(_pixmap)
                                       
                        formLayout.addLayout(getboxlayout([
                              QLabel(_TR("封面")),imgpath,
                              getcolorbutton('','',selectimg,icon='fa.gear',constcolor="#FF69B4"),
                              

                        ]))

                        vndbid=QLineEdit(str(savehook_new_data[exepath]['vid']))
                        vndbid.setValidator(QIntValidator())
                        vndbid.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

                        def changevid(exepath,text):
                              savehook_new_data[exepath]['vid']=int(text)
                              savehook_new_data[exepath]['infopath']=None
                              savehook_new_data[exepath]['searchnoresulttime']=0
                              #savehook_new_data[exepath]['imagepath']=None
                        vndbid.textEdited.connect(functools.partial(changevid,exepath))
                        
                        statiswids=[
                              QLabel(_TR("统计信息")),getcolorbutton('','',lambda:dialog_statistic(self,exepath),icon='fa.bar-chart',constcolor="#FF69B4"),
                              QLabel(_TR("vndbid")),vndbid,getcolorbutton('','',lambda: browserdialog(self,exepath),icon='fa.book',constcolor="#FF69B4")
                        ]
                        formLayout.addLayout(getboxlayout(statiswids))
                editpath=QLineEdit(exepath)
                editpath.setReadOnly(True)
                if item:
                        self.table=parent.table
                        self.model=parent.model
                        editpath.textEdited.connect(lambda _:item.__setitem__('savetext',_)) 
                self.editpath=editpath
                self.setWindowTitle(savehook_new_data[exepath]['title'])
                self.resize(QSize(600,200))
                self.setWindowIcon(getExeIcon(exepath,cache=True))
                formLayout.addLayout(getboxlayout([
                      QLabel(_TR("修改路径")),editpath,
                      getcolorbutton('','',functools.partial(self.selectexe),icon='fa.gear',constcolor="#FF69B4")
                ]))
                
                
                b=windows.GetBinaryType(exepath)
                
                if type==2: 
                        formLayout.addLayout(getboxlayout([
                              QLabel(_TR("转区启动")),
                              getsimpleswitch(savehook_new_data[exepath],'leuse')
                        ]))


                if b==6: 
                        _methods=['','Locale_Remulator','Ntleas' ]
                else:
                        _methods=['Locale-Emulator','Locale_Remulator','Ntleas' ]
                if b==6 and savehook_new_data[exepath]['localeswitcher']==0:
                        savehook_new_data[exepath]['localeswitcher']=2 
                formLayout.addLayout(getboxlayout([
                      QLabel(_TR("转区方法")),getsimplecombobox(_TRL(_methods),savehook_new_data[exepath],'localeswitcher')
                ])) 

 
                formLayout.addLayout(getboxlayout([
                      QLabel(_TR("自动切换到模式")),
                      getsimplecombobox(_TRL(['不切换','HOOK','剪贴板','OCR','FridaHook']),savehook_new_data[exepath],'onloadautochangemode2')
                ]))
                 

                methodtab=QTabWidget()
                methodtab.addTab(self.gethooktab(exepath),"HOOK")
                methodtab.addTab(self.getfridatab(exepath),"FridaHook")
                formLayout.addWidget(methodtab)
                
                self.show()
        def getfridatab(self,exepath):
                _w=QWidget()
                formLayout = QVBoxLayout()
                formLayout.setAlignment(Qt.AlignTop)
                _w.setLayout(formLayout)
                Scriptscombo=QComboBox() 
                Scriptscombo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
                fridascripts=loadfridascriptslist(globalconfig['fridahook']['path'],Scriptscombo)
                fridahook=savehook_new_data[exepath]['fridahook']
                try:
                      Scriptscombo.setCurrentIndex(fridascripts.index(fridahook['js']))
                except:
                      Scriptscombo.setCurrentIndex(0)
                Scriptscombo.currentTextChanged.connect(lambda text:fridahook.__setitem__('js',text))
                wids=[QLabel('Scripts'),Scriptscombo]
                wids[0].setFixedWidth(100)
                formLayout.addLayout(getboxlayout(wids))

                formLayout.addLayout(getboxlayout([
                      QLabel('Load Method'),
                      getsimplecombobox(['Attach','Spawn'],fridahook,'loadmethod')
                ]))


                return _w
        def gethooktab(self,exepath):
                _w=QWidget()
                formLayout = QVBoxLayout()
                _w.setLayout(formLayout) 
                formLayout.addLayout(getboxlayout([
                      QLabel(_TR('代码页')),
                      getsimplecombobox(_TRL(static_data['codepage_display']),savehook_new_data[exepath],'codepage_index' ,lambda x: gobject.baseobject.textsource.setsettings())
                ]))
 
                formLayout.addLayout(getboxlayout([
                      QLabel(_TR('移除非选定hook')),
                      getsimpleswitch(savehook_new_data[exepath],'removeuseless')
                ]))
                

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
                 
                formLayout.addLayout(getboxlayout([
                      QLabel(_TR('插入特殊码延迟(ms)')),
                      getspinbox(0,1000000,savehook_new_data[exepath],'inserthooktimeout' )
                ]))
                if savehook_new_data[exepath]['use_saved_text_process'] or 'save_text_process_info' in savehook_new_data[exepath]:  
                        formLayout.addLayout(getboxlayout([
                              QLabel(_TR("使用保存的文本处理流程")),
                              getsimpleswitch(savehook_new_data[exepath],'use_saved_text_process')
                        ]))
                if globalconfig['allow_set_text_name']:
                        edit=QLineEdit(savehook_new_data[exepath]['allow_tts_auto_names'])
                        edit.textChanged.connect(lambda x:savehook_new_data[exepath].__setitem__('allow_tts_auto_names',x))
                        formLayout.addLayout(getboxlayout([QLabel(_TR('禁止自动朗读的人名(以|分隔多个)')),edit]))
                return _w
        def clicked2(self):
                try: 
                        savehook_new_data[self.exepath]['needinserthookcode'].pop(self.hctable.currentIndex().row()) 
                        self.hcmodel.removeRow(self.hctable.currentIndex().row())
                except:
                        pass
        
        def newline(self,row,k):  
                 
                self.hcmodel.insertRow(row,[QStandardItem( ),QStandardItem(k)])  
                    
                self.hctable.setIndexWidget(self.hcmodel.index(row, 0),getcolorbutton('','',self.clicked2,icon='fa.times',constcolor="#FF69B4")) 
@Singleton
class dialog_syssetting(QDialog):
         
                
        def __init__(self, parent) -> None:
                super().__init__(parent, Qt.WindowCloseButtonHint )
                self.setWindowTitle(_TR("其他设置"))
                formLayout = QFormLayout(self) 
                formLayout.addRow(QLabel(_TR('隐藏不存在的游戏')),getsimpleswitch(globalconfig,'hide_not_exists')) 
                for key,name in [('itemw','宽度'),('itemh','高度'),('imgw','图片宽度'),('imgh','图片高度')]:
                        formLayout.addRow(QLabel(_TR(name)),getspinbox(0,1000,globalconfig['dialog_savegame_layout'],key)) 
                for key,name in [('onselectcolor','选中时颜色'),('onfilenoexistscolor','游戏不存在时颜色')]:
                        formLayout.addRow(QLabel(_TR(name)),getcolorbutton(globalconfig['dialog_savegame_layout'],key,callback= functools.partial(selectcolor,self,globalconfig['dialog_savegame_layout'],key,None,self,key),name=key,parent=self)) 
                          
                        
                self.show()
@Singleton
class dialog_statistic(QDialog):
        def formattime(self,t):
                t=int(t)
                s=t%60
                t=t//60
                m=t%60
                t=t//60
                h=t
                string=''
                if h:
                        string+=str(h)+_TR("时")
                if m:
                      string+=str(m)+_TR("分")
                if s: 
                      string+=str(s)+_TR('秒')
                if string=='':
                      string=_TR("未开始")
                return string
        refreshsignal=pyqtSignal()
        def refresh(self):
              while self.isVisible():
                        time.sleep(1) 
                        self._timelabel.setText(self.formattime(savehook_new_data[self.exepath]['statistic_playtime']))
                        self._wordlabel.setText(str(savehook_new_data[self.exepath]['statistic_wordcount']))
        def __init__(self, parent,exepath ) -> None:
                super().__init__(parent, Qt.WindowCloseButtonHint )
                checkifnewgame(exepath)
                self.exepath=exepath
                self.setWindowTitle(_TR("统计信息"))
                #self.resize(QSize(800,400))
                formlayout=QFormLayout()
                self._timelabel=QLabel(self.formattime(savehook_new_data[exepath]['statistic_playtime']))
                formlayout.addRow(_TR("游戏时间"),self._timelabel)
                self._wordlabel=QLabel(str(savehook_new_data[exepath]['statistic_wordcount']))
                formlayout.addRow(_TR("文字计数"),self._wordlabel)
                self.setLayout(formlayout)
                self.refreshsignal.connect(self.refresh)
                self.show()
                threading.Thread(target=self.refresh).start()
                
def startgame(game):
    try:         
        if os.path.exists(game):
                mode=savehook_new_data[game]['onloadautochangemode2']
                if mode==0:
                        pass
                else:
                    _={
                    1:'texthook', 
                    2:'copy',
                    3:'ocr',
                    4:'fridahook'
                    } 
                    if globalconfig['sourcestatus2'][_[mode]]['use']==False:
                            globalconfig['sourcestatus2'][_[mode]]['use']=True
                            
                            yuitsu_switch(gobject.baseobject.settin_ui,globalconfig['sourcestatus2'],'sourceswitchs',_[mode],None ,True) 
                            gobject.baseobject.starttextsource(use=_[mode],checked=True)
                if globalconfig['sourcestatus2']['fridahook']['use'] and savehook_new_data[game]['fridahook'].get('loadmethod')==1:
                        gobject.baseobject.textsource=fridahook(1,savehook_new_data[game]['fridahook'].get('js'),game)
                        return
                if savehook_new_data[game]['leuse']==False or (game.lower()[-4:] not in ['.lnk','.exe']):
                        #对于其他文件，需要AssocQueryStringW获取命令行才能正确le，太麻烦，放弃。
                        windows.ShellExecute(None, "open", game, "", os.path.dirname(game), windows.SW_SHOW) 
                        return 
                
                execheck3264=game
                usearg='"{}"'.format(game)
                dirpath=os.path.dirname(game)
                if game.lower()[-4:]=='.lnk':
                  exepath,args,iconpath,dirp=(winsharedutils.GetLnkTargetPath(game))
                  
                  if args!='':
                        usearg='"{}" {}'.format(exepath,args) 
                  elif exepath!='':
                        usearg='"{}"'.format(exepath)
                        
                  if exepath!='':
                        execheck3264=exepath
                   
                  if dirp!='':
                        dirpath=dirp
                
                localeswitcher=savehook_new_data[game]['localeswitcher'] 
                b=windows.GetBinaryType(execheck3264) 
                if b==6 and localeswitcher==0:
                        localeswitcher=1
                if (localeswitcher==2 and b==6):
                        _shareddllproxy='shareddllproxy64'
                else:
                        _shareddllproxy='shareddllproxy32'
                shareddllproxy=os.path.abspath('./files/plugins/'+_shareddllproxy)
                _cmd={0:'le',1:"LR",2:"ntleas"}[localeswitcher] 
                windows.CreateProcess(None,'"{}" {} {}'.format(shareddllproxy,_cmd,usearg), None,None,False,0,None, dirpath, windows.STARTUPINFO()  )  
    except:
            print_exc()

@Singleton_close
class dialog_savedgame_new(saveposwindow):  
        def startgame(self,game): 
                if os.path.exists(game):
                        idx =savehook_new_list.index(game)
                        savehook_new_list.insert(0,savehook_new_list.pop(idx)) 
                        self.close() 
                        startgame(game)
                
        def clicked2(self): 
                try: 
                        game=self.currentfocuspath 
                        idx=savehook_new_list.index(game) 
                        savehook_new_list.pop(idx)
                        if game in savehook_new_data:
                                savehook_new_data.pop(game) 
                        self.flow.removeidx(self.idxsave.index(game))
                        self.idxsave.pop(self.idxsave.index(game))
                        self.keepocus(idx)
                except:
                        pass
        def clicked4(self):
              opendir(self.currentfocuspath )
        def clicked3(self): 
                
                f=QFileDialog.getOpenFileName(directory='',options=QFileDialog.DontResolveSymlinks )
                
                res=f[0]
                if res!='': 
                        res=res.replace('/','\\')
                        if res not in savehook_new_list:  
                                self.newline(res)  
                                self.idxsave.append(res)
        def keepocus(self,idx):
                idx=min(len(savehook_new_list)-1,idx) 
                if len(savehook_new_list): 
                      self.flow.l._item_list[idx].widget().setFocus() 
        def top1focus(self): 
                if len(savehook_new_list): 
                      self.flow.l._item_list[0].widget().setFocus()
        def __init__(self, parent ) -> None:
                super().__init__(parent ,flags= Qt.WindowMinMaxButtonsHint|Qt.WindowCloseButtonHint,dic=globalconfig,key='savegamedialoggeo')
                self.setWindowTitle(_TR('已保存游戏'))
                if globalconfig['showintab_sub']:
                        showintab(int(self.winId()),True)
                formLayout = QVBoxLayout()  # 
                self.flow=ScrollFlow()
                
                formLayout.addWidget(self.flow)
                
                buttonlayout=QHBoxLayout()
                self.buttonlayout=buttonlayout
                self.savebutton=[] 
                self.simplebutton("开始游戏",True,lambda: self.startgame(self.currentfocuspath ),True)
                self.simplebutton("游戏设置",True,self.showsettingdialog,False) 
                self.simplebutton("删除游戏",True,self.clicked2,False)
                self.simplebutton("打开目录",True,self.clicked4,True)
 
                self.simplebutton("添加游戏",False,self.clicked3,1)
                self.simplebutton("其他设置",False,lambda:dialog_syssetting(self) ,False)
                formLayout.addLayout(buttonlayout)
                _W=QWidget()
                _W.setLayout(formLayout)
                self.setCentralWidget(_W)
                self.activategamenum=1
                self.itemfocuschanged(False,None)
                self.show()  
                self.idxsave=[]
                for  i,k in  enumerate(savehook_new_list):   
                     if globalconfig['hide_not_exists'] and os.path.exists(k)==False:continue
                     self.newline(k)
                     self.idxsave.append(k)
                     if i==0:
                           self.top1focus() 
                     QApplication.processEvents()
        def showsettingdialog(self ):
                idx =self.idxsave.index(self.currentfocuspath)
                
                dialog_setting_game(self,self.currentfocuspath,None,type=2,gametitleitme=self.flow.l._item_list[idx].widget()) 
        def simplebutton(self,text,save,callback,exists):
                button5=QPushButton( )
                button5.setText(_TR(text))
                if save:
                        self.savebutton.append((button5,exists))
                button5.clicked.connect(callback)
                button5.setFocusPolicy(Qt.NoFocus)   
                self.buttonlayout.addWidget(button5)
                return button5
        def itemfocuschanged(self,b,k):
                
                if b:
                        if self.currentfocuspath==k:return
                        self.activategamenum+=1
                        self.currentfocuspath=k
                else:
                      self.activategamenum-=1
                      self.currentfocuspath=None
                
                _able= (self.activategamenum>0)
                         

                for _btn,exists in self.savebutton:
                        _able1=_able and ((not exists) or (self.currentfocuspath) and (os.path.exists(self.currentfocuspath)))
                        _btn.setEnabled(_able1)  
        def newline(self,k): 
                checkifnewgame(k)
                def _getpixfunction(kk):
                        _pix=QPixmap(savehook_new_data[kk]['imagepath'])
                        if _pix.isNull():
                              _pix=getExeIcon(kk,False,cache=True)
                        return _pix
                gameitem=ItemWidget(functools.partial(_getpixfunction,k),savehook_new_data[k]['title'])
                gameitem.connectexepath(k)
                gameitem.doubleclicked.connect(self.startgame)
                gameitem.focuschanged.connect(self.itemfocuschanged) 
                self.flow.addwidget(gameitem)
                
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
                if os.path.exists(self.model.item(self.table.currentIndex().row(),2).savetext):
                        savehook_new_list.insert(0,savehook_new_list.pop(self.table.currentIndex().row())) 
                        self.close() 
                        startgame(self.model.item(self.table.currentIndex().row(),2).savetext)
                 
        
        def newline(self,row,k): 
                keyitem=QStandardItem()
                keyitem.savetext=k
                k=k.replace('/','\\')
                checkifnewgame(k)
                self.model.insertRow(row,[QStandardItem( ),QStandardItem( ),keyitem,QStandardItem( (savehook_new_data[k]['title'] ) )])  
                self.table.setIndexWidget(self.model.index(row, 0),getsimpleswitch(savehook_new_data[k],'leuse'))
                self.table.setIndexWidget(self.model.index(row, 1),getcolorbutton('','',functools.partial( opendir,k),qicon=getExeIcon(k,cache=True) ))
                
                self.table.setIndexWidget(self.model.index(row, 2),getcolorbutton('','',functools.partial(self.showsettingdialog,k,keyitem ),icon='fa.gear',constcolor="#FF69B4")) 
        def __init__(self, parent ) -> None:
                # if dialog_savedgame._sigleton :
                #         return
                # dialog_savedgame._sigleton=True 
                super().__init__(parent, Qt.WindowCloseButtonHint)
                self.setWindowTitle(_TR('已保存游戏')) 
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
                for row,k in enumerate(savehook_new_list):                                   # 2
                        self.newline(row,k) 
                        QApplication.processEvents()
