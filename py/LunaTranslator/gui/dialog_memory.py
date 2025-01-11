from qtsymbols import *
import gobject, os, qtawesome
from myutils.config import globalconfig, uid2gamepath
from myutils.wrapper import Singleton_close
from myutils.utils import getfilemd5, getimagefilefilter
from gui.usefulwidget import saveposwindow
from gui.dynalang import LPushButton


@Singleton_close
class dialog_memory(saveposwindow):
    # _sigleton=False
    def save(self) -> None:
        with open(self.rwpath, "w", encoding="utf8") as ff:
            ff.write(self.showtext.toHtml())

    def insertpic(self):
        f = QFileDialog.getOpenFileName(filter=getimagefilefilter())
        res = f[0]
        if res != "":
            self.showtext.insertHtml('<img src="{}">'.format(res))

    def __init__(self, parent) -> None:

        super().__init__(
            parent,
            flags=Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinMaxButtonsHint,
            poslist=globalconfig["memorydialoggeo"],
        )
        self.setWindowTitle("备忘录")
        self.setWindowIcon(qtawesome.icon(globalconfig["toolbutton"]["buttons"]["memory"]["icon"]))
        _w = QWidget()
        formLayout = QVBoxLayout(_w)  #
        self.showtext = QTextEdit()
        self.rwpath = gobject.getuserconfigdir(
            "memory/{}.html".format(gobject.baseobject.gameuid)
        )
        try:
            if os.path.exists(self.rwpath) == False:
                md5 = getfilemd5(uid2gamepath[gobject.baseobject.gameuid])
                f2 = gobject.getuserconfigdir("memory/{}.html".format(md5))
                try:
                    os.rename(f2, self.rwpath)
                except:
                    pass
            with open(self.rwpath, "r", encoding="utf8") as ff:
                text = ff.read()
        except:
            text = ""
        self.showtext.insertHtml(text)
        self.showtext.moveCursor(QTextCursor.MoveOperation.Start)
        formLayout.addWidget(self.showtext)

        x = QHBoxLayout()
        insertpicbtn = LPushButton("插入图片")
        insertpicbtn.clicked.connect(self.insertpic)
        self.showtext.textChanged.connect(self.save)
        x.addWidget(insertpicbtn)
        formLayout.addLayout(x)
        self.setCentralWidget(_w)
        self.show()
