import requests 
def ocr(imgfile,_,space): 

    headers = { 
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }
    
    file = open(imgfile,'rb')
    files = {'pic': ('pic.jpg', file) }
    r = requests.post(url='http://ocr.shouji.sogou.com/v2/ocr/json', files=files, headers=headers) 
    res=''
    for l in r.json()['result']:
        if res!='':
                res+=space
        res+=l['content']
    return res
 