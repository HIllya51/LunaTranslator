from PyQt5.QtCore import QFile, QTextStream
from . import breeze_resources


def stylesheet():
    file = QFile(":/dark/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    return stream.readAll()
