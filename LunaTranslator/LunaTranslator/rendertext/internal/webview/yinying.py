from qtsymbols import *
from rendertext.internal.webview.base import base, datas


class TextLine(base):

    def gen_html(self, text, data: datas):
        _id = self.getuid()
        ntimes = ""
        for i in range(self.config["shadowforce"]):
            ntimes += f"0px 0px {data.font_size*self.config['shadowR']}px {data.color}"
            if i == self.config["shadowforce"] - 1:
                ntimes += ";"
            else:
                ntimes += ","
        style = f"""#{_id}{{
            {self.fontinfo}
            color:{self.config['fillcolor']}; 
            text-shadow:{ntimes}; 
            {self.align}
            {self.line_height}
        }}
        """
        return self.makedivstyle(_id, text, style)
