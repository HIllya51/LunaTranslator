namespace lic_codec
{

    inline uint64_t modpow(uint64_t b, uint64_t e, uint64_t m)
    {
        uint64_t r = 1 % m;
        b %= m;
        while (e)
        {
            if (e & 1)
                r = (r * b) % m;
            b = (b * b) % m;
            e >>= 1;
        }
        return r;
    }

    // 解码 .lic -> 明文字节
    inline std::string decode(const uint8_t *data, size_t len)
    {
        const uint64_t n = 9179;
        const uint64_t d = 1379;
        std::string out;
        out.reserve(len / 2);
        for (size_t i = 0; i + 1 < len; i += 2)
        {
            uint64_t c = (uint64_t(data[i]) << 8) | data[i + 1]; // 大端
            uint64_t m = modpow(c, d, n);
            out.push_back(char(m & 0xFF));
        }
        return out;
    }

    inline bool readFile(const std::string &path, std::vector<uint8_t> &out)
    {
        std::ifstream f(path, std::ios::binary);
        if (!f)
            return false;
        f.seekg(0, std::ios::end);
        size_t n = (size_t)f.tellg();
        f.seekg(0);
        out.resize(n);
        f.read((char *)out.data(), n);
        return f.good() || f.eof();
    }

    // 从明文里取前 numFields 个"长度前缀字符串"
    inline std::vector<std::string> extractFields(const std::string &s, size_t numFields)
    {
        std::vector<std::string> res;
        size_t i = 0, n = s.size();
        while (i < n && res.size() < numFields)
        {
            // 读取"最多2位"十进制长度
            size_t j = i;
            while (j < n && j - i < 2 && s[j] >= '0' && s[j] <= '9')
                ++j;
            if (j == i)
                break; // 不是数字 -> 结束
            size_t L = 0;
            for (size_t k = i; k < j; ++k)
                L = L * 10 + (s[k] - '0');
            i = j;
            if (i + L > n)
                L = n - i; // 防越界
            res.push_back(s.substr(i, L));
            i += L;
        }
        return res;
    }

    // 对一个 .lic 文件, 返回 [key2(=field0), key1(=field1)]
    // 失败返回空 vector.
    inline std::vector<std::string> extractKeys(const std::string &licPath)
    {
        std::vector<uint8_t> raw;
        if (!readFile(licPath, raw) || raw.empty())
            return {};
        std::string plain = decode(raw.data(), raw.size());
        return extractFields(plain, 2);
    }

} // namespace lic_codec
