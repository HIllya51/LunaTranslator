from PyQt5.QtCore import Qt,QSize,pyqtSignal ,QRect ,QPoint
from PyQt5.QtWidgets import QProxyStyle

from PyQt5.QtWidgets import  QColorDialog,QTabBar,QStylePainter,QStyleOptionTab,QStyle
from PyQt5.QtGui import QColor,QBrush,QTextOption,QFont
from PyQt5.QtWidgets import  QTabWidget,QMainWindow 

import utils.screen_rate 
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
        
# class customtabstyle(QProxyStyle): 
    
#     def sizeFromContents(self, types, option, size, widget):
#         size = super(customtabstyle, self).sizeFromContents(
#             types, option, size, widget)
#         if types == self.CT_TabBarTab:
#             size.transpose()
#             rt = utils.screen_rate.getScreenRate() 
#             # size.setHeight(70*rt)
#             # size.setWidth(200*rt)
#             size.scale(200,70,Qt.IgnoreAspectRatio)
#             # size.setHeight(70)
#             # size.setWidth(200)
#         return size
#     def drawControl(self,element,option,painter,widget):
#         if element == self.CE_TabBarTabLabel: 
#             allrect=option.rect 
            
#             painter.save()
#             painter.setPen(QColor('#dadbdc') )
#             #painter.setBrush(QBrush(QColor('#ffffff')))
#             painter.drawRect(allrect)#.adjust(6,6,-6,-6))
#             painter.restore()
#             painter.save()
#             #painter.setPen(QColor('#006ab1')) 
#             painter.setFont(QFont("",15,QFont.Bold))
#             painter.drawText(allrect,Qt.AlignCenter, option.text)
#             painter.restore()
            
#             return 
            
#         super(customtabstyle, self).drawControl(element, option, painter, widget)

# class TabBarStyle(QProxyStyle):

#     def sizeFromContents(self, types, option, size, widget):
#         size = super(TabBarStyle, self).sizeFromContents(
#             types, option, size, widget)
#         if types == self.CT_TabBarTab:
#             size.transpose()
#         return size

#     def drawControl(self, element, option, painter, widget):
#         if element == self.CE_TabBarTabLabel:
#             painter.drawText(option.rect, Qt.AlignCenter, option.text)
#             return
#         super(TabBarStyle, self).drawControl(element, option, painter, widget)


# from PyQt5.QtWidgets import QTabWidget, QLabel, QWidget, QGridLayout
 

# class TabWidget(QTabWidget):

#     def __init__(self, *args, **kwargs):
#         super(TabWidget, self).__init__(*args, **kwargs)
#         for i in range(10):
#             self.addTab(QLabel('Tab' + str(i)), str(i))


# class Window(QWidget):

#     def __init__(self, *args, **kwargs):
#         super(Window, self).__init__(*args, **kwargs)
#         x=QTabWidget(self )
#         x.setGeometry(0,0,400,400)
#         x.setTabPosition(QTabWidget.West)
#         x.addTab(QLabel('Tab' + str(1)), str(1))
#         x.addTab(QLabel('Tab' + str(1)), str(1))
#         x.addTab(QLabel('Tab' + str(1)), str(1))
 


# if __name__ == '__main__':
#     import sys
#     from PyQt5.QtWidgets import QApplication

#     app = QApplication(sys.argv)
#     app.setStyle(customtabstyle())
#     w = Window()
#     w.show()
#     sys.exit(app.exec_())
