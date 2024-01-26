 
from libcurl import *
import winsharedutils 

from network.requests_common import *
class autostatus:
    def __init__(self,ref) -> None:
        self.ref=ref
        ref._status=1
        
    def __del__(self):
        self.ref._status=0
class Response(ResponseBase):  
    def __init__(self):
        super().__init__()
        self.last_error=0
    def iter_content(self,chunk_size=1024):
        yield self.content
    def raise_for_status(self): 
        if self.last_error:
            raise CURLException(self.last_error) 
def ExceptionFilter(func):
    def _wrapper(*args,**kwargs): 
        try:
            _= func(*args,**kwargs)
            return _
        except CURLException as e:
            if e.errorcode==CURLcode.CURLE_OPERATION_TIMEDOUT:
                raise Timeout(e)
            else:
                raise e
    return _wrapper
class Session(Sessionbase):
 
    def __init__(self) -> None:
        super().__init__()
        self._status=0
        self.curl=AutoCURLHandle(curl_easy_init()) 
        curl_easy_setopt(self.curl,CURLoption.CURLOPT_COOKIEJAR,'') 
        curl_easy_setopt(self.curl,CURLoption.CURLOPT_USERAGENT,self.UA.encode('utf8'))
    def raise_for_status(self): 
        if self.last_error:
            raise CURLException(self.last_error)
      
     
    def _getStatusCode(self,curl):
        status_code=c_long()
        self.last_error=curl_easy_getinfo(curl,CURLINFO.CURLINFO_RESPONSE_CODE, pointer(status_code))
        self.raise_for_status()
        return status_code.value 
      
    def _set_proxy(self,curl,proxy):
        if proxy:
            self.last_error=curl_easy_setopt(curl,CURLoption.CURLOPT_PROXY,proxy.encode('utf8') )
            self.raise_for_status()
    def _set_verify(self,curl,verify):
        if verify==False:
            curl_easy_setopt(curl,CURLoption.CURLOPT_SSL_VERIFYPEER, 0)
            curl_easy_setopt(curl,CURLoption.CURLOPT_SSL_VERIFYHOST, 0)
        else:
            curl_easy_setopt(curl,CURLoption.CURLOPT_SSL_VERIFYPEER, 1)
            curl_easy_setopt(curl,CURLoption.CURLOPT_SSL_VERIFYHOST, 2)
    
    
    def _perform(self,curl):
        self.last_error=curl_easy_perform(curl)
        self.raise_for_status()
     
    def _getmembyte(self,mem):
        return cast(mem.memory,POINTER(c_char))[:mem.size]
    @ExceptionFilter
    def request_impl(self,
        method,scheme,server,port,param,url,headers,cookies,dataptr,datalen,proxy,stream,verify,timeout):
          
        if self._status==0:
            curl=self.curl
            __=autostatus(self)
        else:
            #不能多线程同时复用同一个curl对象
            curl=AutoCURLHandle(curl_easy_duphandle(self.curl)) 
            if cookies:
                cookies.update(self.cookies)
            else:
                cookies=self.cookies
        if cookies:
            cookie=self._parsecookie(cookies)
            curl_easy_setopt(curl, CURLoption.CURLOPT_COOKIE, cookie.encode('utf8'));
        if timeout:
            curl_easy_setopt(curl, CURLoption.CURLOPT_TIMEOUT_MS, timeout);
            curl_easy_setopt(curl, CURLoption.CURLOPT_CONNECTTIMEOUT_MS, timeout);
        curl_easy_setopt(curl,CURLoption.CURLOPT_ACCEPT_ENCODING, headers['Accept-Encoding'].encode('utf8'))

        curl_easy_setopt(curl,CURLoption.CURLOPT_CUSTOMREQUEST,method.upper().encode('utf8'))
        
        self.last_error=curl_easy_setopt(curl,CURLoption.CURLOPT_URL,url.encode('utf8'))
        self.raise_for_status()
        curl_easy_setopt(curl, CURLoption.CURLOPT_PORT, port ) 

        lheaders=Autoslist()
        for _ in self._parseheader(headers,None):
            lheaders = curl_slist_append(cast(lheaders,POINTER(curl_slist)), _.encode('utf8'));
        self.last_error=curl_easy_setopt(curl, CURLoption.CURLOPT_HTTPHEADER, lheaders);
        self.raise_for_status()

        self._set_verify(curl,verify)
        self._set_proxy(curl,proxy) 
        if datalen:
            curl_easy_setopt(curl,CURLoption.CURLOPT_POSTFIELDS,dataptr)
            curl_easy_setopt(curl,CURLoption.CURLOPT_POSTFIELDSIZE,datalen)

        _content=winsharedutils.MemoryStruct() 
        curl_easy_setopt(curl,CURLoption.CURLOPT_WRITEDATA,pointer(_content))
        curl_easy_setopt(curl,CURLoption.CURLOPT_WRITEFUNCTION,winsharedutils.WriteMemoryCallback)
        _headers=winsharedutils.MemoryStruct() 
        curl_easy_setopt(curl,CURLoption.CURLOPT_HEADERDATA,pointer(_headers))
        curl_easy_setopt(curl,CURLoption.CURLOPT_HEADERFUNCTION,winsharedutils.WriteMemoryCallback)  

        self._perform(curl)
        resp=Response()
        resp.content=self._getmembyte(_content)
        resp.status_code=self._getStatusCode(curl) 
        resp.last_error=self.last_error
        resp.headers=self._update_header_cookie(self._getmembyte(_headers).decode('utf8'))
        resp.cookies=self.cookies
        curl_easy_reset(curl)
        return resp
    
Sessionimpl[0]=Session
if __name__=='__main__':
     pass