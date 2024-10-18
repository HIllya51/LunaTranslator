
#define MINIAUDIO_IMPLEMENTATION
#include <miniaudio.h>

void data_callback(ma_device *pDevice, void *pOutput, const void *pInput, ma_uint32 frameCount)
{
    ma_decoder *pDecoder = (ma_decoder *)pDevice->pUserData;
    if (pDecoder == NULL)
    {
        return;
    }

    ma_decoder_read_pcm_frames(pDecoder, pOutput, frameCount, NULL);

    (void)pInput;
}
extern "C" __declspec(dllexport) void PlayAudioInMem_Stop(ma_decoder *decoder, ma_device *device)
{
    ma_device_stop(device);
    ma_device_uninit(device);
    ma_decoder_uninit(decoder);
    delete decoder;
    delete device;
}

extern "C" __declspec(dllexport) int PlayAudioInMem(void *ptr, size_t len, float volume, ma_decoder **decoderet, ma_device **deviceret, float *duration)
{
    ma_result result;
    ma_decoder *decoder = new ma_decoder;
    ma_device_config deviceConfig;
    ma_device *device = new ma_device;
    ZeroMemory(device, sizeof(ma_device));
    ZeroMemory(decoder, sizeof(ma_decoder));
    result = ma_decoder_init_memory(ptr, len, NULL, decoder);
    if (result != MA_SUCCESS)
    {
        delete decoder;
        delete device;
        return -2;
    }
    deviceConfig = ma_device_config_init(ma_device_type_playback);
    deviceConfig.playback.format = decoder->outputFormat;
    deviceConfig.playback.channels = decoder->outputChannels;
    deviceConfig.sampleRate = decoder->outputSampleRate;
    deviceConfig.dataCallback = data_callback;
    deviceConfig.pUserData = decoder;

    if (ma_device_init(NULL, &deviceConfig, device) != MA_SUCCESS)
    {
        ma_decoder_uninit(decoder);
        delete decoder;
        delete device;
        return -3;
    }
    ma_device_set_master_volume(device, volume);
    if (ma_device_start(device) != MA_SUCCESS)
    {
        ma_device_uninit(device);
        ma_decoder_uninit(decoder);
        delete decoder;
        delete device;
        return -4;
    }

    *decoderet = decoder;
    *deviceret = device;
    ma_uint64 frames;
    ma_decoder_get_length_in_pcm_frames(decoder, &frames);
    *duration = 1.0f * frames / (decoder->outputSampleRate);
    return 0;
}
