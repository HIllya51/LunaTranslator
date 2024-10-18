mswebview2_version = "1.0.2535.41"

import os, subprocess

target = os.path.normpath(os.path.join(os.path.dirname(__file__), r"..\libs\webview2"))
os.makedirs(target, exist_ok=True)
nuget_exe = os.path.join(target, "nuget.exe")
print(nuget_exe)
if os.path.exists(nuget_exe) == False:
    os.system(
        rf'curl -sSLo "{nuget_exe}" https://dist.nuget.org/win-x86-commandline/latest/nuget.exe'
    )

mswebview2_dir = os.path.join(target, f"Microsoft.Web.WebView2.{mswebview2_version}")
if os.path.exists(mswebview2_dir) == False:
    os.mkdir(mswebview2_dir)
    print(
        rf""""{nuget_exe}" install Microsoft.Web.Webview2 -Verbosity quiet -Version "{mswebview2_version}" -OutputDirectory {target}"""
    )
    subprocess.run(
        rf'"{nuget_exe}" install Microsoft.Web.Webview2 -Verbosity quiet -Version "{mswebview2_version}" -OutputDirectory {target}'
    )
