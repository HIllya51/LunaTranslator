from PyQt5.QtCore import Qt, QPoint, QPointF, pyqtSignal
from PyQt5.QtGui import (
    QTextCharFormat,
    QTextBlockFormat,
    QResizeEvent,
    QTextCursor,
    QPixmap,
    QFontMetricsF,
    QMouseEvent,
)
from PyQt5.QtWidgets import (
    QTextBrowser,
    QLabel,
    QGraphicsDropShadowEffect,
)
import functools
from myutils.config import globalconfig
from traceback import print_exc
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QFont,
    QPen,
    QPainterPath,
    QBrush,
    QFontMetrics,
)


class Qlabel_c(QLabel):

    def mousePressEvent(self, ev):
        self.pr = True
        return super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        pass
        # return super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, event: QMouseEvent):
        try:
            if self.underMouse():
                try:
                    if self.pr:
                        if event.button() == Qt.RightButton:
                            self.callback(True)
                        else:
                            self.callback(False)
                except:
                    print_exc()
            self.pr = False
        except:
            print_exc()
        return super().mouseReleaseEvent(event)

    def enterEvent(self, a0) -> None:
        if self.company:
            self.company.setStyleSheet("background-color: rgba(0,0,0,0.5);")
        self.setStyleSheet("background-color: rgba(0,0,0,0.5);")
        return super().enterEvent(a0)

    def leaveEvent(self, a0) -> None:
        if self.company:
            self.company.setStyleSheet("background-color: rgba(0,0,0,0.01);")
        self.setStyleSheet("background-color: rgba(0,0,0,0.01);")
        return super().leaveEvent(a0)


class QGraphicsDropShadowEffect_multi(QGraphicsDropShadowEffect):
    def __init__(self, x) -> None:
        self.x = x
        super().__init__()

    def draw(self, painter) -> None:
        for i in range(self.x):
            super().draw(painter)


class PlainLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextFormat(Qt.PlainText)

    def move(self, point: QPoint):
        text = self.text()
        isarabic = any((ord(char) >= 0x0600 and ord(char) <= 0x06E0) for char in text)
        if isarabic:
            point.setX(point.x() - self.width())
        super().move(point)


class ShadowLabel(PlainLabel):
    def setShadow(self, colorshadow, width, deepth, trace=False):
        shadow2 = QGraphicsDropShadowEffect_multi(deepth)
        if trace:
            shadow2.setBlurRadius(width)
            shadow2.setOffset(QPointF(width, width))
        else:
            shadow2.setBlurRadius(width)
            shadow2.setOffset(0)
        shadow2.setColor(QColor(colorshadow))
        self.setGraphicsEffect(shadow2)


class BorderedLabel(ShadowLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_outLineColor = QColor()
        self.m_fontOutLineWidth = 1
        self.m_contentColor = QColor()
        self._type = 0
        self._pix = None
        self._m_text = ""

    def text(self):
        return self._m_text

    def setText(self, text):
        self._m_text = text

    def setColorWidth(self, outLineColor, contentColor, width, _type=0):
        self.m_outLineColor = QColor(outLineColor)
        self.m_contentColor = QColor(contentColor)
        self.m_fontOutLineWidth = width
        self._type = _type

    def move(self, point: QPoint):
        point.setX(int(point.x() - self.m_fontOutLineWidth))
        point.setY(int(point.y() - self.m_fontOutLineWidth))
        super().move(point)

    def adjustSize(self):
        font = self.font()
        text = self.text()
        font_m = QFontMetrics(font)
        self.resize(
            int(font_m.width(text) + 2 * self.m_fontOutLineWidth),
            int(font_m.height() + 2 * self.m_fontOutLineWidth),
        )

    def paintEvent(self, event):
        if not self._pix:
            rate = self.devicePixelRatioF()
            self._pix = QPixmap(self.size() * rate)
            self._pix.setDevicePixelRatio(rate)
            self._pix.fill(Qt.transparent)
            text = self.text()
            font = self.font()
            font_m = QFontMetrics(font)
            painter = QPainter(self._pix)

            path = QPainterPath()
            path.addText(
                self.m_fontOutLineWidth,
                self.m_fontOutLineWidth + font_m.ascent(),
                font,
                text,
            )

            pen = QPen(
                self.m_outLineColor,
                self.m_fontOutLineWidth,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )

            painter.setRenderHint(QPainter.Antialiasing)
            if self._type == 0:
                painter.strokePath(path, pen)
                painter.fillPath(path, QBrush(self.m_contentColor))
            elif self._type == 1:
                painter.fillPath(path, QBrush(self.m_contentColor))
                painter.strokePath(path, pen)

        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pix)


