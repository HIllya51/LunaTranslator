 // -------------------------------------------------------------------
 // AITalk(R) SDK AudioEncoder WaveEncoder API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_WAVE_ENCODER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_WAVE_ENCODER_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/audio_encoder/audio_config.h"
 #include "aitalk-sdk/audio_encoder/type.h"
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 typedef struct AITalk_AudioEncoder_WaveEncoder AITalk_AudioEncoder_WaveEncoder;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_WaveEncoder_new(
     AITalk_AudioEncoder_WaveEncoder **ptrptr,
     AITalk_AudioEncoder_AudioConfig *config_ptr,
     AITalk_AudioEncoder_EncodedCallback callback,
     void *userdata);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_WaveEncoder_delete(AITalk_AudioEncoder_WaveEncoder *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_WaveEncoder_addData(AITalk_AudioEncoder_WaveEncoder *ptr, const char *buf, const size_t size);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_WaveEncoder_endData(AITalk_AudioEncoder_WaveEncoder *ptr);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_AudioEncoder_WaveEncoder
   // addtogroup AITalk_SDK_AudioEncoder
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_WAVE_ENCODER_H_
