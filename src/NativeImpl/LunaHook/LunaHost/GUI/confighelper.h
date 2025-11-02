#ifndef LUNA_CONFIG_HELPER
#define LUNA_CONFIG_HELPER
#include <nlohmann/json.hpp>

class confighelper
{
    std::wstring configpath;

public:
    nlohmann::json configs;
    confighelper();
    ~confighelper();
    template <class T>
    T get(const std::string &key, T default1)
    {
        if (configs.find(key) == configs.end())
            return default1;
        return configs[key];
    }
    template <class T>
    void set(const std::string &key, T v)
    {
        configs[key] = v;
    }
};
template <typename T>
T safequeryjson(const nlohmann::json &js, const std::string &key, const T &defaultv)
{
    if (js.find(key) == js.end())
    {
        return defaultv;
    }
    return js[key];
}

constexpr auto pluginkey = x64 ? "plugins64" : "plugins32";

#endif