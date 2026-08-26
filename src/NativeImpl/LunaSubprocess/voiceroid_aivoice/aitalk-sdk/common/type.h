 // -------------------------------------------------------------------
 // AITalk(R) SDK Common Type API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_TYPE_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_TYPE_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common/macro.h"
  
 AITALK_BEGIN_EXTERN_C
  
 typedef union {
     int32_t int32;
     double floating;
     const char *str;
     void *any;
     uint8_t boolean;
 } AITalkMixedType;
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Common
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_TYPE_H_
