from myutils.config import globalconfig, ocrsetting, ocrerrorfix, _TR, isascii
from myutils.commonbase import commonbase
import re


class baseocr(commonbase):
    def langmap(self):
        return {}

    def init(self):
        pass

    def ocr(self, imagebinary):
        raise Exception()

    ############################################################

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

    def guessvertial(self, boxs):
        whs = 1
        for x1, y1, x2, y2 in boxs:
            w = x2 - x1
            h = y2 - y1
            if h == 0 or w == 0:
                continue
            whs *= w / h
        return whs < 1

    def sort_text_lines(self, boxs, texts):
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
            vertical = self.guessvertial(boxs)
        else:
            vertical = vertical != 0
        # print(list(zip(boxs,texts)))

        mids = [((box[0] + box[2]) / 2, (box[1] + box[3]) / 2) for box in boxs]
        ranges = [((box[0], box[2]), (box[1], box[3])) for box in boxs]
        juhe = []
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
            text = self.multiapikeywrapper(self.ocr)(imagebinary)
        except Exception as e:
            self.needinit = True
            raise e

        if isinstance(text, str):
            text = {"text": [text]}
        elif isinstance(text, (tuple, list)):
            text = {"text": text}
        elif not text:
            return
        boxs = text.get("box")
        texts = text.get("text")
        if not boxs:
            # 若无标注，则合并显示
            boxs = [[0, 0, 0, 0, 0, 0, 0, 0]]
            textonly = self.space.join(texts)
            texts = ["\n".join(texts)]
        else:
            textonly = self.space.join(self.sort_text_lines(boxs, texts))
            # 对齐box成4点格式
            for i, box in enumerate(boxs):
                if len(box) == 8:
                    continue
                x1, y1, x2, y2 = box
                boxs[i] = (x1, y1, x2, y1, x2, y2, x1, y2)
        textonly = self._100_f(textonly)
        text = {
            "box": boxs,
            "text": texts,
            "textonly": textonly,
            "isocrtranslate": text.get("isocrtranslate", False),
        }
        return text

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
