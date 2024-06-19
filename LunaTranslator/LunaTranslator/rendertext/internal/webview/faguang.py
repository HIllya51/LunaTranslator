from qtsymbols import *
import uuid


def gen_html(configs, text, fm, fs, bold, atcenter, color, extra_space):
    align = "text-align: center;" if atcenter else ""
    bold = "font-weight: bold;" if bold else ""
    _id = f"luna_{uuid.uuid4()}"
    ntimes = ""
    for i in range(configs["shadowforce"]):
        ntimes += f"0px 0px {fs*0.4}px {color}"
        if i == configs["shadowforce"] - 1:
            ntimes += ";"
        else:
            ntimes += ","
    style = f"""<style>#{_id}{{
        font-family: {fm};
        font-size: {fs}pt;
        color:{configs['fillcolor']}; 
        {bold}
        text-shadow:{ntimes}; 
        {align};
        line-height: calc(1.2em + {extra_space}px);
    }}</style>"""
    return style + f'<div id="{_id}">{text}</div>'
