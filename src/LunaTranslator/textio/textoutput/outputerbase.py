from myutils.config import globalconfig
from threading import Thread
from queue import Queue


class Base:
    @property
    def config(self):
        return globalconfig["textoutputer"][self.classname]

    @property
    def using(self):
        return self.config["use"]

    def dispatch(self, text:str, isorigin:bool):
        pass

    def init(self):
        pass

    def __init__(self, classname):
        self.classname = classname
        self.queue = Queue()
        self.init()
        Thread(target=self.dothread).start()

    def dothread(self):
        while True:
            text, isorigin = self.queue.get()
            self.dispatch(text, isorigin)

    def puttask(self, text, isorigin):
        if not self.using:
            return
        self.queue.put((text, isorigin))
