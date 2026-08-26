 // -------------------------------------------------------------------
 // AITalk(R) SDK Common ReturnCode API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_RETURN_CODE_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_RETURN_CODE_H_
  
 #include <stdint.h>
  
 #include "aitalk-sdk/common/macro.h"
  
 AITALK_BEGIN_EXTERN_C
  
 enum AITalkReturnCodeEnum {
     AITalkReturnCode_Ok = 0,
  
     AITalkReturnCode_SomeRecordsInvalid = 1,
  
     AITalkReturnCode_InternalError = -1,
  
     AITalkReturnCode_UnsupportedError = -2,
  
     AITalkReturnCode_InvalidArgumentError = -3,
  
     AITalkReturnCode_IncorrectFormatError = -4,
  
     AITalkReturnCode_AlreadyInitializedError = -5,
  
     AITalkReturnCode_NotInitializedError = -6,
  
     AITalkReturnCode_FileNotFoundError = -7,
  
     AITalkReturnCode_AlreadyLoadedError = -8,
  
     AITalkReturnCode_NotLoadedError = -9,
  
     AITalkReturnCode_NotEnoughMemoryError = -10,
  
     AITalkReturnCode_UserCanceled = -11,
  
     AITalkReturnCode_UserCallbackError = -12,
  
     AITalkReturnCode_ResourceIsFullError = -13,
  
     AITalkReturnCode_NlpDllNotFoundError = -14,
  
     AITalkReturnCode_ResourceIsBusyError = -1001,
  
     AITalkReturnCode_InsufficientPutValueError = -1002,
  
     AITalkReturnCode_KeyNotFoundError = -1003,
  
     AITalkReturnCode_KeyAlreadyUsedError = -1004,
  
     AITalkReturnCode_UnsupportedIdError = -1005,
  
     AITalkReturnCode_NotEnoughBufferSizeError = -1006,
  
     AITalkReturnCode_InsufficientSetPlatformError = -1007,
  
     AITalkReturnCode_ParenIncludedWarning = -1008,
  
     AITalkReturnCode_ResourceAlreadyUsedError = -1009,
  
     AITalkReturnCode_CallbackSuccess = 2000,
  
     AITalkReturnCode_CallbackCancel = -2001,
  
     AITalkReturnCode_CallbackError = -2002,
  
     AITalkReturnCode_UserCallbackBufferSizeError = -2003,
  
     AITalkReturnCode_NotAuthenticatedError = -3001,
  
     AITalkReturnCode_AlreadyAuthenticatedError = -3002,
  
     AITalkReturnCode_SpecifiedVoiceLicenseNotLoadedError = -3003,
  
     AITalkReturnCode_LicensePathIsEmptyError = -3004,
  
     AITalkReturnCode_LicenseCodeIsEmptyError = -3005,
  
     AITalkReturnCode_LicenseFileOpenError = -3006,
  
     AITalkReturnCode_LicenseFileReadError = -3007,
  
     AITalkReturnCode_LicenseFileWriteError = -3008,
  
     AITalkReturnCode_LicenseFormatError = -3009,
  
     AITalkReturnCode_LicenseItemNotFoundError = -3010,
  
     AITalkReturnCode_LicenseItemAlreadyExistsError = -3011,
  
     AITalkReturnCode_LicenseCodeUnmatchedError = -3012,
  
     AITalkReturnCode_LicenseProductAuthError = -3013,
  
     AITalkReturnCode_LicenseVoiceAuthError = -3014,
  
     AITalkReturnCode_LicenseVoiceDictionaryReadError = -3015,
  
     AITalkReturnCode_LicenseExpiredError = -3016,
  
     AITalkReturnCode_UnknownError = -10000,
  
     AITalkReturnCode_NotImplementedError = -10001,
 };
  
 typedef int32_t AITalkReturnCode;
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Common
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_RETURN_CODE_H_
