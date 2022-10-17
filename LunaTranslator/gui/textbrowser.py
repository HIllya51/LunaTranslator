 
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QPen,QColor ,QTextCharFormat 
from PyQt5.QtWidgets import  QTextBrowser 
 
class Textbrowser():
    def __init__(self, parent ) : 
        
        self.textbrowserback=QTextBrowser(parent)
        self.textbrowser=QTextBrowser(parent)
    def setText(self,text):
        self.textbrowser.setText(text)
        self.textbrowserback.setText(text)
    def setVerticalScrollBarPolicy(self,x):
        self.textbrowser.setVerticalScrollBarPolicy(x)
        self.textbrowserback.setVerticalScrollBarPolicy(x)
    def setHorizontalScrollBarPolicy(self,x): 
        self.textbrowser.setHorizontalScrollBarPolicy(x)
        self.textbrowserback.setHorizontalScrollBarPolicy(x)
    def setFont(self,x): 
        self.textbrowser.setFont(x)
        self.textbrowserback.setFont(x)
    def setStyleSheet(self,x): 
        self.textbrowser.setStyleSheet(x)
        self.textbrowserback.setStyleSheet(x)
    def move(self,x,y):
        self.textbrowser.move(x,y)
        self.textbrowserback.move(x,y)
    def document(self):
        return self.textbrowser.document()
    def setGeometry(self,_1,_2,_3,_4):
        self.textbrowser.setGeometry(_1,_2,_3,_4)
        self.textbrowserback.setGeometry(_1,_2,_3,_4)
    def setAlignment(self,x):
        self.textbrowser.setAlignment(x)
        self.textbrowserback.setAlignment(x)
    def append(self,x):
        self.textbrowserback.append(x)
        
        self.textbrowser.append(x)
    def mergeCurrentCharFormat(self,colormiao,width):
        format2=QTextCharFormat()
        format2.setTextOutline(QPen(QColor(colormiao),width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
         
        self.textbrowser.setCurrentCharFormat(format2)
        self.textbrowserback.setCurrentCharFormat(format2)
    def mergeCurrentCharFormat_out(self,colorinner,colormiao,width):
        format1 = QTextCharFormat() 
        format1.setForeground(QColor(colorinner))
        format2=QTextCharFormat()
        format2.setTextOutline(QPen(QColor(colormiao),width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        self.textbrowser.setCurrentCharFormat(format1)
        self.textbrowserback.setCurrentCharFormat(format2)
    def clear(self):
        self.textbrowser.clear()
        self.textbrowserback.clear()