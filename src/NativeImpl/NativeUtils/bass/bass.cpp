#include <bass.h>
#include <bassenc.h>
#include <bassenc_mp3.h>
#include <bassenc_opus.h>

static std::filesystem::path getcurrpath()
{
    WCHAR path[MAX_PATH];
    HMODULE hd;
    GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, (LPCTSTR)getcurrpath, &hd);
    GetModuleFileNameW(hd, path, MAX_PATH);
    return std::filesystem::path(path).parent_path();
}
static HMODULE load_bass_dll(const wchar_t *dll)
{
    auto currdir = getcurrpath();
    auto mydml = (currdir / dll).wstring();
    return LoadLibrary(mydml.c_str());
}
static void(CALLBACK BASS_Encode_MP3_Start_ENCODEPROCEX)(HENCODE handle, DWORD channel, const void *buffer, DWORD length, QWORD offset, void *user)
{
    auto recv = static_cast<std::vector<char> *>(user);
    recv->insert(recv->end(), (char *)buffer, (char *)buffer + length);
}
static void(CALLBACK BASS_Encode_OPUS_Start_ENCODEPROC)(HENCODE handle, DWORD channel, const void *buffer, DWORD length, void *user)
{
    auto recv = static_cast<std::vector<char> *>(user);
    recv->insert(recv->end(), (char *)buffer, (char *)buffer + length);
}
static void bass_init()
{
    static std::once_flag callonce;
    std::call_once(callonce, []()
                   {
                       auto curr = getcurrpath();
                       LoadLibrary((curr / "bass.dll").wstring().c_str());
                       BASS_Init(-1, 44100, 0, 0, 0);
                       BASS_PluginLoad((curr / "bass_spx.dll").wstring().c_str(), 0);
                       BASS_PluginLoad((curr / "bass_aac.dll").wstring().c_str(), 0);
                       BASS_PluginLoad((curr / "bassopus.dll").wstring().c_str(), 0); });
}

static void bass_init_enc()
{
    static std::once_flag callonce;
    std::call_once(callonce, []()
                   { LoadLibrary((getcurrpath() / "bassenc.dll").wstring().c_str()); });
}
static void bass_init_enc_opus()
{
    static std::once_flag callonce;
    std::call_once(callonce, []()
                   { LoadLibrary((getcurrpath() / "bassenc_opus.dll").wstring().c_str()); });
}
static void bass_init_enc_mp3()
{
    static std::once_flag callonce;
    std::call_once(callonce, []()
                   { LoadLibrary((getcurrpath() / "bassenc_mp3.dll").wstring().c_str()); });
}
DECLARE_API HSTREAM bass_handle_create(const void *data, size_t size, bool isbytes)
{
    bass_init();
    if (isbytes)
        return BASS_StreamCreateFile(BASS_FILE_MEM, data, 0, size, 0);
    else
        return BASS_StreamCreateFile(BASS_FILE_NAME, static_cast<LPCWSTR>(data), 0, 0, 0);
}
struct stream_user_data
{
    static inline std::map<HSTREAM, stream_user_data *> mapdata;
    static inline std::mutex mapdatalock;

