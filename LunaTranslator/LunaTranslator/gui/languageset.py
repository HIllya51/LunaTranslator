from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QComboBox, QPushButton, QDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import qtawesome


class languageset(QDialog):
    getnewsentencesignal = pyqtSignal(str)
    getnewtranssignal = pyqtSignal(str, str)
    showsignal = pyqtSignal()

    def __init__(self, language_list):

        super(languageset, self).__init__(
            None, Qt.WindowStaysOnTopHint
        )  # 设置为顶级窗口，无边框
        self.setWindowIcon(qtawesome.icon("fa.language"))
        self.setMinimumSize(400, 100)
        self.setWindowTitle("语言设置 LanguageSetting")
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        self.setFont(font)
        self.current = 0
        language_listcombox = QComboBox()
        language_listcombox.addItems(language_list)
        language_listcombox.currentIndexChanged.connect(
            lambda x: setattr(self, "current", x)
        )
        vb = QVBoxLayout(self)

        vb.addWidget(language_listcombox)
        bt = QPushButton("OK")
        vb.addWidget(bt)
        bt.clicked.connect(self.accept)
