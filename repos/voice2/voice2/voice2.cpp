// voice2.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include<windows.h>
#include<string>
#include<vector>
#include"types.h"
char* UnicodeToShift_jis(const wchar_t* unicode)
{ 
    int len;
    len = WideCharToMultiByte(932, 0, unicode, -1, NULL, 0, NULL, NULL);
    char* szUtf8 = (char*)malloc(len + 1);
    memset(szUtf8, 0, len + 1);
    WideCharToMultiByte(932, 0, unicode, -1, szUtf8, len, NULL, NULL);
    return szUtf8;
}
char text_buf[16384];
std::vector<char> output;
AITalkAPI_GetKana _AITalkAPI_GetKana;
int TextBufferCallback(int reason_code, int job_id, void* user_data) {
    while (1) {
        int bytes_read, position;
        int res = _AITalkAPI_GetKana(job_id, text_buf, 16384, &bytes_read, &position);
        std::cout << "ss" << res;
        std::cout << text_buf;
    }
         
}
int wmain1 (int argc, wchar_t* argv[])
{   
    std::wstring path = L"C:/dataH/Yukari2";
    HMODULE lib=LoadLibraryW(L"C:/dataH/Yukari2/aitalked.dll");
    if (lib) {
        AITalkAPI_Init _AITalkAPI_Init = (AITalkAPI_Init)GetProcAddress(lib, "_AITalkAPI_Init@4");
        AITalkAPI_LangClear _AITalkAPI_LangClear=(AITalkAPI_LangClear)GetProcAddress(lib, "_AITalkAPI_LangClear@0");
        AITalkAPI_LangLoad _AITalkAPI_LangLoad = (AITalkAPI_LangLoad)GetProcAddress(lib, "_AITalkAPI_LangLoad@4");
        AITalkAPI_VoiceLoad _AITalkAPI_VoiceLoad = (AITalkAPI_VoiceLoad)GetProcAddress(lib, "_AITalkAPI_VoiceLoad@4");
        AITalkAPI_SetParam _AITalkAPI_SetParam = (AITalkAPI_SetParam)GetProcAddress(lib, "_AITalkAPI_SetParam@4");
        AITalkAPI_GetParam _AITalkAPI_GetParam = (AITalkAPI_GetParam)GetProcAddress(lib, "_AITalkAPI_GetParam@8");
        _AITalkAPI_GetKana = (AITalkAPI_GetKana)GetProcAddress(lib, "_AITalkAPI_GetKana@20");
        AITalkAPI_TextToKana _AITalkAPI_TextToKana = (AITalkAPI_TextToKana)GetProcAddress(lib, "_AITalkAPI_TextToKana@12");
        TConfig config = { 
            44100 ,
            (char*)UnicodeToShift_jis((path+ L"/Voice").c_str()) ,
            10000,
            (char*)UnicodeToShift_jis(L"C:/dataH/Yukari2/aitalk.lic" ),
            (char*)"ORXJC6AIWAUKDpDbH2al"
        };

        int ret;
        
        _AITalkAPI_Init(&config);
           
        _AITalkAPI_LangClear(); 

       // SetCurrentDirectoryW(path.c_str());
        wchar_t buffer[1000]={0};
        DWORD sz=1000;
        GetCurrentDirectoryW(sz, buffer);
        wprintf(L"%s\n", buffer);
         ret=_AITalkAPI_LangLoad(UnicodeToShift_jis((path + L"/Lang/standard").c_str()));  
        _AITalkAPI_VoiceLoad(UnicodeToShift_jis((L"yukari_emo_44"))); 

        printf("%d ？", ret);

        TTtsParam _TTtsParam = TTtsParam();
        _TTtsParam.size = 500;
        int param_size=500; 
        _AITalkAPI_GetParam(&_TTtsParam, &param_size); 
        _TTtsParam.pauseBegin = 0;
        _TTtsParam.pauseTerm = 0;
        _TTtsParam.extendFormat = 17;
        _TTtsParam.procRawBuf = 0;
        _TTtsParam.procEventTts = 0;
        _TTtsParam.procTextBuf = (ProcTextBuf)TextBufferCallback;
        ret = _AITalkAPI_SetParam(&_TTtsParam);
        std::cout << ret;
        std::cout << _TTtsParam.voiceName;
        int job_id;
        TJobParam job_param = TJobParam();
        job_param.modeInOut = 21;
        //_AITalkAPI_TextToKana(&job_id,&job_param,)

        char * text=UnicodeToShift_jis(L"こんにちは。明日の天気は晴れの予報です");
    } 

}
 