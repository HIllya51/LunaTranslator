 // -------------------------------------------------------------------
 // AITalk(R) SDK Core Tts API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_TTS_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_TTS_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
 #include "aitalk-sdk/core/aikana_container.h"
 #include "aitalk-sdk/core/tts_parameter.h"
 #include "aitalk-sdk/core/value.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_Core_TtsIdEnum {
     AITalk_Core_TtsId_LanguageDictionary = 1,
     AITalk_Core_TtsId_VoiceDictionary = 2,
     AITalk_Core_TtsId_VoiceDictionaryLicense = 3,
     AITalk_Core_TtsId_TtsParameter = 4,
     AITalk_Core_TtsId_InputEncoding = 5,
     AITalk_Core_TtsId_TypeOfInput = 6,
     AITalk_Core_TtsId_TagTokenBegin = 100,
     AITalk_Core_TtsId_TagTokenEnd = 101,
     AITalk_Core_TtsId_AutoBookmarkMode = 201,
     AITalk_Core_TtsId_AutoBookmarkMarkPrefix = 202,
     AITalk_Core_TtsId_BookmarkMarkerMode = 301,
     AITalk_Core_TtsId_LipsyncMarkerMode = 302,
     AITalk_Core_TtsId_AccentMarkerMode = 303,
     AITalk_Core_TtsId_PhraseMarkerMode = 304,
     AITalk_Core_TtsId_PresetSet = 401,
     AITalk_Core_TtsId_Uid = 402,
 };
  
 typedef int32_t AITalk_Core_TtsId;
  
 enum AITalk_Core_Tts_AutoBookmarkModeIdEnum {
     AITalk_Core_Tts_AutoBookmarkModeId_None = 1,
     AITalk_Core_Tts_AutoBookmarkModeId_Sentence = 2,
     AITalk_Core_Tts_AutoBookmarkModeId_HighLight = 3,
 };
  
 typedef int32_t AITalk_Core_Tts_AutoBookmarkModeId;
  
  
 typedef struct AITalk_Core_Tts AITalk_Core_Tts;
  
 typedef AITalkReturnCode (*AITalk_Core_TtsOutCallback)(void *user_data, AITalk_Core_TtsOutEventId event_id, void *data);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_new(AITalk_Core_Tts **ptrptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_delete(AITalk_Core_Tts *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_duplicate(AITalk_Core_Tts **ptrptr, AITalk_Core_Tts *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_copy(AITalk_Core_Tts *dst_ptr, AITalk_Core_Tts *src_ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_putKeyValue(AITalk_Core_Tts *ptr, const AITalk_Core_TtsId id, const char *key, const AITalkMixedType value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_getKeyValue(AITalk_Core_Tts *ptr, const AITalk_Core_TtsId id, const char *key, AITalkMixedType *value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_getKeyList(AITalk_Core_Tts *ptr, const AITalk_Core_TtsId id, const char *const **keyList, size_t *size);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_selectDefaultKey(AITalk_Core_Tts *ptr, const AITalk_Core_TtsId id, const char *key);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_getDefaultKey(AITalk_Core_Tts *ptr, const AITalk_Core_TtsId id, const char **key);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_hasKey(AITalk_Core_Tts *ptr, const AITalk_Core_TtsId id, const char *key);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_deleteKey(AITalk_Core_Tts *ptr, const AITalk_Core_TtsId id, const char *key);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_isBusy(AITalk_Core_Tts *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_run(AITalk_Core_Tts *ptr, const char *input, AITalk_Core_TtsOutCallback callback, void *user_data);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_generateAIKanaContainer(AITalk_Core_Tts *ptr, AITalk_Core_AIKanaContainer **ptrptr, const char *text, AITalk_TextEncodingsId encoding);
  
 enum AITalk_Core_Tts_MergeProsodyLevelEnum {
     AITalk_Core_Tts_MergeProsodyLevel_1 = 1,
     AITalk_Core_Tts_MergeProsodyLevel_2 = 2,
 };
  
 typedef int32_t AITalk_Core_Tts_MergeProsodyLevel;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Tts_generateMergedVoiceDictionary(AITalk_Core_Tts *ptr, const char *new_key, const char *base_key, const char *additional_key, AITalk_Core_Tts_MergeProsodyLevel level);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Tts_Tts
   // addtogroup AITalk_SDK_Core_Tts
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_TTS_H_
