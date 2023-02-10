import time
import sys  
from PyQt5.QtWidgets import QMainWindow,QApplication
from rpcman3 import RpcServer
from gameagent3 import GameAgent 
if __name__=="__main__":
    app =  QApplication(sys.argv) 
    rpc=RpcServer()
    rpc.start()   
    ga=GameAgent(rpc)
    ga.attachProcess(pid=16256)
    rpc.engineTextReceived.connect(ga.sendEmbeddedTranslation)
    rpc.clearAgentTranslation()
    x=QMainWindow()
    x.show()
    sys.exit(app.exec_())