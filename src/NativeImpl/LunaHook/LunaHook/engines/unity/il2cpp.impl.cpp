#include "il2cpp.def.hpp"
#include "monoil2cpp.h"

struct il2cpp_impl : monoil2cpp
{
	const Il2CppClass *get_il2cppclass1(const char *assemblyName, const char *namespaze,
										const char *klassName, bool strict)
	{
		auto il2cpp_domain = (SafeFptr(il2cpp_domain_get))();
		if (!il2cpp_domain)
			return NULL;
		do
		{
			auto assembly = (SafeFptr(il2cpp_domain_assembly_open))(il2cpp_domain, assemblyName);
			if (!assembly)
				break;
			auto image = (SafeFptr(il2cpp_assembly_get_image))(assembly);
			if (!image)
				break;
			auto klass = (SafeFptr(il2cpp_class_from_name))(image, namespaze, klassName);
			if (klass)
				return klass;
		} while (0);
		if (strict)
			return NULL;

		int _ = 0;
		size_t sz = 0;
		auto assemblies = (SafeFptr(il2cpp_domain_get_assemblies))(il2cpp_domain, &sz);
		if (assemblies)
			for (auto i = 0; i < sz; i++, assemblies++)
			{
				auto image = (SafeFptr(il2cpp_assembly_get_image))(*assemblies);
				if (!image)
					continue;
				auto cls = (SafeFptr(il2cpp_class_from_name))(image, namespaze, klassName);
				if (cls)
					return cls;
			}
		return NULL;
	}
	static void foreach_func(Il2CppClass *klass, void *userData)
	{
		auto st = (std::vector<Il2CppClass *> *)userData;
		st->push_back(klass);
	}
	std::vector<const Il2CppClass *> loopclass()
	{
		std::vector<const Il2CppClass *> klasses;
		(SafeFptr(il2cpp_class_for_each))(foreach_func, &klasses);
		if (klasses.size())
			return klasses;

		auto domain = (SafeFptr(il2cpp_domain_get))();
		if (!domain)
			return klasses;
		size_t assemblyCount = 0;
		Il2CppAssembly **assemblies = SafeFptr(il2cpp_domain_get_assemblies)(domain, &assemblyCount);
		for (size_t i = 0; i < assemblyCount; i++)
		{
			Il2CppAssembly *assembly = assemblies[i];
			auto image = SafeFptr(il2cpp_assembly_get_image)(assembly);
			if (!image)
				continue;
			auto classcount = SafeFptr(il2cpp_image_get_class_count)(image);
			for (auto ci = 0; ci < classcount; ci++)
			{
				auto klass = SafeFptr(il2cpp_image_get_class)(image, ci);
				if (!klass)
					continue;
				klasses.push_back(klass);
			}
		}
		return klasses;
	}
	std::vector<const Il2CppClass *> get_il2cppclass2(const char *namespaze, const char *klassName)
	{
		std::vector<const Il2CppClass *> maybes;
		auto klasses = loopclass();
		for (auto klass : klasses)
		{
			auto classname = (SafeFptr(il2cpp_class_get_name))(klass);
			if (!classname)
				continue;
			if (strcmp(classname, klassName) != 0)
				continue;
			maybes.push_back(klass);
			auto namespacename = (SafeFptr(il2cpp_class_get_namespace))(klass);
			if (!namespacename)
				continue;
			if (strlen(namespaze) && (strcmp(namespacename, namespaze) == 0))
			{
				return {klass};
			}
		}
		return maybes;
	}
	struct AutoThread
	{
		void *thread = NULL;
		static void *attach_thread()
		{
			auto d = (SafeFptr(il2cpp_domain_get))();
			if (!d)
				return nullptr;
			return (SafeFptr(il2cpp_thread_attach))(d);
		}
		AutoThread()
		{
			thread = attach_thread();
		}
		~AutoThread()
		{
			if (!thread)
				return;
			(SafeFptr(il2cpp_thread_detach))(thread);
		}
	};
	std::optional<std::string> getclassinfo(const Il2CppClass *klass)
	{
		auto image = (SafeFptr(il2cpp_class_get_image))(klass);
		if (!image)
			return {};
		auto imagen = (SafeFptr(il2cpp_image_get_name))(image);
		auto names = (SafeFptr(il2cpp_class_get_namespace))(klass);
		auto classname = (SafeFptr(il2cpp_class_get_name))(klass);
		if (imagen && names && classname)
		{
			std::string _ = imagen;
			_ += ":";
			_ += names;
			_ += ":";
			_ += classname;
			return _;
		}
		return {};
	}
	std::string getmethodinfo(const MethodInfo *method)
	{
		const char *methodName = SafeFptr(il2cpp_method_get_name)(method);
		std::stringstream info;
		if (method->methodPointer)
			info << std::hex << (method->methodPointer - (uintptr_t)game_dll);
		else
			info << "??";

		if (methodName) // il2cpp似乎没办法从method查询name
			info << " " << methodName;
		info << " (";
		for (uint32_t i = 0; i < SafeFptr(il2cpp_method_get_param_count)(method); i++)
		{
			if (i != 0)
				info << ", ";
			if (auto rt = SafeFptr(il2cpp_method_get_param)(method, i))
				if (auto tp = SafeFptr(il2cpp_type_get_name)(rt))
					info << tp;
		}
		info << ")";
		if (auto rt = SafeFptr(il2cpp_method_get_return_type)(method))
			if (auto returntype = SafeFptr(il2cpp_type_get_name)(rt))
			{
				info << " -> " << returntype;
			}
		return info.str();
	}
	const MethodInfo *getmethodofklass_1(const Il2CppClass *klass, const char *name, int argsCount)
	{
		if (!klass)
			return NULL;
		auto ret = (SafeFptr(il2cpp_class_get_method_from_name))(klass, name, argsCount);

		if (!ret)
			return NULL;
		if (auto s = getclassinfo(klass))
		{
			Msg::Log(s.value().c_str());
			Msg::Log(getmethodinfo(ret).c_str());
		}
		return ret;
	}
	uintptr_t getmethodofklass(const Il2CppClass *klass, const char *name, int argsCount)
	{
		auto ret = getmethodofklass_1(klass, name, argsCount);
		if (!ret)
			return NULL;
		return ret->methodPointer;
	}
	static const Il2CppType *gettypeofklass(const Il2CppClass *klass)
	{
		if (!klass)
			return NULL;
		auto ret = (SafeFptr(il2cpp_class_get_type))(const_cast<Il2CppClass *>(klass));

		return ret;
	}
	template <typename F>
	std::invoke_result_t<F, const Il2CppClass *> get_pointer_in_class(const char *assemblyName, const char *namespaze,
																	  const char *klassName, bool strict, F GetPointer)
	{
		auto thread = AutoThread();
		if (!thread.thread)
			return NULL;

		auto klass = get_il2cppclass1(assemblyName, namespaze, klassName, strict); // 正向查询，assemblyName可以为空
		if (klass)
			return GetPointer(klass);
		if (strict)
			return NULL;
		auto klasses = get_il2cppclass2(namespaze, klassName); // 反向查询，namespace可以为空
		for (auto klass : klasses)
		{
			auto method = GetPointer(klass);
			if (method)
				return method;
		}
		return NULL;
	}
	HMODULE game_dll;
	il2cpp_impl(HMODULE game_module)
	{
		game_dll = game_module;
		RESOLVE_IMPORT(il2cpp_type_get_name);
		RESOLVE_IMPORT(il2cpp_method_get_name);
		RESOLVE_IMPORT(il2cpp_method_get_param_count);
		RESOLVE_IMPORT(il2cpp_string_new_utf16);
		RESOLVE_IMPORT(il2cpp_string_chars);
		RESOLVE_IMPORT(il2cpp_string_length);
		RESOLVE_IMPORT(il2cpp_image_get_name);
		RESOLVE_IMPORT(il2cpp_class_get_image);
		RESOLVE_IMPORT(il2cpp_string_new_utf16);
		RESOLVE_IMPORT(il2cpp_string_new);
		RESOLVE_IMPORT(il2cpp_domain_get);
		RESOLVE_IMPORT(il2cpp_domain_assembly_open);
		RESOLVE_IMPORT(il2cpp_assembly_get_image);
		RESOLVE_IMPORT(il2cpp_image_get_class);
		RESOLVE_IMPORT(il2cpp_image_get_class_count);
		RESOLVE_IMPORT(il2cpp_class_from_name);
		RESOLVE_IMPORT(il2cpp_class_get_methods);
		RESOLVE_IMPORT(il2cpp_class_get_method_from_name);
		RESOLVE_IMPORT(il2cpp_method_get_param);
		RESOLVE_IMPORT(il2cpp_object_new);
		RESOLVE_IMPORT(il2cpp_resolve_icall);
		RESOLVE_IMPORT(il2cpp_array_new);
		RESOLVE_IMPORT(il2cpp_thread_attach);
		RESOLVE_IMPORT(il2cpp_thread_detach);
		RESOLVE_IMPORT(il2cpp_class_get_field_from_name);
		RESOLVE_IMPORT(il2cpp_field_get_value);
		RESOLVE_IMPORT(il2cpp_field_set_value);
		RESOLVE_IMPORT(il2cpp_field_static_set_value);
		RESOLVE_IMPORT(il2cpp_field_get_offset);
		RESOLVE_IMPORT(il2cpp_runtime_object_init);
		RESOLVE_IMPORT(il2cpp_class_get_parent);
		RESOLVE_IMPORT(il2cpp_class_is_assignable_from);
		RESOLVE_IMPORT(il2cpp_class_for_each);
		RESOLVE_IMPORT(il2cpp_class_get_nested_types);
		RESOLVE_IMPORT(il2cpp_class_get_type);
		RESOLVE_IMPORT(il2cpp_type_get_object);
		RESOLVE_IMPORT(il2cpp_gchandle_new);
		RESOLVE_IMPORT(il2cpp_gchandle_free);
		RESOLVE_IMPORT(il2cpp_gchandle_get_target);
		RESOLVE_IMPORT(il2cpp_class_from_type);
		RESOLVE_IMPORT(il2cpp_runtime_class_init);
		RESOLVE_IMPORT(il2cpp_runtime_invoke);
		RESOLVE_IMPORT(il2cpp_class_get_name);
		RESOLVE_IMPORT(il2cpp_class_get_namespace);
		RESOLVE_IMPORT(il2cpp_method_get_return_type);
		RESOLVE_IMPORT(il2cpp_domain_get_assemblies);
	}
	void *get_method_pointer(const char *assemblyName, const char *namespaze, const char *klassName, const char *name, int argsCount, bool strict) override
	{
		return (void *)get_pointer_in_class(assemblyName, namespaze, klassName, strict, [&](const Il2CppClass *klass)
											{ return getmethodofklass(klass, name, argsCount); });
	}
	void *get_method_internal(const char *assemblyName, const char *namespaze, const char *klassName, const char *name, int argsCount, bool strict)
	{
		return (void *)get_pointer_in_class(assemblyName, namespaze, klassName, strict, [&](const Il2CppClass *klass)
											{ return getmethodofklass_1(klass, name, argsCount); });
	}
	void *get_type_pointer(const char *assemblyName, const char *namespaze, const char *klassName, bool strict) override
	{
		return (void *)get_pointer_in_class(assemblyName, namespaze, klassName, strict, gettypeofklass);
	}
	void *get_class_pointer(const char *assemblyName, const char *namespaze, const char *klassName, bool strict) override
	{
		return (void *)get_pointer_in_class(assemblyName, namespaze, klassName, strict, [](const Il2CppClass *klass)
											{ return klass; });
	}
	std::optional<std::wstring_view> get_string(void *ptr) override
	{
		auto str = reinterpret_cast<Il2CppString *>(ptr);
		if (!str)
			return {};
		auto wc = (SafeFptr(il2cpp_string_chars))(str);
		auto len = (SafeFptr(il2cpp_string_length))(str);
		if (!(wc && len))
			return {};
		return std::wstring_view(wc, len);
	}
	void *create_string(std::wstring_view ws) override
	{
		return (SafeFptr(il2cpp_string_new_utf16))(ws.data(), ws.length());
	}
	std::variant<monoloopinfo, il2cpploopinfo> loop_all_methods(std::function<void(const std::string &)> show) override
	{
		auto thread = AutoThread();
		if (!thread.thread)
			return il2cpploopinfo{};
		auto klasses = loopclass();
		il2cpploopinfo hps;
		for (auto klass : klasses)
		{
			auto s = getclassinfo(klass);
			if (!s)
				continue;
			if (show)
				show(s.value());

			void *iter = nullptr;
			while (auto method = SafeFptr(il2cpp_class_get_methods)(klass, &iter))
			{
				if (show)
					show(getmethodinfo(method));
				else
				{
					if (method->methodPointer)
					{
						for (uint32_t i = 0; i < SafeFptr(il2cpp_method_get_param_count)(method); i++)
						{
							if (auto rt = SafeFptr(il2cpp_method_get_param)(method, i))
								if (auto tp = SafeFptr(il2cpp_type_get_name)(rt))
									if (strcmp(tp, "System.String") == 0)
									{
										hps.push_back({i + 1, method->methodPointer});
										break;
									}
						}
					}
				}
			}
		}
		if (show && klasses.size())
			return il2cpploopinfo{{0, 0}};
		return hps;
	}
	void *invoke(void *method, void *obj, void **params, void **exc_out)
	{
		if (!method)
			return nullptr;
		AutoThread::attach_thread();
		void *exc = nullptr;
		void *ret = nullptr;
		ret = (SafeFptr(il2cpp_runtime_invoke))((MethodInfo *)method, obj, params, (Il2CppObject **)&exc);
		if (exc_out)
			*exc_out = exc;
		return ret;
	}
	void log_managed_exception(void *exc)
	{
		if (!exc)
			return;
		const char *name = nullptr;
		auto klass = ((Il2CppObject *)exc)->klass;
		if (klass)
			name = (SafeFptr(il2cpp_class_get_name))(klass);
		if (name)
			Msg::Log(name);
		void *toStringM = get_method_internal("mscorlib", "System", "Exception", "ToString", 0, false);
		if (!toStringM)
			return;
		void *ex2 = nullptr;
		void *ret = invoke(toStringM, exc, nullptr, &ex2);
		if (!ret)
			return;
		if (auto sw = commonsolvemonostring((uintptr_t)ret))
			Msg::Log(WideStringToString(sw.value()).c_str());
	}
	void *m_font = nullptr;
	void *m_dynFont = nullptr;
	void *m_setFont = nullptr;
	void *m_getFont = nullptr;
	void *m_loadFontAsset = nullptr;
	void *m_setAllDirty = nullptr;
	void *m_hasChar = nullptr;
	void *m_getFallbackTable = nullptr;
	void *m_setFallbackTable = nullptr;
	FieldInfo *m_fFontAsset = nullptr;
	FieldInfo *m_fHavePropsChanged = nullptr;
	const Il2CppClass *m_tTMP_Text = nullptr;
	const Il2CppClass *m_tFontAsset = nullptr;
	const Il2CppClass *m_tFontList = nullptr;

