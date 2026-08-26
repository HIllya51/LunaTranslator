 // -------------------------------------------------------------------
 // AITalk(R) SDK Core CallbackSelector API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_CALLBACK_SELECTOR_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_CALLBACK_SELECTOR_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
 #include "aitalk-sdk/core/value.h"
  
 AITALK_BEGIN_EXTERN_C
  
 typedef AITalkReturnCode (*AITalk_Core_CallbackSelector_BufreqCallback)(void *user_data, char **audio_buffer, size_t *audio_buffer_size, char **marker_buffer, size_t *marker_buffer_size);
  
 typedef AITalkReturnCode (*AITalk_Core_CallbackSelector_BufdoneCallback)(void *user_data, char *audio_buffer, size_t audio_buffer_size, char *marker_buffer, size_t marker_buffer_size);
  
 typedef AITalkReturnCode (*AITalk_Core_CallbackSelector_BookmarkCallback)(void *user_data, AITalk_Core_TtsOutEventId event_id, size_t audio_sample_pos, size_t input_text_pos, const char *bookmark_id, size_t bookmark_id_size);
  
 typedef AITalkReturnCode (*AITalk_Core_CallbackSelector_LipsyncCallback)(void *user_data, AITalk_Core_TtsOutEventId event_id, size_t audio_sample_pos, const char *phoneme, size_t phoneme_size);
  
 typedef AITalkReturnCode (*AITalk_Core_CallbackSelector_AccentCallback)(void *user_data, AITalk_Core_TtsOutEventId event_id, size_t audio_sample_pos, size_t accent_index);
  
 typedef AITalkReturnCode (*AITalk_Core_CallbackSelector_PhraseCallback)(void *user_data, AITalk_Core_TtsOutEventId event_id, size_t audio_sample_pos, size_t phrase_index);
  
 enum AITalk_Core_CallbackSelector_CallbackIdEnum {
     AITalk_Core_CallbackSelector_CallbackId_Bufreq = 1,
     AITalk_Core_CallbackSelector_CallbackId_Bufdone = 2,
     AITalk_Core_CallbackSelector_CallbackId_Bookmark = 3,
     AITalk_Core_CallbackSelector_CallbackId_Lipsync = 4,
     AITalk_Core_CallbackSelector_CallbackId_Accent = 5,
     AITalk_Core_CallbackSelector_CallbackId_Phrase = 6,
 };
  
 typedef int32_t AITalk_Core_CallbackSelector_CallbackId;
  
  
 typedef struct AITalk_Core_CallbackSelector AITalk_Core_CallbackSelector;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_CallbackSelector_new(AITalk_Core_CallbackSelector **ptrptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_CallbackSelector_delete(AITalk_Core_CallbackSelector *ptr);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_CallbackSelector_putValue(AITalk_Core_CallbackSelector *ptr, AITalk_Core_CallbackSelector_CallbackId id, void *callback);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_CallbackSelector_select(AITalk_Core_CallbackSelector *ptr, void *user_data, AITalk_Core_TtsOutEventId event_id, void *data);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Support_Callback
   // addtogroup AITalk_SDK_Core_Support
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_CALLBACK_SELECTOR_H_
