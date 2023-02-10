import subprocess

#x=subprocess.Popen('C:/Users/11737/Documents/GitHub/LunaTranslator/CXXplugins/win32dllforward/Release/jbj7.exe C:/dataH/JBeijing7/JBJCT.dll  "C:/dataH/vnr3/Visual Novel Reader V3/Library/Dictionaries/jb/@djz020815/JcUserdic/Jcuser"  "C:/dataH/vnr3/Visual Novel Reader V3/Library/Dictionaries/jb/@jichi/JcUserdic/Jcuser" "C:/dataH/vnr3/Visual Novel Reader V3/Library/Dictionaries/jb/@najizhimo/JcUserdic/Jcuser"',stdin=subprocess.PIPE , stdout=subprocess.PIPE ,encoding='utf-16-le')
x=subprocess.Popen('C:/Users/11737/Documents/GitHub/LunaTranslator/CXXplugins/win32dllforward/Release/jbj7.exe C:/dataH/JBeijing7/JBJCT.dll',stdin=subprocess.PIPE , stdout=subprocess.PIPE ,encoding='utf-16-le',errors='ignore' )
x.stdin.write('936\r\n「とうとう行政をあてにしだしたよ、ウチのお兄ちゃん」\r\n')#.encode(encoding= 'utf-16-le',errors='ignore'))
x.stdin.flush()
print(x.stdout.read())