    std::vector<byte> data;
    size_t curr;
    HSTREAM ref;
    bool end = false;
    void push(const void *_data, size_t size)
    {
        data.insert(data.end(), (char *)_data, (char *)_data + size);
    }
    static DWORD CALLBACK MyFileRead(void *buffer, DWORD length, void *_user)
    {
        auto user = static_cast<stream_user_data *>(_user);
        if (!user)
            return 0;
        if (!user->data.data())
            return 0;
        length = std::min(length, (DWORD)(user->data.size() - user->curr));
        memcpy(buffer, user->data.data() + user->curr, length);
        user->curr += length;
        return length;
    }
    static BOOL CALLBACK MyFileSeek(QWORD offset, void *_user)
    {
        auto user = static_cast<stream_user_data *>(_user);
        if (!user)
            return FALSE;
        user->curr = std::min((size_t)offset, user->data.size());
        return user->curr == offset;
    }
    static QWORD CALLBACK MyFileLen(void *_user)
    {
        auto user = static_cast<stream_user_data *>(_user);
        if (!user)
            return 0;
        // 增加一个冗余长度，来防止停止。
        // 即使预知了长度，也会提前停止。
        return user->data.size() + !user->end;
    }
    static void CALLBACK MyFileClose(void *_user)
    {
        auto user = static_cast<stream_user_data *>(_user);
        if (!user)
            return;
        {
            std::unique_lock _(stream_user_data::mapdatalock);
            stream_user_data::mapdata.erase(user->ref);
        }
        delete user;
    }
    static inline const BASS_FILEPROCS fileProcs{MyFileClose, MyFileLen, MyFileRead, MyFileSeek};
};
DECLARE_API bool bass_stream_push_data(HSTREAM hs, const void *data, size_t size)
{
    if (!hs)
        return false;
    std::unique_lock _(stream_user_data::mapdatalock);
    auto f = stream_user_data::mapdata.find(hs);
    if (f == stream_user_data::mapdata.end())
        return false;
    if (!data)
    {
        f->second->end = true;
        BASS_ChannelStop(hs);
    }
    else
        f->second->push(data, size);
    return true;
}
DECLARE_API HSTREAM bass_stream_handle_create(const void *_data, size_t size)
{
    bass_init();
    auto data = new stream_user_data{};
    data->push(_data, size);
    auto h = BASS_StreamCreateFileUser(0, BASS_STREAM_AUTOFREE, &stream_user_data::fileProcs, data);
    data->ref = h;
    {
        std::unique_lock _(stream_user_data::mapdatalock);
        stream_user_data::mapdata[h] = data;
    }
    return h;
}
DECLARE_API void bass_handle_free(HSTREAM h)
{
    if (!h)
        return;
    BASS_StreamFree(h);
}
DECLARE_API bool bass_handle_play(HSTREAM handle, float volume)
{
    if (!handle)
        return false;
    BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL, volume / 100.0f);
    return BASS_ChannelPlay(handle, False);
}
DECLARE_API bool bass_handle_isplaying(HSTREAM handle)
{
    if (!handle)
        return false;
    return BASS_ChannelIsActive(handle);
}
DECLARE_API void bass_code_cast(void (*cb)(byte *, size_t), const byte *data, size_t size, const char *to_, int mp3kbps, int opusbitrate)
{
    std::string to = to_;
    if (!((to == "opus") || (to == "mp3")))
        return;
    bass_init();
    auto stream = BASS_StreamCreateFile(BASS_FILE_MEM, data, 0, size, BASS_STREAM_DECODE);
    if (!stream)
        return;
    HENCODE encoder;
    std::vector<byte> recv;
    bass_init_enc();
    if (to == "mp3")
    {
        bass_init_enc_mp3();
        auto opts = L"-b" + std::to_wstring(mp3kbps);
        encoder = BASS_Encode_MP3_Start(stream, opts.c_str(), BASS_UNICODE, BASS_Encode_MP3_Start_ENCODEPROCEX, &recv);
    }
    else if (to == "opus")
    {
        bass_init_enc_opus();
        auto opts = L"--bitrate " + std::to_wstring(opusbitrate);
        encoder = BASS_Encode_OPUS_Start(stream, opts.c_str(), BASS_UNICODE, BASS_Encode_OPUS_Start_ENCODEPROC, &recv);
    }
    if (!encoder)
    {
        BASS_StreamFree(stream);
        return;
    }
    char buff[0x10000];
    while (BASS_ChannelIsActive(stream))
    {
        if (!BASS_Encode_IsActive(stream))
            break;
        BASS_ChannelGetData(stream, buff, 0x10000);
    }
    BASS_Encode_Stop(stream);
    BASS_StreamFree(stream);
    cb(recv.data(), recv.size());
}