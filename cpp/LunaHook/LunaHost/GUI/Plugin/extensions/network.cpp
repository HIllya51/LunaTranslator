#include "network.h"

HttpRequest::HttpRequest(
	const wchar_t* agentName,
	const wchar_t* serverName,
	const wchar_t* action,
	const wchar_t* objectName,
	std::string body,
	const wchar_t* headers,
	DWORD port,
	const wchar_t* referrer,
	DWORD requestFlags,
	const wchar_t* httpVersion,
	const wchar_t** acceptTypes
)
{
	static std::atomic<HINTERNET> internet = NULL;
	if (!internet) internet = WinHttpOpen(agentName, WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, NULL, NULL, 0);
	if (internet)
		if (InternetHandle connection = WinHttpConnect(internet, serverName, port, 0))
			if (InternetHandle request = WinHttpOpenRequest(connection, action, objectName, httpVersion, referrer, acceptTypes, requestFlags))
				if (WinHttpSendRequest(request, headers, -1UL, body.empty() ? NULL : body.data(), body.size(), body.size(), NULL))
				{
					WinHttpReceiveResponse(request, NULL);

					//DWORD size = 0;
					//WinHttpQueryHeaders(request, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, NULL, &size, WINHTTP_NO_HEADER_INDEX);
					//this->headers.resize(size);
					//WinHttpQueryHeaders(request, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, this->headers.data(), &size, WINHTTP_NO_HEADER_INDEX);
					std::string data;
					DWORD availableSize, downloadedSize;
					do
					{
						availableSize = 0;
						WinHttpQueryDataAvailable(request, &availableSize);
						if (!availableSize) break;
						std::vector<char> buffer(availableSize);
						WinHttpReadData(request, buffer.data(), availableSize, &downloadedSize);
						data.append(buffer.data(), downloadedSize);
					} while (availableSize > 0);
					response = StringToWideString(data);
					this->connection = std::move(connection);
					this->request = std::move(request);
				}
				else errorCode = GetLastError();
			else errorCode = GetLastError();
		else errorCode = GetLastError();
	else errorCode = GetLastError();
}

std::wstring Escape(const std::wstring& text)
{
	std::wstring escaped;
	for (unsigned char ch : WideStringToString(text)) escaped += FormatString(L"%%%02X", (int)ch);
	return escaped;
}

std::string Escape(const std::string& text)
{
	std::string escaped;
	for (unsigned char ch : text) escaped += FormatString("%%%02X", (int)ch);
	return escaped;
}

TEST(assert(JSON::Parse<wchar_t>(LR"([{"string":"hello world","boolean":false,"number":1.67e+4,"null":null,"array":[]},"hello world"])")));
