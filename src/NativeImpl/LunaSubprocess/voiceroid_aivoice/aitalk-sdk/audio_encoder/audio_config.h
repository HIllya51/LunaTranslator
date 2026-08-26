 // -------------------------------------------------------------------
 // AITalk(R) SDK AudioEncoder AudioConfig API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_AUDIO_CONFIG_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_AUDIO_CONFIG_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/audio_encoder/value.h"
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_AudioEncoder_AudioConfigIdEnum {
     AITalk_AudioEncoder_AudioConfigId_depth = 1,
     AITalk_AudioEncoder_AudioConfigId_freq = 2,
     AITalk_AudioEncoder_AudioConfigId_channel = 3,
     AITalk_AudioEncoder_AudioConfigId_format = 4,
 };
  
 typedef int32_t AITalk_AudioEncoder_AudioConfigId;
  
  
 typedef struct AITalk_AudioEncoder_AudioConfig AITalk_AudioEncoder_AudioConfig;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_AudioConfig_new(
     AITalk_AudioEncoder_AudioConfig **ptrptr,
     uint16_t depth,
     uint32_t freq,
     uint16_t channel,
     AITalk_AudioEncoder_SoundFormatType format);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_AudioConfig_delete(AITalk_AudioEncoder_AudioConfig *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_AudioConfig_setValue(
     AITalk_AudioEncoder_AudioConfig *ptr,
     AITalk_AudioEncoder_AudioConfigId id,
     const AITalkMixedType value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_AudioConfig_getValue(
     AITalk_AudioEncoder_AudioConfig *ptr,
     AITalk_AudioEncoder_AudioConfigId id,
     AITalkMixedType *value);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_AudioEncoder_AudioConfig
   // addtogroup AITalk_SDK_AudioEncoder
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_AUDIO_CONFIG_H_
