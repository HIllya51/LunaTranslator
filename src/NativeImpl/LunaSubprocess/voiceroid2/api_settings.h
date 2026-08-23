#ifndef API_SETTINGS_H
#define API_SETTINGS_H
#include "lic_codec.h"
namespace ebyroid
{

  static const char *kDllFilename = "aitalked.dll";
#ifndef _WIN64
  static constexpr int32_t kFrequency44 = 0xAC44;
  static constexpr int32_t kFrequency22 = 0x5622;
  static const char *kLicFilename = "aitalk.lic";
  static const int msec_timeout = 1000;
#else
  // AIVoice
  static constexpr int32_t kFrequency44 = 0xbb80;
  static const char *kLicFilename = "aitalk5.lic";
  static const int msec_timeout = 0x2710;
#endif
  static const char *kWinDelimit = "\\";

  struct Settings
  {
    static Settings Create(const std::string &base_dir_, const std::string &voice_name_, const std::string &Lang_)
    {
      Settings settings;
      settings.voice_name = voice_name_;
      settings.license_path = base_dir_ + kWinDelimit + kLicFilename;

      auto &&keys = lic_codec::extractKeys(settings.license_path);
      if (keys.size() == 2)
      {
        settings.seed = keys[1];
      }
      else
      {
        char m[64];
        std::snprintf(m, 64, "Unsupported Voice.", settings.voice_name.c_str());
        throw std::runtime_error(m);
      }

#ifndef _WIN64
      if (voice_name_.find("_22") != std::string::npos)
      {
        // this means the given library is VOICEROID+
        settings.frequency = kFrequency22;

        settings.voice_dir = base_dir_ + kWinDelimit + "voice";
        settings.language_dir = base_dir_ + kWinDelimit + "lang";
      }
      else
#endif
      {
        // this means it is either VOICEROID2 or an unexpected library
        // try to setup as VOICEROID2 anyways
        settings.frequency = kFrequency44;

        settings.voice_dir = base_dir_ + kWinDelimit + "Voice";
        settings.language_dir = base_dir_ + kWinDelimit + "Lang" + kWinDelimit + Lang_;
        if (!PathFileExistsA(settings.language_dir.c_str()))
        {
          settings.language_dir = base_dir_ + kWinDelimit + "Lang" + kWinDelimit + "standard_" + Lang_;
        }
        if (!PathFileExistsA(settings.language_dir.c_str()))
        {
          settings.language_dir = base_dir_ + kWinDelimit + "Lang" + kWinDelimit + "standard";
        }
#ifdef _WIN64
        // AIVoice & AIVoice2
        if (!PathFileExistsA((settings.voice_dir + "\\" + voice_name_).c_str()))
        {
          settings.voice_dir = base_dir_.substr(0, base_dir_.rfind('\\')) + "\\Voice\\" + voice_name_;
        }
#endif
      }

      return settings;
    }
    std::string voice_dir;
    std::string voice_name;
    std::string language_dir;
    std::string license_path;
    std::string seed;
    uint32_t frequency;
  };

} // namespace ebyroid

#endif // API_SETTINGS_H
