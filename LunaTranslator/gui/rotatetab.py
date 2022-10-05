from PyQt5.QtCore import Qt,QSize,pyqtSignal ,QRect 
from PyQt5.QtWidgets import QProxyStyle

from PyQt5.QtWidgets import  QColorDialog
from PyQt5.QtGui import QColor,QBrush,QTextOption,QFont
from PyQt5.QtWidgets import  QTabWidget,QMainWindow 

import utils.screen_rate 
class customtabstyle(QProxyStyle): 
    def sizeFromContents(self, types, option, size, widget):
        size = super(customtabstyle, self).sizeFromContents(
            types, option, size, widget)
        if types == self.CT_TabBarTab:
            size.transpose()
            rt = utils.screen_rate.getScreenRate() 
            size.setHeight(70*rt)
            size.setWidth(200*rt)
        return size
    def drawControl(self,element,option,painter,widget):
        if element == self.CE_TabBarTabLabel: 
            allrect=option.rect 
            
            painter.save()
            painter.setPen(QColor('#dadbdc') )
            #painter.setBrush(QBrush(QColor('#ffffff')))
            painter.drawRect(allrect)#.adjust(6,6,-6,-6))
            painter.restore()
            painter.save()
            #painter.setPen(QColor('#006ab1')) 
            painter.setFont(QFont("",15,QFont.Bold))
            painter.drawText(allrect,Qt.AlignCenter, option.text)
            painter.restore()
            
            return 
            
        super(customtabstyle, self).drawControl(element, option, painter, widget)

class TabBarStyle(QProxyStyle):

    def sizeFromContents(self, types, option, size, widget):
        size = super(TabBarStyle, self).sizeFromContents(
            types, option, size, widget)
        if types == self.CT_TabBarTab:
            size.transpose()
        return size

    def drawControl(self, element, option, painter, widget):
        if element == self.CE_TabBarTabLabel:
            painter.drawText(option.rect, Qt.AlignCenter, option.text)
            return
        super(TabBarStyle, self).drawControl(element, option, painter, widget)


from PyQt5.QtWidgets import QTabWidget, QLabel, QWidget, QGridLayout
 

class TabWidget(QTabWidget):

    def __init__(self, *args, **kwargs):
        super(TabWidget, self).__init__(*args, **kwargs)
        for i in range(10):
            self.addTab(QLabel('Tab' + str(i)), str(i))


class Window(QWidget):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        x=QTabWidget(self )
        x.setGeometry(0,0,400,400)
        x.setTabPosition(QTabWidget.West)
        x.addTab(QLabel('Tab' + str(1)), str(1))
        x.addTab(QLabel('Tab' + str(1)), str(1))
        x.addTab(QLabel('Tab' + str(1)), str(1))
 


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle(customtabstyle())
    w = Window()
    w.show()
    sys.exit(app.exec_())