	static std::wstring pick_bundle(std::wstring_view ver)
	{
		int n = 0;
		bool any = false;
		for (wchar_t c : ver)
		{
			if (c >= L'0' && c <= L'9')
			{
				n = n * 10 + (c - L'0');
				any = true;
			}
			else if (any)
				break;
		}
		if (n == 6)
			return L"arialuni_sdf_u6000";
		if (n >= 2022)
			return L"arialuni_sdf_u2022";
		if (n == 2020 || n == 2021)
			return L"arialuni_sdf_u2021";
		if (n == 2019)
			return L"arialuni_sdf_u2019";
		if (n == 2018)
			return L"arialuni_sdf_u2018";
		return L"arialuni_sdf-u55to2017";
	}

	const MethodInfo *find_method_in_hierarchy(const Il2CppClass *klass, const char *name, int argsCount)
	{
		const Il2CppClass *cur = klass;
		while (cur)
		{
			if (auto m = (SafeFptr(il2cpp_class_get_method_from_name))(cur, name, argsCount))
				return m;
			cur = il2cpp_class_get_parent ? (SafeFptr(il2cpp_class_get_parent))(const_cast<Il2CppClass *>(cur)) : cur->parent;
		}
		return nullptr;
	}

	void add_to_font_list(void *listObj, void *fontObj)
	{
		if (!listObj || !fontObj)
			return;
		auto listKlass = ((Il2CppObject *)listObj)->klass;
		if (!listKlass)
			return;
		if (!m_tFontList)
			m_tFontList = listKlass;
		auto mContains = (void *)getmethodofklass_1(listKlass, "Contains", 1);
		auto mAdd = (void *)getmethodofklass_1(listKlass, "Add", 1);
		if (!mAdd)
			return;
		void *exc = nullptr;
		if (mContains)
		{
			void *args[1] = {fontObj};
			void *res = invoke(mContains, listObj, args, &exc);
			if (!exc && res && *(bool *)((uintptr_t)res + sizeof(Il2CppObject)))
				return;
		}
		void *args[1] = {fontObj};
		invoke(mAdd, listObj, args, &exc);
	}

