 // -------------------------------------------------------------------
 // AITalk(R) SDK AudioEncoder ResamplingEncoder API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_RESAMPLING_ENCODER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_RESAMPLING_ENCODER_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/audio_encoder/type.h"
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 typedef struct AITalk_AudioEncoder_ResamplingEncoder AITalk_AudioEncoder_ResamplingEncoder;
  
 struct AITalk_AudioEncoder_ResamplingEncoderConfig {
     const size_t current_rate;
     const size_t conversion_rate;
     AITalk_AudioEncoder_EncodedCallback callback;
     void *userdata;
     size_t callback_size;
     size_t range;
     size_t depth;
 };
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_ResamplingEncoderConfig_new(AITalk_AudioEncoder_ResamplingEncoderConfig **ptrptr, const size_t current_rate, const size_t conversion_rate, AITalk_AudioEncoder_EncodedCallback callback, void *userdata);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_ResamplingEncoderConfig_delete(AITalk_AudioEncoder_ResamplingEncoderConfig *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_ResamplingEncoder_new(AITalk_AudioEncoder_ResamplingEncoder **ptrptr, const AITalk_AudioEncoder_ResamplingEncoderConfig *config);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_ResamplingEncoder_delete(AITalk_AudioEncoder_ResamplingEncoder *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_ResamplingEncoder_addData(AITalk_AudioEncoder_ResamplingEncoder *ptr, const char *buf, const size_t size);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_ResamplingEncoder_endData(AITalk_AudioEncoder_ResamplingEncoder *ptr);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_AudioEncoder_ResamplingEncoder
   // addtogroup AITalk_SDK_AudioEncoder
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_RESAMPLING_ENCODER_H_
