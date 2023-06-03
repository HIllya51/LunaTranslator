import json
import os ,time,win32utils
from utils.subproc import subproc_w
from ctypes import c_bool,c_uint32,c_wchar,c_int,c_float,sizeof,Structure,cast,POINTER,memset
from utils.config import magpie10_config,globalconfig
MAX_PARAM_NUM =32
MAX_Effects_NUM =32
MAX_NAME_LENGTH =128
class parameter_t(Structure):
    _fields_=[
        ('paramname',c_wchar*MAX_NAME_LENGTH),
        ('param',c_float)
    ]
class scale_t(Structure):
    _fields_=[
        ('sx',c_float),
        ('sy',c_float)
    ]
class EffectOption_t(Structure):
    _fields_=[
        ('name',c_wchar*MAX_NAME_LENGTH),
        ('paramnum',c_int),
        ('parameters',parameter_t*MAX_PARAM_NUM),
        ('scalingType',c_int),
        ('scale',scale_t),
        ('flags',c_uint32)
    ]
class DownscalingEffect_t(Structure):
    _fields_=[
        ('name',c_wchar*MAX_NAME_LENGTH),
        ('paramnum',c_int),
        ('parameters',parameter_t*MAX_PARAM_NUM)
    ]
class Cropping(Structure):
    _fields_=[
        ('Left',c_float),
        ('Top',c_float),
        ('Right',c_float),
        ('Bottom',c_float),
    ]
class MagOptions_t(Structure):
    _fields_=[
        ('IsDisableWindowResizing',c_bool),
        ('IsDebugMode',c_bool),
        ('IsDisableEffectCache',c_bool),
        ('IsSaveEffectSources',c_bool),
        ('IsWarningsAreErrors',c_bool),
        ('IsSimulateExclusiveFullscreen',c_bool),
        ('Is3DGameMode',c_bool),
        ('IsShowFPS',c_bool),
        ('IsVSync',c_bool),
        ('IsTripleBuffering',c_bool),
        ('IsCaptureTitleBar',c_bool),
        ('IsAdjustCursorSpeed',c_bool),
        ('IsDrawCursor',c_bool),
        ('IsDisableDirectFlip',c_bool),
        ('cropping',Cropping),
        ('graphicsCard',c_int),
        ('cursorScaling',c_float),
        ('captureMethod',c_int),
        ('multiMonitorUsage',c_int),
        ('cursorInterpolationMode',c_int),
        ('downscalingEffect',DownscalingEffect_t),
        ('effectnum',c_int),
        ('effects',EffectOption_t*MAX_Effects_NUM)
    ]
 
