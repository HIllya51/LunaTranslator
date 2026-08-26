 // -------------------------------------------------------------------
 // AITalk(R) SDK Core UserDictionary API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_USER_DICTIONARY_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_USER_DICTIONARY_H_
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_createBinaryUserWordDictionary(const char *text_path, const char *binary_path);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Tts_UserDictionary
   // addtogroup AITalk_SDK_Core_Tts
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_USER_DICTIONARY_H_
