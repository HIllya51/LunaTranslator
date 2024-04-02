#include "api_settings.h"

#include <stdexcept>

#include "ebyutil.h"
namespace ebyroid
{

  using std::string;

  Settings SettingsBuilder::Build()
  {
    Settings settings;
    string dll_path = base_dir_ + kWinDelimit + kDllFilename;
    string license_path = base_dir_ + kWinDelimit + kLicFilename;
    std::strcpy(settings.base_dir, base_dir_.c_str());
    std::strcpy(settings.voice_name, voice_name_.c_str());
    std::strcpy(settings.dll_path, dll_path.c_str());
    std::strcpy(settings.license_path, license_path.c_str());

    Dprintf("SettingBuilder\nbase_dir=%s\ndll_path=%s\nlicense_path=%s\nvoice_name=%s",
            settings.base_dir,
            settings.dll_path,
            settings.license_path,
            settings.voice_name);

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
    {
      // this means it is either VOICEROID2 or an unexpected library
      // try to setup as VOICEROID2 anyways
      settings.frequency = kFrequency44;

      string voice_dir = base_dir_ + kWinDelimit + "Voice";
      string language_dir = base_dir_ + kWinDelimit + "Lang" + kWinDelimit + "standard";
      std::strcpy(settings.voice_dir, voice_dir.c_str());
      std::strcpy(settings.language_dir, language_dir.c_str());
      // if (voice_name_ == "yukari_emo_44") {
      //     settings.seed = "PROJECT-VOICeVIO-SFE";//
      // }
      // else {
      settings.seed = EBY_SEED_A;
      //}
    }

    Dprintf("SettingBuilder\nfrequency=%d\nlanguage_dir=%s\nvoice_dir=%s",
            settings.frequency,
            settings.language_dir,
            settings.voice_dir);

    return std::move(settings);
  }

} // namespace ebyroid
