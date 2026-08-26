 // -------------------------------------------------------------------
 // AITalk(R) SDK AudioEncoder Value API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_VALUE_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_VALUE_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_AudioEncoder_SoundFormatTypeEnum {
     AITalk_AudioEncoder_SoundFormatType_Lpcm = 1,
     AITalk_AudioEncoder_SoundFormatType_Mulaw = 7,
 };
  
 typedef uint16_t AITalk_AudioEncoder_SoundFormatType;
  
 enum AITalk_AudioEncoder_EncoderEventIdEnum {
     AITalk_AudioEncoder_EncoderEventId_Bufreq = 1,
     AITalk_AudioEncoder_EncoderEventId_Bufdone = 2,
 };
  
 typedef int32_t AITalk_AudioEncoder_EncoderEventId;
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_AudioEncoder_Common
   // addtogroup AITalk_SDK_AudioEncoder
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_AUDIO_ENCODER_VALUE_H_
