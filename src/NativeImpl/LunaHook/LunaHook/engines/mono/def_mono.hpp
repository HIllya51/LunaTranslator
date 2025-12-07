#pragma once

typedef signed long SInt32;
typedef unsigned long UInt32;
typedef signed short SInt16;
typedef unsigned short UInt16;
typedef unsigned char UInt8;
typedef signed char SInt8;
typedef unsigned long long UInt64;
typedef signed long long SInt64;
#define MONO_ZERO_LEN_ARRAY 1
#define MONO_TOKEN_TYPE_DEF 0x02000000
#define MONO_TABLE_TYPEDEF 0x2
struct MonoException;
struct MonoAssembly;
struct MonoClassField;
struct MonoClass;
struct MonoDomain;
struct MonoImage;
struct MonoType;
struct MonoMethodSignature;
struct MonoArray;
struct MonoThread;
struct MonoThreadsSync;
struct MonoVTable;
struct MonoProperty;
struct MonoReflectionAssembly;
struct MonoReflectionMethod;
struct MonoAppDomain;
struct MonoCustomAttrInfo;
struct MonoTableInfo;
struct MonoReflectionType
{
	UInt32 offset[2];
	MonoType *type;
};

typedef void *gconstpointer;
typedef void *gpointer;
typedef int gboolean;
typedef unsigned int guint32;
typedef int gint32;
typedef long gint64;
typedef unsigned char guchar;
typedef UInt16 gunichar2;

struct MonoObject
{
	MonoVTable *vtable;
	MonoThreadsSync *synchronisation;
};

typedef MonoObject *MonoStruct;
typedef MonoObject **MonoStruct_out;

struct MonoString
{
	MonoObject object;
	gint32 length;
	gunichar2 chars[0];
};

struct MonoMethod
{
	UInt16 flags;
	UInt16 iflags;
};

typedef enum
{
	MONO_VERIFIER_MODE_OFF,
	MONO_VERIFIER_MODE_VALID,
	MONO_VERIFIER_MODE_VERIFIABLE,
	MONO_VERIFIER_MODE_STRICT
} MiniVerifierMode;

typedef enum
{
	MONO_SECURITY_MODE_NONE,
	MONO_SECURITY_MODE_CORE_CLR,
	MONO_SECURITY_MODE_CAS,
	MONO_SECURITY_MODE_SMCS_HACK
} MonoSecurityMode;

typedef void GFuncRef(void *, void *);
typedef GFuncRef *GFunc;

typedef enum
{
	MONO_UNHANDLED_POLICY_LEGACY,
	MONO_UNHANDLED_POLICY_CURRENT
} MonoRuntimeUnhandledExceptionPolicy;

struct MonoMethodDesc
{
	char *namespace2;
	char *klass;
	char *name;
	char *args1;
	UInt32 num_args;
	gboolean include_namespace, klass_glob, name_glob;
};

struct MonoJitInfo;
struct MonoAssemblyName;
struct MonoDebugSourceLocation;
struct MonoLoaderError;
struct MonoDlFallbackHandler;
struct LivenessState;

struct MonoBreakPolicy;

typedef bool (*MonoCoreClrPlatformCB)(const char *image_name);

typedef unsigned int guint;
typedef void (*register_object_callback)(gpointer *arr, int size, void *callback_userdata);
typedef gboolean (*MonoStackWalk)(MonoMethod *method, gint32 native_offset, gint32 il_offset, gboolean managed, gpointer data);
typedef MonoBreakPolicy (*MonoBreakPolicyFunc)(MonoMethod *method);
typedef void *(*MonoDlFallbackLoad)(const char *name, int flags, char **err, void *user_data);
typedef void *(*MonoDlFallbackSymbol)(void *handle, const char *name, char **err, void *user_data);
typedef void *(*MonoDlFallbackClose)(void *handle, void *user_data);

typedef enum
{
	MONO_TYPE_NAME_FORMAT_IL,
	MONO_TYPE_NAME_FORMAT_REFLECTION,
	MONO_TYPE_NAME_FORMAT_FULL_NAME,
	MONO_TYPE_NAME_FORMAT_ASSEMBLY_QUALIFIED
} MonoTypeNameFormat;

