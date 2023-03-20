import os
import platform
import site
import subprocess
import glob

def mecab_config(com="mecab-config"):
    output = subprocess.check_output([com, "--inc-dir", "--libs-only-L", "--libs-only-l"])
    if not isinstance(output, str):
        output = output.decode("utf-8")
    return output.split('\n'), []

def mecab_config_windows():
    ## Windows
    if not os.name == 'nt':
        return

    win_mecab_dir = r'.'
    win_bin_dir = win_mecab_dir # this is separate from the sdk dir on some installs
    mecab_details = (win_mecab_dir, win_mecab_dir, 'libmecab')
    data_files = [("lib\\site-packages\\fugashi\\", ["{}\\libmecab.dll".format(win_bin_dir)])]
    return mecab_details, data_files

def mecab_config_cygwin():
    ## Cygwin
    os.chdir("build/mecab")
    if platform.system().startswith("CYGWIN"):
        rep = "mecab-cygwin64" if platform.machine() == "x86_64" else "mecab-cygwin32"
        subprocess.run(["git", "clone", "--depth=1", "https://github.com/KoichiYasuoka/"+rep])
        mecab_details = ("build/mecab/"+rep+"/include", "build/mecab/"+rep+"/lib", "mecab stdc++")
        return mecab_details, []

def check_libmecab():
    """Get MeCab build parameters.

    Where available the mecab-config script is used, but if it's available it
    will be installed or the parameters will otherwise be figured out."""

    configs = [
            mecab_config_windows,
            mecab_config,
            mecab_config_cygwin,
            ]

    # A few scripts will use a build directory. Save where we start so we can
    # reset the directory after each build step.
    cwd = os.getcwd()
    os.makedirs("build/mecab", exist_ok=True)
    for config in configs:
        try:
            out = config()
            os.chdir(cwd)
            if out:
                return out
        except:
            # failure is normal, typically just a different platform
            os.chdir(cwd)
    raise RuntimeError("Could not configure working env. Have you installed MeCab?")
