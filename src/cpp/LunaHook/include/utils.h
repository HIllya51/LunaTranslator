#pragma once

#ifdef _WIN64
constexpr bool x64 = true;
#else
constexpr bool x64 = false;
#endif

template <typename T, typename... Xs>
struct ArrayImpl
{
	using Type = std::tuple<T, Xs...>[];
};
template <typename T>
struct ArrayImpl<T>
{
	using Type = T[];
};
template <typename... Ts>
using Array = typename ArrayImpl<Ts...>::Type;

template <auto F>
using Functor = std::integral_constant<std::remove_reference_t<decltype(F)>, F>; // shouldn't need remove_reference_t but MSVC is bugged

struct PermissivePointer
{
	template <typename T>
	operator T *() { return (T *)p; }
	void *p;
};
// 仿函数会多一层jump，毫无必要。
template <auto HandleCloser = CloseHandle> // Functor<CloseHandle>
class AutoHandle
{
public:
	AutoHandle(HANDLE h) : h(h) {}
	operator HANDLE() { return h.get(); }
	PHANDLE operator&()
	{
		static_assert(sizeof(*this) == sizeof(HANDLE));
		assert(!h);
		return (PHANDLE)this;
	}
	operator bool() { return h.get() != NULL && h.get() != INVALID_HANDLE_VALUE; }

private:
	struct HandleCleaner
	{
		void operator()(void *h)
		{
			if (h != INVALID_HANDLE_VALUE)
				HandleCloser(PermissivePointer{h});
		}
	};
	std::unique_ptr<void, HandleCleaner> h;
};

template <typename T, typename M = std::mutex>
class Synchronized
{
public:
	template <typename... Args>
	Synchronized(Args &&...args) : contents(std::forward<Args>(args)...) {}

	struct Locker
	{
		T *operator->() { return &contents; }
		std::unique_lock<M> lock;
		T &contents;
	};

	Locker Acquire() { return {std::unique_lock(m), contents}; }
	Locker operator->() { return Acquire(); }
	T Copy() { return Acquire().contents; }

private:
	T contents;
	M m;
};

template <typename F>
void SpawnThread(const F &f) // works in DllMain unlike std thread
{
	F *copy = new F(f);
	CloseHandle(CreateThread(nullptr, 0, [](void *copy)
							 {
		(*(F*)copy)();
		delete (F*)copy;
		return 0UL; }, copy, 0, nullptr));
}

inline struct // should be inline but MSVC (linker) is bugged
{
	inline static BYTE DUMMY[100];
	template <typename T>
	operator T *()
	{
		static_assert(sizeof(T) < sizeof(DUMMY));
		return (T *)DUMMY;
	}
} DUMMY;

inline auto Swallow = [](auto &&...) {};

template <typename T>
std::optional<std::remove_cv_t<T>> Copy(T *ptr)
{
	if (ptr)
		return *ptr;
	return {};
}

inline std::optional<std::wstring> getModuleFilename(DWORD processId, HMODULE module = NULL)
{
	std::vector<wchar_t> buffer(MAX_PATH);
	if (AutoHandle<> process = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, FALSE, processId))
		if (GetModuleFileNameExW(process, module, buffer.data(), MAX_PATH))
			return buffer.data();
	return {};
}

inline std::optional<std::wstring> getModuleFilename(HMODULE module = NULL)
{
	std::vector<wchar_t> buffer(MAX_PATH);
	if (GetModuleFileNameW(module, buffer.data(), MAX_PATH))
		return buffer.data();
	return {};
}

template <typename T>
struct SafeFptr
{
	T ptr;
	uintptr_t errorvalue;
	SafeFptr(T _ptr, uintptr_t v = {NULL}) : ptr(_ptr), errorvalue(v) {}

	template <typename... Args>
	std::invoke_result_t<T, Args...> operator()(Args... args)
	{
		if (!ptr)
			return (std::invoke_result_t<T, Args...>)(errorvalue);
		return ptr(std::forward<Args>(args)...);
	}
};
namespace simplehash
{
	enum : UINT64
	{
		djb2_hash0 = 5381
	};
	inline UINT64 djb2(const UINT8 *str, UINT64 hash = djb2_hash0)
	{
		UINT8 c;
		while ((c = *str++))
			hash = ((hash << 5) + hash) + c; // hash * 33 + c
		return hash;
	}
	inline UINT64 djb2_n2(const unsigned char *str, size_t len, UINT64 hash = djb2_hash0)
	{
		while (len--)
			hash = ((hash << 5) + hash) + (*str++); // hash * 33 + c
		return hash;
	}
	inline UINT64 hashByteArraySTD(const std::string &b, UINT64 h = djb2_hash0)
	{
		return djb2_n2((const unsigned char *)b.c_str(), b.size(), h);
	}
	inline UINT64 hashCharArray(const void *lp)
	{
		return djb2(reinterpret_cast<const UINT8 *>(lp));
	}
}