	void attach_fallbacks_to_font(void *fontObj)
	{
		if (!fontObj || !m_getFallbackTable)
			return;
		void *exc = nullptr;
		void *fbList = invoke(m_getFallbackTable, fontObj, nullptr, &exc);
		if ((exc || !fbList) && m_tFontList && m_setFallbackTable)
		{
			fbList = (SafeFptr(il2cpp_object_new))(const_cast<Il2CppClass *>(m_tFontList));
			if (fbList)
			{
				(SafeFptr(il2cpp_runtime_object_init))((Il2CppObject *)fbList);
				void *sArgs[1] = {fbList};
				invoke(m_setFallbackTable, fontObj, sArgs, &exc);
			}
		}
		if (fbList)
		{
			if (m_dynFont && m_dynFont != fontObj)
				add_to_font_list(fbList, m_dynFont);
			if (m_font && m_font != fontObj && m_font != m_dynFont)
				add_to_font_list(fbList, m_font);
		}
	}

	bool has_char_il2cpp(void *fontAsset, wchar_t ch)
	{
		if (!fontAsset || !m_hasChar)
			return true;
		void *args[1] = {&ch};
		void *exc = nullptr;
		void *res = invoke(m_hasChar, fontAsset, args, &exc);
		if (exc || !res)
			return true;
		return *(bool *)((uintptr_t)res + sizeof(Il2CppObject));
	}

