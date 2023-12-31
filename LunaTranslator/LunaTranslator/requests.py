
from collections.abc import Callable, Mapping, MutableMapping
from collections import OrderedDict
from urllib.parse import urlencode,urlsplit
import gzip,json,base64
from winhttp import *

class CaseInsensitiveDict(MutableMapping): 

    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))
 
class Session:
    def __init__(self) -> None:
        self.UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.hSession=0
        self.status_code=0
        self.content=b'{}'
        self.cookies={}
        
        self.dfheaders=CaseInsensitiveDict({
            "User-Agent": self.UA,
            "Accept-Encoding": 'gzip, deflate',#br
            "Accept": "*/*",
            "Connection": "keep-alive",
        })
        self.headers=CaseInsensitiveDict()
    def __enter__(self):
        return self 
    def __exit__(self, *args):
        pass
    @staticmethod
    def _encode_params(data): 
        if isinstance(data, (str, bytes)):
            return data
        elif hasattr(data, "read"):
            return data
        elif hasattr(data, "__iter__"):
            result = []
            for k, vs in list(data.items()):
                if isinstance(vs, (str, bytes)) or not hasattr(vs, "__iter__"):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (
                                k.encode("utf-8") if isinstance(k, str) else k,
                                v.encode("utf-8") if isinstance(v, str) else v,
                            )
                        )
            return urlencode(result, doseq=True)
        else:
            return data
    def _parsedata(self,data,headers,js): 
         
        if data is None and js is None:
            dataptr=WINHTTP_NO_REQUEST_DATA
            datalen=0
        else:
            if data:
                dataptr=self._encode_params(data)
                
                if isinstance(dataptr,str):
                    dataptr=( dataptr).encode('utf8')
                datalen=len(dataptr)
                #print('dataptr',dataptr)
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = "application/x-www-form-urlencoded"
            elif js:
                dataptr=json.dumps(js).encode('utf8')
                datalen=len(dataptr)
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = "application/json"
        if datalen:
            headers['Content-Length']=str(datalen)
        #print(headers,dataptr,datalen)
        return headers,dataptr,datalen
     
    def raise_for_status(self):
        error=GetLastError()
        if error:
            raise WinhttpException(error)
     
    def _parseheader(self,headers,cookies):
        _x=[]
        #print(headers)
        
        if cookies:
            
            self.cookies.update(cookies)
            _c=[]
            for k ,v in self.cookies.items():
                _c.append('{}={}'.format(k,v)) 
            cookie='; '.join(_c)
            headers.update({'Cookie':cookie})
        for k  in sorted(headers.keys()):
            _x.append('{}: {}'.format(k,headers[k]))
        return '\r\n'.join(_x)
    
    def _getheaders(self,hreq):
        dwSize=DWORD()
        WinHttpQueryHeaders(hreq, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, None, pointer(dwSize), WINHTTP_NO_HEADER_INDEX);
        
        pszCookies=create_unicode_buffer(dwSize.value//2+1)
        succ=WinHttpQueryHeaders(hreq, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, pszCookies , pointer(dwSize), WINHTTP_NO_HEADER_INDEX)
        if succ==0:
            return {},{}
        return self._parseheader2dict(pszCookies.value)
    def _getStatusCode(self,hreq):
        dwSize=DWORD(sizeof(DWORD))
        dwStatusCode=DWORD()
        bResults = WinHttpQueryHeaders( hreq,   WINHTTP_QUERY_STATUS_CODE |   WINHTTP_QUERY_FLAG_NUMBER,  None, 
                                      pointer(dwStatusCode), 
                                      pointer(dwSize), 
                                      None )
        if bResults==0:
            self.raise_for_status()
        return dwStatusCode.value
    def _parseheader2dict(self,headerstr):
        #print(headerstr)
        header=CaseInsensitiveDict()
        cookie={}
        for line in headerstr.split('\r\n')[1:]:
            idx=line.find(': ')
            if line[:idx].lower()=='set-cookie':
                _c=line[idx+2:].split('; ')[0]
                _idx=_c.find('=')
                cookie[_c[:_idx]]=_c[idx+1:]
            else:   
                header[line[:idx]]=line[idx+2:] 
        return CaseInsensitiveDict(header),cookie
     
    def _parseurl(self,url,param):
        url=url.strip()
        scheme,server,path,query,_=urlsplit(url)
        if scheme=='https':
            ishttps=True
        elif scheme=='http':
            ishttps=False
        else:
            raise WinhttpException('unknown scheme '+scheme)
        spl=server.split(':')
        if len(spl)==2:
            server=spl[0]
            port=int(spl[1])
        elif len(spl)==1:
            spl[0]
            if ishttps:
                port=INTERNET_DEFAULT_HTTPS_PORT
            else:
                port=INTERNET_DEFAULT_HTTP_PORT
        else:
            raise WinhttpException('invalid url')
        if param:
            param=self._encode_params(param)
            query+=('&' if len(query) else '')+param
        if len(query):
            path+='?'+query
        return scheme,ishttps,server,port,path
    def _setproxy(self,hsess,proxy,scheme):
        if proxy is None:return 
        proxy= proxy.get(scheme,None)
        if proxy is None or proxy=='':return 
        winhttpsetproxy(hsess,proxy)
    
    def request(self,
        method, url, params=None, data=None, headers=None,proxies=None, json=None,cookies=None,  files=None,
        auth=None, timeout=None, allow_redirects=True,  hooks=None,   stream=None, verify=None, cert=None, ):
        if headers is None:
            headers=self.dfheaders
        else:
            headers=CaseInsensitiveDict(headers)
        if auth and isinstance(auth,tuple) and len(auth)==2: 
            headers['Authorization']="Basic " +   ( base64.b64encode(b":".join((auth[0].encode("latin1"), auth[1].encode("latin1")))).strip() ).decode() 
        
        scheme,ishttps,server,port,param=self._parseurl(url,params) 
        headers,dataptr,datalen=self._parsedata(data,headers,json)
        flag=WINHTTP_FLAG_SECURE if ishttps else 0
        #print(server,port,param,dataptr)
        headers= self._parseheader(headers,cookies)
        
        if self.hSession==0:
            self.hSession=AutoWinHttpHandle(WinHttpOpen(self.UA,WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,WINHTTP_NO_PROXY_NAME,WINHTTP_NO_PROXY_BYPASS,0))
            if self.hSession==0:
                raise WinhttpException(GetLastError())  
        
        hConnect=AutoWinHttpHandle(WinHttpConnect(self.hSession,server,port,0))
        if hConnect==0:
            raise WinhttpException(GetLastError())  
        hRequest=AutoWinHttpHandle(WinHttpOpenRequest( hConnect ,method,param,None,WINHTTP_NO_REFERER,WINHTTP_DEFAULT_ACCEPT_TYPES,flag) )
    
        self._setproxy(hRequest,proxies,scheme) 
        
        if hRequest==0:
            raise WinhttpException(GetLastError())
        succ=WinHttpSendRequest(hRequest,headers,-1,dataptr,datalen,datalen,None)
        if succ==0:
            raise WinhttpException(GetLastError())
        
        succ=WinHttpReceiveResponse(hRequest,None)
        if succ==0:
            raise WinhttpException(GetLastError())
        
        self.headers,self.cookies=((self._getheaders(hRequest))) 
        self.status_code=self._getStatusCode(hRequest)
        if stream:
            self.hconn=hConnect
            self.hreq=hRequest
            return self
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
            #这里可以做成流式的
            succ=WinHttpReadData(hRequest,buff,availableSize,pointer(downloadedSize))
            if succ==0:raise WinhttpException(GetLastError())
            downloadeddata+=buff[:downloadedSize.value]
        self.content=downloadeddata
        #print(self.text)
        
        return self
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
    @property
    def text(self): 
        encode=self.headers.get('Content-Encoding',None)
        try:
            if encode =='gzip':
                self.content=gzip.decompress(self.content)
            # elif encode=='br':
            #     self.content=brotli.decompress(self.content)
            return self.content.decode('utf8')
        except:
            raise Exception('unenable to decode {}'.format(encode))
    def json(self):
        return json.loads(self.text)
    def get(self, url, **kwargs): 
        return self.request("GET", url, **kwargs)
    def post(self, url, **kwargs): 
        return self.request("POST", url, **kwargs)
    def options(self, url, **kwargs): 
        return self.request("OPTIONS", url, **kwargs)
def request(method, url, **kwargs): 
    with Session() as session:
        return session.request(method=method, url=url, **kwargs)
def get(url, params=None, **kwargs):
    return request("GET", url, params=params, **kwargs)
def post(url, params=None, **kwargs):
    return request("POST", url, params=params, **kwargs)
def options(url, params=None, **kwargs):
    return request("OPTIONS", url, params=params, **kwargs)
def session():
    with Session() as session:
        return session
if __name__=='__main__':
    pass
     