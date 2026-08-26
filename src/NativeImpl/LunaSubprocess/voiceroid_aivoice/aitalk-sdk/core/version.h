 // -------------------------------------------------------------------
 // AITalk(R) SDK Core Version API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VERSION_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VERSION_H_
  
 #include "aitalk-sdk/common/macro.h"
 #include "aitalk-sdk/common/return_code.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_getVersion(const char **version);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Support_Version
   // addtogroup AITalk_SDK_Core_Support
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VERSION_H_
