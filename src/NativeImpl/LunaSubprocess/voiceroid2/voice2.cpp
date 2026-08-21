
#include "ebyroid.h"
#include "api_adapter.h"
#include "ebyutil.h"
using ebyroid::Ebyroid;
#include "types.h"
#include "../../wav.hpp"
#include "../pipehost.hpp"

int voiceroid2wmain(int argc, wchar_t *wargv[])
{
    // Ebyroid 接口需 ACP（Shift-JIS）窄串；仅转这四个 argv。管道/事件/映射名为 ASCII uuid，
    // 直接以 wchar 交给 PipeHost（W 版 API）即可，不必再走 ACP 转换。
    auto acp = [](const wchar_t *w) -> std::string {
        if (!w)
            return {};
        int n = WideCharToMultiByte(CP_ACP, 0, w, -1, NULL, 0, NULL, NULL);
        if (n <= 0)
            return {};
        std::string s(n, '\0'); // n 含结尾 '\0'
        WideCharToMultiByte(CP_ACP, 0, w, -1, s.data(), n, NULL, NULL);
        s.resize(n - 1);
        return s;
    };
    std::string dlldir = acp(wargv[4]);
    std::string dllpath = acp(wargv[5]);

    lunasp::PipeHost host(wargv[1], wargv[2], wargv[3]);
    if (!host.ok())
        return 0;
    Ebyroid *ebyroid = Ebyroid::Create(dlldir, dllpath, acp(wargv[6]), acp(wargv[7]));

    int freq1;
    std::string last;
    char input_j[4096] = {0};
    while (true)
    {
        ZeroMemory(input_j, sizeof(input_j));

        if (!host.read(input_j, 4096))
            break;
        std::string voice = (char *)input_j;
        ZeroMemory(input_j, sizeof(input_j));

        if (!host.read(input_j, 4096))
            break;
        std::string lang = (char *)input_j;
        float _rate;
        if (!host.read(&_rate, 4))
            break;
        float _pitch;
        if (!host.read(&_pitch, 4))
            break;
        if (voice != last)
        {
            if (ebyroid)
                delete ebyroid;
            ebyroid = Ebyroid::Create(dlldir, dllpath, voice, lang);
            last = voice;
        }
        ebyroid->Setparam(2, _rate, _pitch); // 0.5-4, 0.5-2
        ZeroMemory(input_j, sizeof(input_j));
        if (!host.read(input_j, 4096))
            break;
        if (voice.find("_44") != voice.npos)
            freq1 = 44100;
        else
            freq1 = 22050;
        std::vector<char> output;
        int result = ebyroid->Hiragana(input_j, output);
        output.push_back(0);
        std::vector<int16_t> binary;
        result = ebyroid->Speech(output.data(), binary);
        size_t output_size = binary.size() * 2;
        int fsize = (int)(output_size + 44);
        if (fsize > 1024 * 1024 * 16)
        {
            fsize = 0;
        }
        else
        {

            const uint16_t channels = 1, bits = 16, block_align = 2;
            const uint32_t freq = static_cast<uint32_t>(freq1);
            auto header = wav::BuildHeader(static_cast<uint16_t>(WAVE_FORMAT_PCM), channels, freq, freq * 2, block_align, bits, static_cast<uint32_t>(output_size));
            memcpy(host.mem(), header.data(), header.size());
            memcpy(host.mem() + header.size(), binary.data(), output_size);
        }
        host.write(&fsize, 4);
    }
    return 0;
}
