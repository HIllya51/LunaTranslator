 
from libcurl import *
import winsharedutils,windows
import threading,queue
from network.requests_common import *
from traceback import print_exc
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
    def iter_content_impl(self,chunk_size=1):
        
        downloadeddata=b''
        getnum=0
        canend=False
        allbs=0
        while not(getnum==self._contentd.size and canend):
            buff=self.queue.get()
            
            if buff is None:
                canend=True
                continue
            allbs+=len(buff)
            if chunk_size:
                downloadeddata+=buff
                while len(downloadeddata)>chunk_size:
                    yield downloadeddata[:chunk_size]
                    downloadeddata=downloadeddata[chunk_size:]
            else:
                yield buff
            getnum+=1
        while len(downloadeddata):
            yield downloadeddata[:chunk_size]
            downloadeddata=downloadeddata[chunk_size:]
        del self.hreadd
        del self.hwrited
        
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
        
        resp=Response()

        if stream:
            resp.queue=queue.Queue()
            hreadd,hwrited=windows.CreatePipe(None,1024*1024*4)
            resp.hreadd=hreadd
            resp.hwrited=hwrited
            _contentd=winsharedutils.Pipeinfo()
            _contentd.memory=hwrited
            resp._contentd=_contentd
            curl_easy_setopt(curl,CURLoption.CURLOPT_WRITEDATA,pointer(resp._contentd))
            curl_easy_setopt(curl,CURLoption.CURLOPT_WRITEFUNCTION,winsharedutils.WriteMemoryToPipe)

            hreadh,hwriteh=windows.CreatePipe(None,1024*1024*4)
            _contenth=winsharedutils.Pipeinfo() 
            _contenth.memory=hwriteh
            curl_easy_setopt(curl,CURLoption.CURLOPT_HEADERDATA,pointer(_contenth))
            curl_easy_setopt(curl,CURLoption.CURLOPT_HEADERFUNCTION,winsharedutils.WriteMemoryToPipe)
            headerqueue=queue.Queue()
            headerok=threading.Lock()
            headerok.acquire()
            def ___perform():
                try:
                    self._perform(curl)
                except:
                    print_exc()
                    headerqueue.put(None)
                headerok.acquire()
                curl_easy_reset(curl)
                resp.queue.put(None)
            def ___read(q,h):
                while True:
                    size=windows.ReadFile(h,4,None)
                    if len(size)==0:break
                    data=windows.ReadFile(h,c_uint.from_buffer_copy(size).value,None)
                    q.put(data)
            threading.Thread(target=___read,args=(resp.queue,hreadd),daemon=True).start()
            threading.Thread(target=___read,args=(headerqueue,hreadh),daemon=True).start()
            threading.Thread(target=___perform,daemon=True).start()
            
            headerb=b''
            while True:
                _headerb=headerqueue.get()
                if _headerb is None:
                    break
                headerb+=_headerb
                if _headerb==b'\r\n':
                    break
            resp.headers=self._update_header_cookie(headerb.decode('utf8'))
            headerok.release()
        else:
            _content=winsharedutils.MemoryStruct() 
            curl_easy_setopt(curl,CURLoption.CURLOPT_WRITEDATA,pointer(_content))
            curl_easy_setopt(curl,CURLoption.CURLOPT_WRITEFUNCTION,winsharedutils.WriteMemoryCallback)
            _headers=winsharedutils.MemoryStruct() 
            curl_easy_setopt(curl,CURLoption.CURLOPT_HEADERDATA,pointer(_headers))
            curl_easy_setopt(curl,CURLoption.CURLOPT_HEADERFUNCTION,winsharedutils.WriteMemoryCallback)
            #curl_easy_setopt(curl,CURLoption.CURLOPT_HEADERFUNCTION,cast(WRITEFUNCTION(WRITEFUNCTIONXX),c_void_p))
            self._perform(curl)
            resp.content=self._getmembyte(_content)
            resp.headers=self._update_header_cookie(self._getmembyte(_headers).decode('utf8'))
        resp.status_code=self._getStatusCode(curl)
        resp.last_error=self.last_error
        resp.cookies=self.cookies
        if stream==False:
            curl_easy_reset(curl)
        return resp
    
Sessionimpl[0]=Session
if __name__=='__main__':
     pass