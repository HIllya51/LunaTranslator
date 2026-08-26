 // -------------------------------------------------------------------
 // AITalk(R) SDK Core VoiceDictionaryMetaContainer API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VOICE_DICTIONARY_META_CONTAINER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VOICE_DICTIONARY_META_CONTAINER_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_Core_VoiceDictionaryMetaContainerIdEnum {
     AITalk_Core_VoiceDictionaryMetaContainerId_Name = 1,
     AITalk_Core_VoiceDictionaryMetaContainerId_Gender = 2,
     AITalk_Core_VoiceDictionaryMetaContainerId_Rate = 3,
     AITalk_Core_VoiceDictionaryMetaContainerId_StyleColorLabels = 4,
 };
  
 typedef int32_t AITalk_Core_VoiceDictionaryMetaContainerId;
  
  
 typedef struct AITalk_Core_VoiceDictionaryMetaContainer AITalk_Core_VoiceDictionaryMetaContainer;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_VoiceDictionaryMetaContainer_new(AITalk_Core_VoiceDictionaryMetaContainer **ptrptr, const char *path);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_VoiceDictionaryMetaContainer_delete(AITalk_Core_VoiceDictionaryMetaContainer *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_VoiceDictionaryMetaContainer_getValue(AITalk_Core_VoiceDictionaryMetaContainer *ptr, AITalk_Core_VoiceDictionaryMetaContainerId id, AITalkMixedType *value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_VoiceDictionaryMetaContainer_getName(AITalk_Core_VoiceDictionaryMetaContainer *ptr, const char **name);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_VoiceDictionaryMetaContainer_getGender(AITalk_Core_VoiceDictionaryMetaContainer *ptr, const char **gender);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_VoiceDictionaryMetaContainer_getRate(AITalk_Core_VoiceDictionaryMetaContainer *ptr, int32_t *rate);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_VoiceDictionaryMetaContainer_getStyleColorLabels(AITalk_Core_VoiceDictionaryMetaContainer *ptr, const char **labels);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Support_DictionaryMetaData
   // addtogroup AITalk_SDK_Core_Support
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_VOICE_DICTIONARY_META_CONTAINER_H_
