
bool ehndSupport = false;
class CTransEngine
{
public:
    CTransEngine();
    bool Init(std::wstring &szTransPath);
    void GetEnginePath(std::wstring szEnginePath);
    ~CTransEngine();

    void J2K_FreeMem(void *addr);
    void J2K_GetPriorDict(void);
    void J2K_GetProperty(void);
    void J2K_Initialize(void);
    bool J2K_InitializeEx(char *data0, const char *key);
    void J2K_ReloadUserDict();
    void J2K_SetDelJPN();
    void J2K_SetField();
    void J2K_SetHnj2han();
    void J2K_SetJWin();
    void J2K_SetPriorDict();
    void J2K_SetProperty();
    void J2K_StopTranslation();
    void J2K_Terminate();
    void J2K_TranslateChat();
    void J2K_TranslateFM();
    void J2K_TranslateMM();
    void J2K_TranslateMMEx();
    ;
    int J2K_TranslateMMNT(int data0, char *krStr);
    int J2K_TranslateMMNTW(int data0, wchar_t *krStr);

private:
    static int ezt_addr[20];
    wchar_t EnginePath[MAX_PATH];
};

static CRITICAL_SECTION CriticalSection;
int CTransEngine::ezt_addr[20];
CTransEngine::CTransEngine()
{
    // InitializeCriticalSection(&CriticalSection);
}

void CTransEngine::GetEnginePath(std::wstring szEnginePath)
{
    szEnginePath = EnginePath;
}

bool CTransEngine::Init(std::wstring &szEnginePath)
{
    // Load ezTrans Engine
    std::wstring szEngineDLL = szEnginePath + L"\\J2KEngine.dll";
    HMODULE hDLL = LoadLibrary(szEngineDLL.c_str());
    if (!hDLL)
        MessageBox(0, L"이지트랜스 번역 엔진 초기화 실패\r\n: LoadLibrary Failed", 0, MB_ICONERROR);

    wcscpy_s(EnginePath, szEngineDLL.c_str());

    // Load ezTrans Function
    ezt_addr[0] = (int)GetProcAddress(hDLL, "J2K_FreeMem");
    ezt_addr[1] = (int)GetProcAddress(hDLL, "J2K_GetPriorDict");
    ezt_addr[2] = (int)GetProcAddress(hDLL, "J2K_GetProperty");
    ezt_addr[3] = (int)GetProcAddress(hDLL, "J2K_Initialize");
    ezt_addr[4] = (int)GetProcAddress(hDLL, "J2K_InitializeEx");
    ezt_addr[5] = (int)GetProcAddress(hDLL, "J2K_ReloadUserDict");
    ezt_addr[6] = (int)GetProcAddress(hDLL, "J2K_SetDelJPN");
    ezt_addr[7] = (int)GetProcAddress(hDLL, "J2K_SetField");
    ezt_addr[8] = (int)GetProcAddress(hDLL, "J2K_SetHnj2han");
    ezt_addr[9] = (int)GetProcAddress(hDLL, "J2K_SetJWin");
    ezt_addr[10] = (int)GetProcAddress(hDLL, "J2K_SetPriorDict");
    ezt_addr[11] = (int)GetProcAddress(hDLL, "J2K_SetProperty");
    ezt_addr[12] = (int)GetProcAddress(hDLL, "J2K_StopTranslation");
    ezt_addr[13] = (int)GetProcAddress(hDLL, "J2K_Terminate");
    ezt_addr[14] = (int)GetProcAddress(hDLL, "J2K_TranslateChat");
    ezt_addr[15] = (int)GetProcAddress(hDLL, "J2K_TranslateFM");
    ezt_addr[16] = (int)GetProcAddress(hDLL, "J2K_TranslateMM");
    ezt_addr[17] = (int)GetProcAddress(hDLL, "J2K_TranslateMMEx");
    ezt_addr[18] = (int)GetProcAddress(hDLL, "J2K_TranslateMMNT");
    ezt_addr[19] = (int)GetProcAddress(hDLL, "J2K_TranslateMMNTW");

    for (int i = 0; i <= 18; i++)
        if (!ezt_addr[i])
        {
            MessageBox(0, L"이지트랜스 번역 엔진 초기화 실패\r\n: 함수 정보 불러오기 실패", 0, MB_ICONERROR);
            return false;
        }

    if (ezt_addr[19])
        ehndSupport = true;

    Sleep(50);

    std::wstring _szEngineDAT = szEnginePath + L"\\Dat";
    std::string szEngineDAT = WideStringToString(_szEngineDAT, CP_ACP);
    char key[] = "CSUSER123455";
    if (J2K_InitializeEx(key, szEngineDAT.c_str()))
        return true;
    return false;
}

