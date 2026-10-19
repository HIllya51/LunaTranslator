import time, json, os
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
import gobject

from qtsymbols import *
from textio.textsource.textsourcebase import basetext
from ocrengines.baseocrclass import OCRResultParsed
from CVUtils import cvMat
from traceback import print_exc


def _hwnd_imageCut(hwnd, rectX: QRect, curr=-1):
    """hwnd 截图，并归一化到选区物理尺寸。curr 同 imageCut（0 仅 HWND、
    1 仅桌面、-1 自动兜底）。

    目标窗口的 DPI 与本软件不同时（典型：DPI 不感知的老游戏在高分屏
    上，GetDC 的 GDI 虚拟化返回低密度位图——像素数少于屏幕物理像素），
    OCR 块坐标与原地显示的字号/位置换算（物理像素 / 覆盖层 DPR）会
    整体偏小。统一缩放到选区物理尺寸，恢复 1:1 对应。
    返回值同 imageCut：hwnd 时 (succ, img)，否则 img。"""
    img = imageCut(hwnd, rectX, curr)
    if not hwnd:
        return img
    succ, img = img
    if (
        succ
        and not img.isNull()
        and rectX.width() > 0
        and rectX.height() > 0
        and (
            abs(img.width() - rectX.width()) > 1
            or abs(img.height() - rectX.height()) > 1
        )
    ):
        img = img.scaled(
            rectX.width(),
            rectX.height(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    return succ, img


def imageCutEx(hwnd, rectX: QRect):
    if hwnd:
        # 先只试 HWND 截图（不隐藏/不排除任何窗口）：GetDC(hwnd)
        # +BitBlt 只截该窗口自身内容，覆盖层与本程序窗口都不在画面里
        # ——成功时无需守卫、也无需因窗口遮挡而暂停（与系统版本无关，
        # 菜单展开同理）。失败（如 DirectX 全屏黑屏）时才走下方守卫
        # 路径：截图瞬间临时排除覆盖层（排除失败才隐藏），然后 仅落桌面。
        succ, img = _hwnd_imageCut(hwnd, rectX, curr=0)
        if succ and not img.isNull():
            return _ocrpreprocess(img)
    img = capture_without_overlays(
        lambda: _hwnd_imageCut(hwnd, rectX, curr=1), rectX)
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
        # 桌面截图兜底：主窗口若压在选区上，白化遮挡部分，避免把
        # 自己的界面识别进去
        rect2 = windows.GetWindowRect(gobject.base.translation_ui.winid)
        rect = QRect(rect2[0], rect2[1], rect2[2] - rect2[0], rect2[3] - rect2[1])
        if rectX.intersected(rect):
            rect.translate(-rectX.x(), -rectX.y())
            painter = QPainter(img)
            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)
            painter.end()
    return _ocrpreprocess(img)


def _ocrpreprocess(img: QImage):
    if globalconfig.get("use_ocr_preprocess", False):
        try:
            img = checkmd5reloadmodule(
                gobject.getconfig("ocr_preprocess.py"), "ocr_preprocess"
            ).Process(img)
        except:
            print_exc()
    return img


def _attach_overlay_sources(result, range_ui, revision, owner, blocks_enabled):
    """把识别结果挂上原地显示来源并发布布局（范围框与单次OCR容器共用）：
    整框来源恒有；块级来源（原地按位置绘制）仅在 blocks_enabled（且
    有坐标、非图片翻译）时按块拆分。"""
    result.ocr_overlay_source = OCRRegionText(
        result.textonly, range_ui, revision, owner=owner
    )
    result.ocr_overlay_block_sources = None
    blocks = None
    if blocks_enabled and result.result.hasboxs and not result.result.isocrtranslate:
        # 布局发布用完整四点（保留倾斜），覆盖层据此旋转绘制
        blocks = [tuple(_.box) for _ in result.result.blocks]
        sources = [
            OCRRegionText(
                _.text, range_ui, revision, owner=owner, block_index=i
            )
            for i, _ in enumerate(result.result.blocks)
            if _.text and _.text.strip()
        ]
        if sources:
            result.ocr_overlay_block_sources = sources
    range_ui.publish_overlay_layout(revision, blocks)


def _flatten_overlay_sources(result):
    """单条识别结果 → 原地显示来源列表：块级来源优先展开，无则整框
    一条；来源过期（选区已变）返回空。"""
    source = result.ocr_overlay_source
    if not overlay_source_is_current(source):
        return []
    source.ocr_direct_translation = result.result.isocrtranslate
    blocksources = getattr(result, "ocr_overlay_block_sources", None)
    if blocksources:
        return [_ for _ in blocksources if overlay_source_is_current(_)]
    return [source]


class rangemanger:
    def __init__(self, ref: "ocrtext", ranges: "list[rangemanger]"):
        self.ref = ref
        # 不挂父窗口：挂隐藏的设置窗口时，主窗口原生最小化会连带
        # 隐藏范围框（Windows 对 owner 链的处理）；无主窗口不受影响
        self.range_ui = rangeadjust(None, ranges)
        self.savelastimg: cvMat = None
        self.savelastrecimg: cvMat = None
        self.lastocrtime: float = 0
        self.savelasttext: str = None
        self._last_capture_rect = None

    def __del__(self):
        self.range_ui.closesignal.emit()

    def _capture_region(self, img=None):
        """选区截图（getresmanual/getresauto/waitforstable 公共开场）：
        返回 (snapshot, img)；选区无效或截图失败返回 (None, None)。
        img 给定时（框选完成时的触发图）直接使用，仅做 OCR 预处理。"""
        snapshot = self.range_ui.capture_snapshot()
        rect = QRect(*snapshot.rect)
        if not rect.isValid():
            return None, None
        if img is None:
            # 绑定窗口优先。未绑定时仅原地显示翻译开启才探测选区下唯一
            # 不透明窗口（完全盖住选区、其下窗口都不可见 → 等价绑定，
            # 覆盖层与本程序窗口都不在其 DC 里，无需隐藏；也避开录屏/
            # 其他窗口的干扰）；普通 OCR 直接落桌面，不做窗口探测
            hwnd = self.ref.hwnd
            if hwnd is None and globalconfig.get("ocr_translation_overlay", False):
                hwnd = NativeUtils.find_sole_opaque_window(
                    *rect.getCoords(), os.getpid()
                )
            img = imageCutEx(hwnd, rect)
            if img.isNull():
                return None, None
        else:
            if img.isNull():
                return None, None
            img = _ocrpreprocess(img)
        return snapshot, img

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
            # 块级来源（原地按位置绘制）：全局开关开启且未出错时，每个
            # OCR 结果区域（合并临近行之后）各自翻译、各回各自位置；
            # 否则整框一条译文（见 OCRTranslationOverlay）。
            _attach_overlay_sources(
                result, self.range_ui, revision, owner=self.ref,
                blocks_enabled=(
                    globalconfig.get("ocr_translation_overlay", False)
                    and not result.error
                ),
            )
            return result

    def getresmanual(self, img=None):
        snapshot, img = self._capture_region(img)
        if snapshot is None:
            return
        if snapshot != self.range_ui.capture_snapshot():
            return
        result = ocr_run(img)
        return self._commit_ocr_result(result, snapshot, img)

    def getresauto(self):
        snapshot, imgr = self._capture_region()
        if snapshot is None:
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
        snapshot, imgr = self._capture_region()
        if snapshot is None:
            return False
        with self.range_ui.ocr_source_lock:
            if snapshot != self.range_ui.capture_snapshot():
                return False
            imgr1 = cvMat(imgr)
            image_score = imgr1.MSSIM(self.savelastimg)
            gobject.base.thresholdsett1.emit(str(float(image_score)))
            self.savelastimg = imgr1
            return image_score > globalconfig.get("ocr_stable_sim2_v2", 0.95)


class ocrbox(rangeadjust):
    """单次OCR右键的常驻容器：与 OCR 范围框同款的边框样式，识别一次
    框内内容并在框内原地显示翻译（不轮询更新）；任意鼠标键一碰即关闭
    （无拖动/缩放）。不受 OCR 设置里 原地显示翻译 开关控制。"""

    def __init__(self, rect: QRect, img: QImage):
        self._boxranges = []
        super().__init__(None, self._boxranges)
        self._closing = False
        self.translation_overlay.display_always = True
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        # 不需要拖动/缩放：隐藏全部手柄，任何点击都用于关闭
        for grip in list(self.cornerGrips) + list(self.sideGrips):
            grip.hide()
        self.setrect(rect)
        # 框选完成时立即截好的图：识别必须用它——稍后再截的话画面可能
        # 已经变了（动画/翻页），就不再是用户框选时看到的内容
        self._img = img
        threader(self.__recognize)()

    def __recognize(self):
        try:
            if self._closing:
                return
            self.__recognize_once()
        except RuntimeError:
            pass  # 窗口已销毁（用户已点击关闭）
        except:
            print_exc()

    def __recognize_once(self):
        result = ocr_run(_ocrpreprocess(self._img))
        if result.error:
            # OCR 出错：报错到主窗口，并清掉容器里的旧译文
            with self.ocr_source_lock:
                if self._closing:
                    return
                revision = self.remember_overlay_source("")
                self.publish_overlay_layout(revision, None)
            gobject.base.displayinfomessage(
                result.errorstring(), "<msg_error_Origin>")
            return
        text = result.textonly
        with self.ocr_source_lock:
            if self._closing:
                return
            revision = self.remember_overlay_source(text)
            # 块级原地显示：有坐标且非图片翻译时按块拆分（不受全局
            # 开关控制，display_always）
            _attach_overlay_sources(
                result, self, revision, owner=None, blocks_enabled=True
            )
        if not text:
            return
        if result.result.isocrtranslate:
            gobject.base.displayinfomessage(
                result.ocr_overlay_source, "<notrans>"
            )
        elif result.ocr_overlay_block_sources:
            gobject.base.textgetmethod(
                OCRRegionBatch(result.ocr_overlay_block_sources),
                is_auto_run=False,
            )
        else:
            gobject.base.textgetmethod(
                result.ocr_overlay_source, is_auto_run=False
            )

    @property
    def _mousetransp(self):
        # 点击即关的容器不参与鼠标穿透（否则内部点击会穿到游戏）
        return False

    def closebox(self):
        self._closing = True
        try:
            self.invalidate_overlay()
            self.close()
        finally:
            self.deleteLater()

    def mousePressEvent(self, e):
        # 任意键一碰即关（不进入父类的拖动逻辑）
        self.closebox()


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
        # 原地显示翻译模式下，隐藏范围框 = 仅藏边框（宽度视作 0），框与
        # 原地译文保持可见；其余模式仍整框隐藏
        hideborder = (not b) and globalconfig.get("ocr_translation_overlay", False)
        for _ in self.ranges:
            if b:
                _r = _.range_ui.getrect()
                if _r:
                    _.range_ui.setrect(_r)
            _.range_ui.set_border_hidden(hideborder)
            if not b and not hideborder:
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

    def getallres(self, auto, region=None, img=None):
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
                # img：框选触发图，只给对应区域的首次识别用
                _ = r.getresmanual(img if r is region else None)
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
                # 块级来源（原地按位置绘制）：展开为各块独立翻译
                sources.extend(_flatten_overlay_sources(result))
            return OCRRegionBatch(sources) if sources else None
        if (
            globalconfig.get("ocr_translation_overlay", False)
            and len(active_ranges) == 1
            and len(recognized_ranges) == 1
        ):
            # 块级来源（原地按位置绘制）：各块独立翻译
            sources = _flatten_overlay_sources(__text[0])
            if sources:
                return OCRRegionBatch(sources)
            return
        if __text[0].result.isocrtranslate:
            gobject.base.displayinfomessage(text, "<notrans>")
        else:
            return text

    def gettextonce(self, region=None, img=None):
        return self.getallres(False, region, img)

    def pause_recognition(self):
        self._pause_state = True

    def resume_recognition(self):
        self._pause_state = False

    def end(self):
        globalconfig["ocrregions2"] = [
            _.range_ui.getrect().getRect() for _ in self.ranges
        ]
        self.ranges.clear()
