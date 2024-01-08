 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QSizePolicy,QMenu,QFileDialog,QLabel
from PyQt5.QtGui import QFont,QTextCursor,QPixmap,QImage
from PyQt5.QtCore import Qt,pyqtSignal 
import qtawesome 
from myutils.ocrutil import imagesolve
from gui.usefulwidget import closeashidewindow
from myutils.config import globalconfig ,_TR
from myutils.config import globalconfig
class showocrimage(closeashidewindow): 
    setimage=pyqtSignal(list)  
    def __init__(self,parent):
        self.img1=None
        self.originimage=None
        super(showocrimage, self).__init__(parent,globalconfig,'showocrgeo')
        self.setWindowIcon(qtawesome.icon("fa.picture-o"  ))
        self.setWindowTitle(_TR('查看处理效果'))
        self.originlabel=QLabel(self) 
        qw=QWidget()
        self.solvedlabel=QLabel(self) 
        self.lay2=QHBoxLayout()
        button=QPushButton(icon=qtawesome.icon("fa.rotate-right" ,color=globalconfig['buttoncolor']))
        button.clicked.connect(self.retest)  
        self.layout1=QVBoxLayout( )
        #self.lay2.addWidget(button)
        self.lay2.addLayout(self.layout1)
        self.setCentralWidget(qw)
        qw.setLayout(self.lay2)
        self.layout1.addWidget(self.originlabel)
        self.layout1.addWidget(button)
        self.layout1.addWidget(self.solvedlabel)
        self.setimage.connect(self.setimagefunction)
    def retest(self):
        if self.originimage is None:return
        img=imagesolve(self.originimage)
        self.setimagefunction([self.originimage,img])
    def showimg(self): 
            
            self.originlabel.setPixmap(self.img1.scaled(self.originlabel.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
            self.solvedlabel.setPixmap(self.img2.scaled(self.solvedlabel.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
    def resizeEvent(self, a0) -> None:
        if self.img1 is not None:
             self.showimg()
        return super().resizeEvent(a0)
    def setimagefunction(self,image):
        originimage,solved=image
        self.originimage=originimage
        self.img1=QPixmap.fromImage(originimage)
        self.img2=QPixmap.fromImage(solved)
        self.showimg()