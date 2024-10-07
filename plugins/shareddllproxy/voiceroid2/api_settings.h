#ifndef API_SETTINGS_H
#define API_SETTINGS_H


namespace ebyroid
{

  static constexpr size_t kMaxPathSize = 0xFF;
  static constexpr int32_t kFrequency44 = 0xAC44;
  static constexpr int32_t kFrequency22 = 0x5622;
  static const char *kDllFilename = "aitalked.dll";
  static const char *kLicFilename = "aitalk.lic";
  static const char *kWinDelimit = "\\";

  struct Settings
  {
    char base_dir[kMaxPathSize];
    char dll_path[kMaxPathSize];
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
    SettingsBuilder(const std::string &base_dir, const std::string &voice_name)
        : base_dir_(base_dir), voice_name_(voice_name) {}

    Settings Build();

  private:
    std::string base_dir_;
    std::string voice_name_;
  };

} // namespace ebyroid

#endif // API_SETTINGS_H
