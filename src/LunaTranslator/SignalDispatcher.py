from qtsymbols import QObject, pyqtSignal, pyqtBoundSignal, QImage
import functools
from traceback import print_exc


class SignalDispatcher(QObject):

    safeinvokefunction = pyqtSignal(object)
    setimage = pyqtSignal(QImage)
    setresult = pyqtSignal(object)
    voicelistsignal = pyqtSignal(object)
    portconflict = pyqtSignal(str)
    thresholdsett2 = pyqtSignal(str)
    thresholdsett1 = pyqtSignal(str)
    progresssignal2 = pyqtSignal(str, int)
    progresssignal3 = pyqtSignal(int)
    progresssignal4 = pyqtSignal(str, int)
    versiontextsignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__cachesignal: "dict[pyqtBoundSignal, tuple]" = {}
        self.__connect_internal(self.portconflict)
        self.__connect_internal(self.thresholdsett1)
        self.__connect_internal(self.thresholdsett2)
        self.__connect_internal(self.voicelistsignal)
        self.__connect_internal(self.setresult)
        self.__connect_internal(self.setimage)
        self.safeinvokefunction.connect(self.__safeinvoke)
        self.__connect_internal(self.progresssignal2)
        self.__connect_internal(self.progresssignal3)
        self.__connect_internal(self.progresssignal4)
        self.__connect_internal(self.versiontextsignal)

    def connectsignal(self, signal: pyqtBoundSignal, callback):
        if signal in self.__cachesignal:
            signal.disconnect()
            callback(*self.__cachesignal[signal])
        signal.connect(callback)

    def __connect_internal(self, signal: pyqtBoundSignal):
        signal.connect(functools.partial(self.__connect_internal_1, signal))

    def __connect_internal_1(self, signal, *arg):
        self.__cachesignal[signal] = arg

    def __safeinvoke(self, fobj):
        try:
            fobj()
        except:
            print_exc()
