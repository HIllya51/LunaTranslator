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
print(POSTSOLVE('「……潮時かもな」「……潮時かもな」「……潮時かもな」'))
 