__declspec(naked) void CTransEngine::J2K_FreeMem(void *addr)
{
    __asm JMP ezt_addr + (4 * 0)
}
__declspec(naked) void CTransEngine::J2K_GetPriorDict(void)
{
    __asm JMP ezt_addr + (4 * 1)
}
__declspec(naked) void CTransEngine::J2K_GetProperty(void)
{
    __asm JMP ezt_addr + (4 * 2)
}
__declspec(naked) void CTransEngine::J2K_Initialize(void)
{
    __asm JMP ezt_addr + (4 * 3)
}
__declspec(naked) bool CTransEngine::J2K_InitializeEx(char *data0, const char *key)
{
    __asm JMP ezt_addr + (4 * 4)
}
__declspec(naked) void CTransEngine::J2K_ReloadUserDict()
{
    __asm JMP ezt_addr + (4 * 5)
}
__declspec(naked) void CTransEngine::J2K_SetDelJPN()
{
    __asm JMP ezt_addr + (4 * 6)
}
__declspec(naked) void CTransEngine::J2K_SetField()
{
    __asm JMP ezt_addr + (4 * 7)
}
__declspec(naked) void CTransEngine::J2K_SetHnj2han()
{
    __asm JMP ezt_addr + (4 * 8)
}
__declspec(naked) void CTransEngine::J2K_SetJWin()
{
    __asm JMP ezt_addr + (4 * 9)
}
__declspec(naked) void CTransEngine::J2K_SetPriorDict()
{
    __asm JMP ezt_addr + (4 * 10)
}
__declspec(naked) void CTransEngine::J2K_SetProperty()
{
    __asm JMP ezt_addr + (4 * 11)
}
__declspec(naked) void CTransEngine::J2K_StopTranslation()
{
    __asm JMP ezt_addr + (4 * 12)
}
__declspec(naked) void CTransEngine::J2K_Terminate()
{
    __asm JMP ezt_addr + (4 * 13)
}
__declspec(naked) void CTransEngine::J2K_TranslateChat()
{
    __asm JMP ezt_addr + (4 * 14)
}
__declspec(naked) void CTransEngine::J2K_TranslateFM()
{
    __asm JMP ezt_addr + (4 * 15)
}
__declspec(naked) void CTransEngine::J2K_TranslateMM()
{
    __asm JMP ezt_addr + (4 * 16)
}
__declspec(naked) void CTransEngine::J2K_TranslateMMEx()
{
    __asm JMP ezt_addr + (4 * 17)
}
__declspec(naked) int CTransEngine::J2K_TranslateMMNT(int data0, char *krStr)
{
    __asm JMP ezt_addr + (4 * 18)
}

__declspec(naked) int CTransEngine::J2K_TranslateMMNTW(int data0, wchar_t *krStr){
    __asm JMP ezt_addr + (4 * 19)}

CTransEngine::~CTransEngine()
{
    // DeleteCriticalSection(&CriticalSection);
    // Cl.TransEngine = 0;
}

