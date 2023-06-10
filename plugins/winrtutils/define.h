#pragma once
#include<string>
#include<vector>
struct ocrres {
    wchar_t** lines;
    int* ys;

};
extern "C" {

    __declspec(dllexport) bool check_language_valid(wchar_t*);
    __declspec(dllexport) wchar_t** getlanguagelist(int*);
    __declspec(dllexport) ocrres OCR(wchar_t* fname, wchar_t* lang, wchar_t*, int*);
   
    __declspec(dllexport) void freewstringlist(wchar_t**, int);
    __declspec(dllexport) void freeocrres(ocrres, int);

}
char** vecstr2c(std::vector<std::string>& vs);
int* vecint2c(std::vector<int>& vs);
wchar_t** vecwstr2c(std::vector<std::wstring>& vs);