 
from PyQt5.QtCore import Qt ,pyqtSignal,QObject
from PyQt5.QtGui import QPen,QColor ,QTextCharFormat ,QTextBlockFormat,QTextCursor,QFont,QColor,QFontMetricsF,QPalette,QTextFormat
from PyQt5.QtWidgets import  QTextBrowser ,QLabel,QPushButton,QGraphicsDropShadowEffect
import random
import functools ,time
from myutils.config import globalconfig
from myutils.wrapper import timer
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
    def enterEvent(self, a0 ) -> None: 
        if self.company:
            self.company.setStyleSheet("background-color: rgba(0,0,0,0.5);")
        self.setStyleSheet("background-color: rgba(0,0,0,0.5);")
        return super().enterEvent(a0)
    def leaveEvent(self, a0 ) -> None:
        if self.company:
            self.company.setStyleSheet("background-color: rgba(0,0,0,0.01);")
        self.setStyleSheet("background-color: rgba(0,0,0,0.01);")
        return super().leaveEvent(a0)
class QGraphicsDropShadowEffect_multi(QGraphicsDropShadowEffect):
    def setx(self,x):
        self.x=x 
    def draw(self, painter ) -> None:
        for i in range(self.x):
            super().draw(painter)
    
class Textbrowser( ):  
    def movep(self,x,y):
        self.savey=y
        self.atback.setGeometry(0,y,9999,9999)
        if globalconfig['isshowhira'] and globalconfig['isshowrawtext']:
            if self.jiaming_y_delta>0:
                y=y+self.jiaming_y_delta
        self.textbrowser.move(x,y)
        self.textbrowserback.move(x,y)
        
        self.atback2.setGeometry(0,y,9999,9999)
        self.toplabel2.setGeometry( 0,y,9999,9999)
        self.toplabel.setGeometry( 0,y,9999,9999)
    def __init__(self, parent ) :  
        self.parent=parent
        #self.shadowlabel=QLabel(parent)
        #self.shadowlabel.savetext=''
        self.align=False
        
        self.atback=QLabel(parent)
        
        self.atback.setMouseTracking(True)

        
        self.atback2=QLabel(parent)
        
        self.atback2.setMouseTracking(True)
        self._rawqlabel=QLabel() 
        self.textbrowserback=QTextBrowser(parent)
        self.textbrowser=QTextBrowser(parent)
        self.cleared=False
        self.toplabel2=QLabel(parent)
        self.font=QFont()
        
        self.toplabel2.setMouseTracking(True)
        self.toplabel=QLabel(parent) 
        
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

        self.textcursor=self.textbrowser.textCursor()
        self.textcursorback=self.textbrowserback.textCursor()
        self.textbrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textbrowserback.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textbrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textbrowserback.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.masklabel = QLabel(self.textbrowser)   
        self.masklabel.setGeometry( 0,0,9999,9999)
        self.masklabel.setMouseTracking(True)
        
        self.masklabelback = QLabel(self.textbrowserback)   
        self.masklabelback.setGeometry( 0, 0,9999,9999)
        self.masklabelback.setMouseTracking(True)
        self.masklabelback.setStyleSheet("background-color: rgba(0,0,0,0)")
         
        self.savetaglabels=[]
        self.searchmasklabels_clicked=[]
        self.searchmasklabels=[]
        self.backcolorlabels=[]
        self.yinyinglabels=[]
        self.addtaged=False
        self.yinyingpos=0
        self.yinyingposline=0
        self.lastcolor=None
        self.jiaming_y_delta=0
        self.setselectable() 
        self.blockcount=0
        self.needdouble=False
    def setselectable(self):
        self.masklabel.setHidden(globalconfig['selectable'])
        self.toplabel2.setHidden(globalconfig['selectable'] and globalconfig['zitiyangshi']!=3) 
        self.toplabel.setHidden(globalconfig['selectable'] and globalconfig['zitiyangshi']!=3)
    def simplecharformat(self,color):
        
        if self.needdouble:
            self.textbrowserback.hide()
            self.needdouble=False

        self.textbrowser.setTextColor(QColor(color)) 
    def setText(self,text):
        self.textbrowser.setText(text)
        self.textbrowserback.setText(text)
         
    def setFont(self,x): 
        f=QTextCharFormat()
        f.setFont(x)
        c=self.textbrowser.textCursor()
        c.setCharFormat(f)
        self.textbrowser.setTextCursor(c)

        f=QTextCharFormat()
        f.setFont(x)
        c=self.textbrowserback.textCursor()
        c.setCharFormat(f)
        self.textbrowserback.setTextCursor(c)
        #self.shadowlabel.setFont(x) 
    def setStyleSheet(self,x): 
        #self.textbrowser.setStyleSheet(x) 
        #self.textbrowserback.setStyleSheet(x)
        self.atback.setStyleSheet(x)
     
    def document(self): 
        return self.textbrowser.document()
    def resize(self,_1,_2):
        self.textbrowser.resize(_1,_2)
        self.textbrowserback.resize(_1,_2)
    def clear(self):
        self.clear()
        self.blockcount=0
    def setnextfont(self,origin): 
        if origin:
            self.font.setFamily(globalconfig['fonttype'])
        else:
            self.font.setFamily(globalconfig['fonttype2'])
        self.font.setPointSizeF(globalconfig['fontsize']) 
        self.font.setBold(globalconfig['showbold'])
        self.setFont(self.font) 
    def setGeometry(self,_1,_2,_3,_4):
        self.textbrowser.setGeometry(_1,_2,_3,_4)
        self.textbrowserback.setGeometry(_1,_2,_3,_4) 

        self.savey=_2
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
     
    def append(self,x ,tag,origin ): 
        
        if self.cleared:
            self.blockcount=0
            self.b1=0
        else:
            self.b1=self.textbrowser.document().blockCount()
        self.cleared=False
        if self.needdouble:
            self.textbrowserback.append(x) 
        self.textbrowser.append(x) 
        self.b2=self.textbrowser.document().blockCount()
        
        if  True:# self.addtaged:
            if self.addtaged:
                self.addtaged=False
               
            fh=globalconfig['extra_space'] 
            for i in range(self.blockcount, self.textbrowser.document().blockCount()): 
                b=self.textbrowser.document().findBlockByNumber(i) 
                tf=b.blockFormat() 
                tf.setLineHeight(fh,QTextBlockFormat.LineDistanceHeight) 
                if self.needdouble: 
                    self.textcursorback.setPosition(b.position()) 
                    self.textcursorback.setBlockFormat(tf) 
                    self.textbrowserback.setTextCursor(self.textcursorback) 
                 
                self.textcursor.setPosition(b.position()) 
                self.textcursor.setBlockFormat(tf)
                self.textbrowser.setTextCursor(self.textcursor) 
            self.blockcount=self.textbrowser.document().blockCount()
        if len(tag)>0:
            self.addtag(tag)

        self.movep(0,self.savey)
    def showyinyingtext(self,color ):   
         
        linei=self.yinyingposline
        
        doc=self.textbrowser.document()
        block=doc.findBlockByNumber(0)
         
        start=self.b1
        end=self.b2 
         
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
                self.textcursor.setPosition(blockstart+s)
                self.textbrowser.setTextCursor(self.textcursor)
                tl1=self.textbrowser.cursorRect(self.textcursor).topLeft()
                #print(tl1)
                if (lc+linei)>len(self.yinyinglabels):
                    self.yinyinglabels+=[QLabel(self.toplabel2) for i in range((lc+linei)-len(self.yinyinglabels))]
                
                index=linei
                _=self.yinyinglabels[index]
                _.move(tl1)
                _.setText(block.text()[s:s+l] )
                _.setFont(self.textbrowser.currentCharFormat().font())
                    
                _.setStyleSheet("color:{}; background-color:rgba(0,0,0,0)".format(globalconfig['miaobiancolor']))
                _.setGraphicsEffect(self.geteffect(globalconfig['fontsize'],color,globalconfig['shadowforce']))
                _.show()
                linei+=1
        self.yinyingposline=linei
    def geteffect(self,fontsize,color,x):
        shadow2 = QGraphicsDropShadowEffect_multi()
        shadow2.setx(x)
        shadow2.setBlurRadius(fontsize)
        shadow2.setOffset(0) 
        shadow2.setColor(QColor(color))
        return shadow2
    def addsearchwordmask(self,x,raw,callback=None ):
        if len(x)==0:
            return
        #print(x)
        pos=0
        labeli=0  
        self.textcursor.setPosition(0)
        self.textbrowser.setTextCursor(self.textcursor)   
        
        
        idx=0
        guesswidth=[]
        guesslinehead=None
        wwww=self.parent.width()
        for word in x:
            idx+=1
            if word['orig']=='\n':
                guesslinehead=None 
                continue
            l=len(word['orig'])
            tl1=self.textbrowser.cursorRect(self.textcursor).topLeft()
             
            tl4=self.textbrowser.cursorRect(self.textcursor).bottomRight()
            if guesslinehead is None:
                guesslinehead=tl1.x()
            if True:  
                self.textcursor.setPosition(pos+l )
                self.textbrowser.setTextCursor(self.textcursor)
                 
                tl2=self.textbrowser.cursorRect(self.textcursor).bottomRight() 
                tl3=self.textbrowser.cursorRect(self.textcursor).topLeft()   
                color=self.randomcolor(word)
                if color:
                    if word['orig'] not in ['\n','\r',' ',''] :
                        if labeli >=len(self.searchmasklabels)-1:
                            ql=QLabel(self.atback2) 
                            ql.setMouseTracking(True)
                            self.searchmasklabels.append(ql)

                            ql=Qlabel_c(self.toplabel) 
                            ql.setMouseTracking(True)
                            ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                            self.searchmasklabels_clicked.append(ql)
                            
                            ql=QLabel(self.atback2) 
                            ql.setMouseTracking(True)
                            self.searchmasklabels.append(ql)

                            ql=Qlabel_c(self.toplabel) 
                            ql.setMouseTracking(True)
                            ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                            self.searchmasklabels_clicked.append(ql)
                        if tl1.y()!=tl3.y():
                            if len(guesswidth)==0:
                                gw=30
                            else:
                                gw=sum(guesswidth)/len(guesswidth)
                            guesswidth1=gw*len(word['orig'])
                            tailx=wwww-guesslinehead
                            pos1=tl1.x()+2 ,tl1.y() ,tailx-tl1.x()-4,tl4.y()-tl1.y()   
                            xx=guesswidth1 -(tailx- tl1.x())  
                            guesslinehead=None
                            pos2=tl3.x()-xx+2,tl3.y() ,xx-4,tl4.y()-tl1.y()    
                            if globalconfig['usesearchword'] or globalconfig['usecopyword']:
                                self.searchmasklabels_clicked[labeli].setGeometry(*pos1) 
                                self.searchmasklabels_clicked[labeli].show()
                                self.searchmasklabels_clicked[labeli].company=self.searchmasklabels_clicked[labeli+1]
                                if callback:
                                    self.searchmasklabels_clicked[labeli].callback=functools.partial(callback,(word['orig'] )) 

                                self.searchmasklabels_clicked[labeli+1].setGeometry(*pos2) 
                                self.searchmasklabels_clicked[labeli+1].show()
                                self.searchmasklabels_clicked[labeli+1].company=self.searchmasklabels_clicked[labeli]
                                if callback:
                                    self.searchmasklabels_clicked[labeli+1].callback=functools.partial(callback,(word['orig'] )) 

                            if globalconfig['show_fenci']  :
                                self.searchmasklabels[labeli].setGeometry(*pos1) 
                                self.searchmasklabels[labeli].setStyleSheet("background-color: rgba{};".format(color)  )
                                self.searchmasklabels[labeli].show()

                                self.searchmasklabels[labeli+1].setGeometry(*pos2) 
                                self.searchmasklabels[labeli+1].setStyleSheet("background-color: rgba{};".format(color)  )
                                self.searchmasklabels[labeli+1].show()
                            labeli+=2
                        else: 
                             
                            guesswidth+=[(tl2.x()-tl1.x())/len(word['orig'])]*(len(word['orig']))
                            pos1=tl1.x()+2,tl1.y() ,tl2.x()-tl1.x()-4,tl2.y()-tl1.y() 
                            if globalconfig['usesearchword'] or globalconfig['usecopyword']:
                                self.searchmasklabels_clicked[labeli].setGeometry(*pos1)
                                self.searchmasklabels_clicked[labeli].company=None
                                self.searchmasklabels_clicked[labeli].show()
                                if callback:
                                    self.searchmasklabels_clicked[labeli].callback=functools.partial(callback,(word['orig'])) 
                            if globalconfig['show_fenci']  :
                                self.searchmasklabels[labeli].setGeometry(*pos1)
                                self.searchmasklabels[labeli].setStyleSheet("background-color: rgba{};".format(color)  )
                                self.searchmasklabels[labeli].show()
                            labeli+=1
                        
                        
                else:
                    if tl1.y()!=tl3.y():
                        guesslinehead=None
                tl1=tl3 
                tl4=tl2
                
                pos+=l
        
                
    def randomcolor(self,word):
        c=QColor("white") 
        if 'cixing' in word : 
            try:
                if globalconfig['cixingcolorshow'][word['cixing']]==False:
                    return None
                c=QColor(globalconfig['cixingcolor'][word['cixing']])
            except:
                pass
        return (c.red(),c.green(),c.blue(), globalconfig['showcixing_touming']/100)
         
    def getfh(self,half ,origin=True   ):
        
        font=QFont()
        if origin:
            font.setFamily(globalconfig['fonttype']) 
        else:
            font.setFamily(globalconfig['fonttype2']) 
        
        #font.setPixelSize(int(globalconfig['fontsize'])  )
        if half:
            font.setPointSizeF((globalconfig['fontsize']) * globalconfig['kanarate'])
        else:
            font.setPointSizeF((globalconfig['fontsize'])  )
        fm=QFontMetricsF(font)
          
        fhall=fm.height()  
        
        return fhall,font
        
     
    def addtag(self,x):  
        if len(self.savetaglabels)<len(x):
            self.savetaglabels+=[QLabel(self.parent) for i in range(len(x)-len(self.savetaglabels))]
         
        pos=0
        self.addtaged=True
        labeli=0 
         
        fhall,fontorig=self.getfh(False)
        
        fhhalf,fonthira=self.getfh(True)  
        fh,_=self.getfh(False,True)
        fh+=globalconfig['extra_space']
        for i in range(0,self.textbrowser.document().blockCount() ):
            b=self.textbrowser.document().findBlockByNumber(i)
                 
            tf=b.blockFormat()
            #tf.setLineHeight(fh,QTextBlockFormat.LineDistanceHeight)
            tf.setLineHeight(max(fh,fhall+fhhalf) ,QTextBlockFormat.FixedHeight)
            
            self.textcursor.setPosition(b.position()) 
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)
            if self.needdouble: 
                self.textcursorback.setPosition(b.position()) 
                self.textcursorback.setBlockFormat(tf) 
                self.textbrowserback.setTextCursor(self.textcursorback) 
         
        tl1=self.textbrowser.cursorRect(self.textcursor).topLeft().y() 
         
        if self.jiaming_y_delta+tl1-fhhalf!=0: 
            self.jiaming_y_delta=fhhalf-tl1
            self.movep(0,self.savey)
        x=self.nearmerge(x,pos,fonthira,fontorig) 
        self.settextposcursor(pos)
        for word in x:
            if word['orig']=='\n':
                continue
            l=len(word['orig'])

            tl1=self.textbrowser.cursorRect(self.textcursor).topLeft()  
             
            self.settextposcursor(pos+l)
            pos+=l 
            
            tl2=self.textbrowser.cursorRect(self.textcursor).topLeft() 
            if word['hira']==word['orig']:
                continue
            #print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())
            if word['orig']==' ':
                continue
            self.solvejiaminglabel(self.savetaglabels,labeli,word,fonthira,tl1,tl2,fhhalf)
            
            labeli+=1 
    def settextposcursor(self,pos):
        self.textcursor.setPosition(pos )
        self.textbrowser.setTextCursor(self.textcursor)
        if self.needdouble: 
            self.textcursorback.setPosition(pos)
            self.textbrowserback.setTextCursor(self.textcursorback)
    def nearmerge(self,x,startpos,fonthira,fontorig):
        pos=startpos 
        linex=[]
        newline=[]
        self.settextposcursor(pos)
        _metrichira=QFontMetricsF(fonthira) 
        _metricorig=QFontMetricsF(fontorig) 
        for i,word in enumerate(x):
            word['orig_w']=_metricorig.width(word['orig'])
            word['hira_w']=_metrichira.width(word['hira'])
            #print(word['hira'],word['hira_w'])
            newline.append(word)
            if word['orig']=='\n':
                continue
            l=len(word['orig'])
            tl1=self.textbrowser.cursorRect(self.textcursor).topLeft()  
            self.settextposcursor(pos+l)
            pos+=l 
            
            tl2=self.textbrowser.cursorRect(self.textcursor).topLeft() 
            
            #print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())
                
            if tl1.y()!=tl2.y() or i==len(x)-1: 
                linex.append(newline)
                newline=[]
        res=[] 
        for line in linex:

            while True:
                allnotbig=True
                newline=[]
                canmerge=False
                for word in line:
                    if word['hira']==word['orig'] or word['hira']=="" or word['orig']=="":
                        newline.append(word.copy())
                        canmerge=False
                    else:
                        if len(newline)>0 and  canmerge and  (word['hira_w']+newline[-1]['hira_w'] >word['orig_w']+newline[-1]['orig_w']) :
                                #print(word['hira'],word['hira_w'],newline[-1]['hira_w'],word['orig_w'],newline[-1]['orig_w'])
                                newline[-1]['hira']+=word['hira']
                                newline[-1]['orig']+=word['orig']
                                newline[-1]['hira_w']+=word['hira_w']
                                newline[-1]['orig_w']+=word['orig_w']
                                allnotbig=False
                        else:
                            newline.append(word.copy())
                        canmerge=True
                line=newline
                if allnotbig:break
            res+=newline
            newline=[] 
        self.settextposcursor(startpos)
        return   res       
    def solvejiaminglabel(self,labels,labeli,word,font,tl1,tl2,fh ):
        label=labels[labeli]

        if globalconfig['zitiyangshi'] ==3: 
            label.setGraphicsEffect(self.geteffect(globalconfig['fontsize'],globalconfig['jiamingcolor'],globalconfig['shadowforce']) ) 
            color=globalconfig['miaobiancolor']
        elif globalconfig['zitiyangshi'] in [0,1,2,4]:
            label.setGraphicsEffect(self._rawqlabel.graphicsEffect() )  
            color=globalconfig['jiamingcolor']
        label.setText(word['hira'])
        label.setFont(font)
        label.adjustSize()
        w=label.width()
        
        if tl1.y()!=tl2.y():
            #print(label,word)
            x=tl1.x() 
            if x+w/2<self.textbrowser.width():
                x=tl1.x() 
                y=tl1.y()-fh 
            else:
                x=tl2.x() -w
                y=tl2.y()-fh  
        else:
            x=tl1.x()/2+tl2.x()/2-w/2
            y=tl2.y()-fh   
        y+=globalconfig['buttonsize']*1.5 *self.parent.rate
        y+=self.jiaming_y_delta
        
        label.move(x,y)   
        label.setStyleSheet("color:{}; background-color:(0,0,0,0)".format(color))
        
        label.show()  
    def mergeCurrentCharFormat(self,colormiao,width):
        format2=self.textbrowser.currentCharFormat()
        format2.setTextOutline(QPen(QColor(colormiao),width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    
        self.textbrowser.setCurrentCharFormat(format2)
        if self.needdouble:
            self.needdouble=False
            self.textbrowserback.hide()
    def mergeCurrentCharFormat_out(self,colorinner,colormiao,width):
        if self.needdouble==False:
            self.textbrowserback.show()
            self.needdouble=True
        format1 =self.textbrowser.currentCharFormat()
        format1.setForeground(QColor(colorinner))
        format2= self.textbrowser.currentCharFormat()
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