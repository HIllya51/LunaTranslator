from qtsymbols import *
import uuid


def gen_html(configs, text, fm, fs, bold, atcenter, color, extra_space):
    align = "text-align: center;" if atcenter else ""
    bold = "font-weight: bold;" if bold else ""
    _id = f"luna_{uuid.uuid4()}"
    style = f"""<style>#{_id}{{
        font-family: {fm};
        font-size: {fs}pt;
        color:white;
        color:{color};
        {bold}
        {align}
        line-height: calc(1.2em + {extra_space}px);
    }}</style>"""

    return style + f'<div id="{_id}">{text}</div>'
