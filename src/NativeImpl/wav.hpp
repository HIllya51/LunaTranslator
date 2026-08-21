#pragma once

namespace wav {

#pragma pack(push, 1)
struct Header {
    char riff[4] = {'R', 'I', 'F', 'F'};
    std::uint32_t overall = 0;
    char wave[4] = {'W', 'A', 'V', 'E'};
    char fmt[4] = {'f', 'm', 't', ' '};
    std::uint32_t fmtSize = 16;
    std::uint16_t formatTag = 0;
    std::uint16_t channels = 0;
    std::uint32_t sampleRate = 0;
    std::uint32_t byteRate = 0;
    std::uint16_t blockAlign = 0;
    std::uint16_t bitsPerSample = 0;
    char data[4] = {'d', 'a', 't', 'a'};
    std::uint32_t dataSize = 0;
};
#pragma pack(pop)
static_assert(sizeof(Header) == 44, "WAV header must be 44 bytes");

inline std::string BuildHeader(std::uint16_t formatTag, std::uint16_t channels,
                               std::uint32_t sampleRate, std::uint32_t byteRate,
                               std::uint16_t blockAlign, std::uint16_t bitsPerSample,
                               std::uint32_t dataSize)
{
    Header h;
    h.overall = dataSize + 36;
    h.formatTag = formatTag;
    h.channels = channels;
    h.sampleRate = sampleRate;
    h.byteRate = byteRate;
    h.blockAlign = blockAlign;
    h.bitsPerSample = bitsPerSample;
    h.dataSize = dataSize;
    return std::string(reinterpret_cast<const char *>(&h), sizeof(h));
}

inline std::string BuildHeader(const WAVEFORMATEX *pwfx, std::uint32_t dataSize)
{
    return BuildHeader(pwfx->wFormatTag, pwfx->nChannels, pwfx->nSamplesPerSec,
                       pwfx->nAvgBytesPerSec, pwfx->nBlockAlign, pwfx->wBitsPerSample,
                       dataSize);
}

inline std::string Build(const WAVEFORMATEX *pwfx, const void *pcm, std::size_t dataSize)
{
    return BuildHeader(pwfx, static_cast<std::uint32_t>(dataSize)) +
           std::string(static_cast<const char *>(pcm), dataSize);
}

inline void FixSizes(std::string &buf, std::size_t headerSize, std::uint32_t dataSize)
{
    std::memcpy(buf.data() + headerSize - sizeof(std::uint32_t), &dataSize,
                sizeof(std::uint32_t));
    const std::uint32_t total =
        dataSize + static_cast<std::uint32_t>(headerSize) - 8;
    std::memcpy(buf.data() + sizeof(std::uint32_t), &total, sizeof(std::uint32_t));
}

}
