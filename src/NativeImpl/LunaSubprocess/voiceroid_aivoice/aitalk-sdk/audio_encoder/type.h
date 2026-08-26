 // -------------------------------------------------------------------
 // AITalk(R) SDK AudioEncoder Type API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_TYPE_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_TYPE_H_
  
 #include "aitalk-sdk/audio_encoder/value.h"
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 typedef AITalkReturnCode (*AITalk_AudioEncoder_EncodedCallback)(void *userdata, AITalk_AudioEncoder_EncoderEventId id, void *body);
  
 typedef struct AITalk_AudioEncoder_Output {
     char *audio_buffer;
     size_t audio_buffer_size;
     size_t audio_buffer_offset;
 } AITalk_AudioEncoder_Output;
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_AudioEncoder_Common
   // addtogroup AITalk_SDK_AudioEncoder
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_TYPE_H_
