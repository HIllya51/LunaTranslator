from traceback import print_exc
import subprocess

allsubprocess2 = {}


class autoproc:
    def __init__(self, proc: subprocess.Popen) -> None:
        self.proc = proc

    def __del__(self):
        try:
            self.proc.kill()
        except:
            pass


def subproc_w(
    cmd, cwd=None, needstdio=False, name=None, encoding=None, run=False
) -> subprocess.Popen:

    _pipe = subprocess.PIPE if needstdio else None
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    if name and name in allsubprocess2:
        try:
            allsubprocess2[name].kill()
        except:
            print_exc()
    try:
        if run:
            _f = subprocess.run
        else:
            _f = subprocess.Popen

        ss = _f(
            cmd,
            cwd=cwd,
            stdin=_pipe,
            stdout=_pipe,
            stderr=_pipe,
            startupinfo=startupinfo,
            encoding=encoding,
        )

        if name:
            allsubprocess2[name] = ss

        return ss
    except:
        print_exc()
        return None


def endsubprocs():
    for _ in allsubprocess2:
        try:
            allsubprocess2[_].kill()
        except:
            pass
