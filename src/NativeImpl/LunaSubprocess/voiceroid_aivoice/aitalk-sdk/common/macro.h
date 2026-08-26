 // -------------------------------------------------------------------
 // AITalk(R) SDK Common Macro API [http://www.ai-j.jp]
 // -------------------------------------------------------------------
  
  
 #ifndef AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_MACRO_H_
 #define AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_MACRO_H_
  
 #ifdef __cplusplus
 // Macro definition to avoid IDE auto indentation
 #define AITALK_BEGIN_EXTERN_C extern "C" { /*}*/
 #define AITALK_END_EXTERN_C /*{*/ }
 #else
 #define AITALK_BEGIN_EXTERN_C
 #define AITALK_END_EXTERN_C
 #endif  // __cplusplus
  
 AITALK_BEGIN_EXTERN_C
  
 #if defined(AITALK_SDK_DLLEXPORT)
 #define AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE __declspec(dllexport)
 #elif defined(AITALK_SDK_DLLIMPORT)
 #define AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE __declspec(dllimport)
 #else
 #define AITALK_SDK_IMPORT_EXPORT_ATTRIBUTE
 #endif
  
 AITALK_END_EXTERN_C
  
 #endif  // AITALK_SDK_SRC_INCLUDE_AITALK_SDK_COMMON_MACRO_H_
