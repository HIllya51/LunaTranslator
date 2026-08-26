 // -------------------------------------------------------------------
 // AITalk(R) SDK Core AIKanaContainer API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_AIKANA_CONTAINER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_AIKANA_CONTAINER_H_
  
 #include <stddef.h>
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 /*
     @ja AI かなをテキスト形式で取得するためのクラス。
 */
 typedef struct AITalk_Core_AIKanaContainer AITalk_Core_AIKanaContainer;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_AIKanaContainer_getAIKana(AITalk_Core_AIKanaContainer *ptr, const char **text, size_t *const size);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_AIKanaContainer_delete(AITalk_Core_AIKanaContainer *ptr);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Tts_Tts
   // addtogroup AITalk_SDK_Core_Tts
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_AIKANA_CONTAINER_H_
