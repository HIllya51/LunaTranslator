import os,sys

def initpath():
    dirname, filename = os.path.split(os.path.abspath(__file__))
    dirname=os.path.dirname(os.path.dirname(dirname))
    os.chdir(dirname) 

    if os.path.exists('./userconfig')==False:
        os.mkdir('./userconfig')
    if os.path.exists('./userconfig/memory')==False:
        os.mkdir('./userconfig/memory')
    if os.path.exists('./transkiroku'):
        os.rename('transkiroku','translation_record')
    if os.path.exists('./translation_record')==False:
        os.mkdir('./translation_record') 
    if os.path.exists('./translation_record/cache')==False:
        os.mkdir('./translation_record/cache') 
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

    sys.path.append('./userconfig')


language_list_show=["简体中文","日本語","English","Русский язык","Español","한국어","Français","繁體中文","Tiếng Việt","Türkçe"] 
language_list_translator=["简体中文","日文","英文","俄语","西班牙语","韩语","法语","繁体中文","越南语","土耳其语"]
language_list_translator_inner=["zh", "ja", "en","ru","es","ko","fr","cht","vi","tr"]


codepage_display=["日语(CP932,SHIFT-JIS)","UTF8(CP65001)","简体中文(CP936,GBK)","繁体中文(CP950,BIG5)","韩语(CP949,EUC-KR)","越南语(CP1258)","泰语(CP874)","阿拉伯语(CP1256)","希伯来语(CP1255)","土耳其语(CP1254)","希腊语(CP1253)","北欧(CP1257)","中东欧(CP1250)","西里尔(CP1251)","拉丁(CP1252)"]
codepage_real=[932,65001,936,950,949,1258,874,1256,1255,1254,1253,1257,1250,1251,1252]



charsetmap=[0,1,128,134,136,129,163,122,161,178,177,162,238,186,204]
charsetmapshow=["自动","系统默认","日语","简体中文","繁体中文","韩语","越南语","泰语","希腊语","阿拉伯语","希伯来语","土耳其语","中东欧","北欧","西里尔"]


fanyi_offline=["jb7","dreye","kingsoft","hanshant","selfbuild"]
fanyi_pre=["rengong","premt","rengong_vnr","rengong_msk"]


key_first=['Ctrl','Shift','Alt','Win' ]+['None']
key_first_reg=['control','shift','alt','super' ]+['']

from utils.winsyshotkey import vk_codes

key_second=[_.upper() for _ in (vk_codes )]
key_second_reg=list(vk_codes.keys())