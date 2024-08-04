from myutils.config import globalconfig, ocrsetting, ocrerrorfix
from myutils.commonbase import commonbase


class baseocr(commonbase):
    def langmap(self):
        return {}

    def initocr(self):
        pass

    def ocr(self, imagebinary):
        raise Exception

    def end(self):
        pass

    ############################################################

    @property
    def space(self):
        if globalconfig["ocrmergelines"] == False:
            space = "\n"
        elif self.srclang_1 in ["zh", "ja", "cht"]:
            space = ""
        else:
            space = " "
        return space

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

    def guessvertial(self, boxs):
        whs = 1
        for x1, y1, x2, y2 in boxs:
            w = x2 - x1
            h = y2 - y1
            whs *= w / h
        return whs < 1

    def common_solve_text_orientation(self, boxs, texts):
        vertical = globalconfig["verticalocr"]

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
            lines.append(" ".join([texts[_] for _ in _j]))
        return self.space.join(lines)

    ########################################################
    def level2init(self):
        self.needinit = True
        try:
            self.initocr()
        except Exception as e:
            raise e
        self.needinit = False

    def _private_ocr(self, imagebinary):
        if self.needinit:
            self.level2init()
        try:
            text = self.ocr(imagebinary)
            if text is None:
                text = ""
        except Exception as e:
            self.needinit = True
            raise e
        return self._100_f(text)

    def _100_f(self, line):
        if ocrerrorfix["use"] == False:
            return line
        filters = ocrerrorfix["args"]["替换内容"]
        for fil in filters:
            if fil == "":
                continue
            else:
                line = line.replace(fil, filters[fil])
        return line