// typedef void (*vprintf_func)(const char* msg, va_list args);

struct MonoProfiler;
typedef void (*MonoProfileFunc)(MonoProfiler *prof);

typedef enum
{
	MONO_PROFILE_NONE = 0,
	MONO_PROFILE_APPDOMAIN_EVENTS = 1 << 0,
	MONO_PROFILE_ASSEMBLY_EVENTS = 1 << 1,
	MONO_PROFILE_MODULE_EVENTS = 1 << 2,
	MONO_PROFILE_CLASS_EVENTS = 1 << 3,
	MONO_PROFILE_JIT_COMPILATION = 1 << 4,
	MONO_PROFILE_INLINING = 1 << 5,
	MONO_PROFILE_EXCEPTIONS = 1 << 6,
	MONO_PROFILE_ALLOCATIONS = 1 << 7,
	MONO_PROFILE_GC = 1 << 8,
	MONO_PROFILE_THREADS = 1 << 9,
	MONO_PROFILE_REMOTING = 1 << 10,
	MONO_PROFILE_TRANSITIONS = 1 << 11,
	MONO_PROFILE_ENTER_LEAVE = 1 << 12,
	MONO_PROFILE_COVERAGE = 1 << 13,
	MONO_PROFILE_INS_COVERAGE = 1 << 14,
	MONO_PROFILE_STATISTICAL = 1 << 15,
	MONO_PROFILE_METHOD_EVENTS = 1 << 16,
	MONO_PROFILE_MONITOR_EVENTS = 1 << 17,
	MONO_PROFILE_IOMAP_EVENTS = 1 << 18, /* this should likely be removed, too */
	MONO_PROFILE_GC_MOVES = 1 << 19
} MonoProfileFlags;

typedef enum
{
	MONO_GC_EVENT_START,
	MONO_GC_EVENT_MARK_START,
	MONO_GC_EVENT_MARK_END,
	MONO_GC_EVENT_RECLAIM_START,
	MONO_GC_EVENT_RECLAIM_END,
	MONO_GC_EVENT_END,
	MONO_GC_EVENT_PRE_STOP_WORLD,
	MONO_GC_EVENT_POST_STOP_WORLD,
	MONO_GC_EVENT_PRE_START_WORLD,
	MONO_GC_EVENT_POST_START_WORLD
} MonoGCEvent;

typedef void (*MonoProfileMethodFunc)(MonoProfiler *prof, MonoMethod *method);
typedef void (*MonoProfileGCFunc)(MonoProfiler *prof, MonoGCEvent event, int generation);
typedef void (*MonoProfileGCMoveFunc)(MonoProfiler *prof, void **objects, int num);
typedef void (*MonoProfileGCResizeFunc)(MonoProfiler *prof, gint64 new_size);
typedef void (*MonoProfileAllocFunc)(MonoProfiler *prof, MonoObject *obj, MonoClass *klass);
typedef void (*MonoProfileJitResult)(MonoProfiler *prof, MonoMethod *method, MonoJitInfo *jinfo, int result);
typedef void (*MonoProfileExceptionFunc)(MonoProfiler *prof, MonoObject *object);
typedef void (*MonoProfileExceptionClauseFunc)(MonoProfiler *prof, MonoMethod *method, int clause_type, int clause_num);
typedef void (*MonoProfileThreadFunc)(MonoProfiler *prof, uint32_t tid);

