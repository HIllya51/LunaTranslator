import time, os, threading
from myutils.config import globalconfig
import winsharedutils, windows
from gui.rangeselect import rangeadjust
from myutils.wrapper import threader
from myutils.ocrutil import imageCut, ocr_run, ocr_init
import time, gobject
from qtsymbols import *
from collections import Counter
from textsource.textsourcebase import basetext


def qimge2np(img: QImage):
    # img=img.convertToFormat(QImage.Format_Grayscale8)
    shape = img.height(), img.width(), 1
    img = img.scaled(128, 8 * 3)
    img.shape = shape
    return img


def compareImage(img1, img2, h=24, w=128):
    cnt = 0
    for i in range(w):
        for j in range(h):
            cnt += img1.pixel(i, j) == img2.pixel(i, j)
    return cnt / (w * h)


class ocrtext(basetext):

    def init(self):
        self.startsql(gobject.gettranslationrecorddir("0_ocr.sqlite"))
        threading.Thread(target=ocr_init).start()
        self.savelastimg = []
        self.savelastrecimg = []
        self.savelasttext = []
        self.lastocrtime = []
        self.range_ui = []
        self.gettextthread()

    def newrangeadjustor(self):
        if len(self.range_ui) == 0 or globalconfig["multiregion"]:
            self.range_ui.append(rangeadjust(gobject.baseobject.settin_ui))
            self.savelastimg.append(None)
            self.savelastrecimg.append(None)
            self.lastocrtime.append(0)
            self.savelasttext.append(None)

    def starttrace(self, pos):
        for _r in self.range_ui:
            _r.starttrace(pos)

    def traceoffset(self, curr):
        for _r in self.range_ui:
            _r.traceoffsetsignal.emit(curr)

    def setrect(self, rect):
        p1, p2 = rect
        h1 = windows.WindowFromPoint(windows.POINT(*p1))
        h2 = windows.WindowFromPoint(windows.POINT(*p2))
        h3 = windows.WindowFromPoint(windows.POINT(p1[0], p2[1]))
        h4 = windows.WindowFromPoint(windows.POINT(p2[0], p1[1]))

        self.range_ui[-1].setrect(rect)
        if not globalconfig["ocrautobindhwnd"]:
            return
        if gobject.baseobject.hwnd:
            return
        usehwnds = []
        for _ in (h1, h2, h3, h4):
            if windows.GetWindowThreadProcessId(_) == os.getpid():
                continue
            usehwnds.append(_)

        if not usehwnds:
            return
        hwnd, count = Counter(usehwnds).most_common()[0]
        if count == len(usehwnds):
            gobject.baseobject.hwnd = hwnd

    def setstyle(self):
        [_.setstyle() for _ in self.range_ui]

    def showhiderangeui(self, b):
        if b and len(self.range_ui) == 0:
            for region in globalconfig["ocrregions"]:
                if region:
                    self.newrangeadjustor()
                    self.setrect(region)
            return
        for _ in self.range_ui:
            if b:
                _r = _.getrect()
                if _r:
                    _.setrect(_r)
            else:
                _.hide()

    @threader
    def gettextthread(self):
        laststate = (0, 0, 0, 0, 0)
        while not self.ending:
            if not self.isautorunning:
                continue

            if globalconfig["ocr_auto_method"] == 3:
                triggered = False
                this = (
                    windows.GetAsyncKeyState(windows.VK_LBUTTON),
                    windows.GetAsyncKeyState(windows.VK_RETURN),
                    windows.GetAsyncKeyState(windows.VK_CONTROL),
                    windows.GetAsyncKeyState(windows.VK_SHIFT),
                    windows.GetAsyncKeyState(windows.VK_MENU),
                )

                if any(((this[_] and (laststate[_] == 0)) for _ in (0, 1))):
                    # 按下
                    triggered = True
                elif any(((this[_] == 0 and laststate[_]) for _ in (2, 3, 4))):
                    # 松开
                    triggered = True
                laststate = this
                if triggered and gobject.baseobject.hwnd:
                    p1 = windows.GetWindowThreadProcessId(gobject.baseobject.hwnd)
                    p2 = windows.GetWindowThreadProcessId(windows.GetForegroundWindow())
                    triggered = p1 == p2
                if triggered:
                    time.sleep(globalconfig["ocr_trigger_delay"])
                    for _ in range(len(self.savelastimg)):
                        self.savelastimg[_] = None
                    while (not self.ending) and (globalconfig["ocr_auto_method"] == 3):
                        if self.waitforstablex():
                            break
                        time.sleep(0.1)
                    t = self.getallres(False)
                    if t:
                        self.dispatchtext(t)
                time.sleep(0.01)
            else:
                laststate = (0, 0, 0, 0, 0)
                t = self.getallres(True)
                if t:
                    self.dispatchtext(t)
                time.sleep(0.1)

    def waitforstable(self, i, imgr):
        imgr1 = qimge2np(imgr)
        if self.savelastimg[i] is not None and (
            imgr1.shape == self.savelastimg[i].shape
        ):
            image_score = compareImage(imgr1, self.savelastimg[i])
        else:
            image_score = 0
        if i == 0:
            try:
                gobject.baseobject.settin_ui.threshold1label.setText(str(image_score))
            except:
                pass
        self.savelastimg[i] = imgr1
        ok = image_score > globalconfig["ocr_stable_sim2"]
        return ok

    def waitforstablex(self):
        for i, range_ui in enumerate(self.range_ui):
            rect = range_ui.getrect()
            if rect is None:
                continue
            img = imageCut(
                gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
            )
            if not self.waitforstable(i, img):
                return False
        return True

    def getresauto(self, i, imgr):
        ok = True
        if globalconfig["ocr_auto_method"] in [0, 2]:
            imgr1 = qimge2np(imgr)
            h, w, c = imgr1.shape
            if self.savelastimg[i] is not None and (
                imgr1.shape == self.savelastimg[i].shape
            ):

                image_score = compareImage(imgr1, self.savelastimg[i])

            else:
                image_score = 0
            if i == 0:
                try:
                    gobject.baseobject.settin_ui.threshold1label.setText(
                        str(image_score)
                    )
                except:
                    pass
            self.savelastimg[i] = imgr1

            if image_score > globalconfig["ocr_stable_sim"]:
                if self.savelastrecimg[i] is not None and (
                    imgr1.shape == self.savelastrecimg[i].shape
                ):
                    image_score2 = compareImage(imgr1, self.savelastrecimg[i])
                else:
                    image_score2 = 0
                if i == 0:
                    try:
                        gobject.baseobject.settin_ui.threshold2label.setText(
                            str(image_score2)
                        )
                    except:
                        pass
                if image_score2 > globalconfig["ocr_diff_sim"]:
                    ok = False
                else:
                    self.savelastrecimg[i] = imgr1
            else:
                ok = False
        if globalconfig["ocr_auto_method"] in [1, 2]:
            if time.time() - self.lastocrtime[i] > globalconfig["ocr_interval"]:
                ok = True
            else:
                ok = False
        if ok == False:
            return
        text, infotype = ocr_run(imgr)
        self.lastocrtime[i] = time.time()
        if self.savelasttext[i] is not None:
            sim = winsharedutils.distance(self.savelasttext[i], text)
            self.savelasttext[i] = text
            if sim < globalconfig["ocr_text_diff"]:
                return
        self.savelasttext[i] = text
        return text, infotype

    def getresmanual(self, i, imgr):

        text, infotype = ocr_run(imgr)
        imgr1 = qimge2np(imgr)
        self.savelastimg[i] = imgr1
        self.savelastrecimg[i] = imgr1
        self.lastocrtime[i] = time.time()
        self.savelasttext[i] = text
        return text, infotype

    def getallres(self, auto):
        __text = []
        info = None
        for i, range_ui in enumerate(self.range_ui):
            rect = range_ui.getrect()
            if rect is None:
                continue
            img = imageCut(
                gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
            )
            if auto:
                _ = self.getresauto(i, img)
                if not _:
                    continue
                text, info = _
            else:
                text, info = self.getresmanual(i, img)
            if not text:
                continue
            if info and info != "<notrans>":
                gobject.baseobject.displayinfomessage(text, info)
                return
            __text.append(text)

        text = "\n".join(__text)
        if info:
            gobject.baseobject.displayinfomessage(text, info)
        else:
            return text

    def gettextonce(self):
        return self.getallres(False)

    def end(self):
        globalconfig["ocrregions"] = [_.getrect() for _ in self.range_ui]
        [_.closesignal.emit() for _ in self.range_ui]
