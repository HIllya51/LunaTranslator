from qtsymbols import *
from myutils.config import globalconfig
from dataclasses import dataclass
import uuid


@dataclass
class datas:
    font_family: str
    font_size: float
    bold: bool
    atcenter: bool
    color: str
    extra_space: float


class base:

    @property
    def config(self):
        return globalconfig["rendertext"]["webview"][self.typename].get("args", {})

    def __init__(self, typename, webview, parent) -> None:
        self.typename = typename
        self.parent = parent
        self.webview = webview

    def gen_html__(
        self, text, font_family, font_size, bold, atcenter, color, extra_space
    ):
        self.data_ = datas(font_family, font_size, bold, atcenter, color, extra_space)
        return self.gen_html(text, self.data_)

    def gen_html(self, text, data: datas):
        raise

    def eval(self, js):
        self.parent.testeval(js)

    def bind(self, name, func):
        self.webview.bind(name, func)

    def measureH(self, font_family, font_size):
        font = QFont(font_family, font_size)
        fmetrics = QFontMetrics(font)

        return fmetrics.height()

    @property
    def line_height(self):
        if self.data_.extra_space == 0:
            return ""
        else:
            return f"line-height: {self.measureH(self.data_.font_family,self.data_.font_size)+self.data_.extra_space}px;"

    @property
    def align(self):
        align = "text-align: center;" if self.data_.atcenter else ""
        return align

    @property
    def fontinfo(self):
        bold = "font-weight: bold;" if self.data_.bold else ""
        fms = f"font-family: {self.data_.font_family};font-size: {self.data_.font_size}pt;"
        return fms + bold

    def getuid(self):
        _id = f"luna_{uuid.uuid4()}"
        return _id

    def makedivstyle(self, _id, inner, style):

        return f'<div id="{_id}">{inner}</div><style>{style}</style>'
