// https://github.com/microsoft/Windows-classic-samples/blob/main/Samples/Win7Samples/netds/http/HttpV2Server/main.c
/*++
 Copyright (c) 2002 - 2002 Microsoft Corporation.  All Rights Reserved.

 THIS CODE AND INFORMATION IS PROVIDED "AS-IS" WITHOUT WARRANTY OF
 ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
 PARTICULAR PURPOSE.

 THIS CODE IS NOT SUPPORTED BY MICROSOFT.

--*/

#define SECURITY_WIN32
#include <http.h>
#include <sspi.h>
#include <strsafe.h>
#define NUM_SCHEMES 2
#define MAX_USERNAME_LENGTH 100
#pragma warning(disable : 4127) // condition expression is constant

//
// Macros.
//
#define INITIALIZE_HTTP_RESPONSE(resp, status, reason) \
    do                                                 \
    {                                                  \
        RtlZeroMemory((resp), sizeof(*(resp)));        \
        (resp)->StatusCode = (status);                 \
        (resp)->pReason = (reason);                    \
        (resp)->ReasonLength = (USHORT)strlen(reason); \
    } while (FALSE)

#define ADD_KNOWN_HEADER(Response, HeaderId, RawValue)                      \
    do                                                                      \
    {                                                                       \
        (Response).Headers.KnownHeaders[(HeaderId)].pRawValue = (RawValue); \
        (Response).Headers.KnownHeaders[(HeaderId)].RawValueLength =        \
            (USHORT)strlen(RawValue);                                       \
    } while (FALSE)

