"""Module for color code."""

import colorsys
import math


def _round_float(number, decimal_points = 3) -> float:
    decimal = 10**decimal_points
    return round(number * decimal) / decimal


class _RGBA:
    """Class handling RGBA color code."""

    def __init__(self, r, g, b, a = 1) -> None:
        """Initialize rgba value.

        Args:
            r: Red(0~255).
            g: Green(0~255).
            b: Blue(0~255).
            a: Alpha(0~1). Defaults to 1.
        """
        self._r = min(255, max(0, r)) | 0
        self._g = min(255, max(0, g)) | 0
        self._b = min(255, max(0, b)) | 0
        self._a = _round_float(max(min(1, a), 0))

    def __str__(self) -> str:
        """Format RGBA class.

        e.g. rgba(100, 100, 100, 0.5).
        """
        return "rgba({}, {}, {}, {:.3f})".format(self.r, self.g, self.b, self.a)

    def __getitem__(self, item):
        """Unpack to (r, g, b, a)."""
        return [self.r, self.g, self.b, self.a][item]

    def __eq__(self, other) -> bool:
        """Returns true if `r`, `g`, `b` and `a` are all the same."""
        return [self.r, self.g, self.b, self.a] == [other.r, other.g, other.b, other.a]

    @property
    def r(self) -> int:
        return self._r

    @property
    def g(self) -> int:
        return self._g

    @property
    def b(self) -> int:
        return self._b

    @property
    def a(self) -> float:
        return self._a


class _HSLA:
    def __init__(self, hue, sat, lum, alpha = 1) -> None:
        self._h = max(min(360, hue), 0) | 0
        self._s = _round_float(max(min(1, sat), 0))
        self._l = _round_float(max(min(1, lum), 0))
        self._a = _round_float(max(min(1, alpha), 0))

    def __eq__(self, other) -> bool:
        """Returns true if `hue`, `sat`, `lum` and `alpha` are all the same."""
        return [self.hue, self.sat, self.lum, self.alpha] == [
            other.hue,
            other.sat,
            other.lum,
            other.alpha,
        ]

    @property
    def hue(self) -> int:
        return self._h

    @property
    def sat(self) -> float:
        return self._s

    @property
    def lum(self) -> float:
        return self._l

    @property
    def alpha(self) -> float:
        return self._a

    @staticmethod
    def from_rgba(rgba):
        hls = colorsys.rgb_to_hls(rgba.r / 255, rgba.g / 255, rgba.b / 255)
        return _HSLA(int(hls[0] * 360), hls[2], hls[1], rgba.a)

    def to_rgba(self) -> _RGBA:
        rgb = colorsys.hls_to_rgb(self.hue / 360, self.lum, self.sat)
        return _RGBA(round(rgb[0] * 255), round(rgb[1] * 255), round(rgb[2] * 255), self.alpha)


class Color:
    """Class handling color code(RGBA and HSLA)."""

    def __init__(self, color_code) -> None:
        """Initialize color code."""
        self._hsla, self._hsva = None, None
        if isinstance(color_code, _RGBA):
            self._rgba = color_code
        elif isinstance(color_code, _HSLA):
            self._hsla = color_code
            self._rgba = self._hsla.to_rgba()

    @property
    def rgba(self) -> _RGBA:
        """Return rgba."""
        return self._rgba

    @property
    def hsla(self) -> _HSLA:
        """Return hsla."""
        return self._hsla if self._hsla else _HSLA.from_rgba(self.rgba)

    def __str__(self) -> str:
        """Format Color class.

        e.g. rgba(100, 100, 100, 0.5).
        """
        return str(self.rgba)

    @staticmethod
    def _check_hex_format(hex_format) -> None:
        """Check if string is hex format."""
        try:
            hex = hex_format.lstrip("#")
            if not len(hex) in (3, 4, 6, 8):
                raise ValueError
            int(hex, 16)
        except ValueError:
            raise ValueError(
                'invalid hex color format: "{}". '
                "Only support following hexadecimal notations: #RGB, #RGBA, #RRGGBB and #RRGGBBAA. "
                "R (red), G (green), B (blue), and A (alpha) are hexadecimal characters "
                "(0-9, a-f or A-F).".format(hex_format)
            ) from None

    @staticmethod
    def from_rgba(r, g, b, a):
        """Convert rgba to Color object."""
        rgba = _RGBA(r, g, b, a / 255)
        return Color(rgba)

    @staticmethod
    def from_hex(hex):
        """Convert hex string to Color object.

        Args:
            color_hex: Color hex string.

        Returns:
            Color: Color object converted from hex.
        """
        Color._check_hex_format(hex)
        hex = hex.lstrip("#")
        r, g, b, a = 255, 0, 0, 1
        if len(hex) == 3:  # #RGB format
            r, g, b = (int(char, 16) for char in hex)
            r, g, b = 16 * r + r, 16 * g + g, 16 * b + b
        if len(hex) == 4:  # #RGBA format
            r, g, b, a = (int(char, 16) for char in hex)
            r, g, b = 16 * r + r, 16 * g + g, 16 * b + b
            a = (16 * a + a) / 255
        if len(hex) == 6:  # #RRGGBB format
            r, g, b = bytes.fromhex(hex)
            a = 1
        elif len(hex) == 8:  # #RRGGBBAA format
            r, g, b, a = bytes.fromhex(hex)
            a = a / 255
        return Color(_RGBA(r, g, b, a))

    def _to_hex(self) -> str:
        """Convert Color object to hex(#RRGGBBAA).

        Args:
            color: Color object.

        Returns:
            str: Hex converted from Color object.
        """
        r, g, b, a = self.rgba.r, self.rgba.g, self.rgba.b, self.rgba.a
        hex_color = "{:02x}{:02x}{:02x}".format(math.floor(r), math.floor(g), math.floor(b))
        if a != 1:
            hex_color += "{:02x}".format(math.floor(a * 255))
        return hex_color

    def to_hex_argb(self) -> str:
        """Convert Color object to hex(#AARRGGBB).

        Args:
            color: Color object.

        Returns:
            str: Hex converted from Color object.
        """
        r, g, b, a = self.rgba.r, self.rgba.g, self.rgba.b, self.rgba.a
        hex_color = "" if a == 1 else "{:02x}".format(math.floor(a * 255))
        hex_color += "{:02x}{:02x}{:02x}".format(math.floor(r), math.floor(g), math.floor(b))
        return hex_color

    def to_svg_tiny_color_format(self) -> str:
        """Convert Color object to string for svg.

        QtSvg does not support #RRGGBBAA format.
        Therefore, we need to set the alpha value to `fill-opacity` instead.

        Returns:
            str: RGBA format.
        """
        r, g, b, a = self.rgba
        if a == 1:
            return 'fill="#{}"'.format(self._to_hex())
        return 'fill="rgb({},{},{})" fill-opacity="{}"'.format(r, g, b, a)

    def lighten(self, factor):
        """Lighten color."""
        return Color(
            _HSLA(self.hsla.hue, self.hsla.sat, self.hsla.lum + self.hsla.lum * factor, self.hsla.alpha)
        )

    def darken(self, factor):
        """Darken color."""
        return Color(
            _HSLA(self.hsla.hue, self.hsla.sat, self.hsla.lum - self.hsla.lum * factor, self.hsla.alpha)
        )

    def transparent(self, factor):
        """Make color transparent."""
        return Color(_RGBA(self.rgba.r, self.rgba.g, self.rgba.b, self.rgba.a * factor))
