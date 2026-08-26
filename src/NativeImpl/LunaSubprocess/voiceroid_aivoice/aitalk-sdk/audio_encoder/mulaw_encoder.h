 // -------------------------------------------------------------------
 // AITalk(R) SDK AudioEncoder MulawEncoder API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_MULAW_ENCODER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_MULAW_ENCODER_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/audio_encoder/type.h"
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 typedef struct AITalk_AudioEncoder_MulawEncoder AITalk_AudioEncoder_MulawEncoder;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_MulawEncoder_new(
     AITalk_AudioEncoder_MulawEncoder **ptrptr,
     AITalk_AudioEncoder_EncodedCallback callback,
     void *userdata);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_MulawEncoder_delete(AITalk_AudioEncoder_MulawEncoder *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_MulawEncoder_addData(AITalk_AudioEncoder_MulawEncoder *ptr, const char *buf, const size_t size);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_MulawEncoder_endData(AITalk_AudioEncoder_MulawEncoder *ptr);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_AudioEncoder_MulawEncoder
   // addtogroup AITalk_SDK_AudioEncoder
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_MULAW_ENCODER_H_
