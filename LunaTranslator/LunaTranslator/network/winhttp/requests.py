
from winhttp import * 
from network.requests_common import *
import gzip,zlib
from ctypes import pointer,create_string_buffer
try:
    from brotli_dec import decompress
except:
    pass
class Response(ResponseBase):  
    def iter_content(self,chunk_size=1024):
        downloadedSize=DWORD()
        buff=create_string_buffer(chunk_size) 
        while True:
            succ=WinHttpReadData(self.hreq,buff,chunk_size,pointer(downloadedSize))
            if succ==0:raise WinhttpException(GetLastError())
            if downloadedSize.value==0:
                del self.hreq
                del self.hconn
                break
            yield buff[:downloadedSize.value]
    def raise_for_status(self):
        error=GetLastError()
        if error:
            raise WinhttpException(error)        
def ExceptionFilter(func):
    def _wrapper(*args,**kwargs): 
        try:
            _= func(*args,**kwargs)
            return _
        except WinhttpException as e:
            if e.errorcode==WinhttpException.ERROR_WINHTTP_TIMEOUT:
                raise Timeout(e)
            else:
                raise e
    return _wrapper
       
class Session(Sessionbase):
    def __init__(self) -> None:
        super().__init__()
        self.hSession=AutoWinHttpHandle(WinHttpOpen(self.UA,WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,WINHTTP_NO_PROXY_NAME,WINHTTP_NO_PROXY_BYPASS,0))
        if self.hSession==0:
            raise WinhttpException(GetLastError())  
      
    
    def _getheaders(self,hreq):
        dwSize=DWORD()
        WinHttpQueryHeaders(hreq, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, None, pointer(dwSize), WINHTTP_NO_HEADER_INDEX);
        
        pszCookies=create_unicode_buffer(dwSize.value//2+1)
        succ=WinHttpQueryHeaders(hreq, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, pszCookies , pointer(dwSize), WINHTTP_NO_HEADER_INDEX)
        if succ==0:
            return ''
        return (pszCookies.value)
    def _getStatusCode(self,hreq):
        dwSize=DWORD(sizeof(DWORD))
        dwStatusCode=DWORD()
        bResults = WinHttpQueryHeaders( hreq,   WINHTTP_QUERY_STATUS_CODE |   WINHTTP_QUERY_FLAG_NUMBER,  None, 
                                      pointer(dwStatusCode), 
                                      pointer(dwSize), 
                                      None )
        if bResults==0:
            error=GetLastError()
            if error:
                raise WinhttpException(error)        
        return dwStatusCode.value
     
    def _set_proxy(self,hsess,proxy):
        if proxy:
            winhttpsetproxy(hsess,proxy)
    def _set_verify(self,curl,verify):
        if verify==False:
            dwFlags=DWORD(SECURITY_FLAG_IGNORE_ALL_CERT_ERRORS)
            WinHttpSetOption(curl,WINHTTP_OPTION_SECURITY_FLAGS, pointer(dwFlags),sizeof(dwFlags))
    @ExceptionFilter
    def request_impl(self,
        method,scheme,server,port,param,url,headers,cookies,dataptr,datalen,proxy,stream,verify,timeout):
        headers=self._parseheader(headers,cookies)
        flag=WINHTTP_FLAG_SECURE if scheme=='https' else 0
        #print(server,port,param,dataptr)
        headers='\r\n'.join(headers)

        hConnect=AutoWinHttpHandle(WinHttpConnect(self.hSession,server,port,0))
        if hConnect==0:
            raise WinhttpException(GetLastError())  
        hRequest=AutoWinHttpHandle(WinHttpOpenRequest( hConnect ,method,param,None,WINHTTP_NO_REFERER,WINHTTP_DEFAULT_ACCEPT_TYPES,flag) )
        if timeout:
            WinHttpSetTimeouts(hRequest, timeout, timeout, timeout, timeout)
        if hRequest==0:
            raise WinhttpException(GetLastError())
        self._set_verify(hRequest,verify)
        self._set_proxy(hRequest,proxy) 
        
        succ=WinHttpSendRequest(hRequest,headers,-1,dataptr,datalen,datalen,None)
        if succ==0:
            raise WinhttpException(GetLastError())
        
        succ=WinHttpReceiveResponse(hRequest,None)
        if succ==0:
            raise WinhttpException(GetLastError())
        
        headers=self._update_header_cookie(self._getheaders(hRequest))
        resp=Response()
        resp.status_code=self._getStatusCode(hRequest)
        resp.headers=headers
        resp.cookies=self.cookies
        if stream:
            resp.hconn=hConnect
            resp.hreq=hRequest
            return resp
        availableSize=DWORD()
        downloadedSize=DWORD()
        downloadeddata=b''
        while True:
            succ=WinHttpQueryDataAvailable(hRequest,pointer(availableSize))
            if succ==0:
                raise WinhttpException(GetLastError())
            if availableSize.value==0:
                break
            buff=create_string_buffer(availableSize.value)
            succ=WinHttpReadData(hRequest,buff,availableSize,pointer(downloadedSize))
            if succ==0:raise WinhttpException(GetLastError())
            downloadeddata+=buff[:downloadedSize.value]
         
        resp.content=self.decompress(downloadeddata,headers)
        
        return resp
     
    def decompress(self,data,headers): 
        #WINHTTP_OPTION_DECOMPRESSION
        #支持gzip和deflate，WINHTTP_DECOMPRESSION_FLAG_GZIP|WINHTTP_DECOMPRESSION_FLAG_DEFLATE
        #但只支持win8.1+,不支持br
        encode=headers.get('Content-Encoding',None)
        try:
            if encode =='gzip':
                data=gzip.decompress(data)
            elif encode =='deflate':
                data=zlib.decompress(data, -zlib.MAX_WBITS)
            elif encode=='br':  
                data=decompress(data)
            return data
        except:
            raise Exception('unenable to decompress {}'.format(encode))
Sessionimpl[0]=Session
if __name__=='__main__':
    pass
     