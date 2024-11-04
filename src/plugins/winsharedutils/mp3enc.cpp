#include "define.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <timing.h>
#include <shine_mp3.h>

#define DR_WAV_IMPLEMENTATION
#include "dr_wav.h"

int stereo = STEREO;

DECLARE_API void encodemp3(void *ptr, size_t size, void (*cb)(void *ptr, size_t size))
{
    shine_config_t config;
    shine_t s;
    int written;
    unsigned char *data;
    /* Set the default MPEG encoding paramters - basically init the struct */
    shine_set_config_mpeg_defaults(&config.mpeg);

    config.mpeg.bitr = 320;

    uint32_t sampleRate = 0;
    uint64_t totalSampleCount = 0;
    uint32_t channels = 0;
    int16_t *data_in = drwav_open_memory_and_read_pcm_frames_s16(ptr, size, &channels, &sampleRate, &totalSampleCount, NULL);
    if (data_in == NULL)
        return;
    totalSampleCount *= channels;
    double startTime = now();
    config.wave.samplerate = sampleRate;
    config.wave.channels = (decltype(config.wave.channels))channels;

    /* See if samplerate and bitrate are valid */
    if (shine_check_config(config.wave.samplerate, config.mpeg.bitr) < 0)
        return;
    // printf("Unsupported samplerate/bitrate configuration.");

    /* Set to stereo mode if wave data is stereo, mono otherwise. */
    if (config.wave.channels > 1)
        config.mpeg.mode = (decltype(config.mpeg.mode))stereo;
    else
        config.mpeg.mode = MONO;

    /* Initiate encoder */
    s = shine_initialise(&config);

    int samples_per_pass = shine_samples_per_pass(s) * channels;
    std::string sdata;
    /* All the magic happens here */
    size_t count = totalSampleCount / samples_per_pass;
    int16_t *buffer = data_in;
    for (int i = 0; i < count; i++)
    {
        data = shine_encode_buffer_interleaved(s, buffer, &written);
        sdata += std::string((char *)data, written);
        buffer += samples_per_pass;
    }
    size_t last = totalSampleCount % samples_per_pass;
    if (last != 0)
    {
        int16_t *cache = (int16_t *)calloc(samples_per_pass, sizeof(int16_t));
        if (cache != NULL)
        {
            memcpy(cache, buffer, last * sizeof(int16_t));
            data = shine_encode_buffer_interleaved(s, cache, &written);
            free(cache);
            sdata += std::string((char *)data, written);
        }
    }
    /* Flush and write remaining data. */
    data = shine_flush(s, &written);
    sdata += std::string((char *)data, written);
    /* Close encoder. */
    shine_close(s);
    free(data_in);
    double time_interval = calcElapsed(startTime, now());
    cb(sdata.data(), sdata.size());
}
