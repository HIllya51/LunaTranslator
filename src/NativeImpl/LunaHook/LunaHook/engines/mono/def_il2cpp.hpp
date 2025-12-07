#pragma once

#if _MSC_VER
typedef wchar_t Il2CppChar;
#elif __has_feature(cxx_unicode_literals)
typedef char16_t Il2CppChar;
#else
typedef uint16_t Il2CppChar;
#endif

struct Int32Object;

struct Boolean
{
	bool m_value;
};

struct Byte
{
	uint8_t m_value;
};

// UnityEngine.Color
struct Color_t
{
public:
	// System.Single UnityEngine.Color::r
	float r;
	// System.Single UnityEngine.Color::g
	float g;
	// System.Single UnityEngine.Color::b
	float b;
	// System.Single UnityEngine.Color::a
	float a;
};

// UnityEngine.Color32
struct Color32_t
{
public:
	// System.Single UnityEngine.Color32::rgba
	unsigned int rgba;
};

// UnityEngine.ScreenOrientation
enum class ScreenOrientation
{
	Unknown,
	Portrait,
	PortraitUpsideDown,
	LandscapeLeft,
	LandscapeRight,
	AutoRotation,
	Landscape = 3
};

// UnityEngine.Vector2
struct Vector2_t
{
public:
	// System.Single UnityEngine.Vector2::x
	float x;
	// System.Single UnityEngine.Vector2::y
	float y;
};

// UnityEngine.Vector2Int
struct Vector2Int_t
{
public:
	// System.Int32 UnityEngine.Vector2Int::m_X
	int x;
	// System.Int32 UnityEngine.Vector2Int::m_Y
	int y;
};

// UnityEngine.Vector3
struct Vector3_t
{
public:
	// System.Single UnityEngine.Vector3::x
	float x;
	// System.Single UnityEngine.Vector3::y
	float y;
	// System.Single UnityEngine.Vector3::z
	float z;
};

// UnityEngine.Vector4
struct Vector4_t
{
public:
	// System.Single UnityEngine.Vector4::x
	float x;
	// System.Single UnityEngine.Vector4::y
	float y;
	// System.Single UnityEngine.Vector4::z
	float z;
	// System.Single UnityEngine.Vector4::w
	float w;
};

struct Rect_t
{
public:
	short x;
	short y;
	short width;
	short height;
};

struct Resolution_t
{
public:
	int width;
	int height;
	int herz;
};

// UnityEngine.TextGenerationSettings
struct TextGenerationSettings_t
{
public:
	// UnityEngine.Font UnityEngine.TextGenerationSettings::font
	void *font;
	// UnityEngine.Color UnityEngine.TextGenerationSettings::color
	Color_t color;
	// System.Int32 UnityEngine.TextGenerationSettings::fontSize
	int32_t fontSize;
	// System.Single UnityEngine.TextGenerationSettings::lineSpacing
	float lineSpacing;
	// System.Boolean UnityEngine.TextGenerationSettings::richText
	bool richText;
	// System.Single UnityEngine.TextGenerationSettings::scaleFactor
	float scaleFactor;
	// UnityEngine.FontStyle UnityEngine.TextGenerationSettings::fontStyle
	int32_t fontStyle;
	// UnityEngine.TextAnchor UnityEngine.TextGenerationSettings::textAnchor
	int32_t textAnchor;
	// System.Boolean UnityEngine.TextGenerationSettings::alignByGeometry
	bool alignByGeometry;
	// System.Boolean UnityEngine.TextGenerationSettings::resizeTextForBestFit
	bool resizeTextForBestFit;
	// System.Int32 UnityEngine.TextGenerationSettings::resizeTextMinSize
	int32_t resizeTextMinSize;
	// System.Int32 UnityEngine.TextGenerationSettings::resizeTextMaxSize
	int32_t resizeTextMaxSize;
	// System.Boolean UnityEngine.TextGenerationSettings::updateBounds
	bool updateBounds;
	// UnityEngine.VerticalWrapMode UnityEngine.TextGenerationSettings::verticalOverflow
	int32_t verticalOverflow;
	// UnityEngine.HorizontalWrapMode UnityEngine.TextGenerationSettings::horizontalOverflow
	int32_t horizontalOverflow;
	// UnityEngine.Vector2 UnityEngine.TextGenerationSettings::generationExtents
	Vector2_t generationExtents;
	// UnityEngine.Vector2 UnityEngine.TextGenerationSettings::pivot
	Vector2_t pivot;
	// System.Boolean UnityEngine.TextGenerationSettings::generateOutOfBounds
	bool generateOutOfBounds;
};

