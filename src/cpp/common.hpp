
inline SECURITY_ATTRIBUTES allAccess = std::invoke([] // allows non-admin processes to access kernel objects made by admin processes
                                                   {
	static SECURITY_DESCRIPTOR sd = {};
	InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
	SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
	return SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE }; });

inline std::wstring StringToWideString(const std::string &text, UINT encoding = CP_UTF8)
{
    std::vector<wchar_t> buffer(text.size() + 1);
    int length = MultiByteToWideChar(encoding, 0, text.c_str(), text.size() + 1, buffer.data(), buffer.size());
    return std::wstring(buffer.data(), length - 1);
}
inline std::string WideStringToString(const std::wstring &text, UINT cp = CP_UTF8)
{
    std::vector<char> buffer((text.size() + 1) * 4);

    WideCharToMultiByte(cp, 0, text.c_str(), -1, buffer.data(), buffer.size(), nullptr, nullptr);
    return buffer.data();
}