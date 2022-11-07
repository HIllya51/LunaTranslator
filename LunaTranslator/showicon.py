import qtawesome,json
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QGridLayout,QPushButton
 

class Demo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)  
        qg=QGridLayout()
        self.setLayout(qg)
        with open(r'./qtawesome/fonts/fontawesome4.7-webfont-charmap.json','r')as ff:
            js=json.load(ff)
        i=0
        for k in js:
            try: 

                qg.addWidget(QPushButton(icon=qtawesome.icon('fa.'+k)),i//20,i%20)
                i+=1
            except:
                1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
