 // -------------------------------------------------------------------
 // AITalk(R) SDK Core License API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_LICENSE_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_LICENSE_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
  
 AITALK_BEGIN_EXTERN_C
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_authenticate();
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_deauthenticate();
  
 enum AITalk_Core_EngineLicenseIdEnum {
     AITalk_Core_EngineLicenseId_Path = 1,
     AITalk_Core_EngineLicenseId_Code = 2,
 };
  
 typedef int32_t AITalk_Core_EngineLicenseId;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_EngineLicense_setValue(const AITalk_Core_EngineLicenseId id, const char *value);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_EngineLicense_setPath(const char *path);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_EngineLicense_setCode(const char *code);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_EngineLicense_getExpiration(int32_t *year, int32_t *month, int32_t *day);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_EngineLicense_getExpirationYmd(int32_t *ymd);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Initialization_License
   // addtogroup AITalk_SDK_Core_Initialization
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_LICENSE_H_
