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
    auto channel_length = BASS_ChannelGetLength(handle, BASS_POS_BYTE);
    if ((!channel_length) || (channel_length == -1))
        return false;
    auto channel_position = BASS_ChannelGetPosition(handle, BASS_POS_BYTE);
    if (channel_position == -1)
        return false;
    return channel_position < channel_length;
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