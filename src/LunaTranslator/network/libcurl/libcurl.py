import gobject
from requests import RequestException, Timeout
from ctypes import (
    CDLL,
    c_void_p,
    c_int,
    c_char_p,
    c_long,
    CFUNCTYPE,
    c_size_t,
    c_char,
    Structure,
    POINTER,
    c_int64,
    c_uint,
)

libcurl = CDLL(gobject.GetDllpath(("libcurl.dll", "libcurl-x64.dll")))


class curl_ws_frame(Structure):
    _fields_ = [
        ("age", c_int),
        ("flags", c_int),
        ("offset", c_int64),
        ("bytesleft", c_int64),
        ("len", c_size_t),
    ]


CURLcode = c_uint


class CURLoption(c_int):
    CURLOPTTYPE_LONG = 0
    CURLOPTTYPE_OBJECTPOINT = 10000
    CURLOPTTYPE_FUNCTIONPOINT = 20000

    CURLOPTTYPE_SLISTPOINT = CURLOPTTYPE_OBJECTPOINT
    CURLOPTTYPE_STRINGPOINT = CURLOPTTYPE_OBJECTPOINT
    CURLOPTTYPE_CBPOINT = CURLOPTTYPE_OBJECTPOINT

    WRITEDATA = CURLOPTTYPE_CBPOINT + 1
    URL = CURLOPTTYPE_STRINGPOINT + 2
    PORT = CURLOPTTYPE_LONG + 3
    PROXY = CURLOPTTYPE_STRINGPOINT + 4
    WRITEFUNCTION = CURLOPTTYPE_FUNCTIONPOINT + 11
    POSTFIELDS = CURLOPTTYPE_OBJECTPOINT + 15
    USERAGENT = CURLOPTTYPE_STRINGPOINT + 18
    COOKIE = CURLOPTTYPE_STRINGPOINT + 22
    HTTPHEADER = CURLOPTTYPE_SLISTPOINT + 23
    HEADERDATA = CURLOPTTYPE_CBPOINT + 29
    COOKIEFILE = CURLOPTTYPE_STRINGPOINT + 31
    CUSTOMREQUEST = CURLOPTTYPE_STRINGPOINT + 36
    NOBODY = CURLOPTTYPE_LONG + 44
    POST = CURLOPTTYPE_LONG + 47
    FOLLOWLOCATION = CURLOPTTYPE_LONG + 52
    POSTFIELDSIZE = CURLOPTTYPE_LONG + 60
    SSL_VERIFYPEER = CURLOPTTYPE_LONG + 64
    MAXREDIRS = CURLOPTTYPE_LONG + 68
    HEADERFUNCTION = CURLOPTTYPE_FUNCTIONPOINT + 79
    HTTPGET = CURLOPTTYPE_LONG + 80
    SSL_VERIFYHOST = CURLOPTTYPE_LONG + 81
    COOKIEJAR = CURLOPTTYPE_STRINGPOINT + 82
    COOKIESESSION = CURLOPTTYPE_LONG + 96
    SHARE = CURLOPTTYPE_OBJECTPOINT + 100
    ACCEPT_ENCODING = CURLOPTTYPE_STRINGPOINT + 102
    CONNECT_ONLY = CURLOPTTYPE_LONG + 141
    TIMEOUT_MS = CURLOPTTYPE_LONG + 155
    CONNECTTIMEOUT_MS = CURLOPTTYPE_LONG + 156