enum Il2CppTypeEnum
{
	IL2CPP_TYPE_END = 0x00, /* End of List */
	IL2CPP_TYPE_VOID = 0x01,
	IL2CPP_TYPE_BOOLEAN = 0x02,
	IL2CPP_TYPE_CHAR = 0x03,
	IL2CPP_TYPE_I1 = 0x04,
	IL2CPP_TYPE_U1 = 0x05,
	IL2CPP_TYPE_I2 = 0x06,
	IL2CPP_TYPE_U2 = 0x07,
	IL2CPP_TYPE_I4 = 0x08,
	IL2CPP_TYPE_U4 = 0x09,
	IL2CPP_TYPE_I8 = 0x0a,
	IL2CPP_TYPE_U8 = 0x0b,
	IL2CPP_TYPE_R4 = 0x0c,
	IL2CPP_TYPE_R8 = 0x0d,
	IL2CPP_TYPE_STRING = 0x0e,
	IL2CPP_TYPE_PTR = 0x0f,
	IL2CPP_TYPE_BYREF = 0x10,
	IL2CPP_TYPE_VALUETYPE = 0x11,
	IL2CPP_TYPE_CLASS = 0x12,
	IL2CPP_TYPE_VAR = 0x13,
	IL2CPP_TYPE_ARRAY = 0x14,
	IL2CPP_TYPE_GENERICINST = 0x15,
	IL2CPP_TYPE_TYPEDBYREF = 0x16,
	IL2CPP_TYPE_I = 0x18,
	IL2CPP_TYPE_U = 0x19,
	IL2CPP_TYPE_FNPTR = 0x1b,
	IL2CPP_TYPE_OBJECT = 0x1c,
	IL2CPP_TYPE_SZARRAY = 0x1d,
	IL2CPP_TYPE_MVAR = 0x1e,
	IL2CPP_TYPE_CMOD_REQD = 0x1f,
	IL2CPP_TYPE_CMOD_OPT = 0x20,
	IL2CPP_TYPE_INTERNAL = 0x21,

	IL2CPP_TYPE_MODIFIER = 0x40,
	IL2CPP_TYPE_SENTINEL = 0x41,
	IL2CPP_TYPE_PINNED = 0x45,

	IL2CPP_TYPE_ENUM = 0x55
};

typedef struct Il2CppType
{
	void *dummy;
	unsigned int attrs : 16;
	Il2CppTypeEnum type : 8;
	unsigned int num_mods : 6;
	unsigned int byref : 1;
	unsigned int pinned : 1;
} Il2CppType;

typedef struct FieldInfo
{
	const char *name;
	const Il2CppType *type;
	void *parent;
	int32_t offset; // If offset is -1, then it's thread static
	uint32_t token;
} FieldInfo;

struct MethodInfo;

