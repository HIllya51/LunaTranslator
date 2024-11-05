#pragma once

#include <istream>

template <typename C, int delimiterCount, int blockSize = 0x1000 / sizeof(C)> // windows file block size
class BlockMarkupIterator
{
public:
	BlockMarkupIterator(const std::istream& stream, const std::basic_string_view<C>(&delimiters)[delimiterCount]) : streambuf(*stream.rdbuf())
	{
		std::copy_n(delimiters, delimiterCount, this->delimiters.begin());
	}

	std::optional<std::array<std::basic_string<C>, delimiterCount>> Next()
	{
		std::array<std::basic_string<C>, delimiterCount> results;
		Find(delimiters[0], true);
		for (int i = 0; i < delimiterCount; ++i)
		{
			const auto delimiter = i + 1 < delimiterCount ? delimiters[i + 1] : end;
			if (auto found = Find(delimiter, false)) results[i] = std::move(found.value());
			else return {};
		}
		return results;
	}

private:
	std::optional<std::basic_string<C>> Find(std::basic_string_view<C> delimiter, bool discard)
	{
		for (int i = 0; ;)
		{
			int pos = buffer.find(delimiter, i);
			if (pos != std::string::npos)
			{
				auto result = !discard ? std::optional(std::basic_string(buffer.begin(), buffer.begin() + pos)) : std::nullopt;
				buffer.erase(buffer.begin(), buffer.begin() + pos + delimiter.size());
				return result;
			}
			int oldSize = buffer.size();
			buffer.resize(oldSize + blockSize);
			if (!streambuf.sgetn((char*)(buffer.data() + oldSize), blockSize * sizeof(C))) return {};
			i = max(0, oldSize - (int)delimiter.size());
			if (discard)
			{
				buffer.erase(0, i);
				i = 0;
			}
		}
	}

	static constexpr C endImpl[5] = { '|', 'E', 'N', 'D', '|' };
	static constexpr std::basic_string_view<C> end{ endImpl, 5 };

	std::basic_streambuf<char>& streambuf;
	std::basic_string<C> buffer;
	std::array<std::basic_string_view<C>, delimiterCount> delimiters;
};
