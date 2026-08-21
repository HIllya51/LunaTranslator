#pragma once

namespace lunasp {

inline constexpr SIZE_T DEFAULT_MEM = 16 * 1024 * 1024; // 与各 engine 原先用的一致

class PipeHost
{
public:
    PipeHost(const wchar_t *pipe, const wchar_t *signal,
             const wchar_t *map = nullptr, SIZE_T memSize = DEFAULT_MEM)
        : memSize_(memSize)
    {
        pipe_ = CreateNamedPipeW(pipe, PIPE_ACCESS_DUPLEX,
                                 PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
                                 PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, &allAccess);
        if (!pipe_ || pipe_ == INVALID_HANDLE_VALUE)
            return;
        if (map)
        {
            map_ = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0,
                                       static_cast<DWORD>(memSize), map);
            mem_ = static_cast<char *>(MapViewOfFile(map_, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, memSize));
            memset(mem_, 0, memSize); // 与原先一致：映射失败（极端情况）行为不变
        }
        if (HANDLE e = CreateEventW(&allAccess, FALSE, FALSE, signal))
        {
            SetEvent(e); // 通知宿主可开始 WaitNamedPipe+CreateFile
            CloseHandle(e);
        }
        // 宿主在事件触发后连接；ERROR_PIPE_CONNECTED 表示其已先连上，均视为成功。
        if (ConnectNamedPipe(pipe_, NULL) || GetLastError() == ERROR_PIPE_CONNECTED)
            ok_ = true;
    }

    ~PipeHost()
    {
        if (mem_)
            UnmapViewOfFile(mem_);
        if (map_)
            CloseHandle(map_);
        if (pipe_ && pipe_ != INVALID_HANDLE_VALUE)
            CloseHandle(pipe_);
    }

    PipeHost(const PipeHost &) = delete;
    PipeHost &operator=(const PipeHost &) = delete;

    HANDLE pipe() const { return pipe_; }
    char *mem() const { return mem_; }
    SIZE_T memSize() const { return memSize_; }
    bool ok() const { return ok_; }

    bool read(void *buf, DWORD n) const
    {
        DWORD got = 0;
        return ReadFile(pipe_, buf, n, &got, nullptr) != 0;
    }
    bool write(const void *buf, DWORD n) const
    {
        DWORD put = 0;
        return WriteFile(pipe_, buf, n, &put, nullptr) != 0;
    }

    std::optional<std::wstring> readstring() const
    {
        DWORD _;
        int len;
        if (!ReadFile(pipe_, &len, 4, &_, NULL))
            return std::nullopt;
        std::wstring s;
        if (len > 0)
        {
            s.resize(len / 2);
            if (!ReadFile(pipe_, s.data(), len, &_, NULL))
                return std::nullopt;
        }
        return s;
    }
    void writestring(const std::optional<std::wstring> &text) const
    {
        DWORD _;
        int len = text ? static_cast<int>(text->size() * 2) : 0;
        if (!WriteFile(pipe_, &len, 4, &_, NULL))
            return;
        if (text && len)
            if (!WriteFile(pipe_, text->c_str(), len, &_, NULL))
                return;
    }

private:
    HANDLE pipe_ = INVALID_HANDLE_VALUE;
    HANDLE map_ = nullptr;
    char *mem_ = nullptr;
    SIZE_T memSize_ = 0;
    bool ok_ = false;
};

} // namespace lunasp
