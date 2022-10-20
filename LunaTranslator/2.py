import requests
session=requests.session()
 
headers = {
    'Host': 'fanyi.baidu.com',
    'accept': 'application/json, text/plain, */*', 
    'user-agent': 'BdTranslateClient/1.5.4',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Dest': 'empty',
    'Accept-Language': 'zh-CN',
}

response = session.get('https://fanyi.baidu.com/client/getUserInfo',  headers=headers) 

headers = {
    'Host': 'fanyi.baidu.com',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN',
    'Referer': 'https://win.client.fanyi.baidu.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) BdTranslateClient/1.5.4 Chrome/87.0.4280.88 Electron/11.1.1 Safari/537.36',
}

data = {
    'query': 'おはよう',
    'from': 'jp',
    'to': 'zh',
    'type': '1|1',
    'domain': 'common',
    'sign': '102744.263241',
}

response = session.post('https://fanyi.baidu.com/client/translate',   headers=headers, data=data)

print('\n'.join([_['dst'] for _ in response.json()['data']['trans_result']['data']])  )