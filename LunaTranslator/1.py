#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
QNetworkAccessManager in PyQt

In this example we get a web page.

Author: Jan Bodnar
Website: zetcode.com
Last edited: September 2017
'''

from PyQt5 import  QtNetwork
from PyQt5.QtCore import QCoreApplication, QUrl
import sys
            
class Example:
  
    def __init__(self):    
        
        self.doRequest()
        
        
    def doRequest(self):   
    
        url = "https://www.google.com.hk/"
        req = QtNetwork.QNetworkRequest(QUrl(url))
        
        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        self.nam.get(req)    
             
      
    def handleResponse(self, reply):

        er = reply.error()
        
        if er == QtNetwork.QNetworkReply.NoError:
    
            bytes_string = reply.readAll()
            print(str(bytes_string, 'utf-8'))
            
        else:
            print("Error occured: ", er)
            print(reply.errorString())
            
        QCoreApplication.quit()    
        

app = QCoreApplication([])
ex = Example()
sys.exit(app.exec_())
