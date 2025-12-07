#include "api_settings.h"

#include "ebyutil.h"
namespace ebyroid
{

  using std::string;

  Settings SettingsBuilder::Build()
  {
    Settings settings;
    string license_path = base_dir_ + kWinDelimit + kLicFilename;
    strcpy_s(settings.voice_name, ARRAYSIZE(settings.voice_name), voice_name_.c_str());
    strcpy_s(settings.license_path, ARRAYSIZE(settings.license_path), license_path.c_str());

#ifndef _WIN64
    if (voice_name_.find("_22") != string::npos)
    {
      // this means the given library is VOICEROID+
      settings.frequency = kFrequency22;

      string voice_dir = base_dir_ + kWinDelimit + "voice";
      string language_dir = base_dir_ + kWinDelimit + "lang";
      std::strcpy(settings.voice_dir, voice_dir.c_str());
      std::strcpy(settings.language_dir, language_dir.c_str());
      if (voice_name_ == "kiritan_22")
      {
        settings.seed = EBY_SEED_B;
      }
      else if (voice_name_ == "zunko_22")
      {
        settings.seed = EBY_SEED_C;
      }
      else if (voice_name_ == "akane_22")
      {
        settings.seed = EBY_SEED_D;
      }
      else if (voice_name_ == "aoi_22")
      {
        settings.seed = EBY_SEED_E;
      }
      else
      {
        char m[64];
        std::snprintf(m, 64, "Unsupported VOICEROID+ library '%s' was given.", settings.voice_name);
        throw new std::runtime_error(m);
      }
    }
    else
#endif
    {
      // this means it is either VOICEROID2 or an unexpected library
      // try to setup as VOICEROID2 anyways
      settings.frequency = kFrequency44;

      string voice_dir = base_dir_ + kWinDelimit + "Voice";
      string language_dir = base_dir_ + kWinDelimit + "Lang" + kWinDelimit + Lang_;
      if (!PathFileExistsA(language_dir.c_str()))
      {
        language_dir = base_dir_ + kWinDelimit + "Lang" + kWinDelimit + "standard_" + Lang_;
      }
      if (!PathFileExistsA(language_dir.c_str()))
      {
        language_dir = base_dir_ + kWinDelimit + "Lang" + kWinDelimit + "standard";
      }
#ifdef _WIN64
      // AIVoice & AIVoice2
      if (!PathFileExistsA((voice_dir + "\\" + voice_name_).c_str()))
      {
        voice_dir = base_dir_.substr(0, base_dir_.rfind('\\')) + "\\Voice\\" + voice_name_;
      }
#endif
      strcpy_s(settings.voice_dir, ARRAYSIZE(settings.voice_dir), voice_dir.c_str());
      strcpy_s(settings.language_dir, ARRAYSIZE(settings.language_dir), language_dir.c_str());

#ifndef _WIN64
      settings.seed = EBY_SEED_A;
#else
      // H3285R43KNOJ8DCaAtbH + aitalk5.dll + AITalkTSTalker2Wrapper.dll
      // 或 cd3y6BYgJXJB6iZsLg6f + aitalk.dll + aitalked.dll 是可以通过init的
      // 但是都无法通过voiceload。我吐了。
      //
      // 经测试应该使用AITalk_SDK.dll系列API，所以拉闸了，得重新写才行。
      settings.seed = "xTsp2BFKY1BPRf2X1a79"; //"H3285R43KNOJ8DCaAtbH"; //"cd3y6BYgJXJB6iZsLg6f"; //
#endif
    }

    Dprintf("SettingBuilder\nfrequency=%d\nlanguage_dir=%s\nvoice_dir=%s",
            settings.frequency,
            settings.language_dir,
            settings.voice_dir);

    return settings;
  }

} // namespace ebyroid
