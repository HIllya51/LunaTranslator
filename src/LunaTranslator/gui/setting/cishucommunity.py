import functools, os, hashlib, uuid
import requests, gobject, qtawesome
from qtsymbols import *
from language import Languages
from myutils.config import _TR, dynamiclink, globalconfig, saveallconfig
from myutils.utils import makehtml, stringfyerror
from myutils.proxy import getproxy
from myutils.wrapper import threader
from gui.dynalang import (
    LDialog,
    LPushButton,
    LLabel,
    LTableView,
    LStandardItemModel,
    LStandardItem,
)
from gui.usefulwidget import LinkLabel, getIconButton

CATALOG_URL_PATH = "Resource/CommunityDict"
_COPYED_DIR = "copyed"
_CENTER_COLS = (1, 2, 3, 4)


def _centered(w: QWidget) -> QWidget:
    c = QWidget()
    lay = QHBoxLayout(c)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addStretch(1)
    lay.addWidget(w)
    lay.addStretch(1)
    return c


def _scan_cishu_sha256():
    result = set()
    bases = ["LunaTranslator/cishu", gobject.getconfig(_COPYED_DIR)]
    for base in bases:
        if not os.path.isdir(base):
            continue
        for fn in os.listdir(base):
            if not fn.endswith(".py"):
                continue
            p = os.path.join(base, fn)
            try:
                h = hashlib.sha256()
                with open(p, "rb") as ff:
                    for blk in iter(lambda: ff.read(65536), b""):
                        h.update(blk)
                result.add(h.hexdigest())
            except:
                pass
    return result


def _langdisplay(code):
    if not code:
        return ""
    info = Languages.fromcode(code)
    if not info:
        return code
    return info.zhsname


