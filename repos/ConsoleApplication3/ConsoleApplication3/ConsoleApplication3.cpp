
#include <windows.h>
#include "modiocr.h"
#include "wincom/wincomptr.h" 
#include "ccmacro.h"
#include"12.0/mdivwctl.tlh"
#include<iostream>
//#import "C:\\Program Files\\Common Files\\Microsoft Shared\\MODI\\11.0\\MDIVWCTL.DLL"
//#import "C:\\Program Files\\Common Files\\Microsoft Shared\\MODI\\12.0\\MDIVWCTL.DLL"
//#import "C:\\Program Files\\Common Files\\Microsoft Shared\\MODI\\12.0\\MDIVWCTL.DLL" \
//     raw_native_types no_namespace named_guids

//using namespace MODI;

static MiLANGUAGES _languages[] = {
  miLANG_JAPANESE   // 0

  , miLANG_CHINESE_SIMPLIFIED   // 1
  , miLANG_CHINESE_TRADITIONAL  // 2

  , miLANG_KOREAN   // 3

  , miLANG_CZECH    // 4
  , miLANG_DANISH   // 5
  , miLANG_DUTCH    // 6
  , miLANG_FINNISH  // 7
  , miLANG_FRENCH   // 8
  , miLANG_GERMAN   // 9
  , miLANG_GREEK    // 10
  , miLANG_HUNGARIAN    // 11
  , miLANG_ITALIAN  // 12
  , miLANG_NORWEGIAN    // 13
  , miLANG_POLISH   // 14
  , miLANG_PORTUGUESE   // 15
  , miLANG_RUSSIAN  // 16
  , miLANG_SPANISH  // 17
  , miLANG_SWEDISH  // 18
  , miLANG_TURKISH  // 19

  , miLANG_ENGLISH  // 20

  , miLANG_SYSDEFAULT   // 21
};

bool modiocr_available()
{
    IDocument* doc = nullptr;
    if (SUCCEEDED(::CoCreateInstance(CLSID_Document, nullptr, CLSCTX_ALL, IID_IDocument,
        reinterpret_cast<LPVOID*>(&doc))) && doc) {
        doc->Release();
        return true;
    }
    return false;
}

modiocr_lang modiocr_readfile(const wchar_t* path, modiocr_flags langs, const modiocr_collect_fun_t& fun)
{
    modiocr_lang ret = (modiocr_lang)modiocr_lang_null;
    if (CC_UNLIKELY(!path || !langs))
        return ret;

    // Use scoped pointers to release IUnknown objects
    // since these functions might raise at unknown point
    try {
        IDocument* doc = nullptr;
        if (!SUCCEEDED(::CoCreateInstance(CLSID_Document, nullptr, CLSCTX_ALL, IID_IDocument,
            reinterpret_cast<LPVOID*>(&doc)) || !doc))
            return ret;
        WinCom::ScopedUnknownPtr scoped_doc(doc);

        WinCom::ScopedBstr scoped_path(path);
        if (!SUCCEEDED(doc->Create(scoped_path.get()))) // raise when path does not exist
            return ret;

        //qDebug() << "crash here";
        //doc->OCR(miLANG_JAPANESE, VARIANT_FALSE, VARIANT_FALSE);
        //qDebug() << "succeed";

        // The OCR might raise without administrator priviledges
        // Disable change orientation and angle of the image
        // OCR(LangId, OCROrientImage, OCRStraightenImage)
        // http://msdn.microsoft.com/en-us/library/office/aa202819%28v=office.11%29.aspx
        for (int i = 0; !ret && i < sizeof(::_languages) / sizeof(*::_languages); i++)
            if ((langs & (1 << i))
                && SUCCEEDED(doc->OCR(_languages[i], VARIANT_FALSE, VARIANT_FALSE)))
                ret = modiocr_lang(1 << i);

        if (!ret)
            return ret;

        IImages* images;
        doc->get_Images(&images);
        WinCom::ScopedUnknownPtr scoped_images(images);

        long imageCount = 0;
        images->get_Count(&imageCount);
        for (long imageIndex = 0; imageIndex < imageCount; imageIndex++) {
            IImage* image;
            images->get_Item(imageIndex, reinterpret_cast<IDispatch**>(&image));
            WinCom::ScopedUnknownPtr scoped_image(image);

            ILayout* layout;
            image->get_Layout(&layout);
            WinCom::ScopedUnknownPtr scoped_layout(layout);

            IWords* words;
            layout->get_Words(&words);
            WinCom::ScopedUnknownPtr scoped_words(words);

            long wordCount = 0;
            //layout->get_NumWords(&wordCount);
            words->get_Count(&wordCount);
            for (long wordIndex = 0; wordIndex < wordCount; wordIndex++) {
                IWord* word;
                words->get_Item(wordIndex, reinterpret_cast<IDispatch**>(&word));
                WinCom::ScopedUnknownPtr scoped_word(word);

                BSTR text = nullptr;
                if (SUCCEEDED(word->get_Text(&text)) && text)
                    fun(text);
            }
        }

    }
    catch (...) { // I don't know the exact exception type
    }

    return ret;
}

int main() {
    std::cout << modiocr_available();;
}