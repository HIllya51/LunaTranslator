#include "def_il2cpp.hpp"
namespace
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
	void foreach_func(Il2CppClass *klass, void *userData)
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
		AutoThread()
		{
			auto il2cpp_domain = (SafeFptr(il2cpp_domain_get))();
			if (!il2cpp_domain)
				return;
			thread = (SafeFptr(il2cpp_thread_attach))(il2cpp_domain);
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
			info << std::hex << (method->methodPointer - (uintptr_t)il2cppfunctions::game_dll);
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
			ConsoleOutput(s.value().c_str());
			ConsoleOutput(getmethodinfo(ret).c_str());
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
	const Il2CppType *gettypeofklass(const Il2CppClass *klass)
	{
		if (!klass)
			return NULL;
		auto ret = (SafeFptr(il2cpp_class_get_type))(const_cast<Il2CppClass *>(klass));

		return ret;
	}
}
il2cpploopinfo il2cppfunctions::loop_all_methods(std::optional<std::function<void(std::string &)>> show)
{
	auto thread = AutoThread();
	if (!thread.thread)
		return {};
	auto klasses = loopclass();
	il2cpploopinfo hps;
	for (auto klass : klasses)
	{
		auto s = getclassinfo(klass);
		if (!s)
			continue;
		if (show)
			show.value()(s.value());

		void *iter = nullptr;
		while (auto method = SafeFptr(il2cpp_class_get_methods)(klass, &iter))
		{
			if (show)
				show.value()(getmethodinfo(method));
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
		return {{0, 0}};
	return hps;
}
void il2cppfunctions::init(HMODULE game_module)
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
template <typename T, typename F>
T get_pointer_in_class(const char *assemblyName, const char *namespaze,
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
const Il2CppType *il2cppfunctions::get_type_pointer(const char *assemblyName, const char *namespaze,
													const char *klassName, bool strict)
{
	return get_pointer_in_class<const Il2CppType *>(assemblyName, namespaze,
													klassName, strict, gettypeofklass);
}
const Il2CppClass *il2cppfunctions::get_class_pointer(const char *assemblyName, const char *namespaze,
													  const char *klassName, bool strict)
{
	return get_pointer_in_class<const Il2CppClass *>(assemblyName, namespaze,
													 klassName, strict, [](const Il2CppClass *klass)
													 { return klass; });
}
uintptr_t il2cppfunctions::get_method_pointer(const char *assemblyName, const char *namespaze,
											  const char *klassName, const char *name, int argsCount, bool strict)
{
	return get_pointer_in_class<uintptr_t>(assemblyName, namespaze,
										   klassName, strict, [&](const Il2CppClass *klass)
										   { return getmethodofklass(klass, name, argsCount); });
}
const MethodInfo *il2cppfunctions::get_method_internal(const char *assemblyName, const char *namespaze,
												 const char *klassName, const char *name, int argsCount, bool strict)
{
	return get_pointer_in_class<const MethodInfo *>(assemblyName, namespaze,
											  klassName, strict, [&](const Il2CppClass *klass)
											  { return getmethodofklass_1(klass, name, argsCount); });
}

std::optional<std::wstring_view> il2cppfunctions::get_string(void *ptr)
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
void *il2cppfunctions::create_string(std::wstring_view ws)
{
	return (SafeFptr(il2cpp_string_new_utf16))(ws.data(), ws.length());
}