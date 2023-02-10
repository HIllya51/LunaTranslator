r"""
qtawesome
=========

Font-Awesome and other iconic fonts for PyQt / PySide applications.

.. currentmodule:: qtawesome

.. autosummary::
   :toctree: _generate

   icon
   load_font
   charmap
   font
   set_defaults
"""

# Third party imports
from unicodedata import name
from PyQt5 import QtCore, QtWidgets, QtGui

from .iconic_font import IconicFont, set_global_defaults

# Constants
_resource = { 'iconic': None }
 
def has_valid_font_ids(inst):
    """Validate instance's font ids are loaded to QFontDatabase.

    It is possible that QFontDatabase was reset or QApplication was recreated
    in both cases it is possible that font is not available.
    """
    # Check stored font ids are still available
    for font_id in inst.fontids.values():
        font_families = QtGui.QFontDatabase.applicationFontFamilies(
            font_id
        )
        if not font_families:
            return False
    return True


def _instance():
    """
    Return the singleton instance of IconicFont.

    Functions ``icon``, ``load_font``, ``charmap``, ``font`` and
    ``set_defaults`` all rebind to methods of the singleton instance of IconicFont.
    """
    if (
        _resource['iconic'] is not None
        and not has_valid_font_ids(_resource['iconic'])
    ):
        # Reset cached instance
        _resource['iconic'] = None

    if _resource['iconic'] is None:
        _resource['iconic'] = IconicFont(
            ('fa',
             'fontawesome4.7-webfont.ttf',
             'fontawesome4.7-webfont-charmap.json'),
        )
    return _resource['iconic']


def reset_cache():
    if _resource['iconic'] is not None:
        _resource['iconic'].icon_cache = {}


def icon(*names, **kwargs):
    #print(names)
    """
    Return a QIcon object corresponding to the provided icon name(s).

    This function is the main interface of qtawesome.

    It can be used to create a QIcon instance from a single glyph
    or from a list of glyphs that are displayed on the top of each other.
    Such icon stacks are generally used to combine multiple glyphs to make
    more complex icons.

    Glyph names are specified by strings, of the form ``prefix.name``.
    The ``prefix`` corresponds to the font to be used and ``name`` is the
    name of the icon.

     - The prefix corresponding to Font-Awesome 4.x is 'fa'
     - The prefix corresponding to Font-Awesome 5.x (regular) is 'fa5'
     - The prefix corresponding to Font-Awesome 5.x (solid) is 'fa5s'
     - The prefix corresponding to Font-Awesome 5.x (brands) is 'fa5b'
     - The prefix corresponding to Elusive-Icons is 'ei'
     - The prefix corresponding to Material-Design-Icons 5.x is 'mdi'
     - The prefix corresponding to Material-Design-Icons 6.x is 'mdi6'
     - The prefix corresponding to Phosphor is 'ph'
     - The prefix corresponding to Remix-Icon is 'ri'
     - The prefix corresponding to Microsoft's Codicons is 'msc'

    When requesting a single glyph, options (such as color or positional offsets)
    can be passed as keyword arguments::

        import qtawesome as qta

        music_icon = qta.icon(
            'fa5s.music',
            color='blue',
            color_active='orange')

    When requesting multiple glyphs, the `options` keyword argument contains
    the list of option dictionaries to be used for each glyph::

        camera_ban = qta.icon('fa5s.camera', 'fa5s.ban', options=[{
                'scale_factor': 0.5,
                'active': 'fa5s.balance-scale'
            }, {
                'color': 'red',
                'opacity': 0.7
            }])

    Qt's ``QIcon`` object has four modes

        - ``Normal``: The user is not interacting with the icon, but the
          functionality represented by the icon is available.
        - ``Disabled``: The functionality corresponding to the icon is not
          available.
        - ``Active``: The functionality corresponding to the icon is available.
          The user is interacting with the icon, for example, moving the mouse
          over it or clicking it.
        - ``Selected``: The item represented by the icon is selected.

    The glyph for the Normal mode is the one specified with the main positional
    argument.

     - ``color``: icon color in the ``Normal`` mode.

    The following four options will apply to the icon regardless of the mode.

     - ``offset``: tuple (x, y) corresponding to the horizontal and vertical
       offsets for the glyph, specified as a proportion of the icon size.
     - ``animation``: animation object for the icon.
     - ``scale_factor``: multiplicative scale factor to be used for the glyph.

    The following options apply to the different modes of the icon

     - ``active``: name of the glyph to be used when the icon is ``Active``.
     - ``color_active``: the corresponding icon color.

     - ``disabled``: name of the glyph to be used when the icon is ``Disabled``.
     - ``color_disabled``: the corresponding icon color.

     - ``selected``: name of the glyph to be used when the icon is ``Selected``.
     - ``color_selected``: the corresponding icon color.

    Default values for these options can be specified via the function
    ``set_defaults``. If unspecified, the default defaults are::

        {
            'opacity': 1.0,
            'scale_factor': 1.0
            'color': QColor(50, 50, 50),
            'color_disabled': QColor(150, 150, 150),
        }

    If no default value is provided for ``active``, ``disabled`` or ``selected``
    the glyph specified for the ``Normal`` mode will be used.

    """
    return _instance().icon(*names, **kwargs)


