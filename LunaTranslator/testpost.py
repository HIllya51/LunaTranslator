import time
starttime=time.time() 
from threading import Thread
import os
import json
import sys

from utils.config import postprocessconfig 
from traceback import print_exc  
dirname, filename = os.path.split(os.path.abspath(__file__))

from postprocess.post import POSTSOLVE 
print(POSTSOLVE('神神様様だだろろううかか？？神神様様だだろろううかか？？'))

print(POSTSOLVE('''
<link rel="canonical" href="https://blog.csdn.net/jackandsnow/article/details/103885422"/>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <meta name="renderer" content="webkit"/>
    <meta name="force-rendering" content="webkit"/>
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="report" content='{"pid": "blog", "spm":"1001.2101"}'>
    <meta name="referrer" content="always">
    <meta http-equiv="Cache-Control" content="no-siteapp" /><link rel="alternate" media="handheld" href="#" />
    <meta name="shenma-site-verification" content="5a59773ab8077d4a62bf469ab966a63b_1497598848">
    <meta name="applicable-device" content="pc">
    <link  href="https://g.csdnimg.cn/static/logo/favicon32.ico"  rel="shortcut icon" type="image/x-icon" />
    <title>re.sub()用法的详细介绍_jackandsnow的博客-CSDN博客_re。sub</title>
    <script>
      (function(){ 
'''))