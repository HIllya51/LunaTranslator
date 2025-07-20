#include "def_mono.hpp"
namespace
{

    void MonoCallBack(void *assembly, void *userData)
    {
        auto Image = (SafeFptr(mono_assembly_get_image))((MonoAssembly *)assembly);
        if (!Image)
            return;
        auto st = reinterpret_cast<std::vector<MonoImage *> *>(userData);
        st->push_back(Image);
    }
    std::vector<MonoImage *> mono_loop_images()
    {
        std::vector<MonoImage *> images;
        (SafeFptr(mono_assembly_foreach))(MonoCallBack, (void *)&images);
        return images;
    }
    MonoClass *mono_findklassby_ass_namespace(std::vector<MonoImage *> &images, const char *_dll, const char *_namespace, const char *_class, bool strict)
    {
        MonoClass *maybe = NULL;

        for (auto Image : images)
        {
            auto tmp = (SafeFptr(mono_class_from_name))(Image, _namespace, _class);
            if (!tmp)
                continue;

            maybe = tmp;
            auto name = (SafeFptr(mono_image_get_name))(Image);
            if (!name)
                continue;
            if (strcmp(_dll, name) == 0)
                return tmp;
        }
        if (strict)
            return NULL;
        return maybe;
    }
    std::vector<MonoClass *> loopclass(std::vector<MonoImage *> &images)
    {
        std::vector<MonoClass *> maybes;
        for (auto image : images)
        {
            auto _1 = (SafeFptr(mono_image_get_table_info))(image, MONO_TABLE_TYPEDEF);
            if (!_1)
                continue;
            auto tdefcount = (SafeFptr(mono_table_info_get_rows))(_1);
            if (!tdefcount)
                continue;
            for (int i = 0; i < tdefcount; i++)
            {
                auto klass = (MonoClass *)(SafeFptr(mono_class_get))(image, MONO_TOKEN_TYPE_DEF | i + 1);
                if (!klass)
                    continue;
                maybes.push_back(klass);
            }
        }
        return maybes;
    }
    std::vector<MonoClass *> mono_findklassby_class(std::vector<MonoImage *> &images, const char *_namespace, const char *_class)
    {
        std::vector<MonoClass *> maybes;
        for (auto klass : loopclass(images))
        {
            auto name = (SafeFptr(mono_class_get_name))(klass);
            if (!name)
                continue;
            if (strcmp(name, _class) != 0)
                continue;
            maybes.push_back(klass);
            auto namespacename = (SafeFptr(mono_class_get_namespace))(klass);
            if (!namespacename)
                continue;
            if (strlen(_namespace) && (strcmp(namespacename, _namespace) == 0))
            {
                return {klass};
            }
        }
        return maybes;
    }
    std::optional<std::string> getclassinfo(MonoClass *klass)
    {
        auto image = (SafeFptr(mono_class_get_image))(klass);
        if (!image)
            return {};
        auto imagen = (SafeFptr(mono_image_get_name))(image);
        auto names = (SafeFptr(mono_class_get_namespace))(klass);
        auto classname = (SafeFptr(mono_class_get_name))(klass);
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
    std::string getmethodinfo(MonoMethod *method)
    {
        const char *methodName = SafeFptr(mono_method_get_name)(method); // 谜之没有输出
        if (!methodName)
            methodName = SafeFptr(mono_method_full_name)(method, true);
        if (methodName)
            return methodName;
        return "";
    }
    uintptr_t getmethodofklass(MonoClass *klass, const char *name, int argsCount)
    {
        if (!klass)
            return NULL;
        auto MonoClassMethod = (SafeFptr(mono_class_get_method_from_name))(klass, name, argsCount);
        if (!MonoClassMethod)
            return NULL;
        if (auto s = getclassinfo(klass))
        {
            ConsoleOutput(s.value().c_str());
            ConsoleOutput(getmethodinfo(MonoClassMethod).c_str());
        }
        return (uintptr_t)(SafeFptr(mono_compile_method))(MonoClassMethod);
    }
    struct AutoThread
    {
        MonoThread *thread = NULL;
        AutoThread()
        {
            auto _root = (SafeFptr(mono_get_root_domain))();
            if (!_root)
                return;
            thread = (SafeFptr(mono_thread_attach))(_root);
        }
        ~AutoThread()
        {
            if (!thread)
                return;
            (SafeFptr(mono_thread_detach))(thread);
        }
    };
    void __safe_getxx(monoloopinfo *hps, MonoMethod *method, MonoClass *klass)
    {
        if (auto methodName = SafeFptr(mono_method_full_name)(method, true))
        {
            if (auto sig = SafeFptr(mono_method_signature)(method))
            {
                if (auto cnt = SafeFptr(mono_signature_get_param_count)(sig))
                {
                    gpointer itertype = nullptr;
                    while (auto type = SafeFptr(mono_signature_get_params)(sig, &itertype))
                    {
                        if (auto tp = SafeFptr(mono_type_get_name)(type))
                        {
                            if (strcmp(tp, "System.String") == 0)
                            {
                                if (auto ptr = (uintptr_t)(SafeFptr(mono_compile_method))(method))
                                {
                                    std::string meth = methodName;
                                    if (meth.find(" (") != meth.npos)
                                    {
                                        meth = meth.substr(0, meth.find(" ("));
                                        auto _ = strSplit(meth, ":");
                                        if (_.size() >= 2)
                                        {
                                            auto m = _[_.size() - 1];

                                            auto image = (SafeFptr(mono_class_get_image))(klass);
                                            auto imagen = (SafeFptr(mono_image_get_name))(image);
                                            auto names = (SafeFptr(mono_class_get_namespace))(klass);
                                            auto classname = (SafeFptr(mono_class_get_name))(klass);
                                            std::string s;
                                            s = imagen;
                                            s += ":";
                                            s += names;
                                            s += ":";
                                            s += classname;
                                            s += ":";
                                            s += m;
                                            s += ":";
                                            s += std::to_string(cnt);
                                            hps->push_back({ptr, s});
                                        }
                                    }
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    void safe_getxx(monoloopinfo *hps, MonoMethod *method, MonoClass *klass)
    {
        __try
        {
            __safe_getxx(hps, method, klass);
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
        }
    }

}
monoloopinfo monofunctions::loop_all_methods(std::optional<std::function<void(std::string &)>> show)
{
    auto thread = AutoThread();
    if (!thread.thread)
        return {};
    monoloopinfo hps;
    auto klasses = loopclass(mono_loop_images());
    for (auto klass : klasses)
    {
        auto s = getclassinfo(klass);
        if (!s)
            continue;
        if (show)
            ConsoleOutput(s.value().c_str());
        gpointer iter = nullptr;
        while (auto method = SafeFptr(mono_class_get_methods)(klass, &iter))
        {
            if (show)
                ConsoleOutput(getmethodinfo(method).c_str());
            else
            {
                safe_getxx(&hps, method, klass);
            }
        }
    }
    if (show && klasses.size())
        return {{0, ""}};
    return hps;
}
void monofunctions::init(HMODULE game_module)
{
    RESOLVE_IMPORT(mono_class_get_methods);
    RESOLVE_IMPORT(mono_string_chars);
    RESOLVE_IMPORT(mono_string_length);
    RESOLVE_IMPORT(mono_table_info_get_rows);
    RESOLVE_IMPORT(mono_image_get_table_info);
    RESOLVE_IMPORT(mono_compile_method);
    RESOLVE_IMPORT(mono_class_from_name);
    RESOLVE_IMPORT(mono_domain_get);
    RESOLVE_IMPORT(mono_get_root_domain);
    RESOLVE_IMPORT(mono_assembly_foreach);
    RESOLVE_IMPORT(mono_image_get_name);
    RESOLVE_IMPORT(mono_assembly_get_image);
    RESOLVE_IMPORT(mono_class_is_valuetype);
    RESOLVE_IMPORT(mono_signature_get_param_count);
    RESOLVE_IMPORT(mono_string_to_utf8);
    RESOLVE_IMPORT(mono_string_new_wrapper);
    RESOLVE_IMPORT(mono_class_get_parent);
    RESOLVE_IMPORT(mono_class_get_namespace);
    RESOLVE_IMPORT(mono_class_is_subclass_of);
    RESOLVE_IMPORT(mono_class_get_name);
    RESOLVE_IMPORT(mono_type_get_name);
    RESOLVE_IMPORT(mono_type_get_class);
    RESOLVE_IMPORT(mono_exception_from_name_msg);
    RESOLVE_IMPORT(mono_raise_exception);
    RESOLVE_IMPORT(mono_get_exception_class);
    RESOLVE_IMPORT(mono_get_array_class);
    RESOLVE_IMPORT(mono_get_string_class);
    RESOLVE_IMPORT(mono_get_int32_class);
    RESOLVE_IMPORT(mono_array_new);
    RESOLVE_IMPORT(mono_array_new_full);
    RESOLVE_IMPORT(mono_array_class_get);
    RESOLVE_IMPORT(mono_class_array_element_size);
    RESOLVE_IMPORT(mono_type_get_object);
    RESOLVE_IMPORT(mono_thread_attach);
    RESOLVE_IMPORT(mono_thread_detach);
    RESOLVE_IMPORT(mono_thread_exit);
    RESOLVE_IMPORT(mono_thread_current);
    RESOLVE_IMPORT(mono_thread_set_main);
    RESOLVE_IMPORT(mono_set_find_plugin_callback);
    RESOLVE_IMPORT(mono_security_enable_core_clr);
    RESOLVE_IMPORT(mono_security_set_core_clr_platform_callback);
    RESOLVE_IMPORT(mono_runtime_unhandled_exception_policy_get);
    RESOLVE_IMPORT(mono_runtime_unhandled_exception_policy_set);
    RESOLVE_IMPORT(mono_class_get_nesting_type);
    RESOLVE_IMPORT(mono_class_vtable);
    RESOLVE_IMPORT(mono_method_get_object);
    RESOLVE_IMPORT(mono_method_signature);
    RESOLVE_IMPORT(mono_signature_get_params);
    RESOLVE_IMPORT(mono_signature_get_return_type);
    RESOLVE_IMPORT(mono_class_get_type);
    RESOLVE_IMPORT(mono_set_ignore_version_and_key_when_finding_assemblies_already_loaded);
    RESOLVE_IMPORT(mono_debug_init);
    RESOLVE_IMPORT(mono_debug_open_image_from_memory);
    RESOLVE_IMPORT(mono_field_get_flags);
    RESOLVE_IMPORT(mono_image_open_from_data_full);
    RESOLVE_IMPORT(mono_image_open_from_data_with_name);
    RESOLVE_IMPORT(mono_assembly_load_from);
    RESOLVE_IMPORT(mono_value_box);
    RESOLVE_IMPORT(mono_class_get_image);
    RESOLVE_IMPORT(mono_signature_is_instance);
    RESOLVE_IMPORT(mono_method_get_last_managed);
    RESOLVE_IMPORT(mono_get_enum_class);
    RESOLVE_IMPORT(mono_class_get_byref_type);
    RESOLVE_IMPORT(mono_field_static_get_value);
    RESOLVE_IMPORT(mono_unity_set_embeddinghostname);
    RESOLVE_IMPORT(mono_set_assemblies_path);
    RESOLVE_IMPORT(mono_gchandle_new);
    RESOLVE_IMPORT(mono_gchandle_get_target);
    RESOLVE_IMPORT(mono_gchandle_new_weakref);
    RESOLVE_IMPORT(mono_assembly_get_object);
    RESOLVE_IMPORT(mono_gchandle_free);
    RESOLVE_IMPORT(mono_class_get_properties);
    RESOLVE_IMPORT(mono_property_get_get_method);
    RESOLVE_IMPORT(mono_object_new_alloc_specific);
    RESOLVE_IMPORT(mono_object_new_specific);
    RESOLVE_IMPORT(mono_gc_collect);
    RESOLVE_IMPORT(mono_gc_max_generation);
    RESOLVE_IMPORT(mono_image_get_assembly);
    RESOLVE_IMPORT(mono_assembly_open);
    RESOLVE_IMPORT(mono_class_is_enum);
    RESOLVE_IMPORT(mono_class_instance_size);
    RESOLVE_IMPORT(mono_object_get_size);
    RESOLVE_IMPORT(mono_image_get_filename);
    RESOLVE_IMPORT(mono_assembly_load_from_full);
    RESOLVE_IMPORT(mono_class_get_interfaces);
    RESOLVE_IMPORT(mono_assembly_close);
    RESOLVE_IMPORT(mono_class_get_property_from_name);
    RESOLVE_IMPORT(mono_class_get_method_from_name);
    RESOLVE_IMPORT(mono_class_from_mono_type);
    RESOLVE_IMPORT(mono_domain_set);
    RESOLVE_IMPORT(mono_thread_push_appdomain_ref);
    RESOLVE_IMPORT(mono_thread_pop_appdomain_ref);
    RESOLVE_IMPORT(mono_runtime_exec_main);
    RESOLVE_IMPORT(mono_get_corlib);
    RESOLVE_IMPORT(mono_class_get_field_from_name);
    RESOLVE_IMPORT(mono_class_get_flags);
    RESOLVE_IMPORT(mono_parse_default_optimizations);
    RESOLVE_IMPORT(mono_set_defaults);
    RESOLVE_IMPORT(mono_set_dirs);
    RESOLVE_IMPORT(mono_jit_parse_options);
    RESOLVE_IMPORT(mono_object_unbox);
    RESOLVE_IMPORT(mono_custom_attrs_get_attr);
    RESOLVE_IMPORT(mono_custom_attrs_has_attr);
    RESOLVE_IMPORT(mono_custom_attrs_from_field);
    RESOLVE_IMPORT(mono_custom_attrs_from_method);
    RESOLVE_IMPORT(mono_custom_attrs_from_class);
    RESOLVE_IMPORT(mono_custom_attrs_free);
    RESOLVE_IMPORT(g_free);
    RESOLVE_IMPORT(mono_runtime_is_shutting_down);
    RESOLVE_IMPORT(mono_object_get_virtual_method);
    RESOLVE_IMPORT(mono_jit_info_get_code_start);
    RESOLVE_IMPORT(mono_jit_info_get_code_size);
    RESOLVE_IMPORT(mono_class_from_name_case);
    RESOLVE_IMPORT(mono_class_get_nested_types);
    RESOLVE_IMPORT(mono_class_get_userdata_offset);
    RESOLVE_IMPORT(mono_class_get_userdata);
    RESOLVE_IMPORT(mono_class_set_userdata);
    RESOLVE_IMPORT(mono_set_signal_chaining);
    RESOLVE_IMPORT(mono_unity_set_unhandled_exception_handler);
    RESOLVE_IMPORT(mono_runtime_invoke_array);
    RESOLVE_IMPORT(mono_array_addr_with_size);
    RESOLVE_IMPORT(mono_string_to_utf16);
    RESOLVE_IMPORT(mono_field_get_parent);
    RESOLVE_IMPORT(mono_method_full_name);
    RESOLVE_IMPORT(mono_object_isinst);
    RESOLVE_IMPORT(mono_string_new_len);
    RESOLVE_IMPORT(mono_string_from_utf16);
    RESOLVE_IMPORT(mono_class_get);
    RESOLVE_IMPORT(mono_string_new_utf16);
}
uintptr_t monofunctions::get_method_pointer(const char *_dll, const char *_namespace, const char *_class, const char *_method, int paramCount, bool strict)
{
    auto thread = AutoThread();
    if (!thread.thread)
        return NULL;

    auto images = mono_loop_images();

    auto pClass = mono_findklassby_ass_namespace(images, _dll, _namespace, _class, strict); // dll可以为空
    if (pClass)
        return getmethodofklass(pClass, _method, paramCount);
    if (strict)
        return NULL;
    auto klasses = mono_findklassby_class(images, _namespace, _class); // namespace可以为空
    for (auto klass : klasses)
    {
        auto method = getmethodofklass(klass, _method, paramCount);
        if (method)
            return method;
    }
    return NULL;
}

std::optional<std::wstring_view> monofunctions::get_string(void *ptr)
{
    auto str = reinterpret_cast<MonoString *>(ptr);
    if (!str)
        return {};
    auto wc = (SafeFptr(mono_string_chars))(str);
    auto len = (SafeFptr(mono_string_length))(str);
    if (!(wc && len))
        return {};
    return std::wstring_view((wchar_t *)wc, len);
}
void *monofunctions::create_string(std::wstring_view ws)
{
    auto domain = (SafeFptr(mono_domain_get))();
    if (!domain)
        return nullptr;
    return (SafeFptr(mono_string_new_utf16))(domain, (gunichar2 *)ws.data(), ws.length());
}