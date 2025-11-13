from myutils.config import globalconfig, ocrsetting, ocrerrorfix, _TR
from myutils.commonbase import commonbase
from language import Languages
from myutils.utils import qimage2binary
import re, gobject, math, time
from qtsymbols import *


def _sort_text_lines(boxs, texts, vertical, space: str):

    mids = [((box[0] + box[2]) / 2, (box[1] + box[3]) / 2) for box in boxs]
    ranges = [((box[0], box[2]), (box[1], box[3])) for box in boxs]
    juhe: "list[list]" = []
    passed = []
    mids_idx = not vertical
    for i in range(len(boxs)):
        ls = [i]
        if i in passed:
            continue
        for j in range(i + 1, len(boxs)):
            if j in passed:
                continue

            if (
                mids[i][mids_idx] > ranges[j][mids_idx][0]
                and mids[i][mids_idx] < ranges[j][mids_idx][1]
                and mids[j][mids_idx] > ranges[i][mids_idx][0]
                and mids[j][mids_idx] < ranges[i][mids_idx][1]
            ):
                passed.append(j)
                ls.append(j)
        juhe.append(ls)

    for i in range(len(juhe)):
        juhe[i].sort(key=lambda x: mids[x][1 - mids_idx])
    juhe.sort(key=lambda x: mids[x[0]][mids_idx], reverse=vertical)
    lines = []
    for _j in juhe:
        lines.append(space.join([texts[_] for _ in _j]))
    return lines