	void *invoke_create_font_asset(void *osFont)
	{
		if (!osFont || !m_tFontAsset)
			return nullptr;
		void *iter = nullptr;
		const MethodInfo *m1 = nullptr;
		const MethodInfo *m8 = nullptr;
		const MethodInfo *m7 = nullptr;
		while (auto m = (SafeFptr(il2cpp_class_get_methods))(const_cast<Il2CppClass *>(m_tFontAsset), &iter))
		{
			auto mname = (SafeFptr(il2cpp_method_get_name))(m);
			if (!mname || strcmp(mname, "CreateFontAsset") != 0)
				continue;
			uint32_t pc = (SafeFptr(il2cpp_method_get_param_count))(m);
			auto p0 = (SafeFptr(il2cpp_method_get_param))(m, 0);
			auto p0n = p0 ? (SafeFptr(il2cpp_type_get_name))(p0) : nullptr;
			if (!p0n || strstr(p0n, "Font") == nullptr)
				continue;
			if (pc == 1)
				m1 = m;
			else if (pc == 8)
				m8 = m;
			else if (pc == 7)
				m7 = m;
		}
		void *exc = nullptr;
		if (m1)
		{
			void *args[1] = {osFont};
			void *fa = invoke((void *)m1, nullptr, args, &exc);
			if (!exc && fa)
				return fa;
		}
		int32_t samplingPointSize = 90;
		int32_t atlasPadding = 9;
		int32_t renderMode = 4165; // GlyphRenderMode.SDFAA
		int32_t atlasWidth = 1024;
		int32_t atlasHeight = 1024;
		int32_t atlasPopulationMode = 1; // AtlasPopulationMode.Dynamic
		bool enableMultiAtlas = true;
		if (m8)
		{
			void *args[8] = {osFont, &samplingPointSize, &atlasPadding, &renderMode, &atlasWidth, &atlasHeight, &atlasPopulationMode, &enableMultiAtlas};
			exc = nullptr;
			void *fa = invoke((void *)m8, nullptr, args, &exc);
			if (!exc && fa)
				return fa;
		}
		if (m7)
		{
			void *args[7] = {osFont, &samplingPointSize, &atlasPadding, &renderMode, &atlasWidth, &atlasHeight, &atlasPopulationMode};
			exc = nullptr;
			void *fa = invoke((void *)m7, nullptr, args, &exc);
			if (!exc && fa)
				return fa;
		}
		return nullptr;
	}

