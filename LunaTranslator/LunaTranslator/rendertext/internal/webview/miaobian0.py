from qtsymbols import *
from rendertext.internal.webview.base import base, datas


class TextLine(base):

    def gen_html(self, text, data: datas):
        _id = self.getuid()

        style = f"""#{_id}{{
             {self.fontinfo}
            color:{self.config["fillcolor"]}; 
            {self.align}
            {self.line_height}
            -webkit-text-stroke: {self.config['width']}px {data.color};
        }}
        """
        return self.makedivstyle(_id, text, style)
