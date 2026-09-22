// https://github.com/microsoft/PowerToys/tree/main/src/modules/FileLocksmith/FileLocksmithLibInterop
#include <FileLocksmith.h>
#include <base64.h>
#include "../NativeUtils/dllanalysis.hpp"

std::wstring readfile(const wchar_t *fname)
{
    FILE *f;
    _wfopen_s(&f, fname, L"rb");
    if (f == 0)
        return {};
    fseek(f, 0, SEEK_END);
    auto len = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::wstring buff;
    buff.resize(len / 2);
    fread(buff.data(), 1, len, f);
    fclose(f);
    return buff;
}
template <class StringT>
inline std::vector<StringT> strSplit_impl(const StringT &s, const StringT &delim)
{
    StringT item;
    std::vector<StringT> tokens;

    StringT str = s;

    size_t pos = 0;
    while ((pos = str.find(delim)) != StringT::npos)
    {
        item = str.substr(0, pos);
        tokens.push_back(item);
        str.erase(0, pos + delim.length());
    }
    tokens.push_back(str);
    return tokens;
}
// 更新防损坏：
// false = 尚在等待/检查阶段，看门狗超时后可直接强杀进程；
// true  = 正在改动文件系统，强杀会把更新做成半截，看门狗只能先请求协作中止。
static std::atomic<bool> g_mutating{false};
// 看门狗发出的协作中止请求，复制循环在每个文件之间检查。
static std::atomic<bool> g_abort{false};
void autoexitafter1min()
{
    // 1min后强制退出进程。避免卡死。
    // 注意：一旦开始改动文件系统就不能直接杀（ExitProcess不走异常回滚）。
    // 等待/检查阶段卡死1min→直接退出；进入突变阶段后重新计时，卡死1min才请求
    // 协作中止（复制循环在文件之间检查g_abort并回滚），再1min无响应才最后手段强杀。
    std::thread([]()
                {
    bool was_mutating = false;
    int idle = 0, busy = 0;
    for (;;)
    {
        Sleep(1000);
        if (!g_mutating)
        {
            if (was_mutating)
                return; // 突变已收尾（无论成败），看门狗正常退出
            if (++idle >= 60)
                ExitProcess(0); // 等待阶段卡死
        }
        else
        {
            was_mutating = true;
            if (++busy == 60)
                g_abort = true; // 突变阶段卡死，请求协作中止
            if (busy >= 120)
                ExitProcess(0); // 请求中止后仍无响应，最后手段
        }
    } })
        .detach();
}
void keeponnxruntimeopenvino()
{
    auto exports = exportAnalysis(LR"(.\files_old\DLL64\onnxruntime.dll)");
    bool found = false;
    for (auto &f : exports)
    {
        if (f == "OrtSessionOptionsAppendExecutionProvider_OpenVINO")
        {
            found = true;
            break;
        }
    }
    if (!found)
        return;
    std::filesystem::copy(LR"(.\files_old\DLL64)", LR"(.\files\DLL64)", std::filesystem::copy_options::recursive | std::filesystem::copy_options::skip_existing);
    std::filesystem::copy(LR"(.\files_old\DLL64\onnxruntime.dll)", LR"(.\files\DLL64\onnxruntime.dll)", std::filesystem::copy_options::overwrite_existing);
}
static bool patheq_under_ignore_case(const std::wstring &path, const std::wstring &prefix)
{
    // path是否严格位于prefix目录之下（大小写不敏感，按分隔符边界）
    auto tolower_ = [](std::wstring s)
    {
        std::transform(s.begin(), s.end(), s.begin(), ::towlower);
        return s;
    };
    auto p = tolower_(path), b = tolower_(prefix);
    while (!b.empty() && (b.back() == L'\\' || b.back() == L'/'))
        b.pop_back();
    if (b.empty())
        return false;
    return p.size() > b.size() && p.compare(0, b.size(), b) == 0 && (p[b.size()] == L'\\' || p[b.size()] == L'/');
}
static void clear_readonly(const std::filesystem::path &p)
{
    // MoveFileEx(REPLACE_EXISTING)无法覆盖只读目标，先清掉只读位
    auto attr = GetFileAttributesW(p.c_str());
    if (attr != INVALID_FILE_ATTRIBUTES && (attr & FILE_ATTRIBUTE_READONLY))
        SetFileAttributesW(p.c_str(), attr & ~FILE_ATTRIBUTE_READONLY);
}
static void copyfile_atomic(const std::filesystem::path &src, const std::filesystem::path &dst)
{
    // 先写同目录临时文件再原子替换：目标文件任何时刻要么是旧内容要么是新内容，绝不半截。
    // （std::filesystem::copy直接CopyFileW覆盖，中途被杀会留下截断文件）
    auto tmp = dst;
    tmp += L".lunaupdate.tmp";
    clear_readonly(tmp); // 上次失败可能残留
    if (!CopyFileW(src.c_str(), tmp.c_str(), FALSE))
        throw std::runtime_error("copy failed: " + src.string());
    clear_readonly(dst);
    if (!MoveFileExW(tmp.c_str(), dst.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH))
    {
        DeleteFileW(tmp.c_str());
        throw std::runtime_error("replace failed: " + dst.string());
    }
}
static void copytree_for_update(const std::filesystem::path &src, const std::filesystem::path &dst)
{
    std::error_code ec;
    std::filesystem::create_directories(dst, ec);
    for (auto it = std::filesystem::recursive_directory_iterator(src);
         it != std::filesystem::recursive_directory_iterator(); ++it)
    {
        if (g_abort)
            throw std::runtime_error("update aborted by watchdog");
        auto target = dst / std::filesystem::relative(it->path(), src);
        if (it->is_symlink(ec))
        {
            it.disable_recursion_pending();
            continue;
        }
        if (it->is_directory(ec))
            std::filesystem::create_directories(target, ec);
        else if (it->is_regular_file(ec))
            copyfile_atomic(it->path(), target);
    }
}
static void copyupdate(const std::filesystem::path &src, const std::filesystem::path &dst)
{
    // 顶层跳过cache（更新暂存与Updater自身所在目录）和files_old（旧文件备份）
    static const wchar_t *skipdirs[] = {L"cache", L"files_old"};
    // 先复制目录树（大块，中途失败最可能发生在这里），后复制顶层文件（量少，窗口小）。
    // 配合顶层文件事先挪入备份目录，任何时刻失败都能整体回滚到旧版本。
    for (auto &entry : std::filesystem::directory_iterator(src))
    {
        if (g_abort)
            throw std::runtime_error("update aborted by watchdog");
        std::error_code ec;
        if (!entry.is_directory(ec))
            continue;
        auto name = entry.path().filename();
        bool skip = false;
        for (auto s : skipdirs)
            if (name == s)
                skip = true;
        if (skip)
            continue;
        copytree_for_update(entry.path(), dst / name);
    }
    for (auto &entry : std::filesystem::directory_iterator(src))
    {
        if (g_abort)
            throw std::runtime_error("update aborted by watchdog");
        std::error_code ec;
        if (entry.is_regular_file(ec))
            copyfile_atomic(entry.path(), dst / entry.path().filename());
    }
}
int updatewmain(int argc, wchar_t *argv[])
{
    // argv: update needreload packdir pid b64texts —— argv[1..4]缺一不可，
    // 否则_wtoi/base64/后续的remove_all(argv[2])都会作用在越界读到的垃圾上
    if (argc <= 4)
        return 0;
    SetProcessDPIAware();
    CHandle hMutex{CreateMutex(NULL, FALSE, L"LUNA_UPDATER_SINGLE")};

    if (GetLastError() == ERROR_ALREADY_EXISTS)
        return 0;
    autoexitafter1min();
    auto pid = _wtoi(argv[3]);
    CHandle hProcess{OpenProcess(SYNCHRONIZE, FALSE, pid)};
    if (hProcess)
    {
        WaitForSingleObject(hProcess, INFINITE);
    }
    for (int i = 0; i < 2; i++)
    {
        CHandle semaphore{CreateMutex(NULL, FALSE, L"LUNA_UPDATER_BLOCK")};
        if (GetLastError() != ERROR_ALREADY_EXISTS)
            break;
        Sleep(1000);
    }
    WCHAR path[MAX_PATH];
    if (!GetModuleFileNameW(GetModuleHandle(0), path, MAX_PATH))
        return 0;
    // 本进程应位于 <root>\cache\update\Updater.exe，向上三级得到root
    auto p1 = wcsrchr(path, L'\\');
    if (!p1)
        return 0;
    *p1 = 0;
    auto p2 = wcsrchr(path, L'\\');
    if (!p2)
        return 0;
    *p2 = 0;
    auto p3 = wcsrchr(path, L'\\');
    if (!p3)
        return 0;
    *p3 = 0;

    SetCurrentDirectory(path);
    // 校验目录没错位（例如被从别处手动运行），避免对错误的目录做增删
    if (!std::filesystem::is_directory(L".\\files"))
        return 0;
    int needreload = _wtoi(argv[1]);
    auto file = StringToWideString(base64_decode(WideStringToString(argv[4])));
    auto ss = strSplit_impl<std::wstring>(file, L"\n");
    if (ss.size() < 5)
        return 0;
    std::wstring text_error = ss[0], text_succ = ss[1], text_update_failed = ss[2], text_update_succ = ss[3], text_failed_occupied = ss[4];
    // 更新包目录：解析为绝对路径后，必须位于root之下、且确实是含LunaTranslator.exe的目录。
    // 参数错位（旧版调用方式/手动执行）时，防止copy/remove_all作用到任意路径。
    std::filesystem::path pack = std::filesystem::path(argv[2]);
    if (pack.is_relative())
        pack = std::filesystem::absolute(pack);
    auto root = std::filesystem::current_path().wstring();
    if (!patheq_under_ignore_case(pack.wstring(), root) ||
        !std::filesystem::is_regular_file(pack / L"LunaTranslator.exe"))
        return 0;

    auto processes = find_processes_recursive({L".\\files"});
    if (processes.size())
    {
        // 杀毒/索引器的瞬时占用很常见，重试几次再判定，避免更新被误杀软静默放弃
        for (int i = 0; i < 3 && processes.size(); i++)
        {
            Sleep(1000);
            processes = find_processes_recursive({L".\\files"});
        }
    }
    if (processes.size())
    {
        // 仍被占用则放弃本次更新（绝不杀进程：可能是挂着hook的游戏进程）。
        // 用户主动触发的更新要把程序拉起来，否则用户会发现程序没了
        if (needreload)
            ShellExecute(0, L"open", L".\\LunaTranslator.exe", NULL, NULL, SW_SHOWNORMAL);
        return 0;
    }
    bool files_moved = false;
    g_mutating = true; // 之后看门狗不再无条件强杀
    try
    {
        std::filesystem::remove_all(L".\\files_old");
        std::filesystem::rename(L".\\files", L".\\files_old");
        files_moved = true;
        // 会被覆盖的顶层文件（LunaTranslator.exe等）先挪进备份目录，
        // 使它们也能随files_old整体回滚（直接覆盖是无法回滚的）
        std::filesystem::path backup = L".\\files_old\\_lunarootbackup_";
        std::filesystem::create_directories(backup);
        for (auto &entry : std::filesystem::directory_iterator(pack))
        {
            std::error_code ec;
            if (!entry.is_regular_file(ec))
                continue;
            auto dstf = std::filesystem::path(L".\\") / entry.path().filename();
            if (std::filesystem::exists(dstf))
                std::filesystem::rename(dstf, backup / entry.path().filename());
        }
        copyupdate(pack, L".\\");
        try
        {
            keeponnxruntimeopenvino();
        }
        catch (...)
        {
        }
        try
        {
            std::filesystem::remove_all(L".\\files_old");
        }
        catch (...)
        {
        }
    }
    catch (std::exception &)
    {
        // 回滚：删掉复制了一半的新files、旧files放回。
        // 注意：rename(files→files_old)没成功时files仍完好，绝不能删它。
        try
        {
            std::error_code ec;
            if (files_moved)
            {
                if (std::filesystem::exists(L".\\files", ec))
                    std::filesystem::remove_all(L".\\files", ec);
                try
                {
                    std::filesystem::rename(L".\\files_old", L".\\files");
                }
                catch (...)
                {
                    // 新files里有删不掉的残留（被占用）时rename会失败，files_old原地保留
                }
            }
        }
        catch (...)
        {
        }
        // 还原被挪走的顶层文件。rename回退成功时备份在files下，失败时仍在files_old下，两种都要尝试
        for (auto &backup : {std::filesystem::path(L".\\files\\_lunarootbackup_"), std::filesystem::path(L".\\files_old\\_lunarootbackup_")})
        {
            std::error_code ec;
            if (!std::filesystem::exists(backup, ec))
                continue;
            for (auto &entry : std::filesystem::directory_iterator(backup))
            {
                auto dstf = std::filesystem::path(L".\\") / entry.path().filename();
                std::error_code ec2;
                if (std::filesystem::exists(dstf, ec2))
                {
                    // 复制了一半的新文件，清掉再还原
                    clear_readonly(dstf);
                    std::filesystem::remove_all(dstf, ec2);
                }
                std::filesystem::rename(entry.path(), dstf, ec2);
            }
            std::filesystem::remove_all(backup, ec);
        }
        g_mutating = false;
        // MessageBoxW(NULL, (std::wstring(text_update_failed) + L"\n\n" + StringToWideString(e.what(), CP_ACP)).c_str(), text_error.c_str(), MB_SYSTEMMODAL);
        if (needreload)
            ShellExecute(0, L"open", L".\\LunaTranslator.exe", NULL, NULL, SW_SHOWNORMAL);
        return 0;
    }
    g_mutating = false;
    try
    {
        std::filesystem::remove_all(pack);
    }
    catch (std::exception &)
    {
        // 暂存目录清理失败不影响更新结果，也不应阻止重启
    }
    // MessageBoxW(NULL, text_update_succ.c_str(), text_succ.c_str(), MB_SYSTEMMODAL);
    if (needreload)
    {
        ShellExecute(0, L"open", L".\\LunaTranslator.exe", NULL, NULL, SW_SHOWNORMAL);
    }
    return 0;
}