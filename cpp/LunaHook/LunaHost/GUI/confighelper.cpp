#include "confighelper.h"
#include "stringutils.h"
std::string readfile(const wchar_t *fname)
{
    FILE *f;
    _wfopen_s(&f, fname, L"rb");
    if (f == 0)
        return {};
    fseek(f, 0, SEEK_END);
    auto len = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::string buff;
    buff.resize(len);
    fread(buff.data(), 1, len, f);
    fclose(f);
    return buff;
}
void writefile(const wchar_t *fname, const std::string &s)
{
    FILE *f;
    _wfopen_s(&f, fname, L"w");
    fprintf(f, "%s", s.c_str());
    fclose(f);
}

confighelper::confighelper()
{
    configpath = std::filesystem::current_path() / "config.json";
    try
    {
        configs = nlohmann::json::parse(readfile(configpath.c_str()));
    }
    catch (std::exception &)
    {
        configs = {};
    }

    if (configs.find(pluginkey) == configs.end())
    {
        configs[pluginkey] = {};
    }
}
confighelper::~confighelper()
{

    writefile(configpath.c_str(), configs.dump(4));
}