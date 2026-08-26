 // -------------------------------------------------------------------
 // AITalk(R) SDK Core Utility API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_UTIL_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_UTIL_H_
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_normalizeUtf8(const char* original_text, char* normalized_text, size_t* size);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Util
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_UTIL_H_
