 
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QPen,QColor ,QTextCharFormat ,QTextBlockFormat,QTextCursor,QFont,QColor
from PyQt5.QtWidgets import  QTextBrowser ,QLabel
from utils.config import globalconfig
class Textbrowser():
    def __init__(self, parent ) : 
        self.parent=parent
        self.textbrowserback=QTextBrowser(parent)
        self.textbrowser=QTextBrowser(parent)
        self.textbrowser.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(0,0,0,0))
        self.savetaglabels=[]
        self.addtaged=False
        self.charformat=self.textbrowser.currentCharFormat()
    def simplecharformat(self,color):
        self.textbrowser.setCurrentCharFormat(self.charformat)
        self.textbrowserback.setCurrentCharFormat(self.charformat)
        self.textbrowser.setTextColor(QColor(color))
        self.textbrowserback.setTextColor(QColor(color))
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
        #self.textbrowser.setStyleSheet(x)
        self.textbrowserback.setStyleSheet(x)
    def move(self,x,y):
        self.textbrowser.move(x,y)
        self.textbrowserback.move(x,y)
    def document(self):
       
        '''
         QTextDocument *doc =  ui->textEdit_label->document();
QTextCursor textcursor = ui->textEdit_label->textCursor();
for(QTextBlock it = doc->begin(); it !=doc->end();it = it.next())
{
    QTextBlockFormat tbf = it.blockFormat();
    tbf.setLineHeight(lineSpacing,QTextBlockFormat::LineDistanceHeight);
    textcursor.setPosition(it.position());
    textcursor.setBlockFormat(tbf);
    ui->textEdit_label->setTextCursor(textcursor);
}
        '''
        return self.textbrowser.document()
    def setGeometry(self,_1,_2,_3,_4):
        self.textbrowser.setGeometry(_1,_2,_3,_4)
        self.textbrowserback.setGeometry(_1,_2,_3,_4)
    def setAlignment(self,x):
        self.textbrowser.setAlignment(x)
        self.textbrowserback.setAlignment(x)
      
    def append(self,x ): 
        
        if self.addtaged:
            self.addtaged=False
            # self.textbrowserback.append(' ') 
            # self.textbrowser.append(' ')
        
            
            self.textbrowserback.append(x) 
            self.textbrowser.append(x)
            f1=QTextBlockFormat()
            f1.setLineHeight(0,QTextBlockFormat.LineDistanceHeight)
            f1.setAlignment(self.textbrowser.alignment()) 
            cursor=self.textbrowser.textCursor() 
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.setBlockFormat(f1)
            self.textbrowser.setTextCursor(cursor)
            cursor=self.textbrowserback.textCursor() 
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.setBlockFormat(f1)
            self.textbrowserback.setTextCursor(cursor)
        else:
            self.textbrowserback.append(x) 
            self.textbrowser.append(x)
           
        
        
     
    def addtag(self,x): 
        if len(self.savetaglabels)<len(x):
            self.savetaglabels+=[QLabel(self.textbrowser) for i in range(len(x)-len(self.savetaglabels))]
        #print(x)
        pos=2
        self.addtaged=True
        labeli=0 
        cursor=self.textbrowser.textCursor()
        cursor.setPosition(2)
        self.textbrowser.setTextCursor(cursor)
        cursor.movePosition(QTextCursor.StartOfBlock)
        self.textbrowser.setTextCursor(cursor)
        cursor=self.textbrowserback.textCursor()
        cursor.setPosition(2)
        self.textbrowserback.setTextCursor(cursor)
        cursor.movePosition(QTextCursor.StartOfBlock)
        self.textbrowserback.setTextCursor(cursor)
        font=QFont()
        font.setFamily(globalconfig['fonttype']) 
        font.setPointSizeF(12) 
        for word in x:
            f1=QTextBlockFormat()
            
            f1.setLineHeight(20,QTextBlockFormat.LineDistanceHeight)
            f1.setAlignment(self.textbrowser.alignment())
            if word['orig']=='\r':
                continue
            l=len(word['orig'])
            tl1=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
            cursor=self.textbrowser.textCursor()
            cursor.setBlockFormat(f1)
            cursor.setPosition(pos+l )
            self.textbrowser.setTextCursor(cursor)
            cursor=self.textbrowserback.textCursor()
            cursor.setBlockFormat(f1)
            cursor.setPosition(pos+l )
            self.textbrowserback.setTextCursor(cursor)
            pos+=l
             
            tl2=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
            #print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())
            self.savetaglabels[labeli].setText(word['hira'])
            self.savetaglabels[labeli].setFont(font)
            self.savetaglabels[labeli].adjustSize()
            w=self.savetaglabels[labeli].width()
            
            if tl1.y()!=tl2.y():
                x=tl2.x()-w
            else:
                x=tl1.x()/2+tl2.x()/2-w/2
            y=tl2.y()-20
            
            self.savetaglabels[labeli].move(x,y)  
            
             
            
            self.savetaglabels[labeli].setStyleSheet("color: %s;background-color:rgba(0,0,0,0)" %(globalconfig['rawtextcolor']))
            self.savetaglabels[labeli].show()
            labeli+=1
       
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
        for label in self.savetaglabels:
            label.hide()
        self.textbrowser.clear()
        self.textbrowserback.clear()