def load_font(prefix, ttf_filename, charmap_filename, directory=None):
    """
    Loads a font file and the associated charmap.

    If ``directory`` is None, the files will be looked for in ``./fonts/``.

    Parameters
    ----------
    prefix: str
        Prefix string to be used when accessing a given font set
    ttf_filename: str
        Ttf font filename
    charmap_filename: str
        Character map filename
    directory: str or None, optional
        Directory for font and charmap files

    Example
    -------
    The spyder ide uses qtawesome and uses a custom font for spyder-specific
    icons::

        qta.load_font('spyder', 'spyder.ttf', 'spyder-charmap.json')

    """
    return _instance().load_font(prefix, ttf_filename, charmap_filename, directory)


def charmap(prefixed_name):
    """
    Return the character map used for a given font.

    Returns
    -------
    return_value: dict
        The dictionary mapping the icon names to the corresponding unicode character.

    """
    prefix, name = prefixed_name.split('.')
    return _instance().charmap[prefix][name]


def font(prefix, size):
    """
    Return the font corresponding to the specified prefix.

    This can be used to render text using the iconic font directly::

        import qtawesome as qta
        from qtpy import QtWidgets

        label = QtWidgets.QLabel(unichr(0xf19c) + ' ' + 'Label')
        label.setFont(qta.font('fa', 16))

    Parameters
    ----------
    prefix: str
        prefix string of the loaded font
    size: int
        size for the font

    """
    return _instance().font(prefix, size)


def set_defaults(**kwargs):
    """
    Set default options for icons.

    The valid keyword arguments are:

    'active', 'animation', 'color', 'color_active', 'color_disabled',
    'color_selected', 'disabled', 'offset', 'scale_factor', 'selected'.

    """
    return set_global_defaults(**kwargs)


class IconWidget(QtWidgets.QLabel):
    """
    IconWidget gives the ability to display an icon as a widget

    if supports the same arguments as icon()
    for example
    music_icon = qta.IconWidget('fa5s.music',
                                color='blue',
                                color_active='orange')

    it also have setIcon() and setIconSize() functions
    """

    def __init__(self, *names, **kwargs):
        super().__init__(parent=kwargs.get('parent'))
        self._icon = None
        self._size = QtCore.QSize(16, 16)
        self.setIcon(icon(*names, **kwargs))

    def setIcon(self, _icon):
        """
        set a new icon()

        Parameters
        ----------
        _icon: qtawesome.icon
            icon to set
        """
        self._icon = _icon
        self.setPixmap(_icon.pixmap(self._size))

    def setIconSize(self, size):
        """
        set icon size

        Parameters
        ----------
        size: QtCore.QSize
            size of the icon
        """
        self._size = size

    def update(self, *args, **kwargs):
        if self._icon:
            self.setPixmap(self._icon.pixmap(self._size))
        return super().update(*args, **kwargs)
