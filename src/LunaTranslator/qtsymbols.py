try:
    from PyQt5 import QtSvg
    from PyQt5.QtWidgets import QFrame,QListView,QCheckBox,QAbstractItemView,QTextEdit,QTableView,QHeaderView,QColorDialog,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMainWindow,QMessageBox,QDialog,QGridLayout,QTextBrowser,QGraphicsDropShadowEffect,QWidget,QScrollArea,QApplication,QPushButton,QSystemTrayIcon,QPlainTextEdit,QAction,QMenu,QFileDialog,QKeySequenceEdit,QLabel,QSpacerItem,QWidgetItem,QLayout,QTextBrowser,QLineEdit,QFormLayout,QSizePolicy,QTabWidget,QTabBar,QSplitter,QListWidget,QListWidgetItem,QHBoxLayout,QVBoxLayout,QSizeGrip,QFontComboBox,QProgressBar,QRadioButton,QButtonGroup,QSlider,QToolTip,QGroupBox,QGraphicsOpacityEffect,QStackedWidget,QStyledItemDelegate,QStyleOptionViewItem,QFontDialog,QTreeView,QToolButton,QAbstractSpinBox,QStylePainter,QStyleOptionComboBox,QStyle
    from PyQt5.QtGui import QIconEngine,QIntValidator,QStandardItem,QStandardItemModel,QImageWriter,QIcon,QTextCharFormat,QTextBlockFormat,QResizeEvent,QTextCursor,QFontMetricsF,QMouseEvent,QImage,QPainter,QRegion,QCloseEvent,QFontDatabase,QKeySequence,QPixmap,QCursor,QColor,QFont,QPen,QPainterPath,QBrush,QFontMetrics,QShowEvent,QWheelEvent,QPaintEvent,QTextLayout, QTextOption,QDragEnterEvent, QDropEvent,QTransform,QKeyEvent,QInputMethodEvent,QValidator,QRegExpValidator,QPalette
    from PyQt5.QtCore import QObject,pyqtSignal,Qt,QSize,QByteArray,QBuffer,QPointF,QPoint,QRect,QEvent,QModelIndex,QTimer,QRectF,QVariantAnimation,QUrl,QPropertyAnimation,QLocale,QSignalBlocker,QMargins,QRegExp,QSizeF
    isqt5 = True
    class LineHeightTypes:
        LineDistanceHeight=QTextBlockFormat.LineHeightTypes.LineDistanceHeight
        FixedHeight=QTextBlockFormat.LineHeightTypes.FixedHeight
except:
    #from traceback import print_exc
    #print_exc()
    from PyQt6 import QtSvg
    from PyQt6.QtWidgets import QFrame,QListView,QCheckBox,QAbstractItemView,QTextEdit,QTableView,QHeaderView,QColorDialog,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMainWindow,QMessageBox,QDialog,QGridLayout,QTextBrowser,QGraphicsDropShadowEffect,QWidget,QScrollArea,QApplication,QPushButton,QSystemTrayIcon,QPlainTextEdit,QMenu,QFileDialog,QKeySequenceEdit,QLabel,QSpacerItem,QWidgetItem,QLayout,QTextBrowser,QLineEdit,QFormLayout,QSizePolicy,QTabWidget,QTabBar,QSplitter,QListWidget,QListWidgetItem,QHBoxLayout,QVBoxLayout,QSizeGrip,QFontComboBox,QProgressBar,QRadioButton,QButtonGroup,QSlider,QToolTip,QGroupBox,QGraphicsOpacityEffect,QStackedWidget,QTreeView,QToolButton,QAbstractSpinBox,QStyledItemDelegate,QStyleOptionViewItem,QFontDialog,QStylePainter,QStyleOptionComboBox,QStyle
    from PyQt6.QtGui import QIconEngine,QIntValidator,QAction,QStandardItem,QStandardItemModel,QImageWriter,QIcon,QTextCharFormat,QTextBlockFormat,QResizeEvent,QTextCursor,QFontMetricsF,QMouseEvent,QImage,QPainter,QRegion,QCloseEvent,QFontDatabase,QKeySequence,QPixmap,QCursor,QColor,QFont,QPen,QPainterPath,QBrush,QFontMetrics,QShowEvent,QWheelEvent,QPaintEvent,QTextLayout, QTextOption,QKeyEvent,QInputMethodEvent,QValidator,QDragEnterEvent,QDropEvent,QTransform,QRegularExpressionValidator,QPalette
    from PyQt6.QtCore import QObject,pyqtSignal,Qt,QSize,QByteArray,QBuffer,QPointF,QPoint,QRect,QEvent,QModelIndex,QTimer,QRectF,QVariantAnimation,QUrl,QPropertyAnimation,QLocale,QMargins,QSignalBlocker,QRegularExpression,QSizeF
    isqt5 = False

    class LineHeightTypes:
        LineDistanceHeight=QTextBlockFormat.LineHeightTypes.LineDistanceHeight.value
        FixedHeight=QTextBlockFormat.LineHeightTypes.FixedHeight.value

    QRegExp=QRegularExpression
    QRegExpValidator=QRegularExpressionValidator