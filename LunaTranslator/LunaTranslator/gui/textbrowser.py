from qtsymbols import *
import functools
from traceback import print_exc
from myutils.config import globalconfig


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
                        if event.button() == Qt.MouseButton.RightButton:
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


class BorderedLabel(QLabel):
    def move(self, point: QPoint):
        self.movedx = 0
        self.movedy = 0
        text = self.text()
        isarabic = any((ord(char) >= 0x0600 and ord(char) <= 0x06E0) for char in text)
        if isarabic:
            self.movedx -= self.width()
        self.movedx -= self.m_fontOutLineWidth
        self.movedy -= self.m_fontOutLineWidth
        point.setX(int(point.x() + self.movedx))
        point.setY(int(point.y() + self.movedy))
        super().move(point)

    def pos(self) -> QPoint:
        p = super().pos()
        p.setX(int(p.x() - self.movedx))
        p.setY(int(p.y() - self.movedy))
        return p

    def clearShadow(self):
        self.setGraphicsEffect(None)

    def setShadow(self, colorshadow, width=1, deepth=1, trace=False):

        shadow2 = QGraphicsDropShadowEffect_multi(deepth)
        if trace:
            shadow2.setBlurRadius(width)
            shadow2.setOffset(QPointF(width, width))
        else:
            shadow2.setBlurRadius(width)
            shadow2.setOffset(0)
        shadow2.setColor(QColor(colorshadow))
        self.setGraphicsEffect(shadow2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.movedy = 0
        self.movedx = 0
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

    def adjustSize(self):
        self._pix = None
        font = self.font()
        text = self.text()
        font_m = QFontMetrics(font)
        self.resize(
            int(font_m.size(0, text).width() + 2 * self.m_fontOutLineWidth),
            int(font_m.height() + 2 * self.m_fontOutLineWidth),
        )

    def labelresetcolor(self, color, rate=1):
        c1 = color
        c2 = globalconfig["miaobiancolor"]
        if c1 is None:
            c1 = ""
        if c2 is None:
            c2 = ""
        if globalconfig["zitiyangshi2"] == 2:
            self.setColorWidth(c1, c2, rate * globalconfig["miaobianwidth2"])
            self.clearShadow()
        elif globalconfig["zitiyangshi2"] == 3:
            self.setColorWidth(c2, c1, rate * globalconfig["miaobianwidth2"])
            self.clearShadow()
        elif globalconfig["zitiyangshi2"] == 1:
            self.setColorWidth(c1, c2, rate * globalconfig["miaobianwidth"], 1)
            self.clearShadow()
        elif globalconfig["zitiyangshi2"] == 4:
            self.setColorWidth(c2, c1, rate * globalconfig["miaobianwidth2"])
            self.setShadow(c2, rate * globalconfig["traceoffset"], 1, True)
        elif globalconfig["zitiyangshi2"] == 0:
            self.setColorWidth("", c1, 0, 2)
            self.clearShadow()
        elif globalconfig["zitiyangshi2"] == 5:
            self.setColorWidth("", c2, 0, 2)
            self.setShadow(
                c1, rate * globalconfig["fontsize"], globalconfig["shadowforce"]
            )

    def paintEvent(self, event):
        if not self._pix:
            rate = self.devicePixelRatioF()
            self._pix = QPixmap(self.size() * rate)
            self._pix.setDevicePixelRatio(rate)
            self._pix.fill(Qt.GlobalColor.transparent)
            text = self.text()
            font = self.font()
            font_m = QFontMetrics(font)
            painter = QPainter(self._pix)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            if self._type == 2:

                path.addText(
                    0,
                    font_m.ascent(),
                    font,
                    text,
                )
                painter.fillPath(path, QBrush(self.m_contentColor))
            else:
                path.addText(
                    self.m_fontOutLineWidth,
                    self.m_fontOutLineWidth + font_m.ascent(),
                    font,
                    text,
                )

                pen = QPen(
                    self.m_outLineColor,
                    self.m_fontOutLineWidth,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )

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

    def __makeborder(self, size: QSize):
        _padding_resize = 5
        _padding_move = 5
        _padding = _padding_resize + _padding_move
        self.masklabel_right.move(self.width() - _padding, 0)
        self.masklabel_bottom.move(0, 0 + size.height() - _padding)
        self.masklabel_left.resize(_padding, size.height())
        self.masklabel_right.resize(_padding, size.height())
        self.masklabel_bottom.resize(size.width(), _padding)

    def move(self, x, y):
        super().move(x, y)
        self.textbrowser.move(x, y)
        self.atback2.move(x, y)
        self.toplabel2.move(x, y)

        self.__makeborder(self.size())

    def resizeEvent(self, event: QResizeEvent):
        self.atback2.resize(event.size())
        self.toplabel2.resize(event.size())
        self.masklabel.resize(event.size())

        self.__makeborder(event.size())

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
        self.textbrowser.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.textbrowser.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.masklabel = QLabel(self.textbrowser)
        self.masklabel.setMouseTracking(True)
        self.masklabel_left = QLabel(self.textbrowser)
        self.masklabel_left.setMouseTracking(True)
        self.masklabel_right = QLabel(self.textbrowser)
        self.masklabel_right.setMouseTracking(True)
        self.masklabel_bottom = QLabel(self.textbrowser)
        self.masklabel_bottom.setMouseTracking(True)

        self.savetaglabels = []
        self.searchmasklabels_clicked = []
        self.searchmasklabels = []
        self.backcolorlabels = []

        self.yinyinglabels = []
        self.yinyinglabels_idx = 0

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

        self.textbrowser.moveCursor(QTextCursor.MoveOperation.End)
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
            if isqt5:
                lht = QTextBlockFormat.LineHeightTypes.LineDistanceHeight
            else:
                lht = 4
            tf.setLineHeight(fh, lht)
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
        self.textcursor.setPosition(p1, QTextCursor.MoveMode.MoveAnchor)
        self.textcursor.setPosition(p2, QTextCursor.MoveMode.KeepAnchor)
        self.textcursor.removeSelectedText()

    def showyinyingtext2(self, color, iter_context_class, pos, text):
        if iter_context_class not in self.iteryinyinglabelsave:
            self.iteryinyinglabelsave[iter_context_class] = [[], 0]
        maxh = 0
        maxh2 = 9999999
        for label in self.iteryinyinglabelsave[iter_context_class][0]:
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
            if self.iteryinyinglabelsave[iter_context_class][1] >= len(
                self.iteryinyinglabelsave[iter_context_class][0]
            ):
                self.iteryinyinglabelsave[iter_context_class][0].append(
                    BorderedLabel(self.toplabel2)
                )
            maxnewh = max(maxnewh, subpos[i].y())
            _ = self.iteryinyinglabelsave[iter_context_class][0][
                self.iteryinyinglabelsave[iter_context_class][1]
            ]
            _.labelresetcolor(color)
            _.setText(subtext[i])
            _.setFont(self.font)
            _.adjustSize()
            _.move(subpos[i])
            _.show()
            self.iteryinyinglabelsave[iter_context_class][1] += 1

        if maxh:
            if maxnewh == 0:
                maxnewh = maxh2
            for label in self.yinyinglabels:
                if label.isVisible() == False:
                    continue
                if label.pos().y() > maxh:
                    label.move(
                        QPoint(label.pos().x(), label.pos().y() + maxnewh - maxh)
                    )
            for klass in self.iteryinyinglabelsave:
                if klass == iter_context_class:
                    continue
                for label in self.iteryinyinglabelsave[klass][0]:
                    if label.isVisible() == False:
                        continue
                    if label.pos().y() > maxh:
                        label.move(
                            QPoint(label.pos().x(), label.pos().y() + maxnewh - maxh)
                        )

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

                if self.yinyinglabels_idx >= len(self.yinyinglabels):
                    self.yinyinglabels.append(BorderedLabel(self.toplabel2))
                _ = self.yinyinglabels[self.yinyinglabels_idx]
                self.yinyinglabels_idx += 1
                _.labelresetcolor(color)
                _.setText(block.text()[s : s + l])
                _.setFont(self.font)
                _.adjustSize()
                _.move(tl1)
                _.show()
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
        heigth, __, _ = self.getfh(False)
        for word in x:
            idx += 1
            l = len(word["orig"])
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            tl4 = self.textbrowser.cursorRect(self.textcursor).bottomRight()

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
                            for __i in range(len(word["orig"])):
                                self.textcursor.setPosition(pos + __i)
                                self.textbrowser.setTextCursor(self.textcursor)
                                _tl = self.textbrowser.cursorRect(
                                    self.textcursor
                                ).topLeft()
                                if _tl.y() != tl1.y():
                                    break
                            self.textcursor.setPosition(pos + l)
                            self.textbrowser.setTextCursor(self.textcursor)
                            __fm = self.getfh(False, getfm=True)
                            w1 = __fm.size(0, word["orig"][:__i]).width()
                            w2 = __fm.size(0, word["orig"][__i:]).width()

                            pos1 = (
                                tl1.x() + 1,
                                tl1.y(),
                                w1 - 2,
                                int(heigth),
                            )
                            pos2 = tl3.x() + 1 - w2, tl3.y(), w2 - 2, int(heigth)

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

                            pos1 = (
                                tl1.x() + 1,
                                tl1.y(),
                                tl2.x() - tl1.x() - 2,
                                int(heigth),
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

                tl1 = tl3
                tl4 = tl2

                pos += l

    def randomcolor(self, word):
        if word.get("isdeli", False):
            return None
        c = QColor("white")
        if "cixing" in word:
            try:
                if globalconfig["cixingcolorshow"][word["cixing"]] == False:
                    return None
                c = QColor(globalconfig["cixingcolor"][word["cixing"]])
            except:
                pass
        return (c.red(), c.green(), c.blue(), globalconfig["showcixing_touming"] / 100)

    def getfh(self, half, origin=True, getfm=False):

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
        if getfm:
            return fm
        return fm.height(), fm.ascent(), font

    def addtag(self, x):
        pos = 0

        fasall, _, fontorig = self.getfh(False)
        fha, fascent, fonthira = self.getfh(True)
        for i in range(0, self.textbrowser.document().blockCount()):
            b = self.textbrowser.document().findBlockByNumber(i)

            tf = b.blockFormat()
            if isqt5:
                lht = QTextBlockFormat.LineHeightTypes.FixedHeight
            else:
                lht = 2
            tf.setLineHeight(fasall + fha, lht)
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)
        x = self.nearmerge(x, pos, fonthira, fontorig)
        self.settextposcursor(pos)
        savetaglabels_idx = 0
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
            if savetaglabels_idx >= len(self.savetaglabels):
                self.savetaglabels.append(BorderedLabel(self.atback2))
            self.solvejiaminglabel(
                self.savetaglabels[savetaglabels_idx], word, fonthira, tl1, tl2, fascent
            )
            savetaglabels_idx += 1

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
            word["orig_w"] = _metricorig.size(0, word["orig"]).width()
            word["hira_w"] = _metrichira.size(0, word["hira"]).width()
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

    def solvejiaminglabel(self, _: BorderedLabel, word, font, tl1, tl2, fh):
        _.labelresetcolor(globalconfig["jiamingcolor"], rate=globalconfig["kanarate"])
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
            label.hide()

        self.yinyinglabels_idx = 0
        for label in self.yinyinglabels:
            label.hide()
        for klass, labels in self.iteryinyinglabelsave.items():
            for label in labels[0]:
                label.hide()
            labels[1] = 0
        self.yinyingpos = 0
        self.yinyingposline = 0
        self.cleared = True
        self.textbrowser.clear()
