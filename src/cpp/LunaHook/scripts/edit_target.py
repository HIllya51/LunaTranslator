import os
#妈的，不知道为什么我重装系统后，装了vs2017 cmake也识别不到，只能手动改了。
for f in ['../build/x86_xp']:
    for dirname,_,fs in os.walk(f):
        for ff in fs:
            if ff.endswith('.vcxproj')==False:continue
            if ff.endswith('QtLoader.vcxproj'):continue
            path=os.path.join(dirname,ff)
            with open(path,'r',encoding='utf-8-sig') as pf:
                file=pf.read()
                file=file.replace('>v143<','>v141_xp<')
            with open(path,'w',encoding='utf-8-sig') as pf:
                pf.write(file)


url = "https://github.com/Chuyu-Team/YY-Thunks/releases/download/v1.0.7/YY-Thunks-1.0.7-Binary.zip"
target = "../../libs/YY-Thunks/objs/X86/YY_Thunks_for_WinXP.obj"
if os.path.exists(target) == False:
    os.system(rf"curl -SLo YY-Thunks-1.0.7-Binary.zip " + url)
    os.system(rf"7z x -y YY-Thunks-1.0.7-Binary.zip -o../../libs/YY-Thunks")