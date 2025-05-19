from network.server.tcpservice import WSHandler
from typing import List
from myutils.wrapper import threader
from traceback import print_exc

mainuiwsoutputsave: List["internalservicemainuiws"] = []
transhistwsoutputsave: List["internalservicetranshistws"] = []
wsoutputsave: List[WSHandler] = []


@threader
def WSForEach(LS: list, func):
    for L in tuple(LS):
        try:
            func(L)
        except Exception as e:
            if not isinstance(e, OSError):
                print_exc()
            else:
                try:
                    LS.remove(L)
                except:
                    pass
