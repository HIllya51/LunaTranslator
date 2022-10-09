 
import functools  
from threading import Thread
import threading 
import time
t1=time.time()
import os
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint,pyqtSignal  
import qtawesome 
from PyQt5.QtCore import pyqtSignal,Qt,QPoint,QRect,QSize  ,QPointF,QRectF
from PyQt5.QtGui import QPen,QColor,QFont,QTextCharFormat ,QIcon,QPixmap ,QPainter,QPainterPath,QPalette
from PyQt5.QtWidgets import  QLabel,QTextBrowser,QPushButton ,QSystemTrayIcon ,QAction,QMenu,QGraphicsEffect,QGraphicsColorizeEffect,QGraphicsBlurEffect,QGraphicsScene,QGraphicsPixmapItem
import pyperclip 
from PyQt5.QtCore import QProcess ,QByteArray ,QTimer

class QGlow(QGraphicsEffect):
    def __init__(self)  :
        self._extent = 5;
        self._color = QColor(255, 255, 255);
        self._strength = 3;
        self._blurRadius = 5.0;
        super().__init__()
    def setColor(self,c):
        self._color=c
    def setStrength(self,v):
        self._strength=v
    def setBlurRadius(self,v):
        self._blurRadius =v
        self._extent = int(v+0.5)
        self.updateBoundingRect()
    def color(self):
        return self._color
    def strength(self) :
        return self._strength;
    def blurRadius(self) :
        return self._blurRadius;
    def boundingRectFor(self,rect) :
        return QRectF(
            rect.left() - self._extent,
            rect.top() - self._extent,
            rect.width() + 2 * self._extent, 
            rect.height() + 2 * self._extent) 
    def draw(self,painter) : 
        source,offset=self.sourcePixmap(Qt.LogicalCoordinates)
        colorize=QGraphicsColorizeEffect()
        colorize.setColor(self._color)
        colorize.setStrength(1)
        glow=self.applyEffectToPixmap(source,colorize,0)
        blur=QGraphicsBlurEffect()
        blur.setBlurRadius(self._blurRadius)
        glow=self.applyEffectToPixmap(glow,blur,self._extent)
        for i in range(self._strength):
            painter.drawPixmap(offset-QPoint(self._extent,self._extent),glow)
            self.drawSource(painter)
    def applyEffectToPixmap(self,src,effect,extent): 
        if src.isNull():return QPixmap()
        if not effect:return src
        scene=QGraphicsScene()
        item=QGraphicsPixmapItem()
        item.setPixmap(src)
        item.setGraphicsEffect(effect)
        scene.addItem(item)
        size=src.size()+QSize(extent*2,extent*2)
        res=QPixmap(size.width(),size.height())
        res.fill(Qt.transparent)
        ptr=QPainter(res)
        scene.render(ptr,QRectF(),QRectF(-extent,-extent,size.width(),size.height()))
        return res


