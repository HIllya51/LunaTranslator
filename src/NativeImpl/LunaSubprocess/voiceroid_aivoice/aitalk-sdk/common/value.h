 // -------------------------------------------------------------------
 // AITalk(R) SDK Common Value API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_VALUE_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_VALUE_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/common/macro.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalk_TextEncodingsIdEnum {
     AITalk_TextEncodingsId_Utf8 = 1,
     AITalk_TextEncodingsId_Cp932 = 2,
     AITalk_TextEncodingsId_Default = 3,
 };
  
 typedef int32_t AITalk_TextEncodingsId;
  
 enum AITalk_TypeOfInputIdEnum {
     AITalk_TypeOfInputId_Plain = 1,
     AITalk_TypeOfInputId_AIKana = 2,
     AITalk_TypeOfInputId_Jeita = 3,
 };
  
 typedef int32_t AITalk_TypeOfInputId;
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Common
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_VALUE_H_
