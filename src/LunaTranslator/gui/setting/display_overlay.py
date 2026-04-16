from qtsymbols import *
import functools
import json
from pathlib import Path
from gui.usefulwidget import (
    D_getspinbox,
    D_getcolorbutton,
    D_getsimpleswitch,
    getboxlayout,
    FocusFontCombo
)
from myutils.config import _TR as _TR_original
import ovl

_en_cache = None
    
def _TR(key):
    global _en_cache
    res = _TR_original(key)
    if res == key and isinstance(key, str):
        if _en_cache is None:
            try:
                with open("files/lang/en.json", "r", encoding="utf-8") as f:
                    _en_cache = json.load(f)
            except:
                _en_cache = {}
        return _en_cache.get(key, key)
    return res

# Ensure config is loaded
ovl.load_config()

def save_overlay_config():
    config_path = Path("userconfig/overlay.json")
    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True)
    
    # Filter only relevant keys to save
    save_data = {k: v for k, v in ovl.CONFIG.items() if k in [
        "enable", "text_color", "stroke_color", "stroke_width",
        "min_font_size", "max_font_size", "font_family",
        "background_color", "box_expansion", "timeout_ms",
        "horizontal_padding", "vertical_padding"
    ]}
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=4)

def update_color_with_opacity(self, color_key, rgb_key, alpha_key):
    # Combine RGB and Alpha to rgba string
    color = QColor(ovl.CONFIG.get(rgb_key, "#000000"))
    alpha = ovl.CONFIG.get(alpha_key, 255)
    ovl.CONFIG[color_key] = f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha/255:.2f})"
    save_overlay_config()

def create_opacity_slider_generic(self, color_key, rgb_key, alpha_key):
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 255)
    
    # Parse current alpha
    current_color = ovl.CONFIG.get(color_key, "rgba(0, 0, 0, 1)")
    current_alpha = 255
    try:
        c = ovl.parse_color(current_color)
        current_alpha = c.alpha()
    except:
        pass
    
    ovl.CONFIG[alpha_key] = current_alpha
    slider.setValue(current_alpha)
    
    label = QLabel(f"{int(current_alpha/255*100)}%")
    
    def on_change(val):
        ovl.CONFIG[alpha_key] = val
        label.setText(f"{int(val/255*100)}%")
        update_color_with_opacity(self, color_key, rgb_key, alpha_key)
        
    slider.valueChanged.connect(on_change)
    
    return getboxlayout([slider, label])

def create_font_combo():
    combo = FocusFontCombo()
    current_font = ovl.CONFIG.get("font_family", "")
    if current_font:
        combo.setCurrentFont(QFont(current_font))
    
    def on_change(font_family):
        ovl.CONFIG["font_family"] = font_family
        save_overlay_config()
        
    combo.currentTextChanged.connect(on_change)
    return combo

def right_layout(w, unit="", fixed_width=None, unit_width=30):
    if callable(w):
        w = w()
    if fixed_width:
        w.setFixedWidth(fixed_width)
    bg = QWidget()
    lay = QHBoxLayout(bg)
    lay.setContentsMargins(0,0,0,0)
    lay.addStretch()
    lay.addWidget(w)
    
    # Always add a unit label with fixed width for alignment
    unit_label = QLabel(unit)
    unit_label.setFixedWidth(unit_width)
    unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    lay.addWidget(unit_label)
    
    return bg