typedef struct Il2CppClass
{
	// The following fields are always valid for a Il2CppClass structure
	const void *image;
	void *gc_desc;
	const char *name;
	const char *namespaze;
	Il2CppType byval_arg;
	Il2CppType this_arg;
	Il2CppClass *element_class;
	Il2CppClass *castClass;
	Il2CppClass *declaringType;
	Il2CppClass *parent;
	void *generic_class;
	void *typeMetadataHandle; // non-NULL for Il2CppClass's constructed from type defintions
	const void *interopData;
	Il2CppClass *klass; // hack to pretend we are a MonoVTable. Points to ourself
	// End always valid fields

	// The following fields need initialized before access. This can be done per field or as an aggregate via a call to Class::Init
	FieldInfo *fields;					 // Initialized in SetupFields
	const void *events;					 // Initialized in SetupEvents
	const void *properties;				 // Initialized in SetupProperties
	const MethodInfo **methods;			 // Initialized in SetupMethods
	Il2CppClass **nestedTypes;			 // Initialized in SetupNestedTypes
	Il2CppClass **implementedInterfaces; // Initialized in SetupInterfaces
	void *interfaceOffsets;				 // Initialized in Init
	void *static_fields;				 // Initialized in Init
	const void *rgctx_data;				 // Initialized in Init
	// used for fast parent checks
	Il2CppClass **typeHierarchy; // Initialized in SetupTypeHierachy
	// End initialization required fields

	void *unity_user_data;

	uint32_t initializationExceptionGCHandle;

	uint32_t cctor_started;
	uint32_t cctor_finished;
	size_t cctor_thread;

	// Remaining fields are always valid except where noted
	void *genericContainerHandle;
	uint32_t instance_size; // valid when size_inited is true
	uint32_t actualSize;
	uint32_t element_size;
	int32_t native_size;
	uint32_t static_fields_size;
	uint32_t thread_static_fields_size;
	int32_t thread_static_fields_offset;
	uint32_t flags;
	uint32_t token;

	uint16_t method_count; // lazily calculated for arrays, i.e. when rank > 0
	uint16_t property_count;
	uint16_t field_count;
	uint16_t event_count;
	uint16_t nested_type_count;
	uint16_t vtable_count; // lazily calculated for arrays, i.e. when rank > 0
	uint16_t interfaces_count;
	uint16_t interface_offsets_count; // lazily calculated for arrays, i.e. when rank > 0

	uint8_t typeHierarchyDepth; // Initialized in SetupTypeHierachy
	uint8_t genericRecursionDepth;
	uint8_t rank;
	uint8_t minimumAlignment; // Alignment of this type
	uint8_t naturalAligment;  // Alignment of this type without accounting for packing
	uint8_t packingSize;

	// this is critical for performance of Class::InitFromCodegen. Equals to initialized && !has_initialization_error at all times.
	// Use Class::UpdateInitializedAndNoError to update
	uint8_t initialized_and_no_error : 1;

	uint8_t valuetype : 1;
	uint8_t initialized : 1;
	uint8_t enumtype : 1;
	uint8_t is_generic : 1;
	uint8_t has_references : 1; // valid when size_inited is true
	uint8_t init_pending : 1;
	uint8_t size_init_pending : 1;
	uint8_t size_inited : 1;
	uint8_t has_finalize : 1;
	uint8_t has_cctor : 1;
	uint8_t is_blittable : 1;
	uint8_t is_import_or_windows_runtime : 1;
	uint8_t is_vtable_initialized : 1;
	uint8_t has_initialization_error : 1;
	void *vtable[0];
} Il2CppClass;

struct ParameterInfo
{
	const char *name;
	int32_t position;
	uint32_t token;
	const Il2CppType *parameter_type;
};

typedef struct Il2CppGenericContainer
{
	/* index of the generic type definition or the generic method definition corresponding to this container */
	int32_t ownerIndex; // either index into Il2CppClass metadata array or Il2CppMethodDefinition array
	int32_t type_argc;
	/* If true, we're a generic method, otherwise a generic type definition. */
	int32_t is_method;
	/* Our type parameters. */
	int32_t genericParameterStart;
} Il2CppGenericContainer;