class Textbrowser(QLabel):
    contentsChanged = pyqtSignal(int, int)

    def move(self, x, y):
        super().move(x, y)
        self.textbrowser.move(x, y)

        self.atback2.move(x, y)
        self.toplabel2.move(x, y)

    def resizeEvent(self, event):
        self.atback2.resize(event.size())
        self.toplabel2.resize(event.size())

    def contentchangedfunction(self):
        sz = self.textbrowser.document().size().toSize()
        self.textbrowser.resize(self.width(), sz.height())
        self.contentsChanged.emit(sz.width(), sz.height())

    def __init__(self, parent):
        super().__init__(parent)

        self.setMouseTracking(True)

        self.atback2 = QLabel(parent)

        self.toplabel2 = QLabel(parent)
        self.atback2.setMouseTracking(True)
        self.textbrowser = QTextBrowser(parent)
        self.textbrowser.document().contentsChanged.connect(self.contentchangedfunction)
        self.tranparentcolor = QColor()
        self.tranparentcolor.setAlpha(0)
        self.textbrowser.setTextColor(self.tranparentcolor)
        self.cleared = False
        self.font = QFont()

        self.toplabel2.setMouseTracking(True)

        self.textbrowser.setStyleSheet(
            "border-width: 0;\
            border-style: outset;\
            background-color: rgba(0, 0, 0, 0)"
        )

        self.textcursor = self.textbrowser.textCursor()
        self.textbrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textbrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.masklabel = QLabel(self.textbrowser)
        self.masklabel.setGeometry(0, 0, 9999, 9999)
        self.masklabel.setMouseTracking(True)

        self.savetaglabels = []
        self.searchmasklabels_clicked = []
        self.searchmasklabels = []
        self.backcolorlabels = []

        self.yinyinglabels = []

        self.yinyingpos = 0
        self.yinyingposline = 0
        self.lastcolor = None
        self.setselectable()
        self.blockcount = 0
        self.iteryinyinglabelsave = {}

    def setselectable(self):
        self.masklabel.setHidden(globalconfig["selectable"])

    def setnextfont(self, origin):
        if origin:
            self.font.setFamily(globalconfig["fonttype"])
        else:
            self.font.setFamily(globalconfig["fonttype2"])
        self.font.setPointSizeF(globalconfig["fontsize"])
        self.font.setBold(globalconfig["showbold"])

        self.textbrowser.moveCursor(QTextCursor.End)
        f = QTextCharFormat()
        f.setFont(self.font)
        f.setForeground(self.tranparentcolor)
        c = self.textbrowser.textCursor()
        c.setCharFormat(f)
        self.textbrowser.setTextCursor(c)

    def setAlignment(self, x):
        self.textbrowser.setAlignment(x)

    def append(self, x, tag, color):
        if self.cleared:
            _space = ""
            self.blockcount = 0
            b1 = 0
        else:
            _space = "\n"
            b1 = self.textbrowser.document().blockCount()
        self.cleared = False
        self.textbrowser.insertPlainText(_space + x)

        b2 = self.textbrowser.document().blockCount()

        fh = globalconfig["extra_space"]
        for i in range(self.blockcount, self.textbrowser.document().blockCount()):
            b = self.textbrowser.document().findBlockByNumber(i)
            tf = b.blockFormat()
            tf.setLineHeight(fh, QTextBlockFormat.LineDistanceHeight)
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)
        self.blockcount = self.textbrowser.document().blockCount()

        if len(tag) > 0:
            self.addtag(tag)

        self.showyinyingtext(b1, b2, color)

    def getcurrpointer(self):
        return self.textcursor.position()

    def insertatpointer(self, pointer, text):
        self.textcursor.setPosition(pointer)
        self.textbrowser.setTextCursor(self.textcursor)
        self.textbrowser.insertPlainText(text)

    def deletebetween(self, p1, p2):
        self.textcursor.setPosition(p1, QTextCursor.MoveAnchor)
        self.textcursor.setPosition(p2, QTextCursor.KeepAnchor)
        self.textcursor.removeSelectedText()

    def showyinyingtext2(self, color, iter_context_class, pos, text):
        if iter_context_class not in self.iteryinyinglabelsave:
            self.iteryinyinglabelsave[iter_context_class] = []
        maxh = 0
        maxh2 = 9999999
        for label in self.iteryinyinglabelsave[iter_context_class]:
            maxh2 = min(label.pos().y(), maxh2)
            if label.isVisible() == False:
                continue
            label.hide()
            maxh = max(label.pos().y(), maxh)

        subtext = []
        subpos = []
        lastpos = None
        posx = pos
        for i in range(len(text)):
            self.textcursor.setPosition(posx)
            posx += 1
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            if lastpos is None or tl1.y() != lastpos.y() or text[i] == "\n":
                lastpos = tl1
                subpos.append(lastpos)
                subtext.append("")
            subtext[-1] += text[i]

        maxnewh = 0
        for i in range(len(subtext)):
            maxnewh = max(maxnewh, subpos[i].y())
            _ = self.guesscreatelabel(self.toplabel2, color)
            _.setText(subtext[i])
            _.setFont(self.font)
            _.adjustSize()
            _.move(subpos[i])
            _.show()
            self.iteryinyinglabelsave[iter_context_class].append(_)
        if maxh:
            if maxnewh == 0:
                maxnewh = maxh2
            for label in self.yinyinglabels:
                if label.isVisible() == False:
                    continue
                if label.pos().y() > maxh:
                    label.move(label.pos().x(), label.pos().y() + maxnewh - maxh)
            for klass in self.iteryinyinglabelsave:
                if klass == iter_context_class:
                    continue
                for label in self.iteryinyinglabelsave[klass]:
                    if label.isVisible() == False:
                        continue
                    if label.pos().y() > maxh:
                        label.move(label.pos().x(), label.pos().y() + maxnewh - maxh)

    def showyinyingtext(self, b1, b2, color):
        linei = self.yinyingposline

        doc = self.textbrowser.document()
        block = doc.findBlockByNumber(0)

        for blocki in range(b1, b2):
            block = doc.findBlockByNumber(blocki)
            layout = block.layout()
            blockstart = block.position()
            lc = layout.lineCount()
            for lineii in range(lc):
                line = layout.lineAt(lineii)

                s = line.textStart()
                l = line.textLength()
                self.textcursor.setPosition(blockstart + s)
                self.textbrowser.setTextCursor(self.textcursor)
                tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

                _ = self.guesscreatelabel(self.toplabel2, color)
                _.setText(block.text()[s : s + l])
                _.setFont(self.font)
                _.adjustSize()
                _.move(tl1)
                _.show()
                self.yinyinglabels.append(_)
                linei += 1
        self.yinyingposline = linei

    def addsearchwordmask(self, x, raw, callback=None):
        if len(x) == 0:
            return
        # print(x)
        pos = 0
        labeli = 0
        self.textcursor.setPosition(0)
        self.textbrowser.setTextCursor(self.textcursor)

        idx = 0
        guesswidth = []
        guesslinehead = None
        wwww = self.width()
        heigth, __, _ = self.getfh(False)
        for word in x:
            idx += 1
            l = len(word["orig"])
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            tl4 = self.textbrowser.cursorRect(self.textcursor).bottomRight()
            if guesslinehead is None:
                guesslinehead = tl1.x()
            if True:
                self.textcursor.setPosition(pos + l)
                self.textbrowser.setTextCursor(self.textcursor)

                tl2 = self.textbrowser.cursorRect(self.textcursor).bottomRight()
                tl3 = self.textbrowser.cursorRect(self.textcursor).topLeft()
                color = self.randomcolor(word)
                if color:
                    if word["orig"] not in ["\n", " ", ""]:
                        if labeli >= len(self.searchmasklabels) - 1:
                            ql = QLabel(self.atback2)
                            ql.setMouseTracking(True)
                            self.searchmasklabels.append(ql)

                            ql = Qlabel_c(self.textbrowser)
                            ql.setMouseTracking(True)
                            ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                            self.searchmasklabels_clicked.append(ql)

                            ql = QLabel(self.atback2)
                            ql.setMouseTracking(True)
                            self.searchmasklabels.append(ql)

                            ql = Qlabel_c(self.textbrowser)
                            ql.setMouseTracking(True)
                            ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                            self.searchmasklabels_clicked.append(ql)
                        if tl1.y() != tl3.y():
                            if len(guesswidth) == 0:
                                gw = 30
                            else:
                                gw = sum(guesswidth) / len(guesswidth)
                            guesswidth1 = gw * len(word["orig"])
                            tailx = wwww - guesslinehead
                            pos1 = (
                                tl1.x() + 1,
                                tl1.y(),
                                tailx - tl1.x() - 2,
                                heigth,
                            )
                            xx = int(guesswidth1 - (tailx - tl1.x()))
                            guesslinehead = None
                            pos2 = tl3.x() + 1 - xx, tl3.y(), xx - 2, heigth
                            if (
                                globalconfig["usesearchword"]
                                or globalconfig["usecopyword"]
                            ):
                                self.searchmasklabels_clicked[labeli].setGeometry(*pos1)
                                self.searchmasklabels_clicked[labeli].show()
                                self.searchmasklabels_clicked[labeli].company = (
                                    self.searchmasklabels_clicked[labeli + 1]
                                )
                                if callback:
                                    self.searchmasklabels_clicked[labeli].callback = (
                                        functools.partial(callback, (word))
                                    )

                                self.searchmasklabels_clicked[labeli + 1].setGeometry(
                                    *pos2
                                )
                                self.searchmasklabels_clicked[labeli + 1].show()
                                self.searchmasklabels_clicked[labeli + 1].company = (
                                    self.searchmasklabels_clicked[labeli]
                                )
                                if callback:
                                    self.searchmasklabels_clicked[
                                        labeli + 1
                                    ].callback = functools.partial(callback, (word))

                            if globalconfig["show_fenci"]:
                                self.searchmasklabels[labeli].setGeometry(*pos1)
                                self.searchmasklabels[labeli].setStyleSheet(
                                    "background-color: rgba{};".format(color)
                                )
                                self.searchmasklabels[labeli].show()

                                self.searchmasklabels[labeli + 1].setGeometry(*pos2)
                                self.searchmasklabels[labeli + 1].setStyleSheet(
                                    "background-color: rgba{};".format(color)
                                )
                                self.searchmasklabels[labeli + 1].show()
                            labeli += 2
                        else:

                            guesswidth += [(tl2.x() - tl1.x()) / len(word["orig"])] * (
                                len(word["orig"])
                            )
                            pos1 = (
                                tl1.x() + 1,
                                tl1.y(),
                                tl2.x() - tl1.x() - 2,
                                heigth,
                            )
                            if (
                                globalconfig["usesearchword"]
                                or globalconfig["usecopyword"]
                            ):
                                self.searchmasklabels_clicked[labeli].setGeometry(*pos1)
                                self.searchmasklabels_clicked[labeli].company = None
                                self.searchmasklabels_clicked[labeli].show()
                                if callback:
                                    self.searchmasklabels_clicked[labeli].callback = (
                                        functools.partial(callback, word)
                                    )
                            if globalconfig["show_fenci"]:
                                self.searchmasklabels[labeli].setGeometry(*pos1)
                                self.searchmasklabels[labeli].setStyleSheet(
                                    "background-color: rgba{};".format(color)
                                )
                                self.searchmasklabels[labeli].show()
                            labeli += 1

                else:
                    if tl1.y() != tl3.y():
                        guesslinehead = None
                tl1 = tl3
                tl4 = tl2

                pos += l

    def randomcolor(self, word):
        c = QColor("white")
        if "cixing" in word:
            try:
                if globalconfig["cixingcolorshow"][word["cixing"]] == False:
                    return None
                c = QColor(globalconfig["cixingcolor"][word["cixing"]])
            except:
                pass
        return (c.red(), c.green(), c.blue(), globalconfig["showcixing_touming"] / 100)

    def getfh(self, half, origin=True):

        font = QFont()
        font.setBold(globalconfig["showbold"])
        if origin:
            font.setFamily(globalconfig["fonttype"])
        else:
            font.setFamily(globalconfig["fonttype2"])

        # font.setPixelSize(int(globalconfig['fontsize'])  )
        if half:
            font.setPointSizeF((globalconfig["fontsize"]) * globalconfig["kanarate"])
        else:
            font.setPointSizeF((globalconfig["fontsize"]))
        fm = QFontMetricsF(font)

        return fm.height(), fm.ascent(), font

    def addtag(self, x):
        pos = 0

        fasall, _, fontorig = self.getfh(False)
        fha, fascent, fonthira = self.getfh(True)
        for i in range(0, self.textbrowser.document().blockCount()):
            b = self.textbrowser.document().findBlockByNumber(i)

            tf = b.blockFormat()
            tf.setLineHeight(fasall + fha, QTextBlockFormat.FixedHeight)
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)
        x = self.nearmerge(x, pos, fonthira, fontorig)
        self.settextposcursor(pos)
        for word in x:
            l = len(word["orig"])

            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            self.settextposcursor(pos + l)
            pos += l

            tl2 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            if word["hira"] == word["orig"]:
                continue
            # print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())
            if word["orig"] == " ":
                continue
            self.savetaglabels.append(
                self.solvejiaminglabel(word, fonthira, tl1, tl2, fascent)
            )

    def settextposcursor(self, pos):
        self.textcursor.setPosition(pos)
        self.textbrowser.setTextCursor(self.textcursor)

    def nearmerge(self, x, startpos, fonthira, fontorig):
        pos = startpos
        linex = []
        newline = []
        self.settextposcursor(pos)
        _metrichira = QFontMetricsF(fonthira)
        _metricorig = QFontMetricsF(fontorig)
        for i, word in enumerate(x):
            word["orig_w"] = _metricorig.width(word["orig"])
            word["hira_w"] = _metrichira.width(word["hira"])
            # print(word['hira'],word['hira_w'])
            newline.append(word)

            l = len(word["orig"])
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            self.settextposcursor(pos + l)
            pos += l

            tl2 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            # print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())

            if tl1.y() != tl2.y() or i == len(x) - 1:
                linex.append(newline)
                newline = []
        res = []
        for line in linex:

            while True:
                allnotbig = True
                newline = []
                canmerge = False
                for word in line:
                    if (
                        word["hira"] == word["orig"]
                        or word["hira"] == ""
                        or word["orig"] == ""
                    ):
                        newline.append(word.copy())
                        canmerge = False
                    else:
                        if (
                            len(newline) > 0
                            and canmerge
                            and (
                                word["hira_w"] + newline[-1]["hira_w"]
                                > word["orig_w"] + newline[-1]["orig_w"]
                            )
                        ):
                            # print(word['hira'],word['hira_w'],newline[-1]['hira_w'],word['orig_w'],newline[-1]['orig_w'])
                            newline[-1]["hira"] += word["hira"]
                            newline[-1]["orig"] += word["orig"]
                            newline[-1]["hira_w"] += word["hira_w"]
                            newline[-1]["orig_w"] += word["orig_w"]
                            allnotbig = False
                        else:
                            newline.append(word.copy())
                        canmerge = True
                line = newline
                if allnotbig:
                    break
            res += newline
            newline = []
        self.settextposcursor(startpos)
        return res

    def guesscreatelabel(self, p, color, rate=1):
        c1 = color
        c2 = globalconfig["miaobiancolor"]
        if globalconfig["zitiyangshi2"] == 2:
            label = BorderedLabel(p)
            label.setColorWidth(c1, c2, rate * globalconfig["miaobianwidth2"])

        elif globalconfig["zitiyangshi2"] == 3:
            label = BorderedLabel(p)
            label.setColorWidth(c2, c1, rate * globalconfig["miaobianwidth2"])
        elif globalconfig["zitiyangshi2"] == 1:

            label = BorderedLabel(p)
            label.setColorWidth(c1, c2, rate * globalconfig["miaobianwidth"], 1)
        elif globalconfig["zitiyangshi2"] == 4:
            label = BorderedLabel(p)
            label.setColorWidth(c2, c1, rate * globalconfig["miaobianwidth2"])
            label.setShadow(c2, rate * globalconfig["traceoffset"], 1, True)
        elif globalconfig["zitiyangshi2"] == 0:
            label = PlainLabel(p)
            label.setStyleSheet("color:{}; background-color:(0,0,0,0)".format(c1))
        elif globalconfig["zitiyangshi2"] == 5:
            label = ShadowLabel(p)
            label.setStyleSheet("color:{}; background-color:(0,0,0,0)".format(c2))
            label.setShadow(
                c1, rate * globalconfig["fontsize"], globalconfig["shadowforce"]
            )
        return label

    def solvejiaminglabel(self, word, font, tl1, tl2, fh):
        _ = self.guesscreatelabel(
            self.atback2, globalconfig["jiamingcolor"], rate=globalconfig["kanarate"]
        )
        _.setText(word["hira"])
        _.setFont(font)
        _.adjustSize()
        w = _.width()

        if tl1.y() != tl2.y():
            # print(label,word)
            x = tl1.x()
            if x + w / 2 < self.textbrowser.width():
                x = tl1.x()
                y = tl1.y() - fh
            else:
                x = tl2.x() - w
                y = tl2.y() - fh
        else:
            x = tl1.x() / 2 + tl2.x() / 2 - w / 2
            y = tl2.y() - fh

        _.move(QPoint(int(x), int(y)))

        _.show()
        return _

    def clear(self):
        for label in self.searchmasklabels:
            label.hide()
        for label in self.searchmasklabels_clicked:
            label.hide()
        for label in self.savetaglabels:
            label.deleteLater()
            del label
        self.savetaglabels.clear()
        for label in self.yinyinglabels:
            label.deleteLater()
            del label
        self.yinyinglabels.clear()
        for klass, labels in self.iteryinyinglabelsave.items():
            for label in labels:
                label.deleteLater()
                del label
        self.iteryinyinglabelsave.clear()
        self.yinyingpos = 0
        self.yinyingposline = 0
        self.cleared = True
        self.textbrowser.setText("")

        # self.shadowlabel.setText('')
        # self.shadowlabel.savetext=''