std::wstring replaceAll(const std::wstring &str, const std::wstring &pattern, const std::wstring &replace)
{
    std::wstring result = str;
    std::wstring::size_type pos = 0;
    std::wstring::size_type offset = 0;

    while ((pos = result.find(pattern, offset)) != std::string::npos)
    {
        result.replace(result.begin() + pos, result.begin() + pos + pattern.size(), replace);
        offset = pos + replace.size();
    }

    return result;
}
namespace CTextProcess
{
    std::optional<std::wstring> eztrans_proc(const std::wstring &input);
    std::wstring HangulEncode(const std::wstring &input);
    std::wstring HangulDecode(const std::wstring &input);
}
std::wstring CTextProcess::HangulEncode(const std::wstring &input)
{
    std::wstring output;
    wchar_t buf[8];

    std::wstring::const_iterator it = input.begin();
    for (; it != input.end(); it++)
    {
        if (*it == L'@' ||
            (*it == '\0') ||
            (*it >= 0x1100 && *it <= 0x11FF) || (*it >= 0x3130 && *it <= 0x318F) ||
            (*it >= 0xA960 && *it <= 0xA97F) || (*it >= 0xAC00 && *it <= 0xD7AF) ||
            (*it >= 0xD7B0 && *it <= 0xD7FF))
        {
            swprintf_s(buf, L"+x%04X", *it);
            output += buf;
        }
        else
        {
            switch (*it)
            {
            case L'↔':
            case L'◁':
            case L'◀':
            case L'▷':
            case L'▶':
            case L'♤':
            case L'♠':
            case L'♡':
            case L'♥':
            case L'♧':
            case L'♣':
            case L'⊙':
            case L'◈':
            case L'▣':
            case L'◐':
            case L'◑':
            case L'▒':
            case L'▤':
            case L'▥':
            case L'▨':
            case L'▧':
            case L'▦':
            case L'▩':
            case L'♨':
            case L'☏':
            case L'☎':
            case L'☜':
            case L'☞':
            case L'↕':
            case L'↗':
            case L'↙':
            case L'↖':
            case L'↘':
            case L'♩':
            case L'♬':
            case L'㉿':
            case L'㈜':
            case L'㏇':
            case L'™':
            case L'㏂':
            case L'㏘':
            case L'＂':
            case L'＇':
            case L'∼':
            case L'ˇ':
            case L'˘':
            case L'˝':
            case L'¡':
            case L'˚':
            case L'˙':
            case L'˛':
            case L'¿':
            case L'ː':
            case L'∏':
            case L'￦':
            case L'℉':
            case L'€':
            case L'㎕':
            case L'㎖':
            case L'㎗':
            case L'ℓ':
            case L'㎘':
            case L'㎣':
            case L'㎤':
            case L'㎥':
            case L'㎦':
            case L'㎙':
            case L'㎚':
            case L'㎛':
            case L'㎟':
            case L'㎠':
            case L'㎢':
            case L'㏊':
            case L'㎍':
            case L'㏏':
            case L'㎈':
            case L'㎉':
            case L'㏈':
            case L'㎧':
            case L'㎨':
            case L'㎰':
            case L'㎱':
            case L'㎲':
            case L'㎳':
            case L'㎴':
            case L'㎵':
            case L'㎶':
            case L'㎷':
            case L'㎸':
            case L'㎀':
            case L'㎁':
            case L'㎂':
            case L'㎃':
            case L'㎄':
            case L'㎺':
            case L'㎻':
            case L'㎼':
            case L'㎽':
            case L'㎾':
            case L'㎿':
            case L'㎐':
            case L'㎑':
            case L'㎒':
            case L'㎓':
            case L'㎔':
            case L'Ω':
            case L'㏀':
            case L'㏁':
            case L'㎊':
            case L'㎋':
            case L'㎌':
            case L'㏖':
            case L'㏅':
            case L'㎭':
            case L'㎮':
            case L'㎯':
            case L'㏛':
            case L'㎩':
            case L'㎪':
            case L'㎫':
            case L'㎬':
            case L'㏝':
            case L'㏐':
            case L'㏓':
            case L'㏃':
            case L'㏉':
            case L'㏜':
            case L'㏆':
            case L'┒':
            case L'┑':
            case L'┚':
            case L'┙':
            case L'┖':
            case L'┕':
            case L'┎':
            case L'┍':
            case L'┞':
            case L'┟':
            case L'┡':
            case L'┢':
            case L'┦':
            case L'┧':
            case L'┪':
            case L'┭':
            case L'┮':
            case L'┵':
            case L'┶':
            case L'┹':
            case L'┺':
            case L'┽':
            case L'┾':
            case L'╀':
            case L'╁':
            case L'╃':
            case L'╄':
            case L'╅':
            case L'╆':
            case L'╇':
            case L'╈':
            case L'╉':
            case L'╊':
            case L'┱':
            case L'┲':
            case L'ⅰ':
            case L'ⅱ':
            case L'ⅲ':
            case L'ⅳ':
            case L'ⅴ':
            case L'ⅵ':
            case L'ⅶ':
            case L'ⅷ':
            case L'ⅸ':
            case L'ⅹ':
            case L'½':
            case L'⅓':
            case L'⅔':
            case L'¼':
            case L'¾':
            case L'⅛':
            case L'⅜':
            case L'⅝':
            case L'⅞':
            case L'ⁿ':
            case L'₁':
            case L'₂':
            case L'₃':
            case L'₄':
            case L'Ŋ':
            case L'đ':
            case L'Ħ':
            case L'Ĳ':
            case L'Ŀ':
            case L'Ł':
            case L'Œ':
            case L'Ŧ':
            case L'ħ':
            case L'ı':
            case L'ĳ':
            case L'ĸ':
            case L'ŀ':
            case L'ł':
            case L'œ':
            case L'ŧ':
            case L'ŋ':
            case L'ŉ':
            case L'㉠':
            case L'㉡':
            case L'㉢':
            case L'㉣':
            case L'㉤':
            case L'㉥':
            case L'㉦':
            case L'㉧':
            case L'㉨':
            case L'㉩':
            case L'㉪':
            case L'㉫':
            case L'㉬':
            case L'㉭':
            case L'㉮':
            case L'㉯':
            case L'㉰':
            case L'㉱':
            case L'㉲':
            case L'㉳':
            case L'㉴':
            case L'㉵':
            case L'㉶':
            case L'㉷':
            case L'㉸':
            case L'㉹':
            case L'㉺':
            case L'㉻':
            case L'㈀':
            case L'㈁':
            case L'㈂':
            case L'㈃':
            case L'㈄':
            case L'㈅':
            case L'㈆':
            case L'㈇':
            case L'㈈':
            case L'㈉':
            case L'㈊':
            case L'㈋':
            case L'㈌':
            case L'㈍':
            case L'㈎':
            case L'㈏':
            case L'㈐':
            case L'㈑':
            case L'㈒':
            case L'㈓':
            case L'㈔':
            case L'㈕':
            case L'㈖':
            case L'㈗':
            case L'㈘':
            case L'㈙':
            case L'㈚':
            case L'㈛':
            case L'ⓐ':
            case L'ⓑ':
            case L'ⓒ':
            case L'ⓓ':
            case L'ⓔ':
            case L'ⓕ':
            case L'ⓖ':
            case L'ⓗ':
            case L'ⓘ':
            case L'ⓙ':
            case L'ⓚ':
            case L'ⓛ':
            case L'ⓜ':
            case L'ⓝ':
            case L'ⓞ':
            case L'ⓟ':
            case L'ⓠ':
            case L'ⓡ':
            case L'ⓢ':
            case L'ⓣ':
            case L'ⓤ':
            case L'ⓥ':
            case L'ⓦ':
            case L'ⓧ':
            case L'ⓨ':
            case L'ⓩ':
            case L'①':
            case L'②':
            case L'③':
            case L'④':
            case L'⑤':
            case L'⑥':
            case L'⑦':
            case L'⑧':
            case L'⑨':
            case L'⑩':
            case L'⑪':
            case L'⑫':
            case L'⑬':
            case L'⑭':
            case L'⑮':
            case L'⒜':
            case L'⒝':
            case L'⒞':
            case L'⒟':
            case L'⒠':
            case L'⒡':
            case L'⒢':
            case L'⒣':
            case L'⒤':
            case L'⒥':
            case L'⒦':
            case L'⒧':
            case L'⒨':
            case L'⒩':
            case L'⒪':
            case L'⒫':
            case L'⒬':
            case L'⒭':
            case L'⒮':
            case L'⒯':
            case L'⒰':
            case L'⒱':
            case L'⒲':
            case L'⒳':
            case L'⒴':
            case L'⒵':
            case L'⑴':
            case L'⑵':
            case L'⑶':
            case L'⑷':
            case L'⑸':
            case L'⑹':
            case L'⑺':
            case L'⑻':
            case L'⑼':
            case L'⑽':
            case L'⑾':
            case L'⑿':
            case L'⒀':
            case L'⒁':
            case L'⒂':
                swprintf_s(buf, L"+X%04X", *it);
                output += buf;
                break;
            default:
                output += *it;
                break;
            }
        }
    }

    return output;
}
std::wstring CTextProcess::HangulDecode(const std::wstring &input)
{
    std::wstring output;
    wchar_t buf[8];
    std::wstring::const_iterator it = input.begin();
    for (DWORD count = 0; it != input.end(); it++, count++)
    {
        // @X = 삭제
        if (count + 2 < input.length() && (*it) == L'@' && *(it + 1) == L'X' && *(it + 2) == L'@')
        {
            it += 2;
            count += 2;
            continue;
        }
        else if (count + 5 < input.length() && *(it) == '+' && (*(it + 1) == 'x' || *(it + 1) == 'X') &&
                 ((*(it + 2) >= L'A' && *(it + 2) <= L'Z') || (*(it + 2) >= L'a' && *(it + 2) <= L'z') || (*(it + 2) >= L'0' && *(it + 2) <= L'9')) &&
                 ((*(it + 3) >= L'A' && *(it + 3) <= L'Z') || (*(it + 3) >= L'a' && *(it + 3) <= L'z') || (*(it + 3) >= L'0' && *(it + 3) <= L'9')) &&
                 ((*(it + 4) >= L'A' && *(it + 4) <= L'Z') || (*(it + 4) >= L'a' && *(it + 4) <= L'z') || (*(it + 4) >= L'0' && *(it + 4) <= L'9')) &&
                 ((*(it + 5) >= L'A' && *(it + 5) <= L'Z') || (*(it + 5) >= L'a' && *(it + 5) <= L'z') || (*(it + 5) >= L'0' && *(it + 5) <= L'9')))
        {
            buf[0] = *(it + 2);
            buf[1] = *(it + 3);
            buf[2] = *(it + 4);
            buf[3] = *(it + 5);
            buf[4] = 0x00;

            swscanf_s(buf, L"%04x", (unsigned int *)&buf[0]);

            output += buf;
            it += 5;
            count += 5;
        }

        else
        {
            output += (*it);
        }
    }
    return output;
}

