
from urllib.parse import quote
import hashlib
import queue,time,requests,re,os

from utils.utils import getproxy
def b64string(a): 
    return hashlib.md5(a.encode('utf8')).digest().hex()


def vndbdownloadimg(url):
    
    if url is None:
         return None
    savepath='./cache/2df/'+b64string(url)+'.jpg'
    if os.path.exists(savepath):
         return savepath
        
    headers = {
        'authority': 'img.achost.top',
        'accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'referer': 'https://2dfan.org/',
        'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
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
    url='https://2dfan.org/subjects/search?keyword='+(title)
    
    savepath='./cache/2df/'+b64string(url)+'.html'
    #print(url,savepath)
    if not os.path.exists(savepath): 
        try: 
            time.sleep(1)
            response = requests.get(
                url, 
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
        found=re.findall('<img class="media-object subject-package"(.*?)data-normal="(.*?)">',text)
    except:
        #print("??")
        return None 
    #print(found)
    if len(found)==0:
         return None
    found=found[0][1] 
    if 'normal_' in found:
        found=found.replace('normal_','')
        return found
    else:
        return None 

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
    url='https://2dfan.org/subjects/search?keyword='+(title)
    
    savepath='./cache/2df/'+b64string(url)+'.html'
    #print(url,savepath)
    if not os.path.exists(savepath): 
        try: 
            time.sleep(1)
            response = requests.get(
                url, 
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
        found=re.findall('<h4 class="media-heading">(.*?)</h4>',text)
    except:
        #print("??")
        return None 
    #print(found)
    if len(found)==0:
         return None
    
    found=found[0]
    found=re.findall('href="(.*?)"',found)[0]
    
    url='https://2dfan.org'+found
    return url
    savepath='./cache/2df/'+b64string(url)+'.html'
    #print(url,savepath)
    if not os.path.exists(savepath): 
        try: 
            time.sleep(1)
            response = requests.get(
                url, 
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
    return savepath


def searchdatamethod(title):

    if os.path.exists('./cache/2df')==False:
        os.mkdir('./cache/2df')
    imgurl=vndbsearch(title) 
    #print(imgurl)
    savepath= vndbdownloadimg(imgurl)
    infosavepath=vndbsearchinfo(title)   
    return {'imagepath':savepath,'infopath':infosavepath}
import re
def parsehtmlmethod(infopath): 
    return infopath