 
import json
import os
import warnings

# Third party imports
from  PyQt5.QtCore import QByteArray, QObject, QPoint, QRect, Qt
from  PyQt5.QtGui import (QColor, QFont, QFontDatabase, QIcon, QIconEngine,
                        QPainter, QPixmap, QTransform, QPalette)
from  PyQt5.QtWidgets import QApplication
  

def text_color():
    try:
        palette = QApplication.instance().palette()
        return palette.color(QPalette.Active, QPalette.Text)
    except AttributeError:
        return QColor(50, 50, 50)


def text_color_disabled():
    try:
        palette = QApplication.instance().palette()
        return palette.color(QPalette.Disabled, QPalette.Text)
    except AttributeError:
        return QColor(150, 150, 150)


_default_options = {
    'color': text_color,
    'color_disabled': text_color_disabled,
    'opacity': 1.0,
    'scale_factor': 1.0,
}


def set_global_defaults(**kwargs):
    """Set global defaults for the options passed to the icon painter."""

    valid_options = [
        'active', 'selected', 'disabled', 'on', 'off',
        'on_active', 'on_selected', 'on_disabled',
        'off_active', 'off_selected', 'off_disabled',
        'color', 'color_on', 'color_off',
        'color_active', 'color_selected', 'color_disabled',
        'color_on_selected', 'color_on_active', 'color_on_disabled',
        'color_off_selected', 'color_off_active', 'color_off_disabled',
        'animation', 'offset', 'scale_factor', 'rotated', 'hflip', 'vflip'
        ]

    for kw in kwargs:
        if kw in valid_options:
            _default_options[kw] = kwargs[kw]
        else:
            error = "Invalid option '{0}'".format(kw)
            raise KeyError(error)


class CharIconPainter:

    """Char icon painter."""

    def paint(self, iconic, painter, rect, mode, state, options):
        """Main paint method."""
        for opt in options:
            self._paint_icon(iconic, painter, rect, mode, state, opt)

    def _paint_icon(self, iconic, painter, rect, mode, state, options):
        """Paint a single icon."""
        painter.save()
        color = options['color']
        char = options['char']

        color_options = {
            QIcon.On: {
                QIcon.Normal: (options['color_on'], options['on']),
                QIcon.Disabled: (options['color_on_disabled'],
                                 options['on_disabled']),
                QIcon.Active: (options['color_on_active'],
                               options['on_active']),
                QIcon.Selected: (options['color_on_selected'],
                                 options['on_selected'])
            },

            QIcon.Off: {
                QIcon.Normal: (options['color_off'], options['off']),
                QIcon.Disabled: (options['color_off_disabled'],
                                 options['off_disabled']),
                QIcon.Active: (options['color_off_active'],
                               options['off_active']),
                QIcon.Selected: (options['color_off_selected'],
                                 options['off_selected'])
            }
        }

        color, char = color_options[state][mode]
        alpha = None

        # If color comes as a tuple, it means we need to set alpha on it.
        if isinstance(color, tuple):
            alpha = color[1]
            color = color[0]

        qcolor = QColor(color)
        if alpha:
            qcolor.setAlpha(alpha)

        painter.setPen(qcolor)

        # A 16 pixel-high icon yields a font size of 14, which is pixel perfect
        # for font-awesome. 16 * 0.875 = 14
        # The reason why the glyph size is smaller than the icon size is to
        # account for font bearing.

        draw_size = round(0.875 * rect.height() * options['scale_factor'])
        prefix = options['prefix']

        # Animation setup hook
        animation = options.get('animation')
        if animation is not None:
            animation.setup(self, painter, rect)

        painter.setFont(iconic.font(prefix, draw_size))
        if 'offset' in options:
            rect = QRect(rect)
            rect.translate(round(options['offset'][0] * rect.width()),
                           round(options['offset'][1] * rect.height()))

        if 'vflip' in options and options['vflip'] == True:
            x_center = rect.width() * 0.5
            y_center = rect.height() * 0.5
            painter.translate(x_center, y_center)
            transfrom = QTransform()
            transfrom.scale(1,-1)
            painter.setTransform(transfrom, True)
            painter.translate(-x_center, -y_center)

        if 'hflip' in options and options['hflip'] == True:
            x_center = rect.width() * 0.5
            y_center = rect.height() * 0.5
            painter.translate(x_center, y_center)
            transfrom = QTransform()
            transfrom.scale(-1, 1)
            painter.setTransform(transfrom, True)
            painter.translate(-x_center, -y_center)

        if 'rotated' in options:
            x_center = rect.width() * 0.5
            y_center = rect.height() * 0.5
            painter.translate(x_center, y_center)
            painter.rotate(options['rotated'])
            painter.translate(-x_center, -y_center)

        painter.setOpacity(options.get('opacity', 1.0))

        painter.drawText(rect, int(Qt.AlignCenter | Qt.AlignVCenter), char)
        painter.restore()


