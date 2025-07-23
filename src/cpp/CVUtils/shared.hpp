using version_t = std::tuple<WORD, WORD, WORD, WORD>;
std::optional<version_t> QueryVersion(const std::wstring& exe);
std::optional<WORD> MyGetBinaryType(LPCWSTR file);