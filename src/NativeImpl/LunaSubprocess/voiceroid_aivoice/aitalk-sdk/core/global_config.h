 // -------------------------------------------------------------------
 // AITalk(R) SDK Core GlobalConfig API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_GLOBAL_CONFIG_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_GLOBAL_CONFIG_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
 #include "aitalk-sdk/core/value.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalkGlobalConfigIdEnum {
     AITalkGlobalConfigId_Log = 1,
 };
  
 typedef int32_t AITalkGlobalConfigId;
  
 enum AITalk_Core_GlobalConfig_Log_TypeEnum {
     AITalk_Core_GlobalConfig_Log_Type_StdOut = 1,
     AITalk_Core_GlobalConfig_Log_Type_StdErr = 2,
     AITalk_Core_GlobalConfig_Log_Type_Callback = 3,
 };
  
 typedef int32_t AITalk_Core_GlobalConfig_Log_Type;
  
  
 typedef void (*AITalk_Core_GlobalConfig_Log_CallbackFunc)(
     void* arg,
     int32_t level,
     const char* rtype,
     size_t rtype_size,
     const char* time,
     size_t time_size,
     const char* message,
     size_t message_size);
  
 struct AITalk_Core_GlobalConfig_Log {
     AITalk_Core_GlobalConfig_Log_Type log_type;
     AITalk_Core_GlobalConfig_Log_Level log_level;
     AITalk_Core_GlobalConfig_Log_CallbackFunc log_callback;
     void* user_data;
 };
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_resetGlobalConfig();
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_setGlobalConfig(AITalkGlobalConfigId id, AITalkMixedType value);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Initialization_GlobalConfig
   // addtogroup AITalk_SDK_Core_Initialization
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_GLOBAL_CONFIG_H_
