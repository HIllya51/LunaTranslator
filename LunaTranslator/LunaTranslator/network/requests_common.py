import json,gzip,base64
from collections.abc import Callable, Mapping, MutableMapping
from collections import OrderedDict
from urllib.parse import urlencode,urlsplit

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

class Sessionbase:
    def __init__(self) -> None:
        self.UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.last_error=0
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
            dataptr=None
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
     
    def _parseurl(self,url,param):
        url=url.strip()
        scheme,server,path,query,_=urlsplit(url)
        if scheme not in ['https','http']:
            raise Exception('unknown scheme '+scheme)
        spl=server.split(':')
        if len(spl)==2:
            server=spl[0]
            port=int(spl[1])
        elif len(spl)==1:
            spl[0]
            if scheme=='https':
                port=443
            else:
                port=80
        else:
            raise Exception('invalid url')
        if param:
            param=self._encode_params(param)
            query+=('&' if len(query) else '')+param
        if len(query):
            path+='?'+query
        url=scheme+'://'+server+path
        return scheme,server,port,path,url
    def _parseheader(self,headers,cookies):
        _x=[] 
        
        if cookies:
            
            self.cookies.update(cookies)
        _c=[]
        for k ,v in self.cookies.items():
            _c.append('{}={}'.format(k,v)) 
        cookie='; '.join(_c)
        headers.update({'Cookie':cookie})
        for k  in sorted(headers.keys()):
            _x.append('{}: {}'.format(k,headers[k]))
        return _x
    def _update_header_cookie(self,headerstr):
        self.headers,cookies=self._parseheader2dict(headerstr)
        self.cookies.update(cookies) 
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
    def request_impl(self,*args):
        pass
    def request(self,
        method, url, params=None, data=None, headers=None,proxies=None, json=None,cookies=None,  files=None,
        auth=None, timeout=None, allow_redirects=True,  hooks=None,   stream=None, verify=False, cert=None, ):
        
        headers=CaseInsensitiveDict(headers) if headers else self.dfheaders
        if auth and isinstance(auth,tuple) and len(auth)==2: 
            headers['Authorization']="Basic " +   ( base64.b64encode(b":".join((auth[0].encode("latin1"), auth[1].encode("latin1")))).strip() ).decode() 
        
        
        scheme,server,port,param,url=self._parseurl(url,params) 
        headers,dataptr,datalen=self._parsedata(data,headers,json)
        headers=self._parseheader(headers,cookies)
        proxy= proxies.get(scheme,None) if proxies  else None
        _= self.request_impl(method,scheme,server,port,param,url,headers,dataptr,datalen,proxy,stream,verify)

        return _
Sessionimpl=[Sessionbase]
def request(method, url, **kwargs): 
    with Sessionimpl[0]() as session:
        return session.request(method=method, url=url, **kwargs)
def get(url, params=None, **kwargs):
    return request("GET", url, params=params, **kwargs)
def post(url, params=None, **kwargs):
    return request("POST", url, params=params, **kwargs)
def options(url, params=None, **kwargs):
    return request("OPTIONS", url, params=params, **kwargs)
def session():
    with Sessionimpl[0]() as session:
        return session