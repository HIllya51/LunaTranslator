import os

def initpath():
    dirname, filename = os.path.split(os.path.abspath(__file__))
    dirname=os.path.dirname(os.path.dirname(dirname))
    os.chdir(dirname) 

    if os.path.exists('./userconfig')==False:
        os.mkdir('./userconfig')
    if os.path.exists('./transkiroku'):
        os.rename('transkiroku','translation_record')
    if os.path.exists('./translation_record')==False:
        os.mkdir('./translation_record') 
    if os.path.exists('./cache')==False:
        os.mkdir('./cache')
    if os.path.exists('./cache/ocr')==False:
        os.mkdir('./cache/ocr')
    if os.path.exists('./cache/update')==False:
        os.mkdir('./cache/update')
    if os.path.exists('./cache/screenshot')==False:
        os.mkdir('./cache/screenshot')
    if os.path.exists('./cache/tts')==False:
        os.mkdir('./cache/tts')
