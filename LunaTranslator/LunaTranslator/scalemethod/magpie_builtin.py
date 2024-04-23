from scalemethod.base import scalebase
import os, json
import windows
from myutils.config import globalconfig, magpie_config
from myutils.subproc import subproc_w
from myutils.wrapper import threader


class Method(scalebase):
    @threader
    def _waitenginestop_magpie(self):
        self.engine.wait()
        self.setuistatus(False)

    def changestatus(self, hwnd, full):
        if full:
            profiles_index = globalconfig["profiles_index"]
            if profiles_index > len(magpie_config["profiles"]):
                profiles_index = 0

            jspath = os.path.abspath("./userconfig/magpie_config.json")
            with open(jspath, "w", encoding="utf-8") as ff:
                ff.write(
                    json.dumps(
                        magpie_config, ensure_ascii=False, sort_keys=False, indent=4
                    )
                )
            self.engine = subproc_w(
                './files/plugins/Magpie/Magpie.Core.exe {} {} "{}"'.format(
                    profiles_index, hwnd, jspath
                ),
                cwd="./files/plugins/Magpie/",
            )
            self._waitenginestop_magpie()
        else:
            windows.SendMessage(
                windows.FindWindow("Magpie_Core_CLI_Message", None),
                windows.RegisterWindowMessage("Magpie_Core_CLI_Message_Stop"),
            )
