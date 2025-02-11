#ifndef API_SETTINGS_H
#define API_SETTINGS_H

namespace ebyroid
{

  static constexpr size_t kMaxPathSize = 0xFF;
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
    char voice_dir[kMaxPathSize];
    char voice_name[256];
    char language_dir[kMaxPathSize];
    char license_path[kMaxPathSize];
    const char *seed;
    uint32_t frequency;
  };

  class SettingsBuilder
  {
  public:
    SettingsBuilder(const std::string &base_dir, const std::string &voice_name, const std::string &Lang)
        : base_dir_(base_dir), voice_name_(voice_name), Lang_(Lang) {}

    Settings Build();

  private:
    std::string base_dir_;
    std::string voice_name_;
    std::string Lang_;
  };

} // namespace ebyroid

#endif // API_SETTINGS_H
