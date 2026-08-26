 // -------------------------------------------------------------------
 // AITalk(R) SDK Core Initialization API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_INITIALIZATION_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_INITIALIZATION_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
 #include "aitalk-sdk/core/value.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_initialize();
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_finalize();
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_setLogLevel(AITalk_Core_GlobalConfig_Log_Level value);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Initialization_Initialize
   // addtogroup AITalk_SDK_Core_Initialization
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_INITIALIZATION_H_
