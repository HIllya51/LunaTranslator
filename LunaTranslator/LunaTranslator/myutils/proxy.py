from myutils.config import globalconfig
from urllib.request import getproxies_registry


def getsysproxy():
    proxies = getproxies_registry()
    try:
        return proxies[list(proxies.keys())[0]].split("//")[1]
    except:
        return ""


def _getproxy():
    if globalconfig["useproxy"]:
        if globalconfig["usesysproxy"]:
            p = getsysproxy()
        else:
            p = globalconfig["proxy"]
    else:
        p = None
    return {"https": p, "http": p}


def getproxy(pair=None):
    if (
        pair is None
        or ("useproxy" not in globalconfig[pair[0]][pair[1]])
        or globalconfig[pair[0]][pair[1]]["useproxy"]
    ):
        return _getproxy()
    else:
        return {"https": None, "http": None}
