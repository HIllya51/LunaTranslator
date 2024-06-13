from qtsymbols import *
import qtawesome, gobject
from myutils.ocrutil import imagesolve
from myutils.config import globalconfig, _TR
from myutils.wrapper import Singleton_close
from gui.usefulwidget import saveposwindow


class pixlabel(QLabel):
    def __init__(self):
        super().__init__()
        self.pix = None

    def setpix(self, pix):
        self.pix = pix
        self.setPixmap(
            self.pix.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, a0):
        if self.pix:
            self.setPixmap(
                self.pix.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        return super().resizeEvent(a0)


@Singleton_close
class showocrimage(saveposwindow):
    setimage = pyqtSignal(list)

    def closeEvent(self, e):
        gobject.baseobject.showocrimage = None
        super().closeEvent(e)

    def __init__(self, parent, cached):
        self.img1 = None
        self.originimage = None
        super().__init__(parent, globalconfig, "showocrgeo")
        self.setWindowIcon(qtawesome.icon("fa.picture-o"))
        self.setWindowTitle(_TR("查看处理效果"))
        self.originlabel = pixlabel()
        qw = QWidget()
        self.solvedlabel = pixlabel()
        self.lay2 = QHBoxLayout()
        button = QPushButton(
            icon=qtawesome.icon("fa.rotate-right", color=globalconfig["buttoncolor"])
        )
        button.clicked.connect(self.retest)
        self.layout1 = QVBoxLayout()
        # self.lay2.addWidget(button)
        self.lay2.addLayout(self.layout1)
        self.setCentralWidget(qw)
        qw.setLayout(self.lay2)
        self.layout1.addWidget(self.originlabel)
        self.layout1.addWidget(button)
        self.layout1.addWidget(self.solvedlabel)
        self.setimage.connect(self.setimagefunction)
        if cached:
            self.setimagefunction(cached)

    def retest(self):
        if self.originimage is None:
            return
        img = imagesolve(self.originimage)
        self.setimagefunction([self.originimage, img])

    def setimagefunction(self, image):
        originimage, solved = image
        self.originimage = originimage
        self.img1 = QPixmap.fromImage(originimage)
        self.img2 = QPixmap.fromImage(solved)
        self.img1.setDevicePixelRatio(self.devicePixelRatioF())
        self.img2.setDevicePixelRatio(self.devicePixelRatioF())
        self.originlabel.setpix(self.img1)
        self.solvedlabel.setpix(self.img2)