DECLARE_PLAIN_FUNCTION(const wchar_t *LUNA_CONTENTBYPASS(const wchar_t *_) { return _; })
DWORD SendHttpResponse(IN HANDLE hReqQueue, IN PHTTP_REQUEST pRequest)
{
    HTTP_RESPONSE response;
    DWORD result;
    DWORD bytesSent;
    ULONG BytesRead;
    HTTP_DATA_CHUNK dataChunk;
    std::string recv;
    std::string buff;
    buff.resize(2048);
    bool recving = true;
    //
    // Initialize the HTTP response structure.
    //
    INITIALIZE_HTTP_RESPONSE(&response, 200, "OK");

    //
    // For POST, we'll echo back the entity that we got from the client.
    //
    // NOTE: If we had passed the HTTP_RECEIVE_REQUEST_FLAG_COPY_BODY
    //       flag with HttpReceiveHttpRequest(), the entity would have
    //       been a part of HTTP_REQUEST (using the pEntityChunks field).
    //       Since we have not passed that flag, we can be assured that
    //       there are no entity bodies in HTTP_REQUEST.
    //
    if (pRequest->Flags & HTTP_REQUEST_FLAG_MORE_ENTITY_BODY_EXISTS)
    {
        // The entity body is send over multiple calls. Let's collect all
        // of these in a file & send it back. We'll create a temp file
        //

        do
        {
            //
            // Read the entity chunk from the request.
            //
            BytesRead = 0;
            result = HttpReceiveRequestEntityBody(
                hReqQueue,
                pRequest->RequestId,
                0,
                buff.data(),
                buff.capacity(),
                &BytesRead,
                NULL);
            switch (result)
            {
            case NO_ERROR:
            case ERROR_HANDLE_EOF:

                if (BytesRead != 0)
                {
                    recv += buff.substr(0, BytesRead);
                }
                if (result == ERROR_HANDLE_EOF)
                    recving = false;
                break;

            default:
                recving = false;
            }

        } while (recving);
    }
    if (recv.size())
        recv = WideStringToString(LUNA_CONTENTBYPASS(StringToWideString(recv).c_str()));
    if (recv.size())
    {
        ADD_KNOWN_HEADER(
            response,
            HttpHeaderContentLength,
            std::to_string(recv.size()).c_str());
    }
    result =
        HttpSendHttpResponse(
            hReqQueue,           // ReqQueueHandle
            pRequest->RequestId, // Request ID
            recv.size() ? HTTP_SEND_RESPONSE_FLAG_MORE_DATA : 0,
            &response,  // HTTP response
            NULL,       // pReserved1
            &bytesSent, // bytes sent (optional)
            NULL,       // pReserved2
            0,          // Reserved3
            NULL,       // LPOVERLAPPED
            NULL        // pReserved4
        );

    if (result != NO_ERROR)
    {
        return result;
    }
    if (!recv.size())
        return result;
    //
    // Send entity body from a file handle.
    //
    dataChunk.DataChunkType = HttpDataChunkFromMemory;
    dataChunk.FromMemory.pBuffer = (PVOID)recv.c_str();
    dataChunk.FromMemory.BufferLength = (ULONG)recv.size();

    result = HttpSendResponseEntityBody(
        hReqQueue,
        pRequest->RequestId,
        0, // This is the last send.
        1, // Entity Chunk Count.
        &dataChunk,
        NULL,
        NULL,
        0,
        NULL,
        NULL);

    return result;
}
DWORD DoReceiveRequests(HANDLE hReqQueue)
{
    ULONG result;
    HTTP_REQUEST_ID requestId;
    DWORD bytesRead;
    PHTTP_REQUEST pRequest;
    ULONG RequestBufferLength;

    //
    // Allocate a 2K buffer. Should be good for most requests, we'll grow
    // this if required. We also need space for a HTTP_REQUEST structure.
    //
    RequestBufferLength = sizeof(HTTP_REQUEST) + 2048;
    auto pRequestBuffer = std::make_unique<CHAR[]>(RequestBufferLength);

    pRequest = (PHTTP_REQUEST)pRequestBuffer.get();

    //
    // Wait for a new request -- This is indicated by a NULL request ID.
    //

    HTTP_SET_NULL_ID(&requestId);

    for (;;)
    {
        RtlZeroMemory(pRequest, RequestBufferLength);

        result = HttpReceiveHttpRequest(
            hReqQueue,           // Req Queue
            requestId,           // Req ID
            0,                   // Flags
            pRequest,            // HTTP request buffer
            RequestBufferLength, // req buffer length
            &bytesRead,          // bytes received
            NULL                 // LPOVERLAPPED
        );

        if (NO_ERROR == result)
        {
            //
            // Worked!
            //
            // switch (pRequest->Verb)
            // {
            // case HttpVerbGET:
            result = SendHttpResponse(
                hReqQueue,
                pRequest);

            // case HttpVerbPOST:
            // default:

            // if (result != NO_ERROR)
            // {
            //     break;
            // }

            //
            // Reset the Request ID so that we pick up the next request.
            //
            HTTP_SET_NULL_ID(&requestId);
        }
        else if (result == ERROR_MORE_DATA)
        {
            //
            // The input buffer was too small to hold the request headers
            // We have to allocate more buffer & call the API again.
            //
            // When we call the API again, we want to pick up the request
            // that just failed. This is done by passing a RequestID.
            //
            // This RequestID is picked from the old buffer.
            //
            requestId = pRequest->RequestId;

            RequestBufferLength = bytesRead;
            pRequestBuffer = std::make_unique<CHAR[]>(RequestBufferLength);

            pRequest = (PHTTP_REQUEST)pRequestBuffer.get();
        }
        else if (ERROR_CONNECTION_INVALID == result &&
                 !HTTP_IS_NULL_ID(&requestId))
        {
            // The TCP connection got torn down by the peer when we were
            // trying to pick up a request with more buffer. We'll just move
            // onto the next request.

            HTTP_SET_NULL_ID(&requestId);
        }
        else
        {
            break;
        }

    } // for(;;)

    return result;
}
namespace httpv1
{
    struct sessioninfo
    {
    };
    int cleanupservice(HANDLE hReqQueue, sessioninfo info)
    {
        CloseHandle(hReqQueue);
        HttpTerminate(HTTP_INITIALIZE_SERVER, NULL);
        return 0;
    }
    auto createservice(int port)
    {
        HANDLE hReqQueue = NULL;

        ULONG retCode;
        HTTPAPI_VERSION HttpApiVersion = HTTPAPI_VERSION_1;

        auto url = std::wstring(L"http://127.0.0.1:") + std::to_wstring(port) + L"/sakurakouji";
        //
        // Initialize HTTP APIs.
        //
        retCode = HttpInitialize(
            HttpApiVersion,
            HTTP_INITIALIZE_SERVER, // Flags
            NULL                    // Reserved
        );

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{}};
        }

        //
        // Create a request queue handle
        //

        retCode = HttpCreateHttpHandle(&hReqQueue,
                                       0);
        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{}};
        }
        retCode = HttpAddUrl(hReqQueue,
                             url.c_str(), 0);

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{}};
        }

        return std::tuple{true, hReqQueue, sessioninfo{}};
    }
}
namespace httpv2
{
    struct sessioninfo
    {
        HTTP_SERVER_SESSION_ID ssID;
        HTTP_URL_GROUP_ID urlGroupId;
    };
    int cleanupservice(HANDLE hReqQueue, sessioninfo info)
    {
        HTTP_SERVER_SESSION_ID ssID = info.ssID;
        HTTP_URL_GROUP_ID urlGroupId = info.urlGroupId;
        ULONG retCode;
        //
        // Call HttpRemoveUrl for all the URLs that we added.
        // HTTP_URL_FLAG_REMOVE_ALL flag allows us to remove
        // all the URLs registered on URL Group at once
        //
        if (!HTTP_IS_NULL_ID(&urlGroupId))
        {

            retCode = HttpRemoveUrlFromUrlGroup(urlGroupId,
                                                NULL,
                                                HTTP_URL_FLAG_REMOVE_ALL);
        }

        //
        // Close the Url Group
        //

        if (!HTTP_IS_NULL_ID(&urlGroupId))
        {
            retCode = HttpCloseUrlGroup(urlGroupId);
        }

        //
        // Close the serversession
        //

        if (!HTTP_IS_NULL_ID(&urlGroupId))
        {
            retCode = HttpCloseServerSession(ssID);
        }

        //
        // Close the Request Queue handle.
        //

        if (hReqQueue)
        {
            retCode = HttpCloseRequestQueue(hReqQueue);
        }

        //
        // Call HttpTerminate.
        //
        HttpTerminate(HTTP_INITIALIZE_SERVER, NULL);
        return retCode;
    }
    auto createservice(int port)
    {
        ULONG retCode;

        HANDLE hReqQueue = NULL;
        HTTP_SERVER_SESSION_ID ssID = HTTP_NULL_ID;
        HTTP_URL_GROUP_ID urlGroupId = HTTP_NULL_ID;
        HTTPAPI_VERSION HttpApiVersion = HTTPAPI_VERSION_2;
        HTTP_BINDING_INFO BindingProperty;
        HTTP_TIMEOUT_LIMIT_INFO CGTimeout;

        auto url = std::wstring(L"http://127.0.0.1:") + std::to_wstring(port) + L"/sakurakouji";
        //
        // Initialize HTTP APIs.
        //

        retCode = HttpInitialize(
            HttpApiVersion,
            HTTP_INITIALIZE_SERVER, // Flags
            NULL                    // Reserved
        );

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{ssID, urlGroupId}};
        }

        //
        // Create a server session handle
        //

        retCode = HttpCreateServerSession(HttpApiVersion,
                                          &ssID,
                                          0);

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{ssID, urlGroupId}};
        }

        //
        // Create UrlGroup handle
        //

        retCode = HttpCreateUrlGroup(ssID,
                                     &urlGroupId,
                                     0);

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{ssID, urlGroupId}};
        }

        //
        // Create a request queue handle
        //

        retCode = HttpCreateRequestQueue(HttpApiVersion,
                                         (std::wstring(L"LUNA_INTERNAL_HTTP_QUEUE") + std::to_wstring(GetCurrentProcessId()) + L"_" + std::to_wstring(rand())).c_str(),
                                         NULL,
                                         0,
                                         &hReqQueue);
        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{ssID, urlGroupId}};
        }

        BindingProperty.Flags.Present = 1; // Specifies that the property is present on UrlGroup
        BindingProperty.RequestQueueHandle = hReqQueue;

        //
        // Bind the request queue to UrlGroup
        //

        retCode = HttpSetUrlGroupProperty(urlGroupId,
                                          HttpServerBindingProperty,
                                          &BindingProperty,
                                          sizeof(BindingProperty));

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{ssID, urlGroupId}};
        }

        //
        // Set EntityBody Timeout property on UrlGroup
        //

        ZeroMemory(&CGTimeout, sizeof(HTTP_TIMEOUT_LIMIT_INFO));

        CGTimeout.Flags.Present = 1; // Specifies that the property is present on UrlGroup
        CGTimeout.EntityBody = 50;   // The timeout is in secs

        retCode = HttpSetUrlGroupProperty(urlGroupId,
                                          HttpServerTimeoutsProperty,
                                          &CGTimeout,
                                          sizeof(HTTP_TIMEOUT_LIMIT_INFO));

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{ssID, urlGroupId}};
        }

        //
        // Add the URLs on URL Group
        // The command line arguments represent URIs that we want to listen on.
        // We will call HttpAddUrlToUrlGroup for each of these URIs.
        //
        // The URI is a fully qualified URI and MUST include the terminating '/'
        //

        retCode = HttpAddUrlToUrlGroup(urlGroupId,
                                       url.c_str(),
                                       0,
                                       0);

        if (retCode != NO_ERROR)
        {
            return std::tuple{false, hReqQueue, sessioninfo{ssID, urlGroupId}};
        }
        return std::tuple{true, hReqQueue, sessioninfo{ssID, urlGroupId}};
    }
}
int GetRandomAvailablePort()
{
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0)
    {
        return 0;
    }

    // 创建一个 TCP 套接字
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET)
    {
        WSACleanup();
        return 0;
    }

    // 绑定到随机端口
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = 0; // 0 表示让系统自动选择一个可用端口

    result = bind(sock, (SOCKADDR *)&addr, sizeof(addr));
    if (result == SOCKET_ERROR)
    {
        closesocket(sock);
        WSACleanup();
        return 0;
    }

    // 获取实际绑定的端口号
    int addrLen = sizeof(addr);
    result = getsockname(sock, (SOCKADDR *)&addr, &addrLen);
    if (result == SOCKET_ERROR)
    {
        closesocket(sock);
        WSACleanup();
        return 0;
    }

    // 关闭套接字
    closesocket(sock);
    WSACleanup();

    // 返回实际绑定的端口号
    return ntohs(addr.sin_port);
}

#ifndef WINXP
using namespace httpv2;
#else
using namespace httpv1;
#endif

int makehttpgetserverinternal()
{
    // 尝试1000次
    for (int i = 0; i < 1000; i++)
    {
        auto port = GetRandomAvailablePort();
        auto [succ, hReqQueue, session] = createservice(port);
        if (!succ)
        {
            cleanupservice(hReqQueue, session);
            continue;
        }
        std::thread([=]()
                    {
                // Loop while receiving requests
                DoReceiveRequests(hReqQueue);
                cleanupservice(hReqQueue, session); })
            .detach();
        return port;
    }
    return 0;
}