struct MethodInfo
{
	uintptr_t methodPointer;
	uintptr_t invoker_method;
	const char *name;
	Il2CppClass *klass;
	const Il2CppType *return_type;
	const ParameterInfo *parameters;
	union
	{
		uintptr_t rgctx_data;
		uintptr_t methodDefinition;
	};
	union
	{
		uintptr_t genericMethod;
		Il2CppGenericContainer *genericContainer;
	};
	uint32_t token;
	uint16_t flags;
	uint16_t iflags;
	uint16_t slot;
	uint8_t parameters_count;
	uint8_t is_generic : 1;
	uint8_t is_inflated : 1;
	uint8_t wrapper_type : 1;
	uint8_t is_marshaled_from_native : 1;
};

struct Il2CppObject
{
	union
	{
		Il2CppClass *klass;
		void *vtable;
	};
	void *monitor;
};
struct Il2CppDomain;
struct Il2CppAssembly;
struct Il2CppImage;
// not real Il2CppString class
struct Il2CppString
{
	Il2CppObject object;
	int32_t length; ///< Length of string *excluding* the trailing null (which is included in 'chars').
	Il2CppChar start_char[0];
};

typedef struct PropertyInfo
{
	Il2CppClass *parent;
	const char *name;
	const MethodInfo *get;
	const MethodInfo *set;
	uint32_t attrs;
	uint32_t token;
} PropertyInfo;

typedef struct Il2CppArraySize
{
	Il2CppObject obj;
	void *bounds;
	uintptr_t max_length;
	alignas(8) void *vector[0];
} Il2CppArraySize;

static const size_t kIl2CppSizeOfArray = (offsetof(Il2CppArraySize, vector));

struct CourseBaseObjectContext
{
	Il2CppObject *coursePrefab;
	Il2CppObject *courseGrassFurPrefab;
	Il2CppObject *monitorRenderTexture;
	Il2CppArraySize *swapTextures;
	Il2CppArraySize *swapSubTextures;
	Il2CppObject *postFilmSetGroup;
	Il2CppObject *grassParam;
};

struct RaceLoaderManagerCourceContext
{
	int courseId;
	int timeEnum;
	int seasonEnum;
	int turfGoalGate;
	int turfGoalFlower;
	int dirtGoalGate;
	int dirtGoalFlower;
	int skydomeCourseId;
	int skydomeSeasonEnum;
	int skydomeWeatherEnum;
	int skydomeTimeEnum;
	int audienceEnum;
	int audienceWeatherEnum;
	int audienceSeasonEnum;
	int treeWeaterEnum;
	int treeTimeEnum;
	int RotationCategoryEnum;
	int lightProbeId;
	Il2CppArraySize *materialTeturePairs;
	Il2CppArraySize *materialSubTexturePairs;
	bool halfStartGate;
	int CourseStartGateBaseId;
};

struct CriAtomExPlayback
{
	uint32_t id;
};

struct AudioPlayback
{
	CriAtomExPlayback criAtomExPlayback;
	bool isError;
	int soundGroup;
};

typedef struct Il2CppReflectionMethod Il2CppReflectionMethod;

typedef void (*Il2CppMethodPointer)();

typedef void *(*InvokerMethod)(Il2CppMethodPointer, const MethodInfo *, void *, void **);

typedef struct Il2CppDelegate
{
	Il2CppObject object;
	/* The compiled code of the target method */
	Il2CppMethodPointer method_ptr;
	/* The invoke code */
	InvokerMethod invoke_impl;
	Il2CppObject *target;
	const MethodInfo *method;

	void *delegate_trampoline;

	intptr_t extraArg;

	/*
	 * If non-NULL, this points to a memory location which stores the address of
	 * the compiled code of the method, or NULL if it is not yet compiled.
	 */
	uint8_t **method_code;
	Il2CppReflectionMethod *method_info;
	Il2CppReflectionMethod *original_method_info;
	Il2CppObject *data;

	bool method_is_virtual;
} Il2CppDelegate;

typedef struct MulticastDelegate : Il2CppDelegate
{
	Il2CppArraySize *delegates;
} MulticastDelegate;

