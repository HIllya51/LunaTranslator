mswebview2_version = "1.0.2535.41"

import os, subprocess, re

dfile = os.path.dirname(__file__)

target = os.path.normpath(os.path.join(dfile, r"..\libs\webview2"))
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

with open(os.path.join(dfile, "../LunaOCR/CMakeLists.txt"), "r", encoding="utf8") as ff:
    onnxver = re.search(r"set\(onnxruntime_version (.*?)\)", ff.read()).groups()[0]

onnx_1 = os.path.normpath(
    os.path.join(dfile, f"../libs/onnxruntime-win-x64-{onnxver}/lib/onnxruntime.dll")
)
if os.path.exists(onnx_1) == False:
    os.system(
        rf"curl -SLo ../libs/onnxruntime-win-x64-{onnxver}.zip https://github.com/microsoft/onnxruntime/releases/download/v{onnxver}/onnxruntime-win-x64-{onnxver}.zip"
    )
    os.system(rf"7z x -y ../libs/onnxruntime-win-x64-{onnxver}.zip -o../libs/")

onnx_1 = os.path.normpath(
    os.path.join(dfile, f"../libs/onnxruntime-win-x86-{onnxver}/lib/onnxruntime.dll")
)
if os.path.exists(onnx_1) == False:
    os.system(
        rf"curl -SLo ../libs/onnxruntime-win-x86-{onnxver}.zip https://github.com/microsoft/onnxruntime/releases/download/v{onnxver}/onnxruntime-win-x86-{onnxver}.zip"
    )
    os.system(rf"7z x -y ../libs/onnxruntime-win-x86-{onnxver}.zip -o../libs/")


opencv = os.path.normpath(
    os.path.join(
        dfile,
        r"..\libs\opencv-static\windows-x64\x64\vc16\staticlib\opencv_core470.lib",
    )
)
opencv_1 = os.path.normpath(
    os.path.join(dfile, r"..\libs\opencv-static\opencv-static.7z")
)

if os.path.exists(opencv) == False:
    os.makedirs(os.path.dirname(opencv_1), exist_ok=True)
    os.system(
        rf'curl -SLo "{opencv_1}" https://github.com/RapidAI/OpenCVBuilder/releases/download/4.7.0/opencv-4.7.0-windows-vs2019-mt.7z'
    )
    os.system(rf'7z x -y "{opencv_1}" -o{os.path.dirname(opencv_1)}')


url = "https://github.com/Chuyu-Team/YY-Thunks/releases/download/v1.1.7-Beta6/YY-Thunks-Objs.zip"
target = "../libs/YY-Thunks/objs/X86/YY_Thunks_for_WinXP.obj"
if os.path.exists(target) == False:
    os.system(rf"curl -SLo ../libs/YY-Thunks-Objs.zip " + url)
    os.system(rf"7z x -y ../libs/YY-Thunks-Objs.zip -o../libs/YY-Thunks")
