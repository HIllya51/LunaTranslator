# coding: utf8
# gameagent.py
# 5/2/2014 jichi
 
from PyQt5.QtCore import QObject, pyqtSignal, QTimer   
import   embedded.sharedmem3 as sharedmem 
from utils.config import globalconfig
from embedded  import inject 
from utils import somedef
class GameAgent(QObject):
  def __init__(self,rpc ):
    super(GameAgent, self).__init__( )
     
    self.mem = sharedmem.VnrAgentSharedMemory( )
    self.hostengine=None
    self.rpc =rpc

    self.rpc.agentConnected.connect(self.processAttached)
    self.rpc.agentDisconnected.connect(self.processDetached)
    self.rpc.engineReceived.connect(self._onEngineReceived)

    t = self.injectTimer = QTimer( ) 
    t.setSingleShot(False) 
    t.setInterval(5000)
    t.timeout.connect(self._onInjectTimeout)

    self.processAttached.connect(self._onAttached)
    self.processDetached.connect(self._onDetached)

    self.clear()
 
    self.extractsAllTexts = False
  processAttached = pyqtSignal(int) # pid
  processDetached = pyqtSignal(int) # pid

  processAttachTimeout = pyqtSignal(int) 
 
  def sendSetting(self,k,v): 
    if self.connectedPid:
        self.sendSetting(k,v)
  def attachProcess(self, pid): # -> bool 
      
      self.clear()
      
      inject.inject_vnragent(pid=pid)
    
      self.injectedPid = pid 
      self.injectTimer.start() 
       
  
  def quit(self): 
    self.mem.quit() 
    if self.connectedPid:
      self.rpc.disableAgent() 
 
  def sendSettings(self):
    if self.isConnected():
      self.sendSettings()
  

  def sendEmbeddedTranslation(self, text, hash, role ):
    """
    @param  text  unicode
    @param  hash  str or int64
    @param  role  int
    @param  language  str
    """
     
    import functools
    if self.hostengine:
      self.hostengine.translate(text,functools.partial(self.sendEmbeddedTranslation_,hash,role))
  def sendEmbeddedTranslation_(self,  hash, role, language,trans):
    hash = int(hash)
    m = self.mem
     
    if m.isAttached(): # and m.lock(): 
      # Due to the logic, locking is not needed
      index = 0
      m.setDataStatus(index, m.STATUS_BUSY)
      m.setDataHash(index, hash)
      m.setDataRole(index, role)
      m.setDataLanguage(index, language)
      
      m.setDataText(index, trans) 
      m.setDataStatus(index, m.STATUS_READY)  
      m.notify(hash, role)
  
  def _setTextExtractionEnabled(self, t):
    if self.textExtractionEnabled != t:
      self.textExtractionEnabled = t
      if self.connectedPid:
        self.sendSetting('embeddedTextEnabled', t)

  def clear(self):
    self.injectedPid = 0 # int
    self.engineName = '' # str
    self.gameEncoding = 'shift-jis' # placeholder

    self.scenarioSignature = 0
    self.nameSignature = 0

  @property # read only
  def connectedPid(self): return self.rpc.agentProcessId()

  def _onInjectTimeout(self): 
    if self.injectedPid:
      self.processAttachTimeout.emit(self.injectedPid)
      self.injectedPid = 0
      self.hostengine.timeout()

  def _onAttached(self,_): 
    self.injectTimer.stop()
    
    self.sendSettings()
    #self.rpc.enableAgent()

  def _onDetached(self, pid): # int -> 
    if self.injectedPid :
      self.mem.detachProcess(pid) 
  def _onEngineReceived(self, name): # str
    self.engineName = name 

    if name and self.connectedPid:
      self.mem.attachProcess(self.connectedPid)
      if self.hostengine:
        self.hostengine.getenginename(name)
      #print("%s: %s" % ( ("Detect game engine"), name))
    else: 
      if self.hostengine:
        self.hostengine.unrecognizedengine()
      if self.injectedPid :
        self.mem.detachProcess(self.injectedPid)
        self.injectedPid=0
  def sendSettings(self): 
    
     
    data={"embeddedScenarioTranscodingEnabled": False, "embeddedFontCharSetEnabled": globalconfig['embedded']['changecharset'], "embeddedTranslationWaitTime":int(1000* globalconfig['embedded']['timeout_translate']), "embeddedOtherTranscodingEnabled": False, "embeddedSpacePolicyEncoding": "shift-jis", "windowTranslationEnabled": True, "windowTextVisible": True, "embeddedNameTranscodingEnabled": False, "gameEncoding": "shift-jis", "embeddedOtherTranslationEnabled": False, "embeddedSpaceSmartInserted": globalconfig['embedded']['insertspace_policy']==2, "embeddedFontCharSet": somedef.charsetmap[globalconfig['embedded']['changecharset_charset']], "embeddedScenarioWidth": 0, "embeddedScenarioTextVisible": globalconfig['embedded']['keeprawtext'], "windowTranscodingEnabled": False, "nameSignature": 0, "embeddedScenarioTranslationEnabled": True, "embeddedScenarioVisible": True, "embeddedFontScale": 0, "embeddedAllTextsExtracted": False, "embeddedOtherVisible": True, "embeddedFontFamily": globalconfig['embedded']['changefont_font'] if globalconfig['embedded']['changefont'] else '', "embeddedTextEnabled": True, "scenarioSignature": 0, "embeddedOtherTextVisible": False, "embeddedNameTextVisible": False, "embeddedSpaceAlwaysInserted": globalconfig['embedded']['insertspace_policy']==1, "embeddedNameTranslationEnabled": True, "debug": True, "embeddedNameVisible": True, "embeddedFontWeight": 0}
    
    self.rpc.setAgentSettings(data)

  def sendSetting(self, k, v):
    data = {k:v}
    print(data)
    self.rpc.setAgentSettings(data)
 
