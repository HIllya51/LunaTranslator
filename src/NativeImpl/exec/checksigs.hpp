
constexpr uint8_t hex_char_to_byte(char c)
{
    return (c >= '0' && c <= '9') ? c - '0' : (c >= 'a' && c <= 'f') ? c - 'a' + 10
                                                                     : c - 'A' + 10;
}

template <std::size_t N>
constexpr auto parse_hex_string(const char (&str)[N])
{
    std::array<std::uint8_t, (N - 1) / 2> result{};
    for (std::size_t i = 0; i < N - 1; i += 2)
    {
        std::uint8_t high = hex_char_to_byte(str[i]);
        std::uint8_t low = hex_char_to_byte(str[i + 1]);
        result[i / 2] = (high << 4) | low;
    }
    return result;
}
using sha512_t = std::array<std::uint8_t, 64>;

struct
{
    const wchar_t *file;
    sha512_t sig;
} checkdigest[] = {
    // CHECK_DIGEST_LIST
    // 占位符，方便python脚本生成列表时替换字符串
    // example:
    //{L"LunaTranslator/__init__.py", {parse_hex_string("cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e")}},
    {nullptr} // 长度占位符
};

const wchar_t *checksig[] = {

    // CHECK_CERT_LIST
    // example:
    // L"files/DLL64/bass.dll",
    nullptr // 长度占位符
};