import qtawesome,json
import sys,functools

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QGridLayout,QPushButton
 

class Demo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)  
        qg=QGridLayout()
        self.setLayout(qg)
        with open(r'C:/Users/11737/Documents/GitHub/LunaTranslator/LunaTranslator/LunaTranslator/qtawesome/fonts/fontawesome4.7-webfont-charmap.json','r')as ff:
            js=json.load(ff)
        i=0
        for k in js:
            try: 
                b=QPushButton(icon=qtawesome.icon('fa.'+k))
                b.clicked.connect(functools.partial(print,k))
                qg.addWidget(b,i//30,i%30)
                i+=1
            except:
                1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
