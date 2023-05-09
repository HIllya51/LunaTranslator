#pragma once


#define CODEPAGE_JA  932
#define CODEPAGE_GB  936 

#define CODEPAGE_BIG5 950

int dllinjectwmain(int argc, wchar_t* argv[]);

#ifndef _WIN64
int jbjwmain(int argc, wchar_t* argv[]);
int dreyewmain(int argc, wchar_t* argv[]);
int kingsoftwmain(int argc, wchar_t* argv[]);
int voiceroid2wmain(int argc, wchar_t* argv[]);
int lewmain(int argc, wchar_t* argv[]);
#else
int magpiewmain(int argc, wchar_t* wargv[]);

#endif // !_WIN64