from PyQt5.QtCore import Qt,QSize,pyqtSignal ,QRect ,QPoint
from PyQt5.QtWidgets import QProxyStyle

from PyQt5.QtWidgets import  QColorDialog,QTabBar,QStylePainter,QStyleOptionTab,QStyle
from PyQt5.QtGui import QColor,QBrush,QTextOption,QFont
from PyQt5.QtWidgets import  QTabWidget,QMainWindow 
 
class rotatetab(QTabBar): 
    def tabSizeHint(self, index): 
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s
    def paintEvent(self, e) : 
        painter = QStylePainter(self)
        opt = QStyleOptionTab() 
        for i in range(self.count()) :
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save() 
            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r 
            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()  
         