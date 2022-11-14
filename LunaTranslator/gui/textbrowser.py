 
from PyQt5.QtCore import Qt ,pyqtSignal,QObject
from PyQt5.QtGui import QPen,QColor ,QTextCharFormat ,QTextBlockFormat,QTextCursor,QFont,QColor,QFontMetricsF,QPalette,QTextFormat
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
class Textbrowser( ):  
    def __init__(self, parent ) :  
        self.parent=parent
        #self.shadowlabel=QLabel(parent)
        #self.shadowlabel.savetext=''
        self.align=False
        self.textbrowserback=QTextBrowser(parent)
        self.textbrowser=QTextBrowser(parent)
        self.cleared=False
        self.toplabel2=QLabel(parent)
        self.font=QFont()
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
     
    def append(self,x ,tag ): 
        
        if self.cleared:
            self.b1=0
        else:
            self.b1=self.textbrowser.document().blockCount()
        self.cleared=False
        self.textbrowserback.append(x) 
        self.textbrowser.append(x) 
        self.b2=self.textbrowser.document().blockCount()
        
        if   self.addtaged:
            
            self.addtaged=False
              
            fh=self.getfh(False)
            for i in range(self.blockcount, self.textbrowser.document().blockCount()):
                b=self.textbrowser.document().findBlockByNumber(i) 
                tf=b.blockFormat() 
                tf.setLineHeight(fh,QTextBlockFormat.FixedHeight) 
                cursor=self.textbrowserback.textCursor() 
                cursor.setPosition(b.position()) 
                cursor.setBlockFormat(tf)
                
                self.textbrowserback.setTextCursor(cursor) 
                
                cursor=self.textbrowser.textCursor()
                cursor.setPosition(b.position()) 
                cursor.setBlockFormat(tf)
                self.textbrowser.setTextCursor(cursor) 
        if len(tag)>0:
            self.addtag(tag)
    def showyinyingtext(self,color ):   
         
        linei=self.yinyingposline
        
        doc=self.textbrowser.document()
        block=doc.findBlockByNumber(0)
         
        start=self.b1
        end=self.b2 
        
        cursor=self.textbrowser.textCursor() 
        for blocki in range(start,end):
            block=doc.findBlockByNumber(blocki)
            layout=block.layout()
            blockstart=block.position()
            lc=layout.lineCount()
            for lineii in range(lc):
                line=layout.lineAt(lineii)
                
                s=line.textStart()
                l=line.textLength()
                #print(blockstart,s,block.text()[s:s+l])
                cursor.setPosition(blockstart+s)
                self.textbrowser.setTextCursor(cursor)
                tl1=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft()
                #print(tl1)
                if globalconfig['shadowforce']*(lc+linei)>len(self.yinyinglabels):
                    self.yinyinglabels+=[QLabel(self.toplabel2) for i in range(globalconfig['shadowforce']*(lc+linei)-len(self.yinyinglabels))]
                for i in range(globalconfig['shadowforce']):
                    index=globalconfig['shadowforce']*linei+i 
                    _=self.yinyinglabels[index]
                    _.move(tl1)
                    _.setText(block.text()[s:s+l] )
                    _.setFont(self.textbrowser.font())
                     
                    shadow2 = QGraphicsDropShadowEffect()
                    shadow2.setBlurRadius(globalconfig['fontsize'])
                    shadow2.setOffset(0) 
                    shadow2.setColor(QColor(color))

                    _.setStyleSheet(f"color:{globalconfig['miaobiancolor']}; background-color:rgba(0,0,0,0)")
                    _.setGraphicsEffect(shadow2)
                    _.show()
                linei+=1
        self.yinyingposline=linei
         
    
    def addsearchwordmask(self,x,raw,callback=None ):
        if len(x)==0:
            return
        #print(x)
        pos=0
        labeli=0 
        cursor=self.textbrowser.textCursor()
        cursor.setPosition(0)
        self.textbrowser.setTextCursor(cursor)  
        cursor=self.textbrowserback.textCursor()
        cursor.setPosition(0) 
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
                            self.searchmasklabels[labeli].setGeometry(tl1.x()+2*(i==1),tl1.y() ,sum(guesswidth)//len(guesswidth)-2*(i==l)-2*(i==1),tl4.y()-tl1.y()) 
                else:
                    guesswidth.append(tl2.x()-tl1.x())
                    if globalconfig['usesearchword']:
                        self.searchmasklabels_clicked[labeli].setGeometry(tl1.x(),tl1.y() ,tl2.x()-tl1.x(),tl2.y()-tl1.y())
                    if globalconfig['show_fenci']  :
                        self.searchmasklabels[labeli].setGeometry(tl1.x()+2*(i==1),tl1.y() ,tl2.x()-tl1.x()-2*(i==l)-2*(i==1),tl2.y()-tl1.y())
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
        c=QColor("white") 
        if 'cixing' in word and globalconfig['mecab']['use']:
            try:
                c=QColor(globalconfig['cixingcolor'][word['cixing']])
            except:
                pass
        return (c.red(),c.green(),c.blue(), globalconfig['showcixing_touming']/100)
         
    def getfh(self,half):
        
        font=QFont()
        font.setFamily(globalconfig['fonttype']) 
        
        #font.setPixelSize(int(globalconfig['fontsize'])  )
        if half:
            font.setPointSizeF((globalconfig['fontsize']) /2 )
        else:
            font.setPointSizeF((globalconfig['fontsize'])  )
        fm=QFontMetricsF(font)
        fhall=fm.height()  
        if half:
            return fhall,font
        else:
            return fhall
     
    def addtag(self,x): 
        if globalconfig['zitiyangshi'] in [0,1,2]:  
            if len(self.savetaglabels)<len(x):
                self.savetaglabels+=[QLabel(self.parent) for i in range(len(x)-len(self.savetaglabels))]
        elif globalconfig['zitiyangshi'] ==3: 
            if len(self.savetaglabels)<len(globalconfig['shadowforce']*x):
                self.savetaglabels+=[QLabel(self.parent) for i in range(len(globalconfig['shadowforce']*x)-len(self.savetaglabels))]
        #print(x)
        pos=0
        self.addtaged=True
        labeli=0 
         
        fhall=self.getfh(False)
           
        fhhalf,font=self.getfh(True)
        self.blockcount=self.textbrowser.document().blockCount() 
        for i in range(0,self.blockcount):
            b=self.textbrowser.document().findBlockByNumber(i)
                 
            tf=b.blockFormat()
            #tf.setLineHeight(fh,QTextBlockFormat.LineDistanceHeight)
            tf.setLineHeight(fhall+fhhalf,QTextBlockFormat.FixedHeight)
            cursor=self.textbrowserback.textCursor() 
            cursor.setPosition(b.position()) 
            cursor.setBlockFormat(tf)
            
            self.textbrowserback.setTextCursor(cursor) 
            
            cursor=self.textbrowser.textCursor()
            cursor.setPosition(b.position()) 
            cursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(cursor)
        self._rawqlabel=QLabel() 
        for word in x:
            if word['orig']=='\n':
                continue
            l=len(word['orig'])
            tl1=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
            cursor=self.textbrowser.textCursor()
             
            cursor.setPosition(pos+l )
            self.textbrowser.setTextCursor(cursor)
            cursor=self.textbrowserback.textCursor() 
            cursor.setPosition(pos+l )
            self.textbrowserback.setTextCursor(cursor)
            pos+=l 
            
            tl2=self.textbrowser.cursorRect(self.textbrowser.textCursor()).topLeft() 
            if word['hira']==word['orig']:
                continue
            #print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())
            
            if globalconfig['zitiyangshi'] in [0,1,2]:  
                self.solvejiaminglabel(self.savetaglabels[labeli ],word,font,tl1,tl2,fhhalf,False,color=(globalconfig['jiamingcolor']))
            elif globalconfig['zitiyangshi'] ==3: 
    
                for _i  in range(globalconfig['shadowforce']): 
                        self.solvejiaminglabel(self.savetaglabels[labeli*globalconfig['shadowforce']+_i],word,font,tl1,tl2,fhhalf,True,color=globalconfig['miaobiancolor'])
                         
                          
            labeli+=1
        
        
         
    def solvejiaminglabel(self,label,word,font,tl1,tl2,fh,effect,color):
        if effect==False:
            label.setGraphicsEffect(self._rawqlabel.graphicsEffect() ) 
            label.savelastfontandcolor=None
        label.setText(word['hira'])
        label.setFont(font)
        label.adjustSize()
        w=label.width()
        
        if tl1.y()!=tl2.y():
            x=tl1.x() 
            if x+w<self.textbrowser.width():
                x=tl1.x() 
                y=tl1.y()-fh 
            else:
                x=tl2.x() -w
                y=tl2.y()-fh  
        else:
            x=tl1.x()/2+tl2.x()/2-w/2
            y=tl2.y()-fh   
        y+=30*self.parent.rate
        if effect:
            if 'savelastfontandcolor' not in dir(label) or label.savelastfontandcolor!=(globalconfig['fontsize'],globalconfig['jiamingcolor']):
                shadow2 = QGraphicsDropShadowEffect()
                shadow2.setBlurRadius(globalconfig['fontsize'])
                shadow2.setOffset(0) 
                shadow2.setColor(QColor(globalconfig['jiamingcolor'])) 
                label.setGraphicsEffect(shadow2)
                label.savelastfontandcolor =(globalconfig['fontsize'],globalconfig['jiamingcolor'])
        label.move(x,y)   
        label.setStyleSheet(f"color:{color}; background-color:(0,0,0,0)")
        
        label.show()  
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
            label.hide()
        # self.textbrowser.clear()
        # self.textbrowserback.clear()
        self.yinyingpos=0
        self.yinyingposline=0
        self.cleared=True
        self.textbrowser.setText('')
        self.textbrowserback.setText('')
        
        # self.shadowlabel.setText('')
        # self.shadowlabel.savetext=''