class FontError(Exception):
    """Exception for font errors."""


class CharIconEngine(QIconEngine):

    """Specialization of QIconEngine used to draw font-based icons."""

    def __init__(self, iconic, painter, options):
        super().__init__()
        self.iconic = iconic
        self.painter = painter
        self.options = options

    def paint(self, painter, rect, mode, state):
        self.painter.paint(
            self.iconic, painter, rect, mode, state, self.options)

    def pixmap(self, size, mode, state):
        pm = QPixmap(size)
        pm.fill(Qt.transparent)
        self.paint(QPainter(pm), QRect(QPoint(0, 0), size), mode, state)
        return pm


class IconicFont(QObject):

    """Main class for managing iconic fonts."""

    def __init__(self, *args):
        """IconicFont Constructor.

        Parameters
        ----------
        ``*args``: tuples
            Each positional argument is a tuple of 3 or 4 values:
            - The prefix string to be used when accessing a given font set,
            - The ttf font filename,
            - The json charmap filename,
            - Optionally, the directory containing these files. When not
              provided, the files will be looked for in ``./fonts/``.
        """
        super().__init__()
        self.painter = CharIconPainter()
        self.painters = {}
        self.fontname = {}
        self.fontids = {}
        self.charmap = {}
        self.icon_cache = {}
        for fargs in args:
            self.load_font(*fargs)

    def load_font(self, prefix, ttf_filename, charmap_filename, directory=None):
         

        def hook(obj):
            result = {}
            for key in obj:
                try:
                    result[key] = chr(int(obj[key], 16))
                except ValueError:
                    if int(obj[key], 16) > 0xffff:
                        # ignoring unsupported code in Python 2.7 32bit Windows
                        # ValueError: chr() arg not in range(0x10000)
                        pass
                    else:
                        raise FontError(u'Failed to load character '
                                        '{0}:{1}'.format(key, obj[key]))
            return result

        if directory is None:
            directory ='./files/fonts'

        # Load font
        if QApplication.instance() is not None:
            with open(os.path.join(directory, ttf_filename), 'rb') as font_data:
                id_ = QFontDatabase.addApplicationFontFromData(QByteArray(font_data.read()))
            font_data.close()

            loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)

            if loadedFontFamilies:
                self.fontids[prefix] = id_
                self.fontname[prefix] = loadedFontFamilies[0]
            else:
                raise FontError(u"Font at '{0}' appears to be empty. "
                                "If you are on Windows 10, please read "
                                "https://support.microsoft.com/"
                                "en-us/kb/3053676 "
                                "to know how to prevent Windows from blocking "
                                "the fonts that come with QtAwesome.".format(
                                        os.path.join(directory, ttf_filename)))

            with open(os.path.join(directory, charmap_filename), 'r') as codes:
                self.charmap[prefix] = json.load(codes, object_hook=hook)
 

    def icon(self, *names, **kwargs):
        """Return a QIcon object corresponding to the provided icon name."""
        cache_key = '{}{}'.format(names,kwargs) 
        if names and 'fa.' in names[0]:
            warnings.warn(
                "The FontAwesome 4.7 ('fa' prefix) icon set will be "
                "removed in a future release in favor of FontAwesome 6. "
                "We recommend you to move to FontAwesome 5 ('fa5*' prefix) "
                "to prevent any issues in the future",
                DeprecationWarning
            )

        if cache_key not in self.icon_cache:
            options_list = kwargs.pop('options', [{}] * len(names))
            general_options = kwargs

            if len(options_list) != len(names):
                error = '"options" must be a list of size {0}'.format(len(names))
                raise Exception(error)

            if QApplication.instance() is not None:
                parsed_options = []
                for i in range(len(options_list)):
                    specific_options = options_list[i]
                    parsed_options.append(self._parse_options(specific_options,
                                                              general_options,
                                                              names[i]))

                # Process high level API
                api_options = parsed_options

                self.icon_cache[cache_key] = self._icon_by_painter(self.painter, api_options)
            else:
                warnings.warn("You need to have a running "
                              "QApplication to use QtAwesome!")
                return QIcon()
        return self.icon_cache[cache_key]

    def _parse_options(self, specific_options, general_options, name):
        live_dict = {k: v() if callable(v) else v for k, v in _default_options.items()}

        options = dict(live_dict, **general_options)
        options.update(specific_options)

        # Handle icons for modes (Active, Disabled, Selected, Normal)
        # and states (On, Off)
        icon_kw = ['char', 'on', 'off', 'active', 'selected', 'disabled',
                   'on_active', 'on_selected', 'on_disabled', 'off_active',
                   'off_selected', 'off_disabled']
        char = options.get('char', name)
        on = options.get('on', char)
        off = options.get('off', char)
        active = options.get('active', on)
        selected = options.get('selected', active)
        disabled = options.get('disabled', char)
        on_active = options.get('on_active', active)
        on_selected = options.get('on_selected', selected)
        on_disabled = options.get('on_disabled', disabled)
        off_active = options.get('off_active', active)
        off_selected = options.get('off_selected', selected)
        off_disabled = options.get('off_disabled', disabled)

        icon_dict = {'char': char,
                     'on': on,
                     'off': off,
                     'active': active,
                     'selected': selected,
                     'disabled': disabled,
                     'on_active': on_active,
                     'on_selected': on_selected,
                     'on_disabled': on_disabled,
                     'off_active': off_active,
                     'off_selected': off_selected,
                     'off_disabled': off_disabled,
                     }
        names = [icon_dict.get(kw, name) for kw in icon_kw]
        prefix, chars = self._get_prefix_chars(names)
        options.update(dict(zip(*(icon_kw, chars))))
        options.update({'prefix': prefix})

        # Handle colors for modes (Active, Disabled, Selected, Normal)
        # and states (On, Off)
        color = options.get('color')
        options.setdefault('color_on', color)
        options.setdefault('color_active', options['color_on'])
        options.setdefault('color_selected', options['color_active'])
        options.setdefault('color_on_active', options['color_active'])
        options.setdefault('color_on_selected', options['color_selected'])
        options.setdefault('color_on_disabled', options['color_disabled'])
        options.setdefault('color_off', color)
        options.setdefault('color_off_active', options['color_active'])
        options.setdefault('color_off_selected', options['color_selected'])
        options.setdefault('color_off_disabled', options['color_disabled'])

        return options

    def _get_prefix_chars(self, names):
        chars = []
        for name in names:
            if '.' in name:
                prefix, n = name.split('.')
                if prefix in self.charmap:
                    if n in self.charmap[prefix]:
                        chars.append(self.charmap[prefix][n])
                    else:
                        error = 'Invalid icon name "{0}" in font "{1}"'.format(
                            n, prefix)
                        raise Exception(error)
                else:
                    error = 'Invalid font prefix "{0}"'.format(prefix)
                    raise Exception(error)
            else:
                raise Exception('Invalid icon name')

        return prefix, chars

    def font(self, prefix, size):
        """Return a QFont corresponding to the given prefix and size."""
        font = QFont()
        font.setFamily(self.fontname[prefix])
        font.setPixelSize(round(size))
        if prefix[-1] == 's':  # solid style
            font.setStyleName('Solid')
        return font
  
    def _icon_by_painter(self, painter, options):
        """Return the icon corresponding to the given painter."""
        engine = CharIconEngine(self, painter, options)
        return QIcon(engine)


# Constants
_resource = { 'iconic': None }
  
def _instance(): 
     
    if _resource['iconic'] is None:
        _resource['iconic'] = IconicFont(
            ('fa',
             'fontawesome4.7-webfont.ttf',
             'fontawesome4.7-webfont-charmap.json'),
        )
    return _resource['iconic']
 
def icon(*names, **kwargs):
    return _instance().icon(*names, **kwargs)
 