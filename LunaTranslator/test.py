import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QWidget, QTableView, QAbstractItemView, QLabel, QVBoxLayout


class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.resize(650, 300)

        self.model = QStandardItemModel(6, 2, self)            # 1
        # self.model = QStandardItemModel(self)
        # self.model.setColumnCount(6)
        # self.model.setRowCount(6)

        for row in range(6):                                   # 2
            for column in range(2):
                item = QStandardItem('({}, {})'.format(row, column))
                self.model.setItem(row, column, item)
        self.model.setHorizontalHeaderLabels([ ("")])
        self.item_list = [QStandardItem('(6, {})'.format(column)) for column in range(2)]
        self.model.appendRow(self.item_list)                   # 3

        self.item_list = [QStandardItem('(7, {})'.format(column)) for column in range(2)]
        self.model.insertRow(7, self.item_list)                # 4

        self.table = QTableView(self)                          # 5
        self.table.setModel(self.model)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.clicked.connect(self.show_info)

        self.info_label = QLabel(self)                         # 6
        self.info_label.setAlignment(Qt.AlignCenter)

        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.table)
        self.v_layout.addWidget(self.info_label)
        self.setLayout(self.v_layout)

    def show_info(self):                                       # 7
        row = self.table.currentIndex().row()
        column = self.table.currentIndex().column()
        print('({}, {})'.format(row, column))

        data = self.table.currentIndex().data()
        self.info_label.setText(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())