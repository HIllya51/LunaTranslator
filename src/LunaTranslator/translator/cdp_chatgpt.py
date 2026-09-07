from translator.cdp_ws_client import BaseCDPTranslator
from translator.cdp_core import DOMToolsWidget


def dom_tools_widget(_dict, key):
    return DOMToolsWidget(_dict, key, provider_key=TS.PROVIDER_KEY)


class TS(BaseCDPTranslator):
    PROVIDER_KEY = "chatgpt"