// UnityEngine.Quaternion
struct Quaternion_t
{
public:
	float w;
	float x;
	float y;
	float z;
};

template <typename T>
struct TypedField
{
	FieldInfo *Field;

	constexpr FieldInfo *operator->() const noexcept
	{
		return Field;
	}
};

struct Il2CppClassHead
{
	const void *image;
	void *gc_desc;
	const char *name;
	const char *namespaze;
};

struct Il2CppReflectionType
{
	Il2CppObject object;
	const Il2CppType *type;
};

inline Il2CppAssembly **(*il2cpp_domain_get_assemblies)(const Il2CppDomain *domain, std::size_t *size);
inline const Il2CppClass *(*il2cpp_class_from_name)(const Il2CppImage *image, const char *namespaze, const char *name);
inline MethodInfo *(*il2cpp_class_get_methods)(const Il2CppClass *klass, void **iter);
inline const MethodInfo *(*il2cpp_class_get_method_from_name)(const Il2CppClass *klass, const char *name, int argsCount);
inline MethodInfo *(*il2cpp_method_get_from_reflection)(Il2CppObject *ref);
inline const Il2CppType *(*il2cpp_method_get_param)(const MethodInfo *method, uint32_t index);
inline char *(*il2cpp_type_get_name)(const Il2CppType *type);
inline Il2CppObject *(*il2cpp_object_new)(Il2CppClass *klass);
inline void (*il2cpp_add_internal_call)(const char *name, uintptr_t pointer);
inline Il2CppArraySize *(*il2cpp_array_new)(Il2CppClass *klass, uintptr_t count);
inline const Il2CppType *(*il2cpp_class_get_type)(Il2CppClass *klass);
inline uint32_t (*il2cpp_class_get_type_token)(Il2CppClass *klass);
inline FieldInfo *(*il2cpp_class_get_field_from_name)(Il2CppClass *klass, const char *name);
inline void (*il2cpp_field_get_value)(Il2CppObject *obj, FieldInfo *field, void *value);
inline void (*il2cpp_field_set_value)(Il2CppObject *obj, FieldInfo *field, void *value);
inline void (*il2cpp_field_static_get_value)(FieldInfo *field, void *value);
inline void (*il2cpp_field_static_set_value)(FieldInfo *field, void *value);
inline const Il2CppType *(*il2cpp_field_get_type)(FieldInfo *field);
inline Il2CppObject *(*il2cpp_type_get_object)(const Il2CppType *type);
inline const char *(*il2cpp_image_get_name)(const Il2CppImage *image);
inline bool (*il2cpp_type_is_byref)(const Il2CppType *type);
inline uint32_t (*il2cpp_method_get_flags)(const MethodInfo *mehod, uint32_t *iflags);
inline const Il2CppType *(*il2cpp_method_get_return_type)(const MethodInfo *method);
inline Il2CppClass *(*il2cpp_class_from_type)(const Il2CppType *type);
inline const char *(*il2cpp_class_get_name)(const Il2CppClass *klass);
inline const PropertyInfo *(*il2cpp_class_get_properties)(Il2CppClass *klass, void **iter);
inline bool (*il2cpp_class_is_enum)(const Il2CppClass *klass);
inline FieldInfo *(*il2cpp_class_get_fields)(Il2CppClass *klass, void **iter);
inline const char *(*il2cpp_method_get_name)(const MethodInfo *method);
inline uint32_t (*il2cpp_method_get_param_count)(const MethodInfo *method);
inline const char *(*il2cpp_method_get_param_name)(const MethodInfo *method, uint32_t index);
inline Il2CppClass *(*il2cpp_class_get_parent)(Il2CppClass *klass);
inline Il2CppClass *(*il2cpp_class_get_interfaces)(Il2CppClass *klass, void **iter);
inline const char *(*il2cpp_class_get_namespace)(const Il2CppClass *klass);
inline const Il2CppImage *(*il2cpp_class_get_image)(const Il2CppClass *klass);
inline int (*il2cpp_class_get_flags)(const Il2CppClass *klass);
inline bool (*il2cpp_class_is_valuetype)(const Il2CppClass *klass);
inline uint32_t (*il2cpp_property_get_flags)(PropertyInfo *prop);
inline const MethodInfo *(*il2cpp_property_get_get_method)(const PropertyInfo *prop);
inline const MethodInfo *(*il2cpp_property_get_set_method)(const PropertyInfo *prop);
inline const char *(*il2cpp_property_get_name)(const PropertyInfo *prop);
inline Il2CppClass *(*il2cpp_property_get_parent)(const PropertyInfo *prop);
inline int (*il2cpp_field_get_flags)(FieldInfo *field);
inline const char *(*il2cpp_field_get_name)(FieldInfo *field);
inline Il2CppClass *(*il2cpp_field_get_parent)(FieldInfo *field);
inline size_t (*il2cpp_field_get_offset)(FieldInfo *field);
inline const PropertyInfo *(*il2cpp_class_get_property_from_name)(Il2CppClass *klass, const char *name);
inline void (*il2cpp_runtime_object_init)(Il2CppObject *obj);
inline Il2CppObject *(*il2cpp_value_box)(Il2CppClass *klass, void *data);
inline void *(*il2cpp_object_unbox)(Il2CppObject *obj);
inline Il2CppString *(*il2cpp_string_new_utf16)(const wchar_t *str, unsigned int len);
inline Il2CppString *(*il2cpp_string_new)(const char *str);
inline Il2CppDomain *(*il2cpp_domain_get)();
inline Il2CppAssembly *(*il2cpp_domain_assembly_open)(Il2CppDomain *domain, const char *name);
inline const Il2CppImage *(*il2cpp_assembly_get_image)(const Il2CppAssembly *assembly);
inline void *(*il2cpp_resolve_icall)(const char *name);
inline void *(*il2cpp_thread_attach)(void *domain);
inline void (*il2cpp_thread_detach)(void *thread);
inline bool (*il2cpp_class_is_assignable_from)(void *klass, void *oklass);
inline void (*il2cpp_class_for_each)(void (*klassReportFunc)(Il2CppClass *klass, void *userData), void *userData);
inline void *(*il2cpp_class_get_nested_types)(void *klass, void **iter);
inline uint32_t (*il2cpp_gchandle_new)(void *obj, bool pinned);
inline void (*il2cpp_gchandle_free)(uint32_t gchandle);
inline void *(*il2cpp_gchandle_get_target)(uint32_t gchandle);
inline void (*il2cpp_runtime_class_init)(void *klass);
inline void *(*il2cpp_runtime_invoke)(MethodInfo *method, void *obj, void **params, Il2CppObject **exc);
inline Il2CppChar *(*il2cpp_string_chars)(Il2CppString *str);
inline int (*il2cpp_string_length)(Il2CppString *str);
inline const Il2CppClass *(*il2cpp_image_get_class)(const Il2CppImage *image, size_t index);
inline size_t (*il2cpp_image_get_class_count)(const Il2CppImage *image);
namespace il2cppfunctions
{
	inline HMODULE game_dll;
	void init(HMODULE dll);
	uintptr_t get_method_pointer(const char *assemblyName, const char *namespaze,
								 const char *klassName, const char *name, int argsCount, bool strict);
	const MethodInfo *get_method_internal(const char *assemblyName, const char *namespaze,
								   const char *klassName, const char *name, int argsCount, bool strict);
	std::optional<std::wstring_view> get_string(void *);
	void *create_string(std::wstring_view ws);
	il2cpploopinfo loop_all_methods(std::optional<std::function<void(const std::string &)>>);
	const Il2CppType *get_type_pointer(const char *_dll, const char *_namespace, const char *_class, bool strict);
	const Il2CppClass *get_class_pointer(const char *_dll, const char *_namespace, const char *_class, bool strict);
}