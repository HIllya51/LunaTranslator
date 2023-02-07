import time
import sys
if sys.version_info.major==3:
    from PyQt5.QtCore import QCoreApplication 
    from PyQt5.QtWidgets import QMainWindow,QApplication
    from rpcman3 import RpcServer
    from gameagent3 import GameAgent
else:
    from PySide.QtCore import QCoreApplication 
    from PySide.QtGui import QMainWindow,QApplication
    from rpcman import RpcServer
    from gameagent import GameAgent
if __name__=="__main__":
    app =  QApplication(sys.argv) 
    rpc=RpcServer()
    rpc.start()   
    ga=GameAgent(rpc)
    ga.attachProcess(pid=4488)
    rpc.engineTextReceived.connect(ga.sendEmbeddedTranslation)
    rpc.clearAgentTranslation()
    x=QMainWindow()
    x.show()
    sys.exit(app.exec_())