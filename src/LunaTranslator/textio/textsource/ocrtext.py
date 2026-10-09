import time, json
from myutils.config import globalconfig
from myutils.utils import checkmd5reloadmodule, parsekeystringtomodvkcode
import NativeUtils, windows
from gui.rangeselect import rangeadjust
from gui.ocrtranslationoverlay import (
    OCRRegionText,
    OCRRegionBatch,
    capture_without_overlays,
    overlay_source_is_current,
)
from myutils.wrapper import threader
from myutils.ocrutil import imageCut, ocr_run, ocr_init
import time, gobject
from qtsymbols import *
from textio.textsource.textsourcebase import basetext
from ocrengines.baseocrclass import OCRResultParsed
from CVUtils import cvMat
from traceback import print_exc


def imageCutEx(hwnd, rectX: QRect, background_callback=None):
    img = capture_without_overlays(lambda: imageCut(hwnd, rectX), rectX)
    if img is None:
        return QImage()
    succ = True
    if hwnd:
        succ, img = img
    else:
        succ = False
    if img.isNull():
        return img
    if not succ:
        rect2 = windows.GetWindowRect(gobject.base.translation_ui.winid)
        rect = QRect(rect2[0], rect2[1], rect2[2] - rect2[0], rect2[3] - rect2[1])
        if rectX.intersected(rect):
            rect.translate(-rectX.x(), -rectX.y())
            painter = QPainter(img)
            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)
            painter.end()

    if background_callback is not None:
        background_callback(img, rectX)
    if globalconfig.get("use_ocr_preprocess", False):
        try:
            img = checkmd5reloadmodule(
                gobject.getconfig("ocr_preprocess.py"), "ocr_preprocess"
            ).Process(img)
        except:
            print_exc()
    return img


class rangemanger:
    def __init__(self, ref: "ocrtext", ranges: "list[rangemanger]"):
        self.ref = ref
        self.range_ui = rangeadjust(gobject.base.settin_ui, ranges)
        self.savelastimg: cvMat = None
        self.savelastrecimg: cvMat = None
        self.lastocrtime: float = 0
        self.savelasttext: str = None
        self._last_capture_rect = None

    def __del__(self):
        self.range_ui.closesignal.emit()

    def _commit_ocr_result(self, result, snapshot, image=None):
        with self.range_ui.ocr_source_lock:
            revision = self.range_ui.remember_overlay_source(
                "" if result.error else result.textonly, snapshot
            )
            if revision is None:
                return
            if image is not None:
                self.savelastimg = cvMat(image)
                self.savelastrecimg = self.savelastimg
            self.lastocrtime = time.time()
            self.savelasttext = result.textonly
            self._last_capture_rect = snapshot.rect
            # Freeze provenance here; batch assembly must not read a newer
            # selection revision and attach it to this older OCR result.
            result.ocr_overlay_source = OCRRegionText(
                result.textonly, self.range_ui, revision, owner=self.ref
            )
            # 块级来源（原地按位置绘制）：有坐标且非图片翻译时，每个
            # OCR 结果区域（合并临近行之后）各自翻译、各回各自位置；
            # 否则整框一条译文（见 OCRTranslationOverlay）。
            result.ocr_overlay_block_sources = None
            blocks = None
            if (
                globalconfig.get("ocr_translation_overlay", False)
                and not result.error
                and result.result.hasboxs
                and not result.result.isocrtranslate
            ):
                blocks = [tuple(_.box4) for _ in result.result.blocks]
                sources = [
                    OCRRegionText(
                        _.text, self.range_ui, revision,
                        owner=self.ref, block_index=i,
                    )
                    for i, _ in enumerate(result.result.blocks)
                    if _.text and _.text.strip()
                ]
                if sources:
                    result.ocr_overlay_block_sources = sources
            self.range_ui.publish_overlay_layout(revision, blocks)
            return result

    def getresmanual(self):
        snapshot = self.range_ui.capture_snapshot()
        rect = QRect(*snapshot.rect)
        if not rect.isValid():
            return
        imgr = imageCutEx(self.ref.hwnd, rect)
        if imgr.isNull():
            return
        if snapshot != self.range_ui.capture_snapshot():
            return
        result = ocr_run(imgr)
        return self._commit_ocr_result(result, snapshot, imgr)

    def getresauto(self):
        snapshot = self.range_ui.capture_snapshot()
        rect = QRect(*snapshot.rect)
        if not rect.isValid():
            return
        imgr = imageCutEx(self.ref.hwnd, rect)
        if imgr.isNull():
            return
        with self.range_ui.ocr_source_lock:
            if snapshot != self.range_ui.capture_snapshot():
                return
            reset = self._last_capture_rect != snapshot.rect or (
                globalconfig.get("ocr_translation_overlay", False)
                and self.range_ui._ocr_overlay_original is None
            )
            ok = True
            analysis_image = None
            recorded_image = self.savelastrecimg
            if globalconfig.get("ocr_auto_method_v2", "period") == "analysis":
                imgr1 = cvMat(imgr)
                analysis_image = imgr1
                image_score = imgr1.MSSIM(self.savelastimg)
                gobject.base.thresholdsett1.emit(str(image_score))
                if image_score > globalconfig.get("ocr_stable_sim_v2", 0.5):
                    image_score2 = imgr1.MSSIM(self.savelastrecimg)
                    gobject.base.thresholdsett2.emit(str(image_score2))
                    if (
                        image_score2 > globalconfig.get("ocr_diff_sim_v2", 0.95)
                        and not reset
                    ):
                        ok = False
                    else:
                        recorded_image = imgr1
                else:
                    ok = False
            elif globalconfig.get("ocr_auto_method_v2", "period") == "period":
                ok = reset or time.time() - self.lastocrtime > globalconfig.get(
                    "ocr_interval", 1.5
                )
            if not ok:
                if analysis_image is not None:
                    self.savelastimg = analysis_image
                    self.savelastrecimg = recorded_image
                return
        result = ocr_run(imgr)
        with self.range_ui.ocr_source_lock:
            if snapshot != self.range_ui.capture_snapshot():
                return
            if analysis_image is not None:
                self.savelastimg = analysis_image
                self.savelastrecimg = recorded_image
            t = result.textonly
            overlay_enabled = globalconfig.get("ocr_translation_overlay", False)
            overlay_reset = (
                overlay_enabled and self.range_ui._ocr_overlay_original is None
            )
            sim = NativeUtils.distance(self.savelasttext, t)
            if overlay_enabled and (result.error or not t):
                return self._commit_ocr_result(result, snapshot)
            if sim < globalconfig.get("ocr_text_diff", 3) and not overlay_reset:
                self.lastocrtime = time.time()
                self.savelasttext = t
                self._last_capture_rect = snapshot.rect
                return
            return self._commit_ocr_result(result, snapshot)

    def waitforstable(self):
        snapshot = self.range_ui.capture_snapshot()
        rect = QRect(*snapshot.rect)
        if not rect.isValid():
            return False
        imgr = imageCutEx(self.ref.hwnd, rect)
        if imgr.isNull():
            return False
        with self.range_ui.ocr_source_lock:
            if snapshot != self.range_ui.capture_snapshot():
                return False
            imgr1 = cvMat(imgr)
            image_score = imgr1.MSSIM(self.savelastimg)
            gobject.base.thresholdsett1.emit(str(float(image_score)))
            self.savelastimg = imgr1
            return image_score > globalconfig.get("ocr_stable_sim2_v2", 0.95)


