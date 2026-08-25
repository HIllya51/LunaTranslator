
#include "aitalked.h"
#include "aitalk_engine.h"
#include "../../wav.hpp"
#include "../pipehost.hpp"
#include "abstract.hpp"
#include "api_settings.h"

int voiceroid_aivoicewmain(int argc, wchar_t *wargv[])
{

    lunasp::PipeHost host(wargv[1], wargv[2], wargv[3]);
    if (!host.ok())
        return 0;
    std::string dllpath = std::filesystem::path(wargv[4]).string();
    std::string voicedir = std::filesystem::path(wargv[5]).string();
    Settings settings;
    Abstracttts *abstracttts;
    try
    {
        settings = Settings::Create(dllpath, voicedir, std::filesystem::path(wargv[6]).string());
#ifndef _WIN64
        abstracttts = new aitalked(settings);
#else
        abstracttts = new aitalk_engine(settings);
#endif
        abstracttts->setvoice(settings);
    }
    catch (std::exception &e)
    {
        MessageBoxA(0, e.what(), "", 0);
        return 0;
    }

    int freq1;
    char input_j[4096] = {0};
    while (true)
    {
        ZeroMemory(input_j, sizeof(input_j));

        if (!host.read(input_j, 4096))
            break;
        std::string _voicedir = (char *)input_j;

        ZeroMemory(input_j, sizeof(input_j));

        if (!host.read(input_j, 4096))
            break;
        std::string lang = (char *)input_j;
        if (_voicedir != voicedir)
        {
            try
            {
                settings = Settings::Create(dllpath, _voicedir, lang);
                abstracttts->setvoice(settings);
            }
            catch (std::exception &e)
            {
                MessageBoxA(0, e.what(), "", 0);
                return 0;
            }
            voicedir = _voicedir;
        }
        float _rate;
        if (!host.read(&_rate, 4))
            break;
        float _pitch;
        if (!host.read(&_pitch, 4))
            break;
        ZeroMemory(input_j, sizeof(input_j));
        if (!host.read(input_j, 4096))
            break;
        auto &&binary = abstracttts->Speech(_rate, _pitch, input_j);
        size_t output_size = binary.size() * 2;
        int fsize = (int)(output_size + 44);
        if (fsize > lunasp::DEFAULT_MEM)
        {
            fsize = 0;
        }
        else
        {

            const uint16_t channels = 1, bits = 16, block_align = 2;
            auto header = wav::BuildHeader(static_cast<uint16_t>(WAVE_FORMAT_PCM), channels, settings.frequency, settings.frequency * 2, block_align, bits, static_cast<uint32_t>(output_size));
            memcpy(host.mem(), header.data(), header.size());
            memcpy(host.mem() + header.size(), binary.data(), output_size);
        }
        host.write(&fsize, 4);
    }
    return 0;
}