int Elapsed_Prepare = 0;
int Elapsed_Translate = 0;
CTransEngine *TransEngine;
std::optional<std::wstring> CTextProcess::eztrans_proc(const std::wstring &input)
{
    int nBufLen;
    char *szBuff, *szBuff2;
    wchar_t *lpszBuff;
    std::wstring szContext, output;

    szContext = HangulEncode(input);

    // 이지트랜스 오류 잡아주기
    // 「よろしければ今度２人でお話しなどできないでしょうか」
    szContext = replaceAll(szContext, L"できないでしょ", L"@X@でき@X@ないでしょ");
    szContext = replaceAll(szContext, L"きないでしょ", L"き@X@ないでしょ");
    szContext = replaceAll(szContext, L"でき@X@ないでしょ", L"できないでしょ");

    if (ehndSupport)
    {
        lpszBuff = (wchar_t *)TransEngine->J2K_TranslateMMNTW(0, (wchar_t *)szContext.c_str());
        output = lpszBuff;
        TransEngine->J2K_FreeMem(lpszBuff);
    }
    else
    {
        nBufLen = WideCharToMultiByte(932, 0, szContext.c_str(), -1, NULL, NULL, NULL, NULL);
        szBuff = new char[((nBufLen + 2) * 2)];

        if (szBuff == NULL)
        {
            // MessageBox(0, L"메모리 할당 실패", 0, 0);
            return {};
        }
        WideCharToMultiByte(932, 0, szContext.c_str(), -1, szBuff, nBufLen, NULL, NULL);
        szBuff2 = (char *)TransEngine->J2K_TranslateMMNT(0, szBuff);
        delete[] szBuff;

        nBufLen = MultiByteToWideChar(949, 0, szBuff2, -1, NULL, NULL);
        lpszBuff = new wchar_t[((nBufLen + 2) * 2)];

        if (lpszBuff == NULL)
        {
            // MessageBox(0, L"메모리 할당 실패", 0, 0);
            return {};
        }

        MultiByteToWideChar(949, 0, szBuff2, -1, lpszBuff, nBufLen);

        output = lpszBuff;
        delete[] lpszBuff;
        TransEngine->J2K_FreeMem(szBuff2);
    }
    output = HangulDecode(output);
    return output;
}
void writestring(const wchar_t *text, HANDLE hPipe);

int eztrans(int argc, wchar_t *argv[])
{
    HANDLE hPipe = CreateNamedPipe(argv[2], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    // system("chcp 932");

    std::wstring _p = argv[1]; //// LR"(C:\Program Files\ChangShinSoft\ezTrans XP)";
    TransEngine = new CTransEngine();
    TransEngine->Init(_p);

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[3]));
    if (!ConnectNamedPipe(hPipe, NULL))
        return 0;
    WCHAR buff[6000];
    while (true)
    {
        DWORD _;
        ZeroMemory(buff, 12000);
        if (!ReadFile(hPipe, buff, 12000, &_, NULL))
            break;
        auto trans = CTextProcess::eztrans_proc(buff);
        if (trans)
            writestring(trans.value().c_str(), hPipe);
        else
            writestring(0, hPipe);
    }

    return 0;
}