
#include<Windows.h>
#include <iostream> 
#include<string>
#pragma comment( linker, "/subsystem:windows /entry:wmainCRTStartup" )

int dllinjectwmain(int argc, wchar_t* argv[]);
int ntleaswmain(int argc, wchar_t* wargv[]);

#ifndef _WIN64
int LRwmain(int argc, wchar_t* argv[]);  
int jbjwmain(int argc, wchar_t* argv[]);
int dreyewmain(int argc, wchar_t* argv[]);
int kingsoftwmain(int argc, wchar_t* argv[]);
int voiceroid2wmain(int argc, wchar_t* argv[]);
int lewmain(int argc, wchar_t* argv[]);
int neospeech(int argc, wchar_t* argv[]);
#else
int magpiewmain(int argc, wchar_t* wargv[]);

#endif // !_WIN64
int wmain(int argc, wchar_t* argv[])
{
    auto argv0 = std::wstring(argv[1]);
    if (argv0 == L"dllinject")
        return dllinjectwmain(argc - 1, argv + 1);
    if (argv0 == L"ntleas")
        return ntleaswmain(argc - 1, argv + 1);
    
#ifndef _WIN64
    else if (argv0 == L"LR")
        return LRwmain(argc - 1, argv + 1);
    else if (argv0 == L"le")
        return lewmain(argc - 1, argv + 1);
    else if (argv0 == L"jbj7")
        return jbjwmain(argc - 1, argv + 1);
    else if (argv0 == L"dreye")
        return dreyewmain(argc - 1, argv + 1);
    else if (argv0 == L"kingsoft")
        return kingsoftwmain(argc - 1, argv + 1);
    else if (argv0 == L"voiceroid2")
        return voiceroid2wmain(argc - 1, argv + 1);
    else if (argv0 == L"neospeech")
        return neospeech(argc - 1, argv + 1);
#else
    else if (argv0 == L"magpie")
        return magpiewmain(argc - 1, argv + 1);
#endif // !_WIN64

}
