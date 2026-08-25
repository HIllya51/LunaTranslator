#ifndef API_SETTINGS_H
#define API_SETTINGS_H
#include "lic_codec.h"
namespace
{

  static const char *kDllFilename = "aitalked.dll";
#ifndef _WIN64
  static constexpr int32_t kFrequency44 = 0xAC44;
  static constexpr int32_t kFrequency22 = 0x5622;
#else
  // AIVoice
  static constexpr int32_t kFrequency44 = 0xbb80;
#endif
}
struct Settings
{
  static std::optional<std::string> findroot(const std::string &dllpath)
  {
    auto basedir = std::filesystem::path(dllpath).parent_path();
    for (auto i = 0; i < 3; i++)
    {
      auto license = basedir / "AI.Framework.License.dll";
      if (std::filesystem::exists(license))
      {
        return basedir.string();
      }
#ifndef _WIN64
      license = basedir / "AITalkEditorCore.dll"; // voiceroid+
      if (std::filesystem::exists(license))
      {
        return basedir.string();
      }
#endif
      basedir = basedir.parent_path();
    }
    return {};
  }
  static std::optional<std::pair<std::string, std::string>> getseed(const std::string &license_path)
  {
    auto &&keys = lic_codec::extractKeys(license_path);
    if (keys.size() == 2)
    {
      return std::make_pair(keys[0], keys[1]);
    }
    return {};
  }
  static std::optional<std::string> getlangdir(const std::string &voiceir, const std::string &Lang_)
  {
    auto basedir = std::filesystem::path(voiceir).parent_path().parent_path();
    auto langdir = basedir / "Lang" / Lang_;
    if (std::filesystem::exists(langdir))
      return langdir.string();
    langdir = basedir / "Lang" / ("standard_" + Lang_);
    if (std::filesystem::exists(langdir))
      return langdir.string();
    langdir = basedir / "Lang" / ("standard");
    if (std::filesystem::exists(langdir))
      return langdir.string();
    return {};
  }
  static Settings Create(const std::string &_dllpath, const std::string &voiceir, const std::string &Lang_)
  {
    auto root = findroot(_dllpath);
    if (!root)
      throw std::runtime_error("Can't find root");
    Settings settings;
    settings.root = root.value();
    settings.dllpath = _dllpath;
    settings.voice_name = std::filesystem::path(voiceir).filename().string();
    settings.license_path = (std::filesystem::path(_dllpath).parent_path() / "aitalk.lic").string();

    auto &&ret = getseed(settings.license_path);
    if (!ret)
      throw std::runtime_error("unknown seed");
    std::tie(settings.product, settings.seed) = ret.value();
    settings.voice_base_dir = std::filesystem::path(voiceir).parent_path().string();
    settings.voice_dir = voiceir;
    auto langdir = getlangdir(voiceir, Lang_);
    if (!langdir)
      throw std::runtime_error("Can't find Lang");
    settings.language = Lang_;
    settings.language_dir = langdir.value();
    settings.language_base_dir = std::filesystem::path(langdir.value()).parent_path().string();
#ifndef _WIN64
    if (settings.voice_name.find("_22") != std::string::npos)
    {
      // this means the given library is VOICEROID+
      settings.frequency = kFrequency22;
    }
    else
#endif
    {
      settings.frequency = kFrequency44;
    }

    SetDllDirectoryA(settings.root.c_str());
    SetCurrentDirectoryA(settings.root.c_str());
    return settings;
  }
  std::string root;
  std::string dllpath;
  std::string voice_dir;
  std::string voice_base_dir;
  std::string voice_name;
  std::string language;
  std::string language_dir;
  std::string language_base_dir;
  std::string license_path;
  std::string seed;
  std::string product;
  uint32_t frequency;
};

#endif // API_SETTINGS_H