def overlaysetting(self):
    # Helper to save on change
    def generic_save(_):
        save_overlay_config()

    # Initialize virtual keys for colors
    for color_key, rgb_key in [
        ("background_color", "_bg_rgb"),
        ("text_color", "_text_rgb"),
        ("stroke_color", "_stroke_rgb")
    ]:
        current_val = ovl.CONFIG.get(color_key, "rgba(0, 0, 0, 1)")
        try:
            c = ovl.parse_color(current_val)
            ovl.CONFIG[rgb_key] = c.name() # Hex
        except:
            ovl.CONFIG[rgb_key] = "#000000"

    box_width = 250

    return [
        [
            dict(
                title=_TR("OverlaySetting"),
                type="grid",
                grid=[
                    [
                        _TR("ovlEnable"),
                        (QWidget(), 0),
                        right_layout(D_getsimpleswitch(ovl.CONFIG, "enable", callback=lambda x: (ovl.CONFIG.update({"enable": int(x)}), save_overlay_config()))),
                    ],
                    [
                        _TR("ovlTextColor"),
                        D_getcolorbutton(self, ovl.CONFIG, "_text_rgb", callback=lambda _: update_color_with_opacity(self, "text_color", "_text_rgb", "_text_alpha")),
                        (QWidget(), 0),
                        _TR("ovlTextOpacity"),
                        functools.partial(create_opacity_slider_generic, self, "text_color", "_text_rgb", "_text_alpha"),
                    ],
                    [
                        _TR("ovlStrokeColor"),
                        D_getcolorbutton(self, ovl.CONFIG, "_stroke_rgb", callback=lambda _: update_color_with_opacity(self, "stroke_color", "_stroke_rgb", "_stroke_alpha")),
                        (QWidget(), 0),
                        _TR("ovlTextOpacity"),
                        functools.partial(create_opacity_slider_generic, self, "stroke_color", "_stroke_rgb", "_stroke_alpha"),
                    ],
                    [
                        _TR("ovlBackColor"),
                        D_getcolorbutton(self, ovl.CONFIG, "_bg_rgb", callback=lambda _: update_color_with_opacity(self, "background_color", "_bg_rgb", "_bg_alpha")),
                        (QWidget(), 0),
                        _TR("ovlTextOpacity"),
                        functools.partial(create_opacity_slider_generic, self, "background_color", "_bg_rgb", "_bg_alpha"),
                    ],
                    [
                        _TR("ovlStrokeWidth"),
                        (QWidget(), 0),
                        right_layout(D_getspinbox(0, 10, ovl.CONFIG, "stroke_width", double=True, step=0.5, callback=generic_save), "px", fixed_width=box_width),
                    ],
                    [
                        _TR("ovlBoxExpansion"),
                        (QWidget(), 0),
                        right_layout(D_getspinbox(0, 50, ovl.CONFIG, "box_expansion", double=True, step=0.5, callback=generic_save), "px", fixed_width=box_width),
                    ],
                    [
                        _TR("ovlTextSizeMin"),
                        (QWidget(), 0),
                        right_layout(D_getspinbox(1, 100, ovl.CONFIG, "min_font_size", double=True, step=0.5, callback=generic_save), "px", fixed_width=box_width),
                    ],
                    [
                        _TR("ovlTextSizeMax"),
                        (QWidget(), 0),
                        right_layout(D_getspinbox(1, 200, ovl.CONFIG, "max_font_size", double=True, step=0.5, callback=generic_save), "px", fixed_width=box_width),
                    ],
                    [
                        _TR("ovlTextFont"),
                        (QWidget(), 0),
                        right_layout(create_font_combo, "", fixed_width=box_width),
                    ],
                    [
                        _TR("ovlPaddingH"),
                        (QWidget(), 0),
                        right_layout(D_getspinbox(0, 50, ovl.CONFIG, "horizontal_padding", double=True, step=0.5, callback=generic_save), "px", fixed_width=box_width),
                    ],
                    [
                        _TR("ovlPaddingV"),
                        (QWidget(), 0),
                        right_layout(D_getspinbox(0, 50, ovl.CONFIG, "vertical_padding", double=True, step=0.5, callback=generic_save), "px", fixed_width=box_width),
                    ],
                    [
                        _TR("ovlTimeout"),
                        (QWidget(), 0),
                        right_layout(D_getspinbox(100, 60000, ovl.CONFIG, "timeout_ms", callback=generic_save), "ms", fixed_width=box_width),
                    ]
                ]
            )
        ]
    ]
