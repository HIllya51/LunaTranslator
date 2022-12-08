from PyQt5.QtWidgets import QWidget,QDesktopWidget,QMainWindow,QLabel,QPushButton,QStatusBar,QDialog,QSizeGrip
from PyQt5.QtGui import  QBitmap,QPainter,QPen,QBrush,QFont
from PyQt5.QtCore import Qt,QPoint,QRect,QEvent,pyqtSignal
import re,threading,time
 
from utils.config import globalconfig
from gui.resizeablemainwindow import Mainw

class rangeadjust(Mainw) :
 
    def __init__(self, object):

        super(rangeadjust, self).__init__(object.translation_ui) 
        self.object = object   
        self.label = QLabel(self) 
        self.label.setStyleSheet(" border:%spx solid %s; background-color: rgba(0,0,0, 0.01)"   %(globalconfig['ocrrangewidth'],globalconfig['ocrrangecolor'] ))
        self.drag_label = QLabel(self)
        self.drag_label.setGeometry(0, 0, 4000, 2000)
        self._isTracking=False 
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground) 

        for s in self.cornerGrips: 
            s.raise_()
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
    def moveEvent(self,e):
                rect = self.geometry() 
                if self.object.rect:    
                    self.object.rect=[(rect.left(),rect.top()),(rect.right(),rect.bottom())]  
    def enterEvent(self, QEvent) :  
        self.drag_label.setStyleSheet("background-color:rgba(0,0,0, 0.1)") 
    def leaveEvent(self, QEvent): 
        self.drag_label.setStyleSheet("background-color:none")  
    def resizeEvent(self, a0 ) :
          
         self.label.setGeometry(0, 0, self.width(), self.height())  
         rect = self.geometry() 
         if self.object.rect:    
             self.object.rect=[(rect.left(),rect.top()),(rect.right(),rect.bottom())]  
         super(rangeadjust, self).resizeEvent(a0)  
class rangeselct(QMainWindow) :

    def __init__(self, object ) :

        super(rangeselct, self).__init__(object.translation_ui)
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

        self.object.rect=None
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
        
        x1,x2=min(x1,x2),max(x1,x2)
        y1,y2=min(y1,y2),max(y1,y2)
        self.object.rect=[(x1,y1),(x2,y2)]
        self.object.range_ui.setGeometry(x1,y1,x2-x1,y2-y1) 
        self.object.range_ui.show() 
    def mouseReleaseEvent(self, event): 
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.getRange() 
            self.close() 
            self.callback()
import win32gui,win32con,win32api
class moveresizegame(QDialog) :

    def __init__(self, object,hwnd ):

        super(moveresizegame, self).__init__(object)
        self.setWindowFlags(Qt.Dialog|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        self.object = object  
        self.setWindowTitle("调整窗口  "+ win32gui.GetWindowText(hwnd))
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint  )
        # self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setWindowOpacity(0.5)

        self.setMouseTracking(True)
         
        self._isTracking=False
         
 
        self.hwnd=hwnd
        self.maxed=False
        if self.hwnd==0:
            self.close()
        try:
            rect=win32gui.GetWindowRect(self.hwnd)  
            self.setGeometry(rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1])
            self.show()
        except:
            self.close()
        #win32gui.SetWindowPos(self.winId(),win32con.HWND_TOPMOST,rect[0],rect[1],1000,1000,  win32con.SWP_NOACTIVATE)
        
    def moveEvent(self, a0 ) -> None:
        rect = self.geometry() 
        if self.isMaximized()==False:
            #win32gui.ShowWindow(self.hwnd,win32con.SW_SHOW)
            try:
                win32gui.MoveWindow(self.hwnd,  rect.left(),rect.top(),rect.right()-rect.left(), rect.bottom()-rect.top(),  False)
            except:
                pass
        return super().moveEvent(a0)
     
    def closeEvent(self, a0 ) -> None:
        self.object.moveresizegame=None
        return super().closeEvent(a0)
    def mouseMoveEvent(self, e ) :  
        if self._isTracking: 
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos) 
            rect = self.geometry() 
            if self.isMaximized()==False:
                #win32gui.ShowWindow(self.hwnd,win32con.SW_SHOW)
                try:
                    win32gui.MoveWindow(self.hwnd,  rect.left(),rect.top(),rect.right()-rect.left(), rect.bottom()-rect.top(),  False)
                except:
                    pass
    def mousePressEvent(self, e ) : 
            if e.button() == Qt.LeftButton :
                self._isTracking = True
                self._startPos = QPoint(e.x(), e.y()) 
    def mouseReleaseEvent(self, e ) : 
            if e.button() == Qt.LeftButton:
                self._isTracking = False
                self._startPos = None
                self._endPos = None 
    def changeEvent(self, a0 ) -> None:
        if a0.type() == QEvent.WindowStateChange:
            try:
                if self.isMaximized():
                    win32gui.ShowWindow(self.hwnd,win32con.SW_MAXIMIZE) 
                #win32gui.MoveWindow(self.hwnd,  0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1),  False)
                else:  
                    win32gui.ShowWindow(self.hwnd,win32con.SW_SHOWNORMAL)
            except:
                pass
    #def moveEvent(self, a0):
    #     self.resizeEvent(a0)
    def resizeEvent(self, a0 ) :
        if self.isMaximized()==False: 
            rect = self.geometry()
            #win32gui.ShowWindow(self.hwnd,win32con.SW_SHOW)
            try:
                win32gui.MoveWindow(self.hwnd,  rect.left(),rect.top(),rect.right()-rect.left(), rect.bottom()-rect.top(),  False)
            except:
                pass
            