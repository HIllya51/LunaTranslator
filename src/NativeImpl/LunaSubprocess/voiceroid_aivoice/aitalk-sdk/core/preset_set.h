 // -------------------------------------------------------------------
 // AITalk(R) SDK Core PresetSet API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_PRESET_SET_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_PRESET_SET_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
 #include "aitalk-sdk/core/tts_parameter.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalkPresetSetIdEnum {
     AITalkPresetSetId_LanguageDictionary = 1,
     AITalkPresetSetId_VoiceDictionary = 2,
     AITalkPresetSetId_Uid = 3,
     AITalkPresetSetId_TtsParameter = 4,
 };
  
 typedef int32_t AITalkPresetSetId;
  
  
 typedef struct AITalk_Core_PresetSet AITalk_Core_PresetSet;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_PresetSet_new(AITalk_Core_PresetSet **ptrptr, const char *language_key, const char *voice_key, const char *uid, AITalk_Core_TtsParameter *tts_parameter);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_PresetSet_delete(AITalk_Core_PresetSet *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_PresetSet_set(AITalk_Core_PresetSet *ptr, AITalkPresetSetId id, AITalkMixedType value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_PresetSet_get(AITalk_Core_PresetSet *ptr, AITalkPresetSetId id, AITalkMixedType *value);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Tts_TtsParameter
   // addtogroup AITalk_SDK_Core_Tts
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_PRESET_SET_H_