class CURLINFO(c_int):
    STRING = 0x100000
    LONG = 0x200000
    DOUBLE = 0x300000
    SLIST = 0x400000
    PTR = 0x400000
    SOCKET = 0x500000
    OFF_T = 0x600000
    MASK = 0x0FFFFF
    TYPEMASK = 0xF00000
    NONE = 0
    EFFECTIVE_URL = STRING + 1
    RESPONSE_CODE = LONG + 2
    TOTAL_TIME = DOUBLE + 3
    NAMELOOKUP_TIME = DOUBLE + 4
    CONNECT_TIME = DOUBLE + 5
    PRETRANSFER_TIME = DOUBLE + 6
    SIZE_UPLOAD = DOUBLE + 7
    SIZE_UPLOAD_T = OFF_T + 7
    SIZE_DOWNLOAD = DOUBLE + 8
    SIZE_DOWNLOAD_T = OFF_T + 8
    SPEED_DOWNLOAD = DOUBLE + 9
    SPEED_DOWNLOAD_T = OFF_T + 9
    SPEED_UPLOAD = DOUBLE + 10
    SPEED_UPLOAD_T = OFF_T + 10
    HEADER_SIZE = LONG + 11
    REQUEST_SIZE = LONG + 12
    SSL_VERIFYRESULT = LONG + 13
    FILETIME = LONG + 14
    FILETIME_T = OFF_T + 14
    CONTENT_LENGTH_DOWNLOAD = DOUBLE + 15
    CONTENT_LENGTH_DOWNLOAD_T = OFF_T + 15
    CONTENT_LENGTH_UPLOAD = DOUBLE + 16
    CONTENT_LENGTH_UPLOAD_T = OFF_T + 16
    STARTTRANSFER_TIME = DOUBLE + 17
    CONTENT_TYPE = STRING + 18
    REDIRECT_TIME = DOUBLE + 19
    REDIRECT_COUNT = LONG + 20
    PRIVATE = STRING + 21
    HTTP_CONNECTCODE = LONG + 22
    HTTPAUTH_AVAIL = LONG + 23
    PROXYAUTH_AVAIL = LONG + 24
    OS_ERRNO = LONG + 25
    NUM_CONNECTS = LONG + 26
    SSL_ENGINES = SLIST + 27
    COOKIELIST = SLIST + 28
    LASTSOCKET = LONG + 29
    FTP_ENTRY_PATH = STRING + 30
    REDIRECT_URL = STRING + 31
    PRIMARY_IP = STRING + 32
    APPCONNECT_TIME = DOUBLE + 33
    CERTINFO = PTR + 34
    CONDITION_UNMET = LONG + 35
    RTSP_SESSION_ID = STRING + 36
    RTSP_CLIENT_CSEQ = LONG + 37
    RTSP_SERVER_CSEQ = LONG + 38
    RTSP_CSEQ_RECV = LONG + 39
    PRIMARY_PORT = LONG + 40
    LOCAL_IP = STRING + 41
    LOCAL_PORT = LONG + 42
    TLS_SESSION = PTR + 43
    ACTIVESOCKET = SOCKET + 44
    TLS_SSL_PTR = PTR + 45
    HTTP_VERSION = LONG + 46
    PROXY_SSL_VERIFYRESULT = LONG + 47
    PROTOCOL = LONG + 48
    SCHEME = STRING + 49
    TOTAL_TIME_T = OFF_T + 50
    NAMELOOKUP_TIME_T = OFF_T + 51
    CONNECT_TIME_T = OFF_T + 52
    PRETRANSFER_TIME_T = OFF_T + 53
    STARTTRANSFER_TIME_T = OFF_T + 54
    REDIRECT_TIME_T = OFF_T + 55
    APPCONNECT_TIME_T = OFF_T + 56
    RETRY_AFTER = OFF_T + 57
    EFFECTIVE_METHOD = STRING + 58
    PROXY_ERROR = LONG + 59
    REFERER = STRING + 60
    CAINFO = STRING + 61
    CAPATH = STRING + 62
    XFER_ID = OFF_T + 63
    CONN_ID = OFF_T + 64
    LASTONE = 64


class CURL(c_void_p):
    def __del__(self):
        if self:
            curl_easy_cleanup(self)


class curl_slist(Structure):
    pass


curl_slist._fields_ = [("data", c_char_p), ("next", POINTER(curl_slist))]


class auto_curl_slist:
    def __del__(self):
        if self.ptr:
            curl_slist_free_all(self.ptr)

    def __init__(self):
        self.ptr = None
        self.tail = None

    def append(self, value: str):
        self.tail = curl_slist_append(self.tail, value.encode("utf8"))
        if not self.ptr:
            self.ptr = self.tail


