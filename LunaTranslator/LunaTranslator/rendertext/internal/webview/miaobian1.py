from qtsymbols import *
from rendertext.internal.webview.base import base, datas


class TextLine(base):

    def colorpair(self, color):
        return self.config["fillcolor"], color

    def gen_html(self, text, data: datas):
        c1, c2 = self.colorpair(data.color)
        _id = self.getuid()
        _text = text.replace('"', '\\"')

        style = f"""#{_id} .text{{
             {self.fontinfo}
            {self.align}
            {self.line_height}
        }}
        #{_id} .stroke {{
    -webkit-text-stroke: {self.config['width']}px {c1};
    position: relative;
  }}
  #{_id} .stroke::after {{
    content: "{_text}";
    color: {c2};
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    -webkit-text-stroke-width: 0;
  }}
        """
        text = f"""<div class="stroke text">
   {text}
  </div>"""
        return self.makedivstyle(_id, text, style)
