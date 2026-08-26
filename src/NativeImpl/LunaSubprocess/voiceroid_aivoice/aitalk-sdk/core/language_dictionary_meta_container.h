 // -------------------------------------------------------------------
 // AITalk(R) SDK Core LanguageDictionaryMetaContainer API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_LANGUAGE_DICTIONARY_META_CONTAINER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_LANGUAGE_DICTIONARY_META_CONTAINER_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_Core_LanguageDictionaryMetaContainerIdEnum {
     AITalk_Core_LanguageDictionaryMetaContainerId_Version = 1,
 };
  
 typedef int32_t AITalk_Core_LanguageDictionaryMetaContainerId;
  
  
 typedef struct AITalk_Core_LanguageDictionaryMetaContainer AITalk_Core_LanguageDictionaryMetaContainer;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_LanguageDictionaryMetaContainer_new(AITalk_Core_LanguageDictionaryMetaContainer **ptrptr, const char *path);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_LanguageDictionaryMetaContainer_delete(AITalk_Core_LanguageDictionaryMetaContainer *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_LanguageDictionaryMetaContainer_getValue(AITalk_Core_LanguageDictionaryMetaContainer *ptr, AITalk_Core_LanguageDictionaryMetaContainerId id, AITalkMixedType *value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_LanguageDictionaryMetaContainer_getVersion(AITalk_Core_LanguageDictionaryMetaContainer *ptr, const char **version);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Support_DictionaryMetaData
   // addtogroup AITalk_SDK_Core_Support
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_LANGUAGE_DICTIONARY_META_CONTAINER_H_
