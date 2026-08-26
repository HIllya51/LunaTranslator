 // -------------------------------------------------------------------
 // AITalk(R) SDK AudioEncoder BitDepthEncoder API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_BIT_DEPTH_ENCODER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_BIT_DEPTH_ENCODER_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/audio_encoder/type.h"
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_AudioEncoder_BitDepthEncodePatternEnum {
     AITalk_AudioEncoder_BitDepthEncodePattern_Int16ToUint8 = 1,
 };
  
 typedef int32_t AITalk_AudioEncoder_BitDepthEncodePattern;
  
  
 typedef struct AITalk_AudioEncoder_BitDepthEncoder AITalk_AudioEncoder_BitDepthEncoder;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_BitDepthEncoder_new(
     AITalk_AudioEncoder_BitDepthEncoder **ptrptr,
     AITalk_AudioEncoder_BitDepthEncodePattern encode_pattern,
     AITalk_AudioEncoder_EncodedCallback callback,
     void *userdata);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_BitDepthEncoder_delete(AITalk_AudioEncoder_BitDepthEncoder *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_BitDepthEncoder_addData(AITalk_AudioEncoder_BitDepthEncoder *ptr, const char *buf, const size_t size);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_AudioEncoder_BitDepthEncoder_endData(AITalk_AudioEncoder_BitDepthEncoder *ptr);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_AudioEncoder_BitDepthEncoder
   // addtogroup AITalk_SDK_AudioEncoder
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_BIT_DEPTH_ENCODER_H_
