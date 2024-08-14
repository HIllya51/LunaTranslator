import time, os, threading
from myutils.config import globalconfig
import winsharedutils, windows
from gui.rangeselect import rangeadjust
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


def sample_compare(img1, img2, h=24, w=128):
    cnt = 0
    for i in range(w):
        for j in range(h):
            cnt += img1.pixel(i, j) == img2.pixel(i, j)
    return cnt / (w * h)


def compareImage(img1: QImage, img2):
    if globalconfig["ocr_presolve_method"] in [2, 3]:
        return sample_compare(img1, img2, img1.height(), img1.width())
    else:
        return sample_compare(img1, img2)


class ocrtext(basetext):

    def __init__(self):
        threading.Thread(target=ocr_init).start()
        self.screen = QApplication.primaryScreen()
        self.savelastimg = []
        self.savelastrecimg = []
        self.savelasttext = []
        self.lastocrtime = []
        self.range_ui = []
        self.timestamp = time.time()
        super(ocrtext, self).__init__("0", "ocr")
        if globalconfig["rememberocrregions"]:
            for region in globalconfig["ocrregions"]:
                if region:
                    self.newrangeadjustor()
                    self.setrect(region)

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
        for _ in self.range_ui:
            if b:
                _r = _.getrect()
                if _r:
                    _.setrect(_r)
            else:
                _.hide()

    def gettextthread(self):
        if all([_.getrect() is None for _ in self.range_ui]):
            time.sleep(1)
            return None
        time.sleep(0.1)
        __text = []
        for i, range_ui in enumerate(self.range_ui):
            rect = range_ui.getrect()

            # img=ImageGrab.grab((self.rect[0][0],self.rect[0][1],self.rect[1][0],self.rect[1][1]))
            # imgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            if rect is None:
                continue
            imgr = imageCut(
                gobject.baseobject.hwnd,
                rect[0][0],
                rect[0][1],
                rect[1][0],
                rect[1][1],
                i == 0,
            )
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
                continue
            text = ocr_run(imgr)
            self.lastocrtime[i] = time.time()

            if self.savelasttext[i] is not None:
                sim = winsharedutils.distance(self.savelasttext[i], text)
                # print(text,sim)
                if sim < globalconfig["ocr_text_diff"]:
                    continue
            self.savelasttext[i] = text

            __text.append(text)
        return "\n".join(__text)

    def gettextonce(self):
        __text = []
        for i, range_ui in enumerate(self.range_ui):
            rect = range_ui.getrect()
            if rect is None:
                continue
            if rect[0][0] > rect[1][0] or rect[0][1] > rect[1][1]:
                return
            img = imageCut(
                gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
            )

            text = ocr_run(img)
            imgr1 = qimge2np(img)
            self.savelastimg[i] = imgr1
            self.savelastrecimg[i] = imgr1
            self.lastocrtime[i] = time.time()
            self.savelasttext[i] = text
            __text.append(text)
        return "\n".join(__text)

    def end(self):
        globalconfig["ocrregions"] = [_.getrect() for _ in self.range_ui]
        [_.closesignal.emit() for _ in self.range_ui]
        super().end()
