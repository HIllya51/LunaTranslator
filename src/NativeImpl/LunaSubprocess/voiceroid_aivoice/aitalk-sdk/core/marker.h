 // -------------------------------------------------------------------
 // AITalk(R) SDK Core Marker API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_MARKER_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_MARKER_H_
  
 #include <stddef.h>
 #include <stdint.h>
  
 #include "aitalk-sdk/common.h"
 #include "aitalk-sdk/core/value.h"
  
 AITALK_BEGIN_EXTERN_C
  
 typedef struct AITalk_Core_TtsBufreqEventInfo {
     char *audio_buffer;
     size_t audio_buffer_size;
     char *marker_buffer;
     size_t marker_buffer_size;
 } AITalk_Core_TtsBufreqEventInfo;
  
 typedef struct AITalk_Core_TtsBufdoneEventInfo {
     char *audio_buffer;
     size_t audio_buffer_size;
     char *marker_buffer;
     size_t marker_buffer_size;
     size_t marker_buffer_count;
 } AITalk_Core_TtsBufdoneEventInfo;
  
 typedef struct AITalk_Core_TtsMarkerEventInfo AITalk_Core_TtsMarkerEventInfo;
  
 typedef struct AITalk_Core_BookmarkMarker {
     size_t audio_sample_pos;
     size_t input_text_pos;
     const char *bookmark_id;
     size_t bookmark_id_size;
 } AITalk_Core_BookmarkMarker;
  
 typedef struct AITalk_Core_LipsyncMarker {
     size_t audio_sample_pos;
     const char *phoneme;
     size_t phoneme_size;
 } AITalk_Core_LipsyncMarker;
  
 typedef struct AITalk_Core_AccentMarker {
     size_t audio_sample_pos;
     size_t accent_index;
 } AITalk_Core_AccentMarker;
  
 typedef struct AITalk_Core_PhraseMarker {
     size_t audio_sample_pos;
     size_t phrase_index;
 } AITalk_Core_PhraseMarker;
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Marker_getTtsMarkerEventInfo(AITalk_Core_TtsMarkerEventInfo **ptrptr, char *buffer, const size_t buffer_size, const size_t index);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_Marker_getType(AITalk_Core_MarkerTypeId *type, AITalk_Core_TtsMarkerEventInfo *data);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_BookmarkMarker_getValues(AITalk_Core_BookmarkMarker *marker, AITalk_Core_TtsMarkerEventInfo *data);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_LipsyncMarker_getValues(AITalk_Core_LipsyncMarker *marker, AITalk_Core_TtsMarkerEventInfo *data);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_AccentMarker_getValues(AITalk_Core_AccentMarker *marker, AITalk_Core_TtsMarkerEventInfo *data);
  
  
 AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 AITalkReturnCode AITalk_Core_PhraseMarker_getValues(AITalk_Core_PhraseMarker *marker, AITalk_Core_TtsMarkerEventInfo *data);
  
 AITALK_END_EXTERN_C
   // addtogroup AITalk_SDK_Core_Tts_Marker
   // addtogroup AITalk_SDK_Core_Tts
   // addtogroup AITalk_SDK_Core
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_CORE_MARKER_H_