curl_global_init = libcurl.curl_global_init
curl_global_init.argtypes = (c_long,)
curl_global_init.restype = CURLcode
curl_global_init(3)
curl_global_cleanup = libcurl.curl_global_cleanup
curl_easy_init = libcurl.curl_easy_init
curl_easy_init.restype = CURL
curl_easy_setopt = libcurl.curl_easy_setopt
curl_easy_setopt.argtypes = CURL, CURLoption, c_void_p
curl_easy_setopt.restype = CURLcode
curl_easy_perform = libcurl.curl_easy_perform
curl_easy_perform.argtypes = (CURL,)
curl_easy_perform.restype = CURLcode
curl_easy_cleanup = libcurl.curl_easy_cleanup
curl_easy_cleanup.argtypes = (CURL,)
curl_slist_append = libcurl.curl_slist_append
curl_slist_append.argtypes = POINTER(curl_slist), c_char_p
curl_slist_append.restype = POINTER(curl_slist)
curl_slist_free_all = libcurl.curl_slist_free_all
curl_slist_free_all.argtypes = (POINTER(curl_slist),)
curl_easy_getinfo = libcurl.curl_easy_getinfo
curl_easy_getinfo.argtypes = CURL, CURLINFO, c_void_p
curl_easy_getinfo.restype = CURLcode
curl_easy_recv = libcurl.curl_easy_recv
curl_easy_recv.argtypes = CURL, c_void_p, c_size_t, POINTER(c_size_t)
curl_easy_recv.restype = CURLcode
curl_easy_strerror = libcurl.curl_easy_strerror
curl_easy_strerror.argtypes = (CURLcode,)
curl_easy_strerror.restype = c_char_p
curl_easy_duphandle = libcurl.curl_easy_duphandle
curl_easy_duphandle.argtypes = (CURL,)
curl_easy_duphandle.restype = CURL
curl_easy_reset = libcurl.curl_easy_reset
curl_easy_reset.argtypes = (CURL,)

try:
    curl_ws_recv = libcurl.curl_ws_recv
    curl_ws_recv.argtypes = (
        CURL,
        c_void_p,
        c_size_t,
        POINTER(c_size_t),
        POINTER(POINTER(curl_ws_frame)),
    )
    curl_ws_recv.restype = CURLcode
    curl_ws_send = libcurl.curl_ws_send
    curl_ws_send.argtypes = CURL, c_void_p, c_size_t, POINTER(c_size_t), c_int64, c_uint
    curl_ws_send.restype = CURLcode
except:

    def curl_ws_send(*a):
        return CURLException.UNSUPPORTED_PROTOCOL

    def curl_ws_recv(*a):
        return CURLException.UNSUPPORTED_PROTOCOL


CURLWS_TEXT = 1 << 0
CURLWS_BINARY = 1 << 1
CURLWS_CLOSE = 1 << 3
WRITEFUNCTION = CFUNCTYPE(c_size_t, POINTER(c_char), c_size_t, c_size_t, c_void_p)