def box8to4(box):
    if len(box) == 4:
        return box
    return (
        min([box[i * 2] for i in range(len(box) // 2)]),
        min([box[i * 2 + 1] for i in range(len(box) // 2)]),
        max([box[i * 2] for i in range(len(box) // 2)]),
        max([box[i * 2 + 1] for i in range(len(box) // 2)]),
    )


def box4to8(box):
    if len(box) == 8:
        return box
    x1, y1, x2, y2 = box
    return (x1, y1, x2, y1, x2, y2, x1, y2)


class _OCRBlockS:
    def __init__(self, blocks: "list[OCRBlock]"):
        self.blocks = blocks

    def distance(self, blocks: "_OCRBlockS"):
        mindis = 9999999
        for block1 in self.blocks:
            for block2 in blocks.blocks:
                mindis = min(mindis, block1.distance(block2))
        return mindis

    @property
    def whmin(self):
        _ = tuple(_.whmin for _ in self.blocks)
        return sum(_) / len(_)

    def merge(self, box: "_OCRBlockS"):
        self.blocks.extend(box.blocks)

    @staticmethod
    def four_point_box_union(aabb1, aabb2):

        x_min = min(aabb1[0], aabb2[0])
        y_min = min(aabb1[1], aabb2[1])
        x_max = max(aabb1[2], aabb2[2])
        y_max = max(aabb1[3], aabb2[3])

        return [x_min, y_min, x_max, y_max]

    def asblock(self, vertical, space: str):
        texts = _sort_text_lines(
            list(_.box4 for _ in self.blocks),
            list(_.text for _ in self.blocks),
            vertical,
            space,
        )
        box0 = self.blocks[0].box4
        for i in range(1, len(self.blocks)):
            box0 = self.four_point_box_union(box0, self.blocks[i].box4)
        return OCRBlock(text=space.join(texts), box=box0)


class OCRBlock:
    def __init__(self, text: str, box: list = None):
        if box:
            box = box4to8(box)
        self.box = box
        self.text = text

    @property
    def box4(self):
        if not self.box:
            return
        return box8to4(self.box)

    @property
    def json(self):
        _ = dict(text=self.text)
        if self.box:
            (x1, y1, x2, y1, x2, y2, x1, y2) = self.box
            box = [
                dict(x=x1, y=y1),
                dict(x=x2, y=y1),
                dict(x=x2, y=y2),
                dict(x=x1, y=y2),
            ]
            _.update(box=box)
        return _

    @property
    def whmin(self):
        box = self.box4
        return min(box[2] - box[0], box[3] - box[1])

    def distance(self, box2: "OCRBlock"):
        box1 = self.box4
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2.box4

        # 检查是否有重叠
        if (
            x1_min <= x2_max
            and x1_max >= x2_min
            and y1_min <= y2_max
            and y1_max >= y2_min
        ):
            return 0  # 有重叠，距离为0

        # 计算水平方向距离
        if x1_max < x2_min:  # box1在box2左边
            dx = x2_min - x1_max
        elif x2_max < x1_min:  # box1在box2右边
            dx = x1_min - x2_max
        else:  # x轴有重叠
            dx = 0

        # 计算垂直方向距离
        if y1_max < y2_min:  # box1在box2下面
            dy = y2_min - y1_max
        elif y2_max < y1_min:  # box1在box2上面
            dy = y1_min - y2_max
        else:  # y轴有重叠
            dy = 0

        # 计算欧几里得距离
        distance = math.sqrt(dx**2 + dy**2)
        return distance


class OCRResult:
    @property
    def texts(self):
        return (_.text for _ in self.blocks)

    def __init__(
        self, texts: "str|list[str]" = None, boxs: list = None, isocrtranslate=False
    ):
        if isinstance(texts, str):
            texts = [texts]
        elif isinstance(texts, (tuple, list)):
            pass
        else:
            texts = []
        self.hasboxs = bool(boxs)
        self.blocks: "list[OCRBlock]" = []
        for i in range(len(texts)):
            self.blocks.append(OCRBlock(texts[i], boxs[i] if boxs else None))
        self.isocrtranslate = isocrtranslate

        vertical = int(globalconfig["verticalocr"])
        if self.hasboxs:
            if vertical == 2:
                vertical = self.__guessvertial(self.blocks)
            else:
                vertical = vertical != 0
        self.vertical = bool(vertical)

    def parse(self, space, scale):
        if not self:
            return
        if self.blocks and scale != 1:
            for block in self.blocks:
                block.box = tuple(_ / scale for _ in block.box)
        if globalconfig["ocrmergelines"] and self.hasboxs:
            self.__nearmergeboxs(space)

    def __bool__(self):
        return bool(self.blocks)

    @property
    def json(self):
        _ = dict(results=tuple(_.json for _ in self.blocks))
        if self.isocrtranslate:
            _.update(isocrtranslate=self.isocrtranslate)

        if self.vertical:
            _.update(vertical=self.vertical)
        return _

    def __guessvertial(self, res: "list[OCRBlock]"):
        whs = 1
        for _ in res:
            x1, y1, x2, y2 = _.box4
            w = x2 - x1
            h = y2 - y1
            if h == 0 or w == 0:
                continue
            whs *= w / h
        return whs < 1

    def __nearmergeboxs(self, space: str):
        blocksX = list(_OCRBlockS([_]) for _ in self.blocks)
        while True:
            found = self.__findnear(blocksX)
            if not found:
                break
            i, j = found
            blocksX[i].merge(blocksX.pop(j))
        self.blocks.clear()
        for _ in blocksX:
            self.blocks.append(_.asblock(self.vertical, space))

    def __findnear(self, blocksX: "list[_OCRBlockS]"):
        for i in range(len(blocksX)):
            box1 = blocksX[i]
            for j in range(i + 1, len(blocksX)):
                box2 = blocksX[j]
                if box1.distance(box2) <= globalconfig["ocrmergelines_distance"] * min(
                    box1.whmin, box2.whmin
                ):
                    return i, j


class OCRResultParsed:
    @property
    def json(self):
        info = {}
        if self.engine:
            info.update(
                engine=dict(
                    id=self.engine, name=_TR(globalconfig["ocr"][self.engine]["name"])
                )
            )
        if self.error:
            info.update(error=self.error)
            return info
        info.update(self.result.json)
        to = self.textonly
        if to:
            info.update(text=to)
        if self.timecost:
            info.update(timecost=self.timecost)
        return info

    def errorstring(self):
        return (
            (_TR(globalconfig["ocr"][self.engine]["name"]) + " ") if self.engine else ""
        ) + self.error

    def displayerror(self):
        gobject.base.displayinfomessage(self.errorstring(), "<msg_error_Origin>")

    def maybeerror(self):
        if self.result.isocrtranslate:
            gobject.base.displayinfomessage(self.textonly, "<notrans>")
        elif self.error:
            gobject.base.displayinfomessage(self.errorstring(), "<msg_error_Origin>")
        else:
            return self.textonly

    @property
    def space(self):
        return self.srclang_1.space

    ############################################################

    def _100_f(self, line):
        if ocrerrorfix["use"] == False:
            return line
        filters: "list[str]" = ocrerrorfix["args"]["替换内容"]
        for fil in filters:
            if fil == "":
                continue
            else:
                if fil.isascii():
                    line = re.sub(r"\b{}\b".format(re.escape(fil)), fil, line)
                else:
                    line = line.replace(fil, filters[fil])
        return line

    def __bool__(self):
        return bool(self.result)

    def __init__(
        self,
        result: "str | list[str] | OCRResult" = None,
        srclang_1: Languages = None,
        error=None,
        engine=None,
        scale=1,
        timecost=None,
    ):
        self.timecost = timecost
        self.engine = engine
        self.error = error
        if not isinstance(result, OCRResult):
            result = OCRResult(result)
        self.srclang_1 = srclang_1
        self.result = result
        if result:
            result.parse(self.space, scale)

    @property
    def textonly(self):
        if not self.result:
            return ""
        if not self.result.hasboxs:
            textonly = "\n".join((_.text for _ in self.result.blocks))
        else:
            textonly = "\n".join(
                _sort_text_lines(
                    list(_.box4 for _ in self.result.blocks),
                    list(_.text for _ in self.result.blocks),
                    self.result.vertical,
                    self.space,
                )
            )
        if self.result.isocrtranslate:
            return textonly
        return self._100_f(textonly)


class baseocr(commonbase):
    def langmap(self):
        return {}

    def init(self):
        pass

    def ocr(self, imagebinary) -> "str | list[str] | OCRResult":
        raise Exception()

    required_image_format = "PNG"
    required_mini_height = 0
    required_mini_width = 0

    ############################################################

    _globalconfig_key = "ocr"
    _setting_dict = ocrsetting

    def flatten4point(self, boxs):
        return [
            [
                box[0][0],
                box[0][1],
                box[1][0],
                box[1][1],
                box[2][0],
                box[2][1],
                box[3][0],
                box[3][1],
            ]
            for box in boxs
        ]

    ########################################################
    def raise_cant_be_auto_lang(self):
        if self.is_src_auto:
            raise Exception(_TR("当前OCR引擎不支持设置语言为自动"))

    def __init__(self, typename):
        super().__init__(typename)
        self.level2init()

    def level2init(self):
        self.needinit = True
        try:
            self.init()
        except Exception as e:
            raise e
        self.needinit = False

    def _private_ocr(self, qimage: QImage):
        if self.needinit:
            self.level2init()
        try:
            scale = 1
            if (
                qimage.height() < self.required_mini_height
                or qimage.width() < self.required_mini_width
            ):
                scaleH = self.required_mini_height / qimage.height()
                scaleW = self.required_mini_width / qimage.width()
                if scaleW > scaleH:
                    qimage = qimage.scaledToWidth(
                        self.required_mini_width,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    scale = scaleW
                else:
                    scale = scaleH
                    qimage = qimage.scaledToHeight(
                        self.required_mini_height,
                        Qt.TransformationMode.SmoothTransformation,
                    )
            required_image_format: str = self.required_image_format
            if required_image_format == QImage:
                image = qimage
            else:
                image = qimage2binary(qimage, required_image_format)
            if not image:
                return OCRResultParsed()
            t = time.time()
            result = self.multiapikeywrapper(self.ocr)(image)
            return OCRResultParsed(
                result,
                srclang_1=self.srclang_1,
                engine=self.typename,
                scale=scale,
                timecost=time.time() - t,
            )
        except Exception as e:
            self.needinit = True
            raise e
