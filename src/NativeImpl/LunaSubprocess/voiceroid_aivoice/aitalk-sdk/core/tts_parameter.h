 // -------------------------------------------------------------------
 // AITalk(R) SDK Core TtsParameter API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_TTS_PARAMETER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_TTS_PARAMETER_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_Core_TtsParameterIdEnum {
     AITalk_Core_TtsParameterId_Context = 1,
     AITalk_Core_TtsParameterId_WaitLast = 2,
     AITalk_Core_TtsParameterId_WaitTime_BeginText = 100,
     AITalk_Core_TtsParameterId_WaitTime_EndText = 101,
     AITalk_Core_TtsParameterId_WaitTime_ShortText = 102,
     AITalk_Core_TtsParameterId_WaitTime_MiddleText = 103,
     AITalk_Core_TtsParameterId_WaitTime_LongText = 104,
     AITalk_Core_TtsParameterId_WaitTime_Eos = 105,
     AITalk_Core_TtsParameterId_Volume = 3,
     AITalk_Core_TtsParameterId_VolumeLevel = 4,
     AITalk_Core_TtsParameterId_Rate = 5,
     AITalk_Core_TtsParameterId_RateLevel = 6,
     AITalk_Core_TtsParameterId_Pitch = 7,
     AITalk_Core_TtsParameterId_PitchLevel = 8,
     AITalk_Core_TtsParameterId_Emphasis = 9,
     AITalk_Core_TtsParameterId_EmphasisLevel = 10,
     AITalk_Core_TtsParameterId_SentenceMaxLength = 11,
     AITalk_Core_TtsParameterId_CompressorMode = 12,
     AITalk_Core_TtsParameterId_MasterVolume = 13,
     AITalk_Core_TtsParameterId_UseRuby = 14,
     AITalk_Core_TtsParameterId_StyleType = 15,
     AITalk_Core_TtsParameterId_StyleColor = 16,
     AITalk_Core_TtsParameterId_EstimatePause = 17,
     AITalk_Core_TtsParameterId_FixedPauseSettings = 18,
     AITalk_Core_TtsParameterId_RateMin = 19,
     AITalk_Core_TtsParameterId_RateMax = 20,
     AITalk_Core_TtsParameterId_PitchMin = 21,
     AITalk_Core_TtsParameterId_PitchMax = 22,
     AITalk_Core_TtsParameterId_EmphasisMax = 23,
     AITalk_Core_TtsParameterId_UserWordDictionary = 300,
     AITalk_Core_TtsParameterId_UserPhraseDictionary = 301,
     AITalk_Core_TtsParameterId_UserSymbolDictionary = 302,
     AITalk_Core_TtsParameterId_UserKeywordReplacementDictionary = 303,
     AITalk_Core_TtsParameterId_AudioFile = 400,
 };
  
 typedef int32_t AITalk_Core_TtsParameterId;
  
  
 typedef struct AITalk_Core_TtsParameter AITalk_Core_TtsParameter;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_new(AITalk_Core_TtsParameter **ptrptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_delete(AITalk_Core_TtsParameter *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_duplicate(AITalk_Core_TtsParameter **ptrptr, AITalk_Core_TtsParameter *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_copy(AITalk_Core_TtsParameter *dst_ptr, AITalk_Core_TtsParameter *src_ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_putKeyValue(AITalk_Core_TtsParameter *ptr, const AITalk_Core_TtsParameterId id, const char *key, const AITalkMixedType value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_getKeyValue(AITalk_Core_TtsParameter *ptr, const AITalk_Core_TtsParameterId id, const char *key, AITalkMixedType *value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_getKeyList(AITalk_Core_TtsParameter *ptr, const AITalk_Core_TtsParameterId id, const char *const **keyList, size_t *size);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_hasKey(AITalk_Core_TtsParameter *ptr, const AITalk_Core_TtsParameterId id, const char *key);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_TtsParameter_deleteKey(AITalk_Core_TtsParameter *ptr, const AITalk_Core_TtsParameterId id, const char *key);
  
 enum AITalk_Core_TtsParameter_ContextIdEnum {
     AITalk_Core_TtsParameter_ContextId_Normal = 1,
     AITalk_Core_TtsParameter_ContextId_Address = 2,
 };
  
 typedef int32_t AITalk_Core_TtsParameter_ContextId;
  
 enum AITalk_Core_TtsParameter_WaitLastModeIdEnum {
     AITalk_Core_TtsParameter_WaitLastModeId_On = 1,
     AITalk_Core_TtsParameter_WaitLastModeId_Off = 2,
 };
  
 typedef int32_t AITalk_Core_TtsParameter_WaitLastModeId;
  
 enum AITalk_Core_TtsParameter_CompressorModeIdEnum {
     AITalk_Core_TtsParameter_CompressorModeId_Default = 1,
     AITalk_Core_TtsParameter_CompressorModeId_Simple = 2,
 };
  
 typedef int32_t AITalk_Core_TtsParameter_CompressorModeId;
  
 enum AITalk_Core_TtsParameter_UseRubyIdEnum {
     AITalk_Core_TtsParameter_UseRubyId_On = 1,
     AITalk_Core_TtsParameter_UseRubyId_Off = 2,
 };
  
 typedef int32_t AITalk_Core_TtsParameter_UseRubyId;
  
 enum AITalk_Core_TtsParameter_EstimatePauseIdEnum {
     AITalk_Core_TtsParameter_EstimatePause_Estimate = 1,
     AITalk_Core_TtsParameter_EstimatePause_Config = 2,
 };
  
 typedef int32_t AITalk_Core_TtsParameter_EstimatePauseId;
  
 enum AITalk_Core_TtsParameter_FixedPauseSettingsIdEnum {
     AITalk_Core_TtsParameter_FixedPauseSettings_FlexibleByRate = 1,
     AITalk_Core_TtsParameter_FixedPauseSettings_Fixed = 2,
 };
  
 typedef int32_t AITalk_Core_TtsParameter_FixedPauseSettingsId;
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Tts_TtsParameter
   // addtogroup AITalk_SDK_Core_Tts
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_TTS_PARAMETER_H_
