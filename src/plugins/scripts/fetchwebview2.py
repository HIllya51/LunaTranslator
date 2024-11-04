mswebview2_version = "1.0.2535.41"

import os, subprocess

target = os.path.normpath(os.path.join(os.path.dirname(__file__), r"..\libs\webview2"))
os.makedirs(target, exist_ok=True)
nuget_exe = os.path.join(target, "nuget.exe")
print(nuget_exe)
if os.path.exists(nuget_exe) == False:
    os.system(
        rf'curl -SLo "{nuget_exe}" https://dist.nuget.org/win-x86-commandline/latest/nuget.exe'
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


onnx = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), "../libs/onnxruntime-static/windows-x64/lib/onnx.lib"
    )
)
opencv = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        r"..\libs\opencv-static\windows-x64\x64\vc16\staticlib\opencv_core470.lib",
    )
)
onnx_1 = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../libs/onnxruntime-static.zip")
)
opencv_1 = os.path.normpath(
    os.path.join(os.path.dirname(__file__), r"..\libs\opencv-static.zip")
)


if os.path.exists(onnx) == False:
    os.system(
        rf'curl -SLo "{onnx_1}" https://github.com/HIllya51/RESOURCES/releases/download/common/onnxruntime-static.zip'
    )
    os.system(rf'7z x -y "{onnx_1}" -o{os.path.dirname(opencv_1)}')
if os.path.exists(opencv) == False:
    os.system(
        rf'curl -SLo "{opencv_1}" https://github.com/HIllya51/RESOURCES/releases/download/common/opencv-static.zip'
    )
    os.system(rf'7z x -y "{opencv_1}" -o{os.path.dirname(opencv_1)}')
