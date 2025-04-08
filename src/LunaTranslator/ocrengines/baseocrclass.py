from myutils.config import globalconfig, ocrsetting, ocrerrorfix, _TR, isascii
from myutils.commonbase import commonbase
from language import Languages
import re, gobject


class OCRResult:
    def __init__(
        self, texts: "str|list[str]" = None, boxs: list = None, isocrtranslate=False
    ):
        if isinstance(texts, str):
            texts = [texts]
        elif isinstance(texts, (tuple, list)):
            pass

        if boxs:
            # 对齐box成4点格式
            for i, box in enumerate(boxs):
                if len(box) == 8:
                    continue
                x1, y1, x2, y2 = box
                boxs[i] = (x1, y1, x2, y1, x2, y2, x1, y2)
        self.boxs = boxs
        self.texts = texts
        self.isocrtranslate = isocrtranslate

    def __bool__(self):
        return bool(self.texts)


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
        if self.texts:
            info.update(texts=self.texts)
        if self.boxs:
            info.update(boxs=self.boxs)
        to = self.textonly
        if to:
            info.update(text=to)
        if self.isocrtranslate:
            info.update(isocrtranslate=self.isocrtranslate)
        return info

    def errorstring(self):
        return (
            (_TR(globalconfig["ocr"][self.engine]["name"]) + " ") if self.engine else ""
        ) + self.error

    def displayerror(self):
        gobject.baseobject.displayinfomessage(self.errorstring(), "<msg_error_Origin>")

    def maybeerror(self):
        if self.isocrtranslate:
            gobject.baseobject.displayinfomessage(self.textonly, "<notrans>")
        elif self.error:
            gobject.baseobject.displayinfomessage(
                self.errorstring(), "<msg_error_Origin>"
            )
        else:
            return self.textonly

    @property
    def space(self):
        if globalconfig["ocrmergelines"] == False:
            space = "\n"
        else:
            space = self.space_1
        return space

    @property
    def space_1(self):
        return self.srclang_1.space

    ############################################################
    def __guessvertial(self, boxs):
        whs = 1
        for x1, y1, x2, y2 in boxs:
            w = x2 - x1
            h = y2 - y1
            if h == 0 or w == 0:
                continue
            whs *= w / h
        return whs < 1

    def _100_f(self, line):
        if ocrerrorfix["use"] == False:
            return line
        filters = ocrerrorfix["args"]["替换内容"]
        for fil in filters:
            if fil == "":
                continue
            else:
                if isascii(fil):
                    line = re.sub(r"\b{}\b".format(re.escape(fil)), fil, line)
                else:
                    line = line.replace(fil, filters[fil])
        return line

    def __sort_text_lines(self, boxs, texts):
        vertical = int(globalconfig["verticalocr"])

        def norm48(box):
            return (
                min([box[i * 2] for i in range(len(box) // 2)]),
                min([box[i * 2 + 1] for i in range(len(box) // 2)]),
                max([box[i * 2] for i in range(len(box) // 2)]),
                max([box[i * 2 + 1] for i in range(len(box) // 2)]),
            )

        boxs = [norm48(box) if len(box) == 8 else box for box in boxs]

        if vertical == 2:
            vertical = self.__guessvertial(boxs)
        else:
            vertical = vertical != 0
        # print(list(zip(boxs,texts)))

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
            lines.append(self.space_1.join([texts[_] for _ in _j]))
        return lines

    def __bool__(self):
        return bool(self.texts)

    def __init__(
        self,
        result: "str | list[str] | OCRResult" = None,
        srclang_1: Languages = None,
        error=None,
        engine=None,
    ):
        self.engine = engine
        self.error = error
        if not isinstance(result, OCRResult):
            result = OCRResult(result)
        boxs = result.boxs
        texts = result.texts
        self.srclang_1 = srclang_1
        self.isocrtranslate = result.isocrtranslate
        self.boxs = boxs
        self.texts = texts

    @property
    def textonly(self):
        if not self.texts:
            return ""
        if not self.boxs:
            textonly = self.space.join(self.texts)
        else:
            textonly = self.space.join(self.__sort_text_lines(self.boxs, self.texts))
        if self.isocrtranslate:
            return textonly
        return self._100_f(textonly)


class baseocr(commonbase):
    def langmap(self):
        return {}

    def init(self):
        pass

    def ocr(self, imagebinary) -> "str | list[str] | OCRResult":
        raise Exception()

    ############################################################

    required_image_format = "PNG"

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

    def _private_ocr(self, imagebinary):
        if self.needinit:
            self.level2init()
        try:
            result = self.multiapikeywrapper(self.ocr)(imagebinary)
            return OCRResultParsed(result, srclang_1=self.srclang_1, engine=self.typename)
        except Exception as e:
            self.needinit = True
            raise e