class CommunityCishuDialog(LDialog):
    catalogloaded = pyqtSignal(object, str)
    downloadfinished = pyqtSignal(int, bool, str, str)

    def __init__(self, parent, oninstalled=None) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("社区辞书")
        self.setWindowIcon(qtawesome.icon("fa.download"))
        self.resize(QSize(720, 420))
        self._entries = []
        self._installed = set()
        self._oninstalled = oninstalled

        form = QVBoxLayout(self)

        top = QHBoxLayout()
        self.status = LLabel("加载中……")
        top.addWidget(self.status, 1)
        top.addWidget(
            getIconButton(callback=self._fetchcatalog, icon="fa.refresh", tips="刷新")
        )
        form.addLayout(top)

        self.table = LTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.model = LStandardItemModel()
        self.table.setModel(self.model)
        self.model.setHorizontalHeaderLabels(
            ["名称", "源语言", "目标语言", "主页", "下载"]
        )
        for _c in _CENTER_COLS:
            h = self.model.horizontalHeaderItem(_c)
            if h:
                h.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Interactive
        )
        self.table.horizontalHeader().resizeSection(3, 100)
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Interactive
        )
        form.addWidget(self.table, 1)

        self.catalogloaded.connect(self._oncatalogloaded)
        self.downloadfinished.connect(self._ondownloadfinished)

        self._fetchcatalog()
        self.show()

    def _fetchcatalog(self):
        self.status.setText("加载中……")
        self._fetchcatalog_safe()

    @threader
    def _fetchcatalog_safe(self):
        try:
            url = dynamiclink(CATALOG_URL_PATH)
            res = requests.get(url, proxies=getproxy(), timeout=15)
            res.raise_for_status()
            entries = res.json()
            if isinstance(entries, dict):
                entries = entries.get("items") or entries.get("list") or []
            if not isinstance(entries, list):
                raise ValueError("bad catalog format")
            entries = [e for e in entries if e.get("name") and e.get("url")]
            self.catalogloaded.emit(entries, "")
        except Exception as e:
            self.catalogloaded.emit(None, stringfyerror(e))

    def _oncatalogloaded(self, entries, error):
        if self.model.rowCount():
            self.model.removeRows(0, self.model.rowCount())
        self._entries = entries or []
        self._installed = _scan_cishu_sha256()
        if error:
            self.status.setText("加载失败")
            return
        self.status.setText("")
        for entry in self._entries:
            self._appendrow(entry)

    def _appendrow(self, entry: dict):
        row = self.model.rowCount()
        src = LStandardItem(_langdisplay(entry.get("srclang")))
        src.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        tgt = LStandardItem(_langdisplay(entry.get("tgtlang")))
        tgt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model.appendRow(
            [
                QStandardItem(entry.get("name") or ""),
                src,
                tgt,
                LStandardItem(""),
                LStandardItem(""),
            ]
        )
        homepage = entry.get("homepage") or ""
        if homepage:
            self.table.setIndexWidget(
                self.model.index(row, 3),
                _centered(LinkLabel(makehtml(homepage))),
            )
        self._set_download_cell(row, entry)

    def _is_downloaded(self, entry):
        sha = entry.get("sha256")
        return bool(sha) and sha.lower() in self._installed

    def _set_download_cell(self, row, entry):
        idx = self.model.index(row, 4)
        if self._is_downloaded(entry):
            w: QWidget = LLabel("已下载")
        else:
            w = LPushButton("下载")
            w.clicked.connect(functools.partial(self._start_download, row))
        self.table.setIndexWidget(idx, _centered(w))
        self._refit_download_column()

    def _refit_download_column(self):
        w = 0
        for r in range(self.model.rowCount()):
            wd = self.table.indexWidget(self.model.index(r, 4))
            if wd is not None:
                try:
                    w = max(w, wd.sizeHint().width())
                except:
                    pass
        if w > 0:
            self.table.horizontalHeader().resizeSection(4, w + 8)

    def _start_download(self, row):
        if not (0 <= row < len(self._entries)):
            return
        entry = self._entries[row]
        idx = self.model.index(row, 4)
        self.table.setIndexWidget(idx, _centered(LLabel("下载中……")))
        self._refit_download_column()
        self._download_safe(row, entry)

    @threader
    def _download_safe(self, row, entry):
        uid = ""
        try:
            url = entry["url"]
            req = requests.get(url, stream=True, proxies=getproxy())
            data = bytearray()
            for _ in req.iter_content(chunk_size=1024 * 32):
                data += _
            content = bytes(data)
            sha = entry.get("sha256")
            if sha and hashlib.sha256(content).hexdigest() != sha.lower():
                raise Exception(_TR("校验失败") + " sha256")
            uid = str(uuid.uuid4())
            target = gobject.getconfig("{}/{}.py".format(_COPYED_DIR, uid))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            tmp = target + ".part"
            with open(tmp, "wb") as ff:
                ff.write(content)
            os.replace(tmp, target)
            self.downloadfinished.emit(row, True, "", uid)
        except Exception as e:
            self.downloadfinished.emit(row, False, stringfyerror(e), uid)

    def _registercishu(self, entry, uid):
        if uid not in globalconfig["cishu"]:
            name = entry.get("name") or uid
            globalconfig["cishu"][uid] = {
                "use": False,
                "name": name,
                "type": entry.get("type", "online"),
                "copyfrom": name,
            }
        saveallconfig()

    def _ondownloadfinished(self, row, succ, failreason, uid):
        if not (0 <= row < self.model.rowCount()):
            return
        if succ:
            if 0 <= row < len(self._entries):
                self._registercishu(self._entries[row], uid)
            self._installed = _scan_cishu_sha256()
            if 0 <= row < len(self._entries):
                self._set_download_cell(row, self._entries[row])
            if self._oninstalled:
                try:
                    self._oninstalled()
                except:
                    pass
        else:
            if 0 <= row < len(self._entries):
                self._set_download_cell(row, self._entries[row])
            QMessageBox.critical(self, _TR("下载失败"), _TR("错误") + "\n" + failreason)
