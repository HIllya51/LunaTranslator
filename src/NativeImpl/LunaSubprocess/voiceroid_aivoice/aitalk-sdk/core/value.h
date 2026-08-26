 // -------------------------------------------------------------------
 // AITalk(R) SDK Core Value API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VALUE_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VALUE_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_Core_GlobalConfig_Log_LevelEnum {
     AITalk_Core_GlobalConfig_Log_Level_Trace = 1,
     AITalk_Core_GlobalConfig_Log_Level_Verbose = 2,
     AITalk_Core_GlobalConfig_Log_Level_Info = 3,
     AITalk_Core_GlobalConfig_Log_Level_Warn = 4,
     AITalk_Core_GlobalConfig_Log_Level_Error = 5,
     AITalk_Core_GlobalConfig_Log_Level_Off = 6,
 };
  
 typedef int32_t AITalk_Core_GlobalConfig_Log_Level;
  
 enum AITalk_Core_TtsOutEventIdEnum {
     AITalk_Core_TtsOutEventId_Begin = 1,
     AITalk_Core_TtsOutEventId_BeginSentence = 2,
     AITalk_Core_TtsOutEventId_AIKana = 3,
     AITalk_Core_TtsOutEventId_Bufreq = 4,
     AITalk_Core_TtsOutEventId_Bufdone = 5,
     AITalk_Core_TtsOutEventId_Marker = 6,
     AITalk_Core_TtsOutEventId_EndSentence = 7,
     AITalk_Core_TtsOutEventId_End = 8,
     AITalk_Core_TtsOutEventId_SwitchParameterBegin = 9,
     AITalk_Core_TtsOutEventId_SwitchParameterEnd = 10,
 };
  
 typedef int32_t AITalk_Core_TtsOutEventId;
  
 enum AITalk_Core_MarkerModeIdEnum {
     AITalk_Core_MarkerModeId_Disable = 1,
     AITalk_Core_MarkerModeId_OutBuffer = 2,
     AITalk_Core_MarkerModeId_CallbackAndBuffer = 3,
 };
 typedef int32_t AITalk_Core_MarkerModeId;
  
 enum AITalk_Core_MarkerTypeIdEnum {
     AITalk_Core_MarkerTypeId_Bookmark = 1,
     AITalk_Core_MarkerTypeId_Lipsync = 2,
     AITalk_Core_MarkerTypeId_Accent = 3,
     AITalk_Core_MarkerTypeId_Phrase = 4,
 };
  
 typedef int32_t AITalk_Core_MarkerTypeId;
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Common
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VALUE_H_