def callmagpie10( hwnd):
    
    profiles_index=globalconfig['profiles_index']
    if profiles_index>len(magpie10_config['profiles']):
        profiles_index=0
        
    scalingModes_index=magpie10_config['profiles'][profiles_index]['scalingMode']
    if scalingModes_index>len(magpie10_config['scalingModes']):
        scalingModes_index=0
    filemappingname='MAGPIE_FILEMAPPING_PARAMS_'+str(time.time())
    
    fm=win32utils.CreateFileMapping(filemappingname,0x40,sizeof(MagOptions_t))
    m=win32utils.MapViewOfFile(fm,0xf001f,sizeof(MagOptions_t))
    print(fm,m)
    memset(m,0,sizeof(MagOptions_t))
   
    MagOptions=cast(m,POINTER(MagOptions_t))
    
    if magpie10_config['profiles'][profiles_index]['croppingEnabled']:
        MagOptions.contents.cropping.Left=magpie10_config['profiles'][profiles_index]['cropping']['left']
        MagOptions.contents.cropping.Top=magpie10_config['profiles'][profiles_index]['cropping']['top']
        MagOptions.contents.cropping.Right=magpie10_config['profiles'][profiles_index]['cropping']['right']
        MagOptions.contents.cropping.Bottom=magpie10_config['profiles'][profiles_index]['cropping']['bottom']

    MagOptions.contents.graphicsCard= magpie10_config['profiles'][profiles_index]['graphicsCard']
    MagOptions.contents.cursorScaling= {
        0:0.5,1:0.75,2:1.0,3:1.25,4:1.5,5:2.0,6:0,
        7:magpie10_config['profiles'][profiles_index].get('customCursorScaling',1.0)
        }.get(magpie10_config['profiles'][profiles_index]['cursorScaling'],1.0)
    MagOptions.contents.captureMethod= magpie10_config['profiles'][profiles_index]['captureMethod']
    MagOptions.contents.multiMonitorUsage= magpie10_config['profiles'][profiles_index]['multiMonitorUsage']
    MagOptions.contents.cursorInterpolationMode= magpie10_config['profiles'][profiles_index]['cursorInterpolationMode']


    MagOptions.contents.IsDisableWindowResizing= magpie10_config['profiles'][profiles_index]['disableWindowResizing']
    MagOptions.contents.IsDebugMode= magpie10_config['debugMode']
    MagOptions.contents.IsDisableEffectCache= magpie10_config['disableEffectCache']
    MagOptions.contents.IsSaveEffectSources= magpie10_config['saveEffectSources']
    MagOptions.contents.IsWarningsAreErrors= magpie10_config['warningsAreErrors']
    MagOptions.contents.IsSimulateExclusiveFullscreen= magpie10_config['simulateExclusiveFullscreen']
    MagOptions.contents.Is3DGameMode= magpie10_config['profiles'][profiles_index]['3DGameMode']
    MagOptions.contents.IsShowFPS= magpie10_config['profiles'][profiles_index]['showFPS']
    MagOptions.contents.IsTripleBuffering= magpie10_config['profiles'][profiles_index]['tripleBuffering']
    MagOptions.contents.IsCaptureTitleBar= magpie10_config['profiles'][profiles_index]['captureTitleBar']
    MagOptions.contents.IsAdjustCursorSpeed= magpie10_config['profiles'][profiles_index]['adjustCursorSpeed']
    MagOptions.contents.IsDrawCursor= magpie10_config['profiles'][profiles_index]['drawCursor']
    MagOptions.contents.IsDisableDirectFlip= magpie10_config['profiles'][profiles_index]['disableDirectFlip']

    downscalingEffect=magpie10_config.get('downscalingEffect',{"name":"","parameters":{}})
    MagOptions.contents.downscalingEffect.name=downscalingEffect['name']

    parameters=downscalingEffect.get('parameters',{})
    paramnum=len(parameters)

    MagOptions.contents.downscalingEffect.paramnum=paramnum
    for i in range(paramnum):
        key=list(parameters.keys())[i]
        MagOptions.contents.downscalingEffect.parameters[i].paramname=key
        MagOptions.contents.downscalingEffect.parameters[i].param=parameters[key]
     

    
    effects=magpie10_config['scalingModes'][scalingModes_index]['effects']

    effectnum=len(effects)
    MagOptions.contents.effectnum=effectnum
    for i in range(effectnum):
        MagOptions.contents.effects[i].name=effects[i]['name']
        MagOptions.contents.effects[i].scalingType=effects[i].get('scalingType',0)
        MagOptions.contents.effects[i].scale.sx=effects[i].get('scale',{'x':1,'y':1}).get('x','1')
        MagOptions.contents.effects[i].scale.sy=effects[i].get('scale',{'x':1,'y':1}).get('y','1')

        parameters=effects[i].get('parameters',{})
        paramnum=len(parameters)
 
        MagOptions.contents.effects[i].paramnum=paramnum
        for i in range(paramnum):
            key=list(parameters.keys())[i]
            MagOptions.contents.effects[i].parameters[i].paramname=key
            MagOptions.contents.effects[i].parameters[i].param=parameters[key]
            
    return subproc_w(f'./files/plugins/Magpie10/Magpie.Core.exe {filemappingname} {hwnd}',name='magpie10',cwd='./files/plugins/Magpie10/')

def endmagpie10():
    endevent = win32utils.CreateEvent(False, False,'MAGPIE_WAITFOR_STOP_SIGNAL')
    win32utils.SetEvent(endevent)
    win32utils.CloseHandle(endevent)