// https://github.com/b1tg/win11-oneocr/blob/master/ocr.cpp
typedef struct
{
    __int32 t;
    __int32 col;
    __int32 row;
    __int32 _unk;
    __int64 step;
    __int64 data_ptr;
} Img;

typedef __int64(__cdecl *CreateOcrInitOptions_t)(__int64 *);
typedef __int64(__cdecl *GetOcrLineCount_t)(__int64, __int64 *);
typedef __int64(__cdecl *GetOcrLine_t)(__int64, __int64, __int64 *);
typedef __int64(__cdecl *GetOcrLineContent_t)(__int64, __int64 *);
typedef __int64(__cdecl *GetOcrLineBoundingBox_t)(__int64, __int64 *);
typedef __int64(__cdecl *GetOcrLineWordCount_t)(__int64, __int64 *);
typedef __int64(__cdecl *GetOcrWord_t)(__int64, __int64, __int64 *);
typedef __int64(__cdecl *GetOcrWordContent_t)(__int64, __int64 *);
typedef __int64(__cdecl *GetOcrWordBoundingBox_t)(__int64, __int64 *);
typedef __int64(__cdecl *OcrProcessOptionsSetMaxRecognitionLineCount_t)(__int64, __int64);
typedef __int64(__cdecl *RunOcrPipeline_t)(__int64, Img *, __int64, __int64 *);
typedef __int64(__cdecl *CreateOcrProcessOptions_t)(__int64 *);
typedef __int64(__cdecl *OcrInitOptionsSetUseModelDelayLoad_t)(__int64, char);
typedef __int64(__cdecl *CreateOcrPipeline_t)(const char *, const char *, __int64, __int64 *);
typedef void(__cdecl *ReleaseOcrResult_t)(__int64);

#define GetProc(Name) Name##_t Name = (Name##_t)GetProcAddress(hDLL, #Name);

int SnippingTool(int argc, wchar_t *argv[])
{

    HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    auto handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, 1024 * 1024 * 16, argv[3]);

    auto mapview = (char *)MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, 1024 * 1024 * 16);
    memset(mapview, 0, 1024 * 1024 * 16);

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
    if (!ConnectNamedPipe(hPipe, NULL))
        return 0;
    auto onnxruntime = std::filesystem::current_path() / "onnxruntime.dll";
    auto oneocr = std::filesystem::current_path() / "oneocr.dll";
    HINSTANCE hDLL2 = LoadLibraryA(onnxruntime.string().c_str());
    HINSTANCE hDLL = LoadLibraryA(oneocr.string().c_str());
    if (hDLL == NULL)
    {
        std::cerr << "Failed to load DLL: " << GetLastError() << std::endl;
        return 0;
    }
    // Get function pointers
    GetProc(ReleaseOcrResult);
    GetProc(CreateOcrInitOptions);
    GetProc(CreateOcrProcessOptions);
    GetProc(CreateOcrPipeline);
    GetProc(OcrInitOptionsSetUseModelDelayLoad);
    GetProc(OcrProcessOptionsSetMaxRecognitionLineCount);
    GetProc(RunOcrPipeline);
    GetProc(GetOcrLine);
    GetProc(GetOcrLineContent);
    GetProc(GetOcrLineCount);
    GetProc(GetOcrLineBoundingBox);
    GetProc(GetOcrLineWordCount);
    GetProc(GetOcrWord);
    GetProc(GetOcrWordContent);
    GetProc(GetOcrWordBoundingBox);
    __int64 ctx = 0;
    __int64 pipeline = 0;
    __int64 opt = 0;
    __int64 instance = 0;
    __int64 res = CreateOcrInitOptions(&ctx);
    assert(res == 0);
    res = OcrInitOptionsSetUseModelDelayLoad(ctx, 0);
    assert(res == 0);
    // key: kj)TGtrK>f]b[Piow.gU+nC@s""""""4
    const char *key = {"kj)TGtrK>f]b[Piow.gU+nC@s\"\"\"\"\"\"4"};
    auto model = std::filesystem::current_path() / "oneocr.onemodel";
    res = CreateOcrPipeline(model.string().c_str(), key, ctx, &pipeline);
    printf("OCR model loaded...\n");
    //  printf("res: %lld, ctx: 0x%llx, pipeline: 0x%llx\n", res, ctx, pipeline);
    //  The key is for the AI model, if key is not right, CreateOcrPipeline will
    //  return 6 with error message: Crypto.cpp:78 Check failed: meta->magic_number
    //  == MAGIC_NUMBER (0 vs. 1) Unable to uncompress. Source data mismatch.
    res = CreateOcrProcessOptions(&opt);
    assert(res == 0);
    res = OcrProcessOptionsSetMaxRecognitionLineCount(opt, 1000);
    DWORD _;
    while (true)
    {
        Img img;
        if (!ReadFile(hPipe, &img, sizeof(Img), &_, NULL))
            break;
        img.data_ptr = (decltype(img.data_ptr))mapview;

        res = RunOcrPipeline(pipeline, &img, opt, &instance);

        __int64 lc;
        auto succ = GetOcrLineCount(instance, &lc);
        assert(succ == 0);
        printf("Recognize %lld lines\n", lc);
        DWORD _;
        WriteFile(hPipe, &lc, sizeof(lc), &_, NULL);
        for (__int64 lci = 0; lci < lc; lci++)
        {
            int len = 0;
            __int64 line = 0;
            __int64 v106 = 0;
            GetOcrLine(instance, lci, &line);
            if (!line)
            {
                WriteFile(hPipe, &len, 4, &_, NULL);
                continue;
            }
            __int64 line_content = 0;
            GetOcrLineContent(line, &line_content);
            char *lcs = reinterpret_cast<char *>(line_content);
            printf("%02lld: %s\n", lci, lcs);
            len = strlen(lcs);

            WriteFile(hPipe, &len, 4, &_, NULL);
            if (len)
                WriteFile(hPipe, lcs, len, &_, NULL);

            GetOcrLineBoundingBox(line, &v106);
            // WriteFile(hPipe, &v106, 8, &_, NULL);
            WriteFile(hPipe, (void *)v106, 32, &_, NULL);
            // __int64 lr = 0;
            // GetOcrLineWordCount(line, &lr);
            // for (__int64 j = 0; j < lr; j++)
            // {
            //     __int64 v105 = 0;
            //     __int64 v107 = 0;
            //     __int64 lpMultiByteStr = 0;
            //     GetOcrWord(line, j, &v105);
            //     GetOcrWordContent(v105, &lpMultiByteStr);
            //     GetOcrWordBoundingBox(v105, &v107);
            // }
        }
        ReleaseOcrResult(res);
    }
    return 0;
}