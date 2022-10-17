from PyQt5.QtCore import *
from PyQt5.QtGui import  *
from PyQt5.QtWidgets import *
import sys


class Window(QWidget) :
    def __init__(self) :
        super().__init__()
        self.setWindowTitle("QTextEdit - PyQt5中文网")
        self.resize(600, 500)
        self.func_list()

    def func_list(self) :
        self.func()


    def func(self) :
        self.qte = QTextEdit('111', self)
        self.qte.move(100, 100)
        self.qte.resize(250, 250)
        self.qte.setStyleSheet('background-color:green')
        self.qte.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.qte.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.qte.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.btn = QPushButton('按  钮', self)
        self.btn.move(120, 50)
        self.btn.resize(70, 30)
        self.btn.pressed.connect(self.text_cur)

    # ==============内容设置=============== # 代码分割线 - 开始

    # 文本光标完成内容和格式设置
    def text_cur(self) :
        # 文本光标设置合并格式
        # setBlockCharFormat
        # setBlockFormat
        # setCharFormat
        # mergeBlockCharFormat
        # mergeBlockFormat
        # mergeCharFormat

        qtc = self.qte.textCursor()
        tcf = QTextCharFormat()
        tcf.setFontPointSize(50)
        qtc.setBlockCharFormat(tcf)  # 设置块内字符格式

        # qtc.setBlockFormat(tcf)  # 设置块格式，传入对象QTextBlockFormat
        # qtc.setCharFormat(tcf)  # 设置选中字符格式，传入对象QTextCharFormat

        # 以下三个可以实现格式的合并，同时调用两种格式,接个172和173行测试
        # qtc.mergeBlockCharFormat(tcf)  # 合并当前块的字符格式，传入对象QTextCharFormat
        # qtc.mergeBlockFormat(tcf)  # 合并当前块格式，传入对象QTextBlockFormat

        tcf2 = QTextCharFormat()
        tcf2.setFontStrikeOut(True)
        # qtc.mergeCharFormat(tcf2)  # 合并当前字符格式，传入对象QTextCharFormat，上面设置好的格式和这段代码中设置的格式可以叠加展现

        # 获取内容和格式
        qtc = self.qte.textCursor()
        qtc.block()  # 获取光标所在文本块
        qtc.block().text()  # 获取光标所在文本块的文本内容
        qtc.block().blockNumber()  # 获取光标所在文本块的段落编号

        # 文本的选中和清除
        qtc = self.qte.textCursor()
        # qtc.setPosition(3)
        # qtc.setPosition(3, QTextCursor.KeepAnchor)
        qtc.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor, 1)
        qtc.select(QTextCursor.BlockUnderCursor)
        self.qte.setTextCursor(qtc)
        self.qte.setFocus()
        # 获取文本选中的内容
        qtc.selectedText()  # 获取当前选中文本内容
        qtc.selection()  # 获取当前选中文本文档
        qtc.selectedTableCells()  # 获取当前选中表格
        # 选中位置获取
        qtc.selectionStart()  # 获取光标起始和结束的位置
        qtc.clearSelection()  # 取消选中文本，需要反向设置光标
        self.qte.setTextCursor(qtc)  # 取消选中文本，需要反向设置光标
        # 选中文本移除
        qtc.removeSelectedText()

        # 删除内容，不必要选中
        qtc = self.qte.textCursor()
        qtc.deleteChar()  # 删除一个字符，光标后面的字符，如果有选中文本，直接删除选中文本
        qtc.deletePreviousChar()  # 删除一个字符，光标前面的字符，如果有选中文本，直接删除选中文本

        # 文本光标的位置获取
        qtc = self.qte.textCursor()
        qtc.atBlockEnd()  # 判断光标是否在段落结尾,相对于文本快
        qtc.atEnd()  # 判断光标是否在文档结尾,相对于文档
        qtc.columnNumber()  # 在第几列
        qtc.positionInBlock()  # 咋子文本快中的位置
        '''

        # 开始和结束编辑标识
        qtc = self.qte.textCursor()
        QTextCursor
        QTextCharFormat
        qtc.beginEditBlock()
        qtc.insertText('aaa')
        qtc.insertBlock()  # 类似于换行
        qtc.insertText('bbb')
        qtc.insertBlock()
        qtc.insertText('ccc')
        qtc.insertBlock()
        qtc.endEditBlock()
        qtc.insertText('ddd')
        qtc.insertBlock()

        '''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(app.exec_())
