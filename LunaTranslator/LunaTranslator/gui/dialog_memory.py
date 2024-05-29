from qtsymbols import *
from myutils.config import _TR, globalconfig
from gui.usefulwidget import saveposwindow
from myutils.wrapper import Singleton_close
import os


@Singleton_close
class dialog_memory(saveposwindow):
    # _sigleton=False
    def save(self) -> None:
        with open(self.rwpath, "w", encoding="utf8") as ff:
            ff.write(self.showtext.toHtml())

    def insertpic(self):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        if res != "":
            self.showtext.insertHtml('<img src="{}">'.format(res))

    def __init__(self, parent, gamemd5="0") -> None:

        super().__init__(
            parent,
            flags=Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinMaxButtonsHint,
            dic=globalconfig,
            key="memorydialoggeo",
        )
        self.setWindowTitle(_TR("备忘录"))
        self.gamemd5 = gamemd5
        formLayout = QVBoxLayout()  #
        self.showtext = QTextEdit()
        os.makedirs("./userconfig/memory", exist_ok=True)
        self.rwpath = "./userconfig/memory/{}.html".format(gamemd5)
        try:
            with open(self.rwpath, "r", encoding="utf8") as ff:
                text = ff.read()
        except:
            text = ""
        self.showtext.insertHtml(text)
        self.showtext.moveCursor(QTextCursor.MoveOperation.Start)
        formLayout.addWidget(self.showtext)

        x = QHBoxLayout()
        insertpicbtn = QPushButton(_TR("插入图片"))
        insertpicbtn.clicked.connect(self.insertpic)
        savebtn = QPushButton(_TR("保存"))
        savebtn.clicked.connect(self.save)
        x.addWidget(insertpicbtn)
        x.addWidget(savebtn)
        formLayout.addLayout(x)
        _w = QWidget()
        _w.setLayout(formLayout)
        self.setCentralWidget(_w)
        self.show()