	bool load_managed_plugin_impl() override
	{
		AutoThread::attach_thread();
		m_tTMP_Text = (const Il2CppClass *)get_class_pointer("Unity.TextMeshPro", "TMPro", "TMP_Text", false);
		m_tFontAsset = (const Il2CppClass *)get_class_pointer("Unity.TextMeshPro", "TMPro", "TMP_FontAsset", false);
		if (m_tTMP_Text)
		{
			m_setFont = (void *)find_method_in_hierarchy(m_tTMP_Text, "set_font", 1);
			m_getFont = (void *)find_method_in_hierarchy(m_tTMP_Text, "get_font", 0);
			m_loadFontAsset = (void *)find_method_in_hierarchy(m_tTMP_Text, "LoadFontAsset", 0);
			m_setAllDirty = (void *)find_method_in_hierarchy(m_tTMP_Text, "SetAllDirty", 0);
			m_fFontAsset = (SafeFptr(il2cpp_class_get_field_from_name))(const_cast<Il2CppClass *>(m_tTMP_Text), "m_fontAsset");
			m_fHavePropsChanged = (SafeFptr(il2cpp_class_get_field_from_name))(const_cast<Il2CppClass *>(m_tTMP_Text), "m_havePropertiesChanged");
		}
		if (m_tFontAsset)
		{
			m_hasChar = (void *)getmethodofklass_1(m_tFontAsset, "HasCharacter", 1);
			m_getFallbackTable = (void *)getmethodofklass_1(m_tFontAsset, "get_fallbackFontAssetTable", 0);
			m_setFallbackTable = (void *)getmethodofklass_1(m_tFontAsset, "set_fallbackFontAssetTable", 1);
			if (m_getFallbackTable)
			{
				if (auto retType = (SafeFptr(il2cpp_method_get_return_type))((const MethodInfo *)m_getFallbackTable))
					m_tFontList = (SafeFptr(il2cpp_class_from_type))(retType);
			}
		}

		using fn_DontDestroyOnLoad = void (*)(void *);
		auto icall_dontDestroy = (fn_DontDestroyOnLoad)(SafeFptr(il2cpp_resolve_icall))("UnityEngine.Object::DontDestroyOnLoad");

		// 1. Load bundle TMP_FontAsset via icalls if unityfontdir is available
		if (commonsharedmem && commonsharedmem->unityfontdir[0] && m_tFontAsset)
		{
			std::wstring ver;
			using fn_get_unityVersion = Il2CppString *(*)();
			if (auto icall_ver = (fn_get_unityVersion)(SafeFptr(il2cpp_resolve_icall))("UnityEngine.Application::get_unityVersion"))
			{
				if (auto verObj = icall_ver())
					if (auto sv = get_string(verObj))
						ver = sv.value();
			}
			std::filesystem::path bundlePath = std::filesystem::path(commonsharedmem->unityfontdir) / pick_bundle(ver);
			if (std::filesystem::exists(bundlePath))
			{
				using fn_LoadFromFile_Internal = void *(*)(void *, uint32_t, uint64_t);
				using fn_LoadAssetWithSubAssets_Internal = Il2CppArraySize *(*)(void *, void *, void *);
				auto icall_loadFromFile = (fn_LoadFromFile_Internal)(SafeFptr(il2cpp_resolve_icall))("UnityEngine.AssetBundle::LoadFromFile_Internal");
				auto icall_loadAssets = (fn_LoadAssetWithSubAssets_Internal)(SafeFptr(il2cpp_resolve_icall))("UnityEngine.AssetBundle::LoadAssetWithSubAssets_Internal");
				if (icall_loadFromFile && icall_loadAssets)
				{
					void *pathStr = create_string(bundlePath.wstring());
					void *ab = icall_loadFromFile(pathStr, 0, 0);
					if (ab)
					{
						(SafeFptr(il2cpp_gchandle_new))(ab, true);
						if (icall_dontDestroy)
							icall_dontDestroy(ab);
						auto tObject = (const Il2CppClass *)get_class_pointer("UnityEngine.CoreModule", "UnityEngine", "Object", false);
						const Il2CppClass *filterKlass = m_tFontAsset ? m_tFontAsset : tObject;
						void *typeObj = filterKlass ? (SafeFptr(il2cpp_type_get_object))((SafeFptr(il2cpp_class_get_type))(const_cast<Il2CppClass *>(filterKlass))) : nullptr;
						if (typeObj)
						{
							Il2CppArraySize *arr = icall_loadAssets(ab, create_string(L""), typeObj);
							if (arr)
							{
								for (uintptr_t i = 0; i < arr->max_length && i < 256; i++)
								{
									void *elem = arr->vector[i];
									if (!elem)
										continue;
									auto k = ((Il2CppObject *)elem)->klass;
									if (k && (k == m_tFontAsset || (SafeFptr(il2cpp_class_is_assignable_from))(const_cast<Il2CppClass *>(m_tFontAsset), const_cast<Il2CppClass *>(k))))
									{
										m_font = elem;
										(SafeFptr(il2cpp_gchandle_new))(m_font, true);
										if (icall_dontDestroy)
											icall_dontDestroy(m_font);
										break;
									}
								}
							}
						}
					}
				}
			}
		}

		// Ensure ShaderUtilities.k_ShaderRef_MobileSDF is populated before CreateFontAsset
		if (m_tFontAsset)
		{
			auto tShaderUtil = (const Il2CppClass *)get_class_pointer("Unity.TextMeshPro", "TMPro", "ShaderUtilities", false);
			if (tShaderUtil)
			{
				(SafeFptr(il2cpp_runtime_class_init))(const_cast<Il2CppClass *>(tShaderUtil));
				void *curShader = nullptr;
				if (auto mGetShader = (void *)getmethodofklass_1(tShaderUtil, "get_ShaderRef_MobileSDF", 0))
				{
					void *exc = nullptr;
					curShader = invoke(mGetShader, nullptr, nullptr, &exc);
				}
				if (!curShader)
				{
					void *donorFont = m_font;
					if (!donorFont)
					{
						if (auto mDefFont = get_method_internal("Unity.TextMeshPro", "TMPro", "TMP_Settings", "get_defaultFontAsset", 0, false))
						{
							void *exc = nullptr;
							donorFont = invoke(mDefFont, nullptr, nullptr, &exc);
						}
					}
					if (donorFont)
					{
						FieldInfo *fMat = (SafeFptr(il2cpp_class_get_field_from_name))(const_cast<Il2CppClass *>(m_tFontAsset), "material");
						if (!fMat)
							fMat = (SafeFptr(il2cpp_class_get_field_from_name))(const_cast<Il2CppClass *>(m_tFontAsset), "m_Material");
						void *matObj = nullptr;
						if (fMat)
							(SafeFptr(il2cpp_field_get_value))((Il2CppObject *)donorFont, fMat, &matObj);
						if (matObj)
						{
							using fn_get_shader = void *(*)(void *);
							if (auto icall_getShader = (fn_get_shader)(SafeFptr(il2cpp_resolve_icall))("UnityEngine.Material::get_shader"))
							{
								void *sh = icall_getShader(matObj);
								if (sh)
								{
									if (FieldInfo *fShaderRef = (SafeFptr(il2cpp_class_get_field_from_name))(const_cast<Il2CppClass *>(tShaderUtil), "k_ShaderRef_MobileSDF"))
										(SafeFptr(il2cpp_field_static_set_value))(fShaderRef, &sh);
								}
							}
						}
					}
				}
			}
		}

		// 2. Create dynamic OS TMP_FontAsset via Font icalls + CreateFontAsset(8 args / 1 arg)
		if (m_tFontAsset)
		{
			auto tUIFont = (const Il2CppClass *)get_class_pointer("UnityEngine.TextRenderingModule", "UnityEngine", "Font", false);
			if (tUIFont)
			{
				using fn_Internal_CreateFontFromPath = void (*)(void *, void *);
				using fn_Internal_CreateDynamicFont = void (*)(void *, void *, int32_t);
				auto icall_fromPath = (fn_Internal_CreateFontFromPath)(SafeFptr(il2cpp_resolve_icall))("UnityEngine.Font::Internal_CreateFontFromPath");
				auto icall_dynFont = (fn_Internal_CreateDynamicFont)(SafeFptr(il2cpp_resolve_icall))("UnityEngine.Font::Internal_CreateDynamicFont");

				if (icall_dynFont)
				{
					auto tString = (const Il2CppClass *)get_class_pointer("mscorlib", "System", "String", false);
					if (tString)
					{
						Il2CppArraySize *namesArr = (SafeFptr(il2cpp_array_new))(const_cast<Il2CppClass *>(tString), 3);
						if (namesArr)
						{
							const wchar_t *fname = (commonsharedmem && commonsharedmem->fontFamily[0]) ? commonsharedmem->fontFamily : L"Arial";
							namesArr->vector[0] = create_string(fname);
							namesArr->vector[1] = create_string(L"Arial");
							namesArr->vector[2] = create_string(L"Tahoma");
							void *fObj = (SafeFptr(il2cpp_object_new))(const_cast<Il2CppClass *>(tUIFont));
							if (fObj)
							{
								icall_dynFont(fObj, namesArr, 32);
								(SafeFptr(il2cpp_gchandle_new))(fObj, true);
								if (icall_dontDestroy)
									icall_dontDestroy(fObj);
								m_dynFont = invoke_create_font_asset(fObj);
							}
						}
					}
				}
				if (!m_dynFont && icall_fromPath)
				{
					const wchar_t *ttfCandidates[] = {
						L"C:\\Windows\\Fonts\\arial.ttf",
						L"C:\\Windows\\Fonts\\tahoma.ttf",
						L"C:\\Windows\\Fonts\\segoeui.ttf",
					};
					for (auto ttf : ttfCandidates)
					{
						if (!std::filesystem::exists(ttf))
							continue;
						void *fObj = (SafeFptr(il2cpp_object_new))(const_cast<Il2CppClass *>(tUIFont));
						if (!fObj)
							break;
						icall_fromPath(fObj, create_string(ttf));
						(SafeFptr(il2cpp_gchandle_new))(fObj, true);
						if (icall_dontDestroy)
							icall_dontDestroy(fObj);
						m_dynFont = invoke_create_font_asset(fObj);
						if (m_dynFont)
							break;
					}
				}
				if (m_dynFont)
				{
					(SafeFptr(il2cpp_gchandle_new))(m_dynFont, true);
					if (icall_dontDestroy)
						icall_dontDestroy(m_dynFont);
				}
			}
		}

		if (!m_font && m_dynFont)
			m_font = m_dynFont;

		if (auto mGetSettingsFb = get_method_internal("Unity.TextMeshPro", "TMPro", "TMP_Settings", "get_fallbackFontAssets", 0, false))
		{
			void *exc = nullptr;
			void *fbList = invoke(mGetSettingsFb, nullptr, nullptr, &exc);
			if (!exc && fbList)
			{
				if (m_dynFont)
					add_to_font_list(fbList, m_dynFont);
				if (m_font && m_font != m_dynFont)
					add_to_font_list(fbList, m_font);
			}
		}

		if (m_font && m_dynFont && m_font != m_dynFont)
			attach_fallbacks_to_font(m_font);

		if (auto mDefFont = get_method_internal("Unity.TextMeshPro", "TMPro", "TMP_Settings", "get_defaultFontAsset", 0, false))
		{
			void *exc = nullptr;
			if (void *defFont = invoke(mDefFont, nullptr, nullptr, &exc))
				attach_fallbacks_to_font(defFont);
		}

		Msg::Log("IL2CPP FontLoader: bundleFont=%p dynFont=%p", m_font, m_dynFont);
		return m_font != nullptr || m_dynFont != nullptr;
	}

