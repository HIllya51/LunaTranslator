#pragma once

// modiocr.h
// 8/11/2014 jichi

#include <functional>

// See: http://msdn.microsoft.com/en-us/library/office/aa167596%28v=office.11%29.aspx
// Copied from mdivwctl.tlh
//enum MiLANGUAGES {
//  miLANG_CHINESE_SIMPLIFIED = 2052,
//  miLANG_CHINESE_TRADITIONAL = 1028,
//  miLANG_CZECH = 5,
//  miLANG_DANISH = 6,
//  miLANG_DUTCH = 19,
//  miLANG_ENGLISH = 9,
//  miLANG_FINNISH = 11,
//  miLANG_FRENCH = 12,
//  miLANG_GERMAN = 7,
//  miLANG_GREEK = 8,
//  miLANG_HUNGARIAN = 14,
//  miLANG_ITALIAN = 16,
//  miLANG_JAPANESE = 17,
//  miLANG_KOREAN = 18,
//  miLANG_NORWEGIAN = 20,
//  miLANG_POLISH = 21,
//  miLANG_PORTUGUESE = 22,
//  miLANG_RUSSIAN = 25,
//  miLANG_SPANISH = 10,
//  miLANG_SWEDISH = 29,
//  miLANG_TURKISH = 31,
//  miLANG_SYSDEFAULT = 2048
//};
enum modiocr_lang : unsigned long {
    modiocr_lang_null = 0 // failed

    , modiocr_lang_ja = 1 << 0 // miLANG_JAPANESE = 17,

    , modiocr_lang_zhs = 1 << 1 // miLANG_CHINESE_SIMPLIFIED = 2052
    , modiocr_lang_zht = 1 << 2 // miLANG_CHINESE_TRADITIONAL = 1028

    , modiocr_lang_ko = 1 << 3  // miLANG_KOREAN = 18,

    , modiocr_lang_cs = 1 << 4  // miLANG_CZECH = 5,
    , modiocr_lang_da = 1 << 5  // miLANG_DANISH = 6,
    , modiocr_lang_nl = 1 << 6  // miLANG_DUTCH = 19,
    , modiocr_lang_fi = 1 << 7  // miLANG_FINNISH = 11,
    , modiocr_lang_fr = 1 << 8  // miLANG_FRENCH = 12,
    , modiocr_lang_de = 1 << 9  // miLANG_GERMAN = 7,
    , modiocr_lang_el = 1 << 10 // miLANG_GREEK = 8,
    , modiocr_lang_hu = 1 << 11 // miLANG_HUNGARIAN = 14,
    , modiocr_lang_it = 1 << 12 // miLANG_ITALIAN = 16,
    , modiocr_lang_no = 1 << 13 // miLANG_NORWEGIAN = 20,
    , modiocr_lang_pl = 1 << 14 // miLANG_POLISH = 21,
    , modiocr_lang_pt = 1 << 15 // miLANG_PORTUGUESE = 22,
    , modiocr_lang_ru = 1 << 16 // miLANG_RUSSIAN = 25,
    , modiocr_lang_es = 1 << 17 // miLANG_SPANISH = 10,
    , modiocr_lang_sv = 1 << 18 // miLANG_SWEDISH = 29,
    , modiocr_lang_tr = 1 << 19 // miLANG_TURKISH = 31,

    , modiocr_lang_en = 1 << 20 // miLANG_ENGLISH = 9,

    , modiocr_lang_default = 1 << 21 // miLANG_SYSDEFAULT = 2048
};
typedef unsigned long modiocr_flags;

bool modiocr_available();

typedef std::function<void(const wchar_t*)> modiocr_collect_fun_t;
modiocr_lang modiocr_readfile(const wchar_t* path, modiocr_flags lang,
    const modiocr_collect_fun_t& fun);

// EOF
#pragma once
