 
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QPen,QColor ,QTextCharFormat ,QTextBlockFormat,QTextCursor,QFont,QColor,QFontMetricsF,QPalette
from PyQt5.QtWidgets import  QTextBrowser ,QLabel,QPushButton,QGraphicsDropShadowEffect
import random
import functools 
from utils.config import globalconfig
from utils.wrapper import timer
from traceback import print_exc
class Qlabel_c(QLabel):
    
    def mousePressEvent(self, ev   )  :
        self.pr=True
        return super().mousePressEvent(ev)
    def mouseMoveEvent(self, ev) :
        self.pr=False
        return super().mouseMoveEvent(ev)
    def mouseReleaseEvent(self, ev )  :
        try:
            if self.pr:
                self.callback()
            self.pr=False
        except:
            print_exc()
        return super().mouseReleaseEvent(ev)
class Textbrowser():
    def __init__(self, parent ) : 
        self.parent=parent
        #self.shadowlabel=QLabel(parent)
        #self.shadowlabel.savetext=''
        self.align=False
        self.textbrowserback=QTextBrowser(parent)
        self.textbrowser=QTextBrowser(parent)
        
        self.toplabel2=QLabel(parent)
        
        self.toplabel2.setGeometry( 0,30*self.parent.rate,9999,9999)
        self.toplabel2.setMouseTracking(True)
        self.toplabel=QLabel(parent)
        
        self.toplabel.setGeometry( 0,30*self.parent.rate,9999,9999)
        self.toplabel.setMouseTracking(True)
        self.textbrowser.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(0,0,0,0))
        self.textbrowserback.setStyleSheet("border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
                                           %(0,0,0,0))
        self.savetaglabels=[]
        self.searchmasklabels_clicked=[]
        self.searchmasklabels=[]
        self.backcolorlabels=[]
        self.yinyinglabels=[]
        self.addtaged=False
        self.yinyingpos=0
        self.yinyingposline=0
        self.lastcolor=None

        
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
        #self.shadowlabel.setFont(x) 
    def setStyleSheet(self,x): 
        #self.textbrowser.setStyleSheet(x)
        
        #self.textbrowserback.setStyleSheet(x)
        self.parent.atback.setStyleSheet(x)
    def move(self,x,y):
        self.textbrowser.move(x,y)
        self.textbrowserback.move(x,y)
        #self.shadowlabel.move(x,y)
       
    def document(self): 
        return self.textbrowser.document()
    def setGeometry(self,_1,_2,_3,_4):
        self.textbrowser.setGeometry(_1,_2,_3,_4)
        self.textbrowserback.setGeometry(_1,_2,_3,_4) 
        #self.shadowlabel.setGeometry(_1,_2,_3,_4)  
        #self.shadowlabel.resize(_3,_4)
    def setAlignment(self,x):
        self.textbrowser.setAlignment(x)
        self.textbrowserback.setAlignment(x)
        if Qt.AlignCenter==x:
            self.align=True
        else:
            self.align=False
        #self.shadowlabel.setAlignment(Qt.AlignTop )
    @timer
    def append(self,x ): 
        
        if self.addtaged:
            
            # self.textbrowserback.append(' ') 
            # self.textbrowser.append(' ')
            # cursor=self.textbrowser.textCursor()
            # cursor.movePosition(QTextCursor.End)
            # self.textbrowser.setTextCursor(cursor)
            # cursor=self.textbrowserback.textCursor()
            # cursor.movePosition(QTextCursor.End)
            # self.textbrowserback.setTextCursor(cursor)
         
            self.textbrowser.append('')
            self.textbrowserback.append('')
             
            self.addtaged=False
            f1=QTextBlockFormat()
            f1.setLineHeight(0,QTextBlockFormat.LineDistanceHeight)
            f1.setAlignment(self.textbrowser.alignment()) 
            cursor=self.textbrowser.textCursor() 
            #cursor.movePosition(QTextCursor.StartOfBlock)
            #cursor.setBlockFormat(f1)
            cursor.mergeBlockFormat(f1)
            self.textbrowser.setTextCursor(cursor)
            cursor=self.textbrowserback.textCursor() 
            #cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.mergeBlockFormat(f1)
            self.textbrowserback.setTextCursor(cursor)
            self.textbrowserback.insertPlainText(x) 
            self.textbrowser.insertPlainText(x)
             
        else:
            self.textbrowserback.append(x) 
            self.textbrowser.append(x) 
        # if self.shadowlabel.savetext!='':
        #     self.shadowlabel.savetext=(self.shadowlabel.savetext+'<br>'+ x)
        # else:
        #     self.shadowlabel.savetext=x
        # if self.align:
        #     self.shadowlabel.setText( '<html><p style="color:rgba(0,0,0)" align=\'center\'> %s</p></html>' %self.shadowlabel.savetext)
        # else:
        #     self.shadowlabel.setText( '<html><p > %s</p></html>' %self.shadowlabel.savetext)
        # if globalconfig['showShadow']:
        #     shadow = QGraphicsDropShadowEffect()
        #     shadow.setBlurRadius(10)
            
        #     shadow.setColor(QColor(globalconfig['shadowcolor']))
        #     shadow.setOffset(0)
        #     # adding shadow to the label
            
        #     self.shadowlabel.setGraphicsEffect(shadow)
    def showyinyingtext(self,color,text): 
         
        #print(x)
        start=self.yinyingpos
        pos=start
        labeli=0 
        cursor=self.textbrowser.textCursor()
        cursor.setPosition(start )
        self.textbrowser.setTextCursor(cursor)
        cursor.movePosition(QTextCursor.StartOfBlock)
        self.textbrowser.setTextCursor(cursor)
        linei=self.yinyingposline
        savestart=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft()
        #print(start,savestart)
        savep=0
        texti=0
        while texti <len(text):
            word=text[texti]
            tl1=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft()
            
            
            cursor=self.textbrowser.textCursor() 
            cursor.setPosition(pos+labeli )
            self.textbrowser.setTextCursor(cursor)
            
            
            tl3=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
            
            if tl1.y()!=tl3.y() or texti==len(text)-1:  
                if texti==len(text)-1:
                    texti+=1
                
                if linei>=len(self.yinyinglabels):
                    self.yinyinglabels.append([])
                    for _ in range(globalconfig['shadowforce']):
                        ql=QLabel(self.toplabel2) 
                        ql.setMouseTracking(True)
                    
                        self.yinyinglabels[-1].append(ql)
                elif len(self.yinyinglabels[linei])<globalconfig['shadowforce']:
                    for _ in range(len(self.yinyinglabels[linei]),globalconfig['shadowforce']):
                        ql=QLabel(self.toplabel2) 
                        ql.setMouseTracking(True)
                    
                        self.yinyinglabels[linei].append(ql)
                for _i,_ in enumerate(self.yinyinglabels[linei]):
                    if _i>=globalconfig['shadowforce']:
                        break
                    _.move(savestart)
                    _.setText(text[savep:texti] )
                    _.setFont(self.textbrowser.font())
                    
                    shadow2 = QGraphicsDropShadowEffect()
                    shadow2.setBlurRadius(globalconfig['fontsize'])
                    shadow2.setOffset(0) 
                    shadow2.setColor(QColor(color))

                    _.setStyleSheet(f"color:{globalconfig['miaobiancolor']}; background-color:rgba(0,0,0,0)")
                    _.setGraphicsEffect(shadow2)
                    _.show()
                linei+=1

                savestart=tl3 
                if word=='\n':
                    texti+=1
                 
                savep=texti
            #self.searchmasklabels[labeli].clicked.connect(lambda x:print(111))
            #self.searchmasklabels[labeli].mousePressEvent=(lambda x:print(111))
            
            labeli+=1 
             
            texti+=1
        self.yinyingpos=pos+labeli+1
        self.yinyingposline=linei
    @timer
    def addsearchwordmask(self,x,raw,callback=None,start=2):
        if len(x)==0:
            return
        #print(x)
        pos=start
         
        labeli=0 
        cursor=self.textbrowser.textCursor()
        cursor.setPosition(start)
        self.textbrowser.setTextCursor(cursor)
        cursor.movePosition(QTextCursor.StartOfBlock)
        self.textbrowser.setTextCursor(cursor)
        cursor=self.textbrowserback.textCursor()
        cursor.setPosition(start)
        self.textbrowserback.setTextCursor(cursor)
        cursor.movePosition(QTextCursor.StartOfBlock)
        self.textbrowserback.setTextCursor(cursor)
        
        guesswidth=[]
        idx=0
        for word in x:
            idx+=1
            if word['orig']=='\n':
                continue
            l=len(word['orig'])
            tl1=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft()
            tl4=self.textbrowser.cursorRect(self.textbrowser.textCursor()).bottomRight()
            color=self.randomcolor(word)
             
            for i in range(1,l+1):
                    
                cursor=self.textbrowser.textCursor() 
                cursor.setPosition(pos+i )
                self.textbrowser.setTextCursor(cursor)
                cursor=self.textbrowserback.textCursor() 
                cursor.setPosition(pos+i )
                self.textbrowserback.setTextCursor(cursor)
                tl2=self.textbrowser.cursorRect(self.textbrowser.textCursor()).bottomRight() 
                tl3=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
 
                if labeli>=len(self.searchmasklabels):
                     
                    ql=QLabel(self.parent.atback) 
                    ql.setMouseTracking(True)
                    self.searchmasklabels.append(ql)

                    ql=Qlabel_c(self.toplabel) 
                    ql.setMouseTracking(True)
                    ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                    self.searchmasklabels_clicked.append(ql)
                if tl1.y()!=tl3.y():
                    if len(guesswidth)>0:
                        if globalconfig['usesearchword']:
                            self.searchmasklabels_clicked[labeli].setGeometry(tl1.x(),tl1.y() ,sum(guesswidth)//len(guesswidth),tl4.y()-tl1.y()) 
                        if globalconfig['show_fenci']  :
                            self.searchmasklabels[labeli].setGeometry(tl1.x(),tl1.y() ,sum(guesswidth)//len(guesswidth),tl4.y()-tl1.y()) 
                else:
                    guesswidth.append(tl2.x()-tl1.x())
                    if globalconfig['usesearchword']:
                        self.searchmasklabels_clicked[labeli].setGeometry(tl1.x(),tl1.y() ,tl2.x()-tl1.x(),tl2.y()-tl1.y())
                    if globalconfig['show_fenci']  :
                        self.searchmasklabels[labeli].setGeometry(tl1.x(),tl1.y() ,tl2.x()-tl1.x(),tl2.y()-tl1.y())
                if globalconfig['show_fenci']  :
                    self.searchmasklabels[labeli].setStyleSheet(f"background-color: rgba{color};"  )
                tl1=tl3 
                tl4=tl2
                if word['orig'] not in ['\n','\r'] :
                    if globalconfig['usesearchword']:
                        self.searchmasklabels_clicked[labeli].show()
                    if globalconfig['show_fenci']  :
                        self.searchmasklabels[labeli].show()
                if callback:
                    self.searchmasklabels_clicked[labeli].callback=functools.partial(callback,(word['orig'],raw,idx-1))
                #self.searchmasklabels[labeli].clicked.connect(lambda x:print(111))
                #self.searchmasklabels[labeli].mousePressEvent=(lambda x:print(111))
                labeli+=1
            pos+=l
        
                
    def randomcolor(self,word):
        if 'cixing' in word and globalconfig['mecab']['use']:
            try:
                c=QColor(globalconfig['cixingcolor'][word['cixing']])
            except:
                c=QColor("yellowgreen")
                print_exc()
            return (c.red(),c.green(),c.blue(), globalconfig['showcixing_touming']/100)
        if self.lastcolor is None:
            self.lastcolor=(random.randint(0,255),random.randint(0,255),random.randint(0,255),1)
         
        self.lastcolor= ((self.lastcolor[0]+ random.randint(64,192))%255,(self.lastcolor[1]+ random.randint(64,192))%255,(self.lastcolor[2]+ random.randint(64,192))%255,globalconfig['showcixing_touming']/100)
        return self.lastcolor
    @timer
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
        f1=QTextBlockFormat()
        
        f1.setLineHeight(20,QTextBlockFormat.LineDistanceHeight)
        f1.setAlignment(self.textbrowser.alignment())
        need=True
        for word in x:
            if word['orig']=='\n':
                continue
            l=len(word['orig'])
            tl1=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
            cursor=self.textbrowser.textCursor()
            if need:
                cursor.setBlockFormat(f1)
            cursor.setPosition(pos+l )
            self.textbrowser.setTextCursor(cursor)
            cursor=self.textbrowserback.textCursor()
            if need:
                cursor.setBlockFormat(f1)
            cursor.setPosition(pos+l )
            self.textbrowserback.setTextCursor(cursor)
            pos+=l
            need=False
            
            tl2=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
            #print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())
            self.savetaglabels[labeli].setText(word['hira'])
            self.savetaglabels[labeli].setFont(font)
            self.savetaglabels[labeli].adjustSize()
            w=self.savetaglabels[labeli].width()
            
            if tl1.y()!=tl2.y():
                x=tl2.x()-w
                need=True
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
        for label in self.searchmasklabels:
            label.hide()
        for label in self.searchmasklabels_clicked:
            label.hide()
        for label in self.savetaglabels:
            label.hide()
        for label in self.yinyinglabels:
            for _ in label:
                _.hide()
        # self.textbrowser.clear()
        # self.textbrowserback.clear()
        self.yinyingpos=0
        self.yinyingposline=0
        self.textbrowser.setText('')
        self.textbrowserback.setText('')
        # self.shadowlabel.setText('')
        # self.shadowlabel.savetext=''