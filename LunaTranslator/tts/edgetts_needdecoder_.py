import requests

from PyQt5.QtWidgets import (QApplication)
import subprocess
import sys
class EDGETTS:
    def __init__(self)  :
        self.p=subprocess.Popen('./files/tts.exe',stdout=subprocess.PIPE)
        self.sess=requests.session()
    def gettts(self,sentence):
                
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain',
            # Requests sorts cookies= alphabetically
            # 'Cookie': 'last_grade27742983=0; last_grade2843471=4',
            'Origin': 'http://127.0.0.1:1233',
            'Pragma': 'no-cache',
            'Referer': 'http://127.0.0.1:1233/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
            'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        data = '        <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">          <voice name="ja-JP-KeitaNeural">              <prosody rate="0%" pitch="0%">                  '+sentence+'              </prosody >          </voice >        </speak > '
        response = self.sess.post('http://127.0.0.1:1233/api/ra' , headers=headers,data=data.encode('utf-8'))
        with open('1.webm','wb') as ff:
            ff.write(response.content   )
                
        import openal

        audio_file1=openal.oalOpen('1.webm')  
        audio_file1.play() #播放音频

        audio_file1.stop()   
if __name__=='__main__':
     
    tts=EDGETTS()
    tts.gettts('おはよう') 
   