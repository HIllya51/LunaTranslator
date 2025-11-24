from qtsymbols import *
import gobject, os
import qtawesome, NativeUtils, functools, json
from myutils.config import globalconfig, _TR
from myutils.utils import get_time_stamp
from gui.usefulwidget import closeashidewindow, WebviewWidget
from gui.dynalang import LAction
from urllib.parse import quote
from myutils.wrapper import threader
from traceback import print_exc
import time

class TransHistSearch(WebviewWidget):
    def __init__(self, parent):
        super().__init__(parent, loadext=False)
        self.bind("copyTranslation", self.copy_translation)
        self.bind("editRecord", self.edit_record)
        self.bind("deleteRecord", self.delete_record)
        self.bind("requestHistoryData", self.request_history_data)
        self.loadex()
    
    def loadex(self, extra=None):
        basepath = r"LunaTranslator\htmlcode\uiwebview\transhistsearch.html"
        return os.path.abspath(basepath)
    
    def copy_translation(self, translation):
        NativeUtils.ClipBoard.text = translation
        self.show_message(_TR("已复制到剪贴板"))
    
    def edit_record(self, record_id, original, translation, api, timestamp):
        # TODO: Implement edit record functionality
        pass
    
    def delete_record(self, record_id):
        # TODO: Implement delete record functionality
        pass
    
    def request_history_data(self):
        # Get all history records from gobject.base.transhis.trace
        history_data = []
        for i, line in enumerate(gobject.base.transhis.trace):
            if line[0] == 0:
                # Original text
                timestamp, original = line[1]
                history_data.append({
                    "id": i,
                    "type": "original",
                    "original": original,
                    "translation": "",
                    "api": "",
                    "timestamp": timestamp
                })
            elif line[0] == 1:
                # Translation
                timestamp, api, translation = line[1]
                # Find the corresponding original text
                original = ""
                for j in range(i-1, -1, -1):
                    if gobject.base.transhis.trace[j][0] == 0:
                        original = gobject.base.transhis.trace[j][1][1]
                        break
                history_data.append({
                    "id": i,
                    "type": "translation",
                    "original": original,
                    "translation": translation,
                    "api": api,
                    "timestamp": timestamp
                })
        
        # Send data to WebView
        self.eval(f"loadHistoryData({json.dumps(history_data)});")
    
    def show_message(self, message):
        self.eval(f"showMessage('{message}');")

class TransHistSearchWindow(closeashidewindow):
    def __init__(self, parent):
        super().__init__(parent, globalconfig.get("hist_search_geo", ""))
        self.setWindowTitle(_TR("翻译历史检索"))
        self.setWindowIcon(qtawesome.icon("fa.search"))
        self.trans_hist_search = TransHistSearch(self)
        self.setCentralWidget(self.trans_hist_search)
    
    def closeEvent(self, event):
        # Save window geometry
        globalconfig["hist_search_geo"] = self.saveGeometry().data().hex()
        super().closeEvent(event)