class CURLException(RequestException):
    OK = 0
    UNSUPPORTED_PROTOCOL = 1
    FAILED_INIT = 2
    URL_MALFORMAT = 3
    NOT_BUILT_IN = 4
    COULDNT_RESOLVE_PROXY = 5
    COULDNT_RESOLVE_HOST = 6
    COULDNT_CONNECT = 7
    FTP_WEIRD_SERVER_REPLY = 8
    REMOTE_ACCESS_DENIED = 9
    FTP_ACCEPT_FAILED = 10
    FTP_WEIRD_PASS_REPLY = 11
    FTP_ACCEPT_TIMEOUT = 12
    FTP_WEIRD_PASV_REPLY = 13
    FTP_WEIRD_227_FORMAT = 14
    FTP_CANT_GET_HOST = 15
    HTTP2 = 16
    FTP_COULDNT_SET_TYPE = 17
    PARTIAL_FILE = 18
    FTP_COULDNT_RETR_FILE = 19
    QUOTE_ERROR = 21
    HTTP_RETURNED_ERROR = 22
    WRITE_ERROR = 23
    UPLOAD_FAILED = 25
    READ_ERROR = 26
    OUT_OF_MEMORY = 27
    OPERATION_TIMEDOUT = 28
    FTP_PORT_FAILED = 30
    FTP_COULDNT_USE_REST = 31
    RANGE_ERROR = 33
    HTTP_POST_ERROR = 34
    SSL_CONNECT_ERROR = 35
    BAD_DOWNLOAD_RESUME = 36
    FILE_COULDNT_READ_FILE = 37
    LDAP_CANNOT_BIND = 38
    LDAP_SEARCH_FAILED = 39
    FUNCTION_NOT_FOUND = 41
    ABORTED_BY_CALLBACK = 42
    BAD_FUNCTION_ARGUMENT = 43
    INTERFACE_FAILED = 45
    TOO_MANY_REDIRECTS = 47
    UNKNOWN_TELNET_OPTION = 48
    TELNET_OPTION_SYNTAX = 49
    PEER_FAILED_VERIFICATION = 51
    GOT_NOTHING = 52
    SSL_ENGINE_NOTFOUND = 53
    SSL_ENGINE_SETFAILED = 54
    SEND_ERROR = 55
    RECV_ERROR = 56
    SSL_CERTPROBLEM = 58
    SSL_CIPHER = 59
    SSL_CACERT = 60
    BAD_CONTENT_ENCODING = 61
    LDAP_INVALID_URL = 62
    FILESIZE_EXCEEDED = 63
    USE_SSL_FAILED = 64
    SEND_FAIL_REWIND = 65
    SSL_ENGINE_INITFAILED = 66
    LOGIN_DENIED = 67
    TFTP_NOTFOUND = 68
    TFTP_PERM = 69
    REMOTE_DISK_FULL = 70
    TFTP_ILLEGAL = 71
    TFTP_UNKNOWNID = 72
    REMOTE_FILE_EXISTS = 73
    TFTP_NOSUCHUSER = 74
    CONV_FAILED = 75
    CONV_REQD = 76
    SSL_CACERT_BADFILE = 77
    REMOTE_FILE_NOT_FOUND = 78
    SSH = 79
    SSL_SHUTDOWN_FAILED = 80
    AGAIN = 81
    SSL_CRL_BADFILE = 82
    SSL_ISSUER_ERROR = 83
    FTP_PRET_FAILED = 84
    RTSP_CSEQ_ERROR = 85
    RTSP_SESSION_ERROR = 86
    FTP_BAD_FILE_LIST = 87
    CHUNK_FAILED = 88
    NO_CONNECTION_AVAILABLE = 89
    SSL_PINNEDPUBKEYNOTMATCH = 90
    SSL_INVALIDCERTSTATUS = 91
    HTTP2_STREAM = 92
    RECURSIVE_API_CALL = 93
    AUTH_ERROR = 94
    HTTP3 = 95
    QUIC_CONNECT_ERROR = 96
    PROXY = 97
    SSL_CLIENTCERT = 98
    UNRECOVERABLE_POLL = 99
    TOO_LARGE = 100
    ECH_REQUIRED = 101
    LAST = 102

    def __init__(self, code) -> None:
        self.code = code
        error = "UNKNOWN ERROR {}".format(code)
        message = curl_easy_strerror(code).decode("utf8")
        for _ in dir(self):
            if _.startswith("") and code == getattr(self, _):
                error = _
                break
        if message:
            error += ": {}".format(message)
        super().__init__(error)


class CURLException_BAD_CONTENT_ENCODING(Exception):
    pass


def MaybeRaiseException(error):
    if not error:
        return
    e = CURLException(error)
    if error == CURLException.OPERATION_TIMEDOUT:
        raise Timeout(e)
    if error == CURLException.BAD_CONTENT_ENCODING:
        raise CURLException_BAD_CONTENT_ENCODING(e)
    raise e
