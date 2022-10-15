import requests
from contextlib import closing
requests.packages.urllib3.disable_warnings()
requests.get('https://github.com/',verify = False,proxies = {"http":'194.195.213.197:1080',"https":'194.195.213.197:1080'})
 