inline void (*mono_thread_suspend_all_other_threads)();
inline void (*mono_thread_pool_cleanup)();
inline void (*mono_threads_set_shutting_down)();
inline void (*mono_runtime_set_shutting_down)();
inline gboolean (*mono_domain_finalize)(MonoDomain *domain, int timeout);
inline void (*mono_runtime_cleanup)(MonoDomain *domain);
inline MonoMethodDesc *(*mono_method_desc_new)(const char *name, gboolean include_namespace);
inline MonoMethod *(*mono_method_desc_search_in_image)(MonoMethodDesc *desc, MonoImage *image);
inline void (*mono_verifier_set_mode)(MiniVerifierMode m);
inline void (*mono_security_set_mode)(MonoSecurityMode m);
inline void (*mono_add_internal_call)(const char *name, gconstpointer method);
inline void (*mono_jit_cleanup)(MonoDomain *domain);
inline MonoDomain *(*mono_jit_init)(const char *file);
inline MonoDomain *(*mono_jit_init_version)(const char *file, const char *runtime_version);
inline int (*mono_jit_exec)(MonoDomain *domain, MonoAssembly *assembly, int argc, char *argv[]);
inline MonoClass *(*mono_class_from_name)(MonoImage *image, const char *name_space, const char *name);
inline MonoAssembly *(*mono_domain_assembly_open)(MonoDomain *domain, const char *name);
inline MonoDomain *(*mono_domain_create_appdomain)(const char *domainname, const char *configfile);
inline void (*mono_domain_unload)(MonoDomain *domain);
inline MonoObject *(*mono_object_new)(MonoDomain *domain, MonoClass *klass);
inline void (*mono_runtime_object_init)(MonoObject *this_obj);
inline MonoObject *(*mono_runtime_invoke)(MonoMethod *method, void *obj, void **params, MonoObject **exc);
inline MonoObject *(*mono_runtime_invoke_array)(MonoMethod *method, void *obj, MonoArray *params, MonoObject **exc);
inline void (*mono_field_set_value)(MonoObject *obj, MonoClassField *field, void *value);
inline void (*mono_field_get_value)(MonoObject *obj, MonoClassField *field, void *value);
inline int (*mono_field_get_offset)(MonoClassField *field);
inline MonoClassField *(*mono_class_get_fields)(MonoClass *klass, gpointer *iter);
inline MonoMethod *(*mono_class_get_methods)(MonoClass *klass, gpointer *iter);
inline MonoDomain *(*mono_domain_get)();
inline MonoDomain *(*mono_get_root_domain)();
inline gint32 (*mono_domain_get_id)(MonoDomain *domain);
inline void (*mono_assembly_foreach)(GFunc func, gpointer user_data);
inline void (*mono_image_close)(MonoImage *image);
inline void (*mono_unity_socket_security_enabled_set)(gboolean b);
inline const char *(*mono_image_get_name)(MonoImage *image);
inline MonoClass *(*mono_get_object_class)();
inline void (*mono_set_commandline_arguments)(int i, const char *argv[], const char *s);
inline const char *(*mono_field_get_name)(MonoClassField *field);
inline MonoType *(*mono_field_get_type)(MonoClassField *field);
inline int (*mono_type_get_type)(MonoType *type);
inline const char *(*mono_method_get_name)(MonoMethod *method);
inline MonoImage *(*mono_assembly_get_image)(MonoAssembly *assembly);
inline MonoClass *(*mono_method_get_class)(MonoMethod *method);
inline MonoClass *(*mono_object_get_class)(MonoObject *obj);
inline gboolean (*mono_class_is_valuetype)(MonoClass *klass);
inline guint32 (*mono_signature_get_param_count)(MonoMethodSignature *sig);
inline char *(*mono_string_to_utf8)(MonoString *string_obj);
inline MonoString *(*mono_string_new_wrapper)(const char *text);
inline MonoClass *(*mono_class_get_parent)(MonoClass *klass);
inline const char *(*mono_class_get_namespace)(MonoClass *klass);
inline gboolean (*mono_class_is_subclass_of)(MonoClass *klass, MonoClass *klassc, gboolean check_interfaces);
inline const char *(*mono_class_get_name)(MonoClass *klass);
inline char *(*mono_type_get_name)(MonoType *type);
inline MonoClass *(*mono_type_get_class)(MonoType *type);
inline MonoException *(*mono_exception_from_name_msg)(MonoImage *image, const char *name_space, const char *name, const char *msg);
inline void (*mono_raise_exception)(MonoException *ex);
inline MonoClass *(*mono_get_exception_class)();
inline MonoClass *(*mono_get_array_class)();
inline MonoClass *(*mono_get_string_class)();
inline MonoClass *(*mono_get_int32_class)();
inline MonoArray *(*mono_array_new)(MonoDomain *domain, MonoClass *eclass, guint32 n);
inline MonoArray *(*mono_array_new_full)(MonoDomain *domain, MonoClass *array_class, guint32 *lengths, guint32 *lower_bounds);
inline MonoClass *(*mono_array_class_get)(MonoClass *eclass, guint32 rank);
inline gint32 (*mono_class_array_element_size)(MonoClass *ac);
inline MonoObject *(*mono_type_get_object)(MonoDomain *domain, MonoType *type);
inline MonoThread *(*mono_thread_attach)(MonoDomain *domain);
inline void (*mono_thread_detach)(MonoThread *thread);
inline MonoThread *(*mono_thread_exit)();
inline MonoThread *(*mono_thread_current)();
inline void (*mono_thread_set_main)(MonoThread *thread);
inline void (*mono_set_find_plugin_callback)(gconstpointer method);
inline void (*mono_security_enable_core_clr)();
inline bool (*mono_security_set_core_clr_platform_callback)(MonoCoreClrPlatformCB a);
inline MonoRuntimeUnhandledExceptionPolicy (*mono_runtime_unhandled_exception_policy_get)();
inline void (*mono_runtime_unhandled_exception_policy_set)(MonoRuntimeUnhandledExceptionPolicy policy);
inline MonoClass *(*mono_class_get_nesting_type)(MonoClass *klass);
inline MonoVTable *(*mono_class_vtable)(MonoDomain *domain, MonoClass *klass);
inline MonoReflectionMethod *(*mono_method_get_object)(MonoDomain *domain, MonoMethod *method, MonoClass *refclass);
inline MonoMethodSignature *(*mono_method_signature)(MonoMethod *method);
inline MonoType *(*mono_signature_get_params)(MonoMethodSignature *sig, gpointer *iter);
inline MonoType *(*mono_signature_get_return_type)(MonoMethodSignature *sig);
inline MonoType *(*mono_class_get_type)(MonoClass *klass);
inline void (*mono_set_ignore_version_and_key_when_finding_assemblies_already_loaded)(gboolean value);
inline void (*mono_debug_init)(int format);
inline void (*mono_debug_open_image_from_memory)(MonoImage *image, const char *raw_contents, int size);
inline guint32 (*mono_field_get_flags)(MonoClassField *field);
inline MonoImage *(*mono_image_open_from_data_full)(const void *data, guint32 data_len, gboolean need_copy, int *status, gboolean ref_only);
inline MonoImage *(*mono_image_open_from_data_with_name)(char *data, guint32 data_len, gboolean need_copy, int *status, gboolean refonly, const char *name);
inline MonoAssembly *(*mono_assembly_load_from)(MonoImage *image, const char *fname, int *status);
inline MonoObject *(*mono_value_box)(MonoDomain *domain, MonoClass *klass, gpointer val);
inline MonoImage *(*mono_class_get_image)(MonoClass *klass);
inline char (*mono_signature_is_instance)(MonoMethodSignature *signature);
inline MonoMethod *(*mono_method_get_last_managed)();
inline MonoClass *(*mono_get_enum_class)();
inline MonoType *(*mono_class_get_byref_type)(MonoClass *klass);
inline void (*mono_field_static_get_value)(MonoVTable *vt, MonoClassField *field, void *value);
inline void (*mono_unity_set_embeddinghostname)(const char *name);
inline void (*mono_set_assemblies_path)(const char *name);
inline guint32 (*mono_gchandle_new)(MonoObject *obj, gboolean pinned);
inline MonoObject *(*mono_gchandle_get_target)(guint32 gchandle);
inline guint32 (*mono_gchandle_new_weakref)(MonoObject *obj, gboolean track_resurrection);
inline MonoObject *(*mono_assembly_get_object)(MonoDomain *domain, MonoAssembly *assembly);
inline void (*mono_gchandle_free)(guint32 gchandle);
inline MonoProperty *(*mono_class_get_properties)(MonoClass *klass, gpointer *iter);
inline MonoMethod *(*mono_property_get_get_method)(MonoProperty *prop);
inline MonoObject *(*mono_object_new_alloc_specific)(MonoVTable *vtable);
inline MonoObject *(*mono_object_new_specific)(MonoVTable *vtable);
inline void (*mono_gc_collect)(int generation);
inline int (*mono_gc_max_generation)();
inline MonoAssembly *(*mono_image_get_assembly)(MonoImage *image);
inline MonoAssembly *(*mono_assembly_open)(const char *filename, int *status);
inline gboolean (*mono_class_is_enum)(MonoClass *klass);
inline gint32 (*mono_class_instance_size)(MonoClass *klass);
inline guint32 (*mono_object_get_size)(MonoObject *obj);
inline const char *(*mono_image_get_filename)(MonoImage *image);
inline MonoAssembly *(*mono_assembly_load_from_full)(MonoImage *image, const char *fname, int *status, gboolean refonly);
inline MonoClass *(*mono_class_get_interfaces)(MonoClass *klass, gpointer *iter);
inline void (*mono_assembly_close)(MonoAssembly *assembly);
inline MonoProperty *(*mono_class_get_property_from_name)(MonoClass *klass, const char *name);
inline MonoMethod *(*mono_class_get_method_from_name)(MonoClass *klass, const char *name, int param_count);
inline MonoClass *(*mono_class_from_mono_type)(MonoType *image);
inline gboolean (*mono_domain_set)(MonoDomain *domain, gboolean force);
inline void (*mono_thread_push_appdomain_ref)(MonoDomain *domain);
inline void (*mono_thread_pop_appdomain_ref)();
inline int (*mono_runtime_exec_main)(MonoMethod *method, MonoArray *args, MonoObject **exc);
inline MonoImage *(*mono_get_corlib)();
inline MonoClassField *(*mono_class_get_field_from_name)(MonoClass *klass, const char *name);
inline guint32 (*mono_class_get_flags)(MonoClass *klass);
inline int (*mono_parse_default_optimizations)(const char *p);
inline void (*mono_set_defaults)(int verbose_level, guint32 opts);
inline void (*mono_set_dirs)(const char *assembly_dir, const char *config_dir);
inline void (*mono_jit_parse_options)(int argc, char *argv[]);
inline gpointer (*mono_object_unbox)(MonoObject *o);
inline MonoObject *(*mono_custom_attrs_get_attr)(MonoCustomAttrInfo *ainfo, MonoClass *attr_klass);
inline gboolean (*mono_custom_attrs_has_attr)(MonoCustomAttrInfo *ainfo, MonoClass *attr_klass);
inline MonoCustomAttrInfo *(*mono_custom_attrs_from_field)(MonoClass *klass, MonoClassField *field);
inline MonoCustomAttrInfo *(*mono_custom_attrs_from_method)(MonoMethod *method);
inline MonoCustomAttrInfo *(*mono_custom_attrs_from_class)(MonoClass *klass);
inline void (*mono_custom_attrs_free)(MonoCustomAttrInfo *attr);
inline void (*g_free)(void *p);
inline gboolean (*mono_runtime_is_shutting_down)();
inline MonoMethod *(*mono_object_get_virtual_method)(MonoObject *obj, MonoMethod *method);
inline gpointer (*mono_jit_info_get_code_start)(MonoJitInfo *ji);
inline int (*mono_jit_info_get_code_size)(MonoJitInfo *ji);
inline MonoClass *(*mono_class_from_name_case)(MonoImage *image, const char *name_space, const char *name);
inline MonoClass *(*mono_class_get_nested_types)(MonoClass *klass, gpointer *iter);
inline int (*mono_class_get_userdata_offset)();
inline void *(*mono_class_get_userdata)(MonoClass *klass);
inline void (*mono_class_set_userdata)(MonoClass *klass, void *userdata);
inline void (*mono_set_signal_chaining)(gboolean chain_signals);
inline void (*mono_unity_set_unhandled_exception_handler)(void *handler);
inline char *(*mono_array_addr_with_size)(MonoArray *array, int size, uintptr_t idx);
inline gunichar2 *(*mono_string_to_utf16)(MonoString *string_obj);
inline MonoClass *(*mono_field_get_parent)(MonoClassField *field);
inline char *(*mono_method_full_name)(MonoMethod *method, gboolean signature);
inline MonoObject *(*mono_object_isinst)(MonoObject *obj, MonoClass *klass);
inline MonoString *(*mono_string_new_len)(MonoDomain *domain, const char *text, guint length);
inline MonoString *(*mono_string_from_utf16)(gunichar2 *data);
inline MonoString *(*mono_string_new_utf16)(MonoDomain *domain, const gunichar2 *text, int32_t len);
inline MonoException *(*mono_get_exception_argument_null)(const char *arg);
inline MonoClass *(*mono_get_boolean_class)();
inline MonoClass *(*mono_get_byte_class)();
inline MonoClass *(*mono_get_char_class)();
inline MonoClass *(*mono_get_int16_class)();
inline MonoClass *(*mono_get_int64_class)();
inline MonoClass *(*mono_get_single_class)();
inline MonoClass *(*mono_get_double_class)();
inline gboolean (*mono_class_is_generic)(MonoClass *klass);
inline gboolean (*mono_class_is_inflated)(MonoClass *klass);
inline gboolean (*unity_mono_method_is_generic)(MonoMethod *method);
inline gboolean (*unity_mono_method_is_inflated)(MonoMethod *method);
inline gboolean (*mono_is_debugger_attached)();
inline gboolean (*mono_assembly_fill_assembly_name)(MonoImage *image, MonoAssemblyName *aname);
inline char *(*mono_stringify_assembly_name)(MonoAssemblyName *aname);
inline gboolean (*mono_assembly_name_parse)(const char *name, MonoAssemblyName *aname);
inline MonoAssembly *(*mono_assembly_loaded)(MonoAssemblyName *aname);
inline int (*mono_image_get_table_rows)(MonoImage *image, int table_id);
inline MonoClass *(*mono_class_get)(MonoImage *image, guint32 type_token);
inline gboolean (*mono_metadata_signature_equal)(MonoMethodSignature *sig1, MonoMethodSignature *sig2);
inline gboolean (*mono_gchandle_is_in_domain)(guint32 gchandle, MonoDomain *domain);
inline void (*mono_stack_walk)(MonoStackWalk func, gpointer user_data);
inline char *(*mono_pmip)(void *ip);
inline MonoObject *(*mono_runtime_delegate_invoke)(MonoObject *delegate, void **params, MonoObject **exc);
inline MonoJitInfo *(*mono_jit_info_table_find)(MonoDomain *domain, char *addr);
inline MonoDebugSourceLocation *(*mono_debug_lookup_source_location)(MonoMethod *method, guint32 address, MonoDomain *domain);
inline void (*mono_debug_free_source_location)(MonoDebugSourceLocation *location);
inline void (*mono_gc_wbarrier_generic_store)(gpointer ptr, MonoObject *value);
inline MonoType *(*mono_class_enum_basetype)(MonoClass *klass);
inline guint32 (*mono_class_get_type_token)(MonoClass *klass);
inline int (*mono_class_get_rank)(MonoClass *klass);
inline MonoClass *(*mono_class_get_element_class)(MonoClass *klass);
inline gboolean (*mono_unity_class_is_interface)(MonoClass *klass);
inline gboolean (*mono_unity_class_is_abstract)(MonoClass *klass);
inline gint32 (*mono_array_element_size)(MonoClass *ac);
inline void (*mono_config_parse)(const char *filename);
inline void (*mono_set_break_policy)(MonoBreakPolicyFunc policy_callback);
inline MonoArray *(*mono_custom_attrs_construct)(MonoCustomAttrInfo *cinfo);
inline MonoCustomAttrInfo *(*mono_custom_attrs_from_assembly)(MonoAssembly *assembly);
inline MonoArray *(*mono_reflection_get_custom_attrs_by_type)(MonoObject *obj, MonoClass *attr_klass);
inline MonoLoaderError *(*mono_loader_get_last_error)();
inline MonoException *(*mono_loader_error_prepare_exception)(MonoLoaderError *error);
inline MonoDlFallbackHandler *(*mono_dl_fallback_register)(MonoDlFallbackLoad load_func, MonoDlFallbackSymbol symbol_func, MonoDlFallbackClose close_func, void *user_data);
inline void (*mono_dl_fallback_unregister)(MonoDlFallbackHandler *handler);
inline LivenessState *(*mono_unity_liveness_allocate_struct)(MonoClass *filter, guint max_count, register_object_callback callback, void *callback_userdata);
inline void (*mono_unity_liveness_stop_gc_world)();
inline void (*mono_unity_liveness_finalize)(LivenessState *state);
inline void (*mono_unity_liveness_start_gc_world)();
inline void (*mono_unity_liveness_free_struct)(LivenessState *state);
inline LivenessState *(*mono_unity_liveness_calculation_begin)(MonoClass *filter, guint max_count, register_object_callback callback, void *callback_userdata);
inline void (*mono_unity_liveness_calculation_end)(LivenessState *state);
inline void (*mono_unity_liveness_calculation_from_root)(MonoObject *root, LivenessState *state);
inline void (*mono_unity_liveness_calculation_from_statics)(LivenessState *state);
inline void (*mono_trace_set_level_string)(const char *value);
inline void (*mono_trace_set_mask_string)(char *value);
inline gint64 (*mono_gc_get_used_size)();
inline gint64 (*mono_gc_get_heap_size)();
inline MonoMethod *(*mono_method_desc_search_in_class)(MonoMethodDesc *desc, MonoClass *klass);
inline void (*mono_method_desc_free)(MonoMethodDesc *desc);
inline char *(*mono_type_get_name_full)(MonoType *type, MonoTypeNameFormat format);
inline void (*mono_unity_thread_clear_domain_fields)();
inline void (*mono_profiler_install)(MonoProfiler *prof, MonoProfileFunc shutdown_callback);
inline void (*mono_profiler_set_events)(MonoProfileFlags events);
inline void (*mono_profiler_install_enter_leave)(MonoProfileMethodFunc enter, MonoProfileMethodFunc fleave);
inline void (*mono_profiler_install_gc)(MonoProfileGCFunc callback, MonoProfileGCResizeFunc heap_resize_callback);
inline void (*mono_profiler_install_allocation)(MonoProfileAllocFunc callback);
inline void (*mono_profiler_install_jit_end)(MonoProfileJitResult end);
inline void (*mono_profiler_install_exception)(MonoProfileExceptionFunc throw_callback, MonoProfileMethodFunc exc_method_leave, MonoProfileExceptionClauseFunc clause_callback);
inline void (*mono_profiler_install_thread)(MonoProfileThreadFunc start, MonoProfileThreadFunc end);
inline uint64_t *(*mono_compile_method)(MonoMethod *);
inline MonoTableInfo *(*mono_image_get_table_info)(MonoImage *, int);
inline int (*mono_table_info_get_rows)(MonoTableInfo *);
inline gunichar2 *(*mono_string_chars)(MonoString *str);
inline int (*mono_string_length)(MonoString *str);
namespace monofunctions
{
	void init(HMODULE dll);
	uintptr_t get_method_pointer(const char *assemblyName, const char *namespaze,
								 const char *klassName, const char *name, int argsCount, bool strict);
	MonoMethod *get_method_internal(const char *assemblyName, const char *namespaze,
									const char *klassName, const char *name, int argsCount, bool strict);

	std::optional<std::wstring_view> get_string(void *);
	void *create_string(std::wstring_view ws);
	monoloopinfo loop_all_methods(std::optional<std::function<void(const std::string &)>>);
	MonoType *get_type_pointer(const char *_dll, const char *_namespace, const char *_class, bool strict);
	MonoClass *get_class_pointer(const char *_dll, const char *_namespace, const char *_class, bool strict);
}