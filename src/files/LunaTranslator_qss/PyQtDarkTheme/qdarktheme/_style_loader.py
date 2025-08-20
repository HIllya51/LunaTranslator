"""Module for loading style data for Qt."""

import json

from qdarktheme import __version__, _resources
from qdarktheme._template import filter
from qdarktheme._template.engine import Template
from qdarktheme._util import get_cash_root_path



def _color_values(theme):
    try:
        return json.loads(_resources.colors.THEME_COLOR_VALUES[theme])
    except KeyError:
        raise ValueError('invalid argument, not a dark, light or auto: "{}"'.format(theme)) from None


def _mix_theme_colors(custom_colors, theme):
    colors = {id: color for id, color in custom_colors.items() if isinstance(color, str)}
    custom_colors_with_theme = custom_colors.get("[{}]".format(theme))
    if isinstance(custom_colors_with_theme, dict):
        colors.update(custom_colors_with_theme)
    elif isinstance(custom_colors_with_theme, str):
        raise ValueError(
            "invalid value for argument custom_colors, not a dict type: "
            '"{}" of "[{}]" key.'.format(custom_colors_with_theme, theme)
        )
    return colors


def _marge_colors(
    color_values, custom_colors, theme
):
    for color_id, color in _mix_theme_colors(custom_colors, theme).items():
        try:
            parent_key, *child_keys = color_id.split(">")
            color_value = color_values[parent_key]
            if len(child_keys) > 1 or (isinstance(color_value, str) and len(child_keys) != 0):
                raise KeyError

            if isinstance(color_value, str):
                color_values[parent_key] = color
            else:
                child_key = "base" if len(child_keys) == 0 else child_keys[0]
                color_value[child_key]  # Check if child_key exists.
                color_value[child_key] = color
        except KeyError:
            raise KeyError('invalid color id for argument custom_colors: "{}".'.format(color_id)) from None


def load_stylesheet(
    theme = "dark",
    corner_shape = "rounded",
    custom_colors = None,
    default_theme = "dark",
) -> str:
    """Load the style sheet which looks like flat design. There are `dark` and `light` theme.

    Args:
        theme: The theme name. There are `dark`, `light` and `auto`.
            If ``auto``, try to detect your OS's theme and accent (accent is only on Mac).
            If failed to detect OS's theme, use the default theme set in argument ``default_theme``.
            When primary color(``primary``) or primary child colors
            (such as ``primary>selection.background``) are set to custom_colors,
            disable to detect the accent.
        corner_shape: The corner shape. There are `rounded` and `sharp` shape.
        custom_colors: The custom color map. Overrides the default color for color id you set.
            Also you can customize a specific theme only. See example 6.
        default_theme: The default theme name.
            The theme set by this argument will be used when system theme detection fails.

    Raises:
        ValueError: If the arguments of this method is wrong.
        KeyError: If the color id of custom_colors is wrong.

    Returns:
        The stylesheet string for the given arguments.

    Examples:
        Set stylesheet to your Qt application.

        1. Dark Theme ::

            app = QApplication([])
            app.setStyleSheet(qdarktheme.load_stylesheet())
            # or
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))

        2. Light Theme ::

            app = QApplication([])
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))

        3. Automatic detection of system theme ::

            app = QApplication([])
            app.setStyleSheet(qdarktheme.load_stylesheet("auto"))

        4. Sharp corner ::

            # Change corner shape to sharp.
            app = QApplication([])
            app.setStyleSheet(qdarktheme.load_stylesheet(corner_shape="sharp"))

        5. Customize color ::

            app = QApplication([])
            app.setStyleSheet(qdarktheme.load_stylesheet(custom_colors={"primary": "#D0BCFF"}))

        6. Customize a specific theme only ::

            app = QApplication([])
            app.setStyleSheet(
                qdarktheme.load_stylesheet(
                    theme="auto",
                    custom_colors={
                        "[dark]": {
                            "primary": "#D0BCFF",
                        }
                    },
                )
            )
    """
    color_values = _color_values(theme)
    if corner_shape not in ("rounded", "sharp"):
        raise ValueError('invalid argument, not a rounded or sharp: "{}"'.format(corner_shape))

    if custom_colors is not None:
        _marge_colors(color_values, custom_colors, theme)
    try:
        get_cash_root_path(__version__).mkdir(parents=True, exist_ok=True)
    except:
        pass

    stylesheet = _resources.stylesheets.TEMPLATE_STYLESHEET
    try:
        from qdarktheme.qtpy.QtCore import QCoreApplication

        app = QCoreApplication.instance()
        if app is not None and not app.property("_qdarktheme_use_setup_style"):
            stylesheet += _resources.stylesheets.TEMPLATE_STANDARD_ICONS_STYLESHEET
    except Exception:  # noqa: PIE786
        pass

    # Build stylesheet
    template = Template(
        stylesheet,
        {"color": filter.color, "corner": filter.corner, "env": filter.env, "url": filter.url},
    )
    replacements = dict(color_values, **{"corner-shape": corner_shape})
    return template.render(replacements)
