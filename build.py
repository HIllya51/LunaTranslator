import shutil
try:
    shutil.rmtree(r'C:\tmp\LunaTranslator\LunaTranslator') 
except:
    1
try:
    shutil.rmtree(r'C:\tmp\LunaTranslator\LunaTranslator.build')
except:
    1
try:
    shutil.move(r"C:\tmp\LunaTranslator\LunaTranslator.dist",r"C:\tmp\LunaTranslator\LunaTranslator") 
except:
    1