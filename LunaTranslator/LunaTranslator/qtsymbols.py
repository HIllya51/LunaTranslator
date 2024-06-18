try:
    from PyQt5 import QtSvg
    from PyQt5.QtWidgets import QFrame,QListView,QCheckBox,QAbstractItemView,QTextEdit,QTableView,QHeaderView,QColorDialog,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMainWindow,QMessageBox,QDialog,QGridLayout,QTextBrowser,QGraphicsDropShadowEffect,QWidget,QSizePolicy,QScrollArea,QApplication,QPushButton,QSystemTrayIcon,QPlainTextEdit,QAction,QMenu,QFileDialog,QKeySequenceEdit,QLabel,QSpacerItem,QWidgetItem,QLayout,QTextBrowser,QLineEdit,QFormLayout,QSizePolicy,QTabWidget,QTabBar,QSplitter,QListWidget,QListWidgetItem,QHBoxLayout,QVBoxLayout,QSizeGrip,QFontComboBox,QProgressBar,QRadioButton,QButtonGroup,QSlider,QToolTip,QGroupBox
    from PyQt5.QtGui import QIconEngine,QIntValidator,QStandardItem,QStandardItemModel,QImageWriter,QIcon,QTextCharFormat,QTextBlockFormat,QResizeEvent,QTextCursor,QFontMetricsF,QMouseEvent,QImage,QPainter,QRegion,QCloseEvent,QFontDatabase,QKeySequence,QPixmap,QCursor,QColor,QFont,QPen,QPainterPath,QBrush,QFontMetrics,QShowEvent,QWheelEvent
    from PyQt5.QtCore import QObject,pyqtSignal,Qt,QSize,QByteArray,QBuffer,QPointF,QPoint,QRect,QEvent,QModelIndex,QTimer
    isqt5 = True
except:
    #from traceback import print_exc
    #print_exc()
    from PyQt6 import QtSvg
    from PyQt6.QtWidgets import QFrame,QListView,QCheckBox,QAbstractItemView,QTextEdit,QTableView,QHeaderView,QColorDialog,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMainWindow,QMessageBox,QDialog,QGridLayout,QTextBrowser,QGraphicsDropShadowEffect,QWidget,QSizePolicy,QScrollArea,QApplication,QPushButton,QSystemTrayIcon,QPlainTextEdit,QMenu,QFileDialog,QKeySequenceEdit,QLabel,QSpacerItem,QWidgetItem,QLayout,QTextBrowser,QLineEdit,QFormLayout,QSizePolicy,QTabWidget,QTabBar,QSplitter,QListWidget,QListWidgetItem,QHBoxLayout,QVBoxLayout,QSizeGrip,QFontComboBox,QProgressBar,QRadioButton,QButtonGroup,QSlider,QToolTip,QGroupBox
    from PyQt6.QtGui import QIconEngine,QIntValidator,QAction,QStandardItem,QStandardItemModel,QImageWriter,QIcon,QTextCharFormat,QTextBlockFormat,QResizeEvent,QTextCursor,QFontMetricsF,QMouseEvent,QImage,QPainter,QRegion,QCloseEvent,QFontDatabase,QKeySequence,QPixmap,QCursor,QColor,QFont,QPen,QPainterPath,QBrush,QFontMetrics,QShowEvent,QWheelEvent
    from PyQt6.QtCore import QObject,pyqtSignal,Qt,QSize,QByteArray,QBuffer,QPointF,QPoint,QRect,QEvent,QModelIndex,QTimer
    isqt5 = False