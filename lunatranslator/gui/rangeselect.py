from PyQt5.QtWidgets import QWidget,QDesktopWidget,QMainWindow,QLabel,QPushButton,QStatusBar
from PyQt5.QtGui import  QBitmap,QPainter,QPen,QBrush,QFont
from PyQt5.QtCore import Qt,QPoint,QRect
import re
 
from utils.config import globalconfig
 

class rangeadjust(QMainWindow) :

    def __init__(self, object):

        super(rangeadjust, self).__init__()

        self.object = object  
          
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground) 

        self.label = QLabel(self) 
        self.label.setStyleSheet("border-width:1;\
                                  border:2px solid #000000;\
                                  background-color:rgba(62, 62, 62, 0.01)")
 
        self.drag_label = QLabel(self)
        self.drag_label.setGeometry(0, 0, 4000, 2000)
        self._isTracking=False
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar) 
    def mouseMoveEvent(self, e ) :  
        if self._isTracking: 
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos) 
    def mousePressEvent(self, e ) : 
            if e.button() == Qt.LeftButton :
                self._isTracking = True
                self._startPos = QPoint(e.x(), e.y()) 
    def mouseReleaseEvent(self, e ) : 
            if e.button() == Qt.LeftButton:
                self._isTracking = False
                self._startPos = None
                self._endPos = None 
    def enterEvent(self, QEvent) :  
        self.drag_label.setStyleSheet("background-color:rgba(62, 62, 62, 0.1)") 
    def leaveEvent(self, QEvent): 
        self.drag_label.setStyleSheet("background-color:none") 
    def moveEvent(self, a0):
        self.resizeEvent(a0)
    def resizeEvent(self, a0 ) :
        self.label.setGeometry(0, 0, self.width(), self.height())  
        rect = self.geometry() 
        self.object.rect=[(rect.left(),rect.top()),(rect.right(),rect.bottom())]  
class rangeselct(QWidget) :

    def __init__(self, object, parent=None) :

        super(rangeselct, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)#|Qt.WindowStaysOnTopHint  )
        self.setStyleSheet('''background-color:black; ''')
        self.setWindowOpacity(0.6)
        desktop_rect = QDesktopWidget().screenGeometry()
        self.setGeometry(desktop_rect)
        self.setCursor(Qt.CrossCursor)
        self.black_mask = QBitmap(desktop_rect.size())
        self.black_mask.fill(Qt.black)
        self.mask = self.black_mask.copy()
        self.is_drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.object = object 

    def paintEvent(self, event):  
            if self.is_drawing:
                self.mask = self.black_mask.copy()
                pp = QPainter(self.mask)
                pen = QPen()
                pen.setStyle(Qt.NoPen)
                pp.setPen(pen)
                brush = QBrush(Qt.white)
                pp.setBrush(brush)
                pp.drawRect(QRect(self.start_point, self.end_point))
                self.setMask(QBitmap(self.mask)) 
    def mousePressEvent(self, event) : 
            if event.button() == Qt.LeftButton:
                self.start_point = event.pos()
                self.end_point = self.start_point
                self.is_drawing = True 
    def mouseMoveEvent(self, event) : 
            if self.is_drawing:
                self.end_point = event.pos()
                self.update() 
    def getRange(self) :
        x1,y1,x2,y2=(self.start_point.x(),self.start_point.y() ,self.end_point.x(),self.end_point.y())
        self.object.rect=[(x1,y1),(x2,y2)]
        self.object.range_ui.setGeometry(x1,y1,x2-x1,y2-y1) 
        self.object.range_ui.show() 
    def mouseReleaseEvent(self, event): 
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.getRange() 
            self.close() 
             
 