class ocrtext(basetext):
    def hwndChanged(self, hwnd):
        self.hwnd = hwnd

    def init(self):
        self.hwnd = None
        self._pause_state = False
        self._overlay_enabled = globalconfig.get("ocr_translation_overlay", False)
        threader(ocr_init)()
        self.ranges: "list[rangemanger]" = []
        self.gettextthread()

    def clearrange(self):
        self.ranges.clear()
        try:
            globalconfig.pop("ocrregions2")
        except:
            pass

    def leaveone(self):
        while len(self.ranges) > 1:
            self.ranges.pop(0)  # 直接[-1:]不知道为什么不work
        if self.ranges:
            self.ranges[0].range_ui.isfocus = False

    def newrangeadjustor(self):
        if len(self.ranges) == 0 or globalconfig.get("multiregion", False):
            self.ranges.append(rangemanger(self, self.ranges))
        return self.ranges[-1]

    def starttrace(self, pos):
        for _r in self.ranges:
            _r.range_ui.starttrace(pos)

    def traceoffset(self, curr):
        for _r in self.ranges:
            _r.range_ui.traceoffsetsignal.emit(curr)

    def setrect(self, rect: QRect):
        self.ranges[-1].range_ui.setrect(rect)

    def setstyle(self, *_):
        enabled = globalconfig.get("ocr_translation_overlay", False)
        if enabled and not self._overlay_enabled:
            for r in self.ranges:
                r.range_ui.invalidate_overlay()
                r.lastocrtime = 0
                r.savelasttext = None
                r.savelastrecimg = None
        self._overlay_enabled = enabled
        [_.range_ui.setstyle() for _ in self.ranges]

    def showhiderangeui(self, b):
        if b and len(self.ranges) == 0:
            for region in globalconfig.get("ocrregions2", []):
                if not region:
                    continue
                self.newrangeadjustor()
                self.setrect(QRect(*region))
            return
        for _ in self.ranges:
            _.range_ui.setmousetransp(False)

            if b:
                _r = _.range_ui.getrect()
                if _r:
                    _.range_ui.setrect(_r)
            else:
                _.range_ui.hide()

    @threader
    def gettextthread(self):
        laststate = tuple((0 for _ in range(len(globalconfig["ocr_trigger_events"]))))
        lastevents = json.dumps(globalconfig["ocr_trigger_events"])
        while not self.ending:
            if self._pause_state:
                time.sleep(0.1)
                continue
            if not self.isautorunning:
                time.sleep(0.1)
                continue
            rs = self.getuseranges()
            if not rs:
                time.sleep(0.1)
                continue
            if globalconfig.get("ocr_auto_method_v2", "period") == "trigger":
                triggered = False
                this = tuple(
                    (
                        windows.GetAsyncKeyState(
                            parsekeystringtomodvkcode(line["vkey"])[1]
                        )
                        for line in globalconfig["ocr_trigger_events"]
                    )
                )
                if lastevents != json.dumps(globalconfig["ocr_trigger_events"]):
                    laststate = this
                    lastevents = json.dumps(globalconfig["ocr_trigger_events"])
                    continue
                for _, line in enumerate(globalconfig["ocr_trigger_events"]):
                    event = line["event"]
                    press = this[_]
                    if ((event == 0) and (laststate[_] == 0) and press) or (
                        (event == 1) and laststate[_] and (press == 0)
                    ):
                        triggered = True
                        break
                laststate = this
                if triggered:
                    if self.hwnd:
                        for _ in range(2):
                            # 切换前台窗口
                            p1 = windows.GetWindowThreadProcessId(self.hwnd)
                            p2 = windows.GetWindowThreadProcessId(
                                windows.GetForegroundWindow()
                            )
                            triggered = p1 == p2
                            if triggered:
                                break
                            time.sleep(0.1)

                if triggered:

                    t1 = time.time()
                    while (not self.ending) and (
                        globalconfig.get("ocr_auto_method_v2", "period") == "trigger"
                    ):
                        time.sleep(0.1)
                        if time.time() - t1 >= globalconfig.get("ocr_trigger_delay", 0):
                            break
                    while (not self.ending) and (
                        globalconfig.get("ocr_auto_method_v2", "period") == "trigger"
                    ):
                        if self.waitforstablex():
                            break
                        time.sleep(0.1)
                    t = self.getallres(False)
                    if t:
                        self.dispatchtext(t)
                time.sleep(0.01)
            else:
                laststate = tuple(
                    (0 for _ in range(len(globalconfig["ocr_trigger_events"])))
                )
                t = self.getallres(True)
                if t:
                    self.dispatchtext(t)
                time.sleep(0.1)

    def waitforstablex(self):
        for range_ui in self.getuseranges():
            if not range_ui.waitforstable():
                return False
        return True

    def getuseranges(self):
        for r in self.ranges:
            if r.range_ui.isfocus:
                return [r]
        return self.ranges

    def getallres(self, auto, region=None):
        if region is not None and (self.ending or region not in self.ranges):
            return
        __text: "list[OCRResultParsed]" = []
        recognized_ranges = []
        active_ranges = [region] if region is not None else list(self.getuseranges())
        independent = len(active_ranges) > 1 and globalconfig.get(
            "ocr_translation_overlay", False
        )
        for r in active_ranges:

            if auto:
                _ = r.getresauto()
            else:
                _ = r.getresmanual()
            if region is not None and (self.ending or region not in self.ranges):
                return
            if _ is None:
                continue
            if globalconfig.get(
                "ocr_translation_overlay", False
            ) and not overlay_source_is_current(_.ocr_overlay_source):
                continue
            if _.error:
                _.displayerror()
                if independent:
                    continue
                return
            __text.append(_)
            recognized_ranges.append(r.range_ui)
        if not __text:
            return
        text = "\n".join(_.textonly for _ in __text)
        if independent:
            sources = []
            for result in __text:
                source = result.ocr_overlay_source
                if not overlay_source_is_current(source):
                    continue
                source.ocr_direct_translation = result.result.isocrtranslate
                # 块级来源（原地按位置绘制）：展开为各块独立翻译
                blocksources = getattr(result, "ocr_overlay_block_sources", None)
                if blocksources:
                    sources.extend(
                        _ for _ in blocksources if overlay_source_is_current(_)
                    )
                else:
                    sources.append(source)
            return OCRRegionBatch(sources) if sources else None
        if (
            globalconfig.get("ocr_translation_overlay", False)
            and len(active_ranges) == 1
            and len(recognized_ranges) == 1
        ):
            # 块级来源（原地按位置绘制）：各块独立翻译
            blocksources = getattr(__text[0], "ocr_overlay_block_sources", None)
            if blocksources:
                valid = [_ for _ in blocksources if overlay_source_is_current(_)]
                if valid:
                    return OCRRegionBatch(valid)
            text = __text[0].ocr_overlay_source
            if not overlay_source_is_current(text):
                return
        if __text[0].result.isocrtranslate:
            gobject.base.displayinfomessage(text, "<notrans>")
        else:
            return text

    def gettextonce(self, region=None):
        return self.getallres(False, region)

    def pause_recognition(self):
        self._pause_state = True

    def resume_recognition(self):
        self._pause_state = False

    def end(self):
        globalconfig["ocrregions2"] = [
            _.range_ui.getrect().getRect() for _ in self.ranges
        ]
        self.ranges.clear()
