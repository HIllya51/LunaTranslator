#include <wechatocr.h>

void *_wcocr_init(const wchar_t *wexe, const wchar_t *wwcdir)
{
    auto obj = new CWeChatOCR(wexe, wwcdir);
    if (obj->wait_connection(5000))
    {
        return obj;
    }
    else
    {
        delete obj;
        return nullptr;
    }
}

void _wcocr_destroy(void *pobj)
{
    if (!pobj)
        return;
    delete (CWeChatOCR *)pobj;
}
bool _wcocr_ocr(void *pobj, const char *u8path, void (*cb)(float, float, float, float, LPCSTR))
{
    if (!pobj)
        return false;
    CWeChatOCR::result_t res;
    if (!((CWeChatOCR *)pobj)->doOCR(u8path, &res))
        return false;
    for (auto &blk : res.ocr_response)
    {
        cb(blk.left, blk.top, blk.right, blk.bottom, blk.text.c_str());
    }
    return true;
}