	void apply_font(void *self) override
	{
		if (!self || (!m_font && !m_dynFont))
			return;
		void *target = m_font ? m_font : m_dynFont;

		void *exc = nullptr;
		void *curFont = nullptr;
		if (m_getFont)
			curFont = invoke(m_getFont, self, nullptr, &exc);
		else if (m_fFontAsset)
			(SafeFptr(il2cpp_field_get_value))((Il2CppObject *)self, m_fFontAsset, &curFont);

		if (curFont && curFont != m_font && curFont != m_dynFont)
			attach_fallbacks_to_font(curFont);

		if (curFont == target)
			return;

		if (m_setFont)
		{
			void *args[1] = {target};
			invoke(m_setFont, self, args, &exc);
		}
		else if (m_fFontAsset)
		{
			(SafeFptr(il2cpp_field_set_value))((Il2CppObject *)self, m_fFontAsset, target);
			if (m_fHavePropsChanged)
			{
				bool bTrue = true;
				(SafeFptr(il2cpp_field_set_value))((Il2CppObject *)self, m_fHavePropsChanged, &bTrue);
			}
			auto selfKlass = ((Il2CppObject *)self)->klass;
			const MethodInfo *updM = selfKlass ? find_method_in_hierarchy(selfKlass, "UpdateFontAsset", 0) : nullptr;
			if (!updM)
				updM = selfKlass ? find_method_in_hierarchy(selfKlass, "LoadFontAsset", 0) : (const MethodInfo *)m_loadFontAsset;
			if (updM)
				invoke((void *)updM, self, nullptr, &exc);
			if (m_setAllDirty)
				invoke(m_setAllDirty, self, nullptr, &exc);
		}
	}
};

monoil2cpp *create_il2cpp_runtime(HMODULE module)
{
	return new il2cpp_impl(module);
}