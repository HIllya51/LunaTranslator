try:
    # from traceback import print_exc
    # print_exc()
    # fmt:off
    from PyQt5.QtSvg import QSvgWidget,QSvgRenderer
    from PyQt5.QtWidgets import QFrame,QListView,QCheckBox,QAbstractItemView,QTextEdit,QTableView,QHeaderView,QColorDialog,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMainWindow,QMessageBox,QDialog,QGridLayout,QTextBrowser,QGraphicsDropShadowEffect,QWidget,QScrollArea,QApplication,QPushButton,QSystemTrayIcon,QPlainTextEdit,QAction,QMenu,QFileDialog,QKeySequenceEdit,QLabel,QSpacerItem,QWidgetItem,QLayout,QTextBrowser,QLineEdit,QFormLayout,QSizePolicy,QTabWidget,QTabBar,QSplitter,QListWidget,QListWidgetItem,QHBoxLayout,QVBoxLayout,QSizeGrip,QFontComboBox,QProgressBar,QRadioButton,QButtonGroup,QSlider,QToolTip,QGroupBox,QGraphicsOpacityEffect,QStackedWidget,QStyledItemDelegate,QStyleOptionViewItem,QFontDialog,QTreeView,QToolButton,QAbstractSpinBox,QStylePainter,QStyleOptionComboBox,QStyle,QAbstractButton,QBoxLayout,QShortcut,QAbstractScrollArea,QInputDialog,QStyleOptionGroupBox,QInputDialog,QDateTimeEdit
    from PyQt5.QtGui import QIconEngine,QIntValidator,QStandardItem,QStandardItemModel,QImageWriter,QIcon,QTextCharFormat,QTextBlockFormat,QResizeEvent,QTextCursor,QFontMetricsF,QMouseEvent,QImage,QPainter,QRegion,QCloseEvent,QFontDatabase,QKeySequence,QPixmap,QCursor,QColor,QFont,QPen,QPainterPath,QBrush,QFontMetrics,QShowEvent,QWheelEvent,QPaintEvent,QTextLayout, QTextOption,QDragEnterEvent, QDropEvent,QTransform,QKeyEvent,QInputMethodEvent,QValidator,QRegularExpressionValidator,QPalette,QDoubleValidator,QSyntaxHighlighter,QContextMenuEvent,QScreen
    from PyQt5.QtCore import QObject,pyqtSignal,Qt,QSize,QByteArray,QBuffer,QPointF,QPoint,QRect,QEvent,QModelIndex,QTimer,QRectF,QVariantAnimation,QUrl,QPropertyAnimation,QLocale,QSignalBlocker,QMargins,QRegularExpression,QSizeF,QEasingCurve,QMimeData,pyqtBoundSignal,QDateTime
    # fmt:on
    isqt5 = True


except:
    # fmt:off
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtSvgWidgets import QSvgWidget
    from PyQt6.QtWidgets import QFrame,QListView,QCheckBox,QAbstractItemView,QTextEdit,QTableView,QHeaderView,QColorDialog,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMainWindow,QMessageBox,QDialog,QGridLayout,QTextBrowser,QGraphicsDropShadowEffect,QWidget,QScrollArea,QApplication,QPushButton,QSystemTrayIcon,QPlainTextEdit,QMenu,QFileDialog,QKeySequenceEdit,QLabel,QSpacerItem,QWidgetItem,QLayout,QTextBrowser,QLineEdit,QFormLayout,QSizePolicy,QTabWidget,QTabBar,QSplitter,QListWidget,QListWidgetItem,QHBoxLayout,QVBoxLayout,QSizeGrip,QFontComboBox,QProgressBar,QRadioButton,QButtonGroup,QSlider,QToolTip,QGroupBox,QGraphicsOpacityEffect,QStackedWidget,QTreeView,QToolButton,QAbstractSpinBox,QStyledItemDelegate,QStyleOptionViewItem,QFontDialog,QStylePainter,QStyleOptionComboBox,QStyle,QAbstractButton,QBoxLayout,QAbstractScrollArea,QInputDialog,QStyleOptionGroupBox,QInputDialog,QDateTimeEdit
    from PyQt6.QtGui import QIconEngine,QIntValidator,QAction,QStandardItem,QStandardItemModel,QImageWriter,QIcon,QTextCharFormat,QTextBlockFormat,QResizeEvent,QTextCursor,QFontMetricsF,QMouseEvent,QImage,QPainter,QRegion,QCloseEvent,QFontDatabase,QKeySequence,QPixmap,QCursor,QColor,QFont,QPen,QPainterPath,QBrush,QFontMetrics,QShowEvent,QWheelEvent,QPaintEvent,QTextLayout, QTextOption,QKeyEvent,QInputMethodEvent,QValidator,QDragEnterEvent,QDropEvent,QTransform,QRegularExpressionValidator,QPalette,QDoubleValidator,QSyntaxHighlighter,QContextMenuEvent,QShortcut,QScreen
    from PyQt6.QtCore import QObject,pyqtSignal,Qt,QSize,QByteArray,QBuffer,QPointF,QPoint,QRect,QEvent,QModelIndex,QTimer,QRectF,QVariantAnimation,QUrl,QPropertyAnimation,QLocale,QMargins,QSignalBlocker,QRegularExpression,QSizeF,QEasingCurve,QMimeData,pyqtBoundSignal,QDateTime
    # fmt:on
    isqt5 = False