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
	bool load_managed_plugin_impl() override
	{
		return false;
	}
	void apply_font(void *self) override {}
};

monoil2cpp *create_il2cpp_runtime(HMODULE module)
{
	return new il2cpp_impl(module);
}