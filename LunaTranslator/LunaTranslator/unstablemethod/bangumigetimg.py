
from urllib.parse import quote
import hashlib
import queue,time,requests,re,os

from utils.utils import getproxy
def b64string(a): 
    return hashlib.md5(a.encode('utf8')).digest().hex()


def vndbdownloadimg(url):
    if url is None:
         return None
    savepath='./cache/bangumi/'+b64string(url)+'.jpg'
    if os.path.exists(savepath):
         return savepath
    headers= {
        'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'Referer': 'https://vndb.org/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
        'sec-ch-ua-platform': '"Windows"',
    }  
    try:
        time.sleep(1)
        _content=requests.get(url,headers=headers,proxies=getproxy()).content
        with open(savepath,'wb') as ff:
            ff.write(_content)
        return savepath
    except:
         return None
def vndbsearch(title): 
     
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0', 
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://bangumi.tv/subject_search/amatutumi?cat=all',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
    }

    params = {
        'cat': '4',
    }
    url='http://bangumi.tv/subject_search/'+(title)
    
    savepath='./cache/bangumi/'+b64string(url)+'.html'
    #print(url,savepath)
    if not os.path.exists(savepath): 
        try: 
            time.sleep(1)
            response = requests.get(
                url,
                params=params, 
                headers=headers,proxies=getproxy(),
                verify=False,
            )  
            with open(savepath,'w',encoding='utf8') as ff:
                 ff.write(response.text)
            text=response.text
        except:
            return None
    else:
         with open(savepath,'r',encoding='utf8') as ff:
            text=ff.read()
     
    try:
        found=re.findall('<a href="(.*?)" class="l">',text)
    except:
        #print("??")
        return None 
    #print(found)
    if len(found)==0:
         return None
     
    url='http://bangumi.tv'+found[0]
    savepath='./cache/bangumi/'+b64string(url)+'.html'
    #print(url,savepath)
    if not os.path.exists(savepath): 
        try: 
            time.sleep(1)
            response = requests.get(url,   headers=headers,proxies=getproxy(),verify=False,)
            with open(savepath,'w',encoding='utf8') as ff:
                 ff.write(response.text)
            text=response.text
        except:
            return None
    else:
         with open(savepath,'r',encoding='utf8') as ff:
            text=ff.read()
    try: 
        imgurl=(re.search('<img src="(.*?)" width="(.*?)" class="cover"',text).groups()[0])
        return 'https:'+imgurl
    except:
        pass

def searchimgmethod(title):

    if os.path.exists('./cache/bangumi')==False:
        os.mkdir('./cache/bangumi')
    imgurl=vndbsearch(title) 
    #print(imgurl)
    savepath= vndbdownloadimg(imgurl)
    return savepath
def vndbsearchinfo(title): 
     
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0', 
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://bangumi.tv/subject_search/amatutumi?cat=all',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
    }

    params = {
        'cat': '4',
    }
    url='http://bangumi.tv/subject_search/'+(title)
    
    savepath='./cache/bangumi/'+b64string(url)+'.html'
    #print(url,savepath)
    if not os.path.exists(savepath): 
        try: 
            time.sleep(1)
            response = requests.get(
                url,
                params=params, 
                headers=headers,proxies=getproxy(),
                verify=False,
            )  
            with open(savepath,'w',encoding='utf8') as ff:
                 ff.write(response.text)
            text=response.text
        except:
            return None
    else:
         with open(savepath,'r',encoding='utf8') as ff:
            text=ff.read()
     
    try:
        found=re.findall('<a href="(.*?)" class="subjectCover cover ll">',text)
    except:
        #print("??")
        return None 
    #print(found)
    if len(found)==0:
         return None
    if found[0]=='/':
        return None
    url='http://bangumi.tv'+found[0]
    return url


def searchinfomethod(title):

    if os.path.exists('./cache/bangumi')==False:
        os.mkdir('./cache/bangumi')
    infosavepath=vndbsearchinfo(title)   
    return infosavepath
import re
def parsehtmlmethod(infopath):
     
    return infopath