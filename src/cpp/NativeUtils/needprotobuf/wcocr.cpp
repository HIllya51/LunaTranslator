void *_wcocr_init(const wchar_t *wexe, const wchar_t *wwcdir);
void _wcocr_destroy(void *pobj);
bool _wcocr_ocr(void *pobj, const char *u8path, void (*cb)(float, float, float, float, LPCSTR));

DECLARE_API void *wcocr_init(const wchar_t *wexe, const wchar_t *wwcdir)
{
    return _wcocr_init(wexe, wwcdir);
}

DECLARE_API void wcocr_destroy(void *pobj)
{
    _wcocr_destroy(pobj);
}
DECLARE_API bool wcocr_ocr(void *pobj, const char *u8path, void (*cb)(float, float, float, float, LPCSTR))
{
    return _wcocr_ocr(pobj, u8path, cb);
}