#pragma once

namespace rpc
{
	struct RpcBlob
	{
		BYTE *data;
		uint32_t size;
	};

	struct Header
	{
		uint32_t id;
		uint32_t payloadSize;
	};

	constexpr uint32_t BLOB_PREFIX = sizeof(Header) + 4;

#define RPC_TABLE(X)                                                  \
	/* ---- host -> hook (commands) ---- */                           \
	X(NewHook, void(HookParam))                                       \
	X(RemoveHook, void(uint64_t))                                     \
	X(FindHook, void(SearchParam))                                    \
	X(Detach, void())                                                 \
	X(InsertPCHooks, void(int))                                       \
	X(QueryI18N, void())                                              \
	X(RespondI18N, void(LANG_STRINGS_HOOK, std::string))              \
	X(SetDetectedCodepage, void(DWORD, uint64_t))                     \
	/* ---- hook -> host (notifications) ---- */                      \
	X(NotifyText, void(HOSTINFO, UINT, std::string))                  \
	X(NotifyTextW, void(HOSTINFO, std::wstring))                      \
	X(NotifyHookFound, void(HookParam, RpcBlob))                      \
	X(NotifyHookRemoved, void(uint64_t))                              \
	X(NotifyHookInserting, void(uint64_t, std::wstring))              \
	X(NotifyEmuGameInfo, void(std::string, std::string, std::string)) \
	X(RequestI18N, void(LANG_STRINGS_HOOK, std::string))              \
	X(NotifyPreparedOK, void())                                       \
	X(OutputText, void(RpcBlob))

	enum class Id : uint32_t
	{
#define X(name, sig) name,
		RPC_TABLE(X)
#undef X
		COUNT
	};

	namespace detail
	{
		template <class T>
		uint32_t dataLen(const T &v)
		{
			using U = std::remove_cv_t<std::remove_reference_t<T>>;
			if constexpr (std::is_same_v<U, std::string>)
				return (uint32_t)v.size();
			else if constexpr (std::is_same_v<U, std::wstring>)
				return (uint32_t)(v.size() * sizeof(wchar_t));
			else if constexpr (std::is_same_v<U, std::string_view>)
				return (uint32_t)v.size();
			else if constexpr (std::is_same_v<U, RpcBlob>)
				return v.size;
			else if constexpr (std::is_pointer_v<U>)
			{
				using E = std::remove_cv_t<std::remove_pointer_t<U>>;
				if constexpr (std::is_same_v<E, char>)
					return (uint32_t)strlen(v);
				else if constexpr (std::is_same_v<E, wchar_t>)
					return (uint32_t)(wcslen(v) * sizeof(wchar_t));
				else
					static_assert(!sizeof(T), "rpc: unsupported pointer argument type");
			}
			else
			{
				return (uint32_t)sizeof(U);
			}
		}

		template <class T>
		const void *dataPtr(const T &v)
		{
			using U = std::remove_cv_t<std::remove_reference_t<T>>;
			if constexpr (std::is_same_v<U, std::string> || std::is_same_v<U, std::wstring> || std::is_same_v<U, std::string_view>)
				return v.data();
			else if constexpr (std::is_same_v<U, RpcBlob>)
				return v.data;
			else if constexpr (std::is_pointer_v<U>)
				return (const void *)v;
			else
				return (const void *)&v;
		}

		inline uint32_t putArg(BYTE *p, const void *src, uint32_t n)
		{
			memcpy(p, &n, 4);
			memcpy(p + 4, src, n);
			return 4 + n;
		}
		template <class T>
		uint32_t putArg(BYTE *p, const T &v)
		{
			return putArg(p, dataPtr(v), dataLen(v));
		}

		template <class T>
		T makeArg(const BYTE *p, uint32_t sz)
		{
			T v;
			if constexpr (std::is_same_v<T, std::string>)
				v.assign((const char *)p, sz);
			else if constexpr (std::is_same_v<T, std::wstring>)
				v.assign((const wchar_t *)p, sz / sizeof(wchar_t));
			else if constexpr (std::is_same_v<T, RpcBlob>)
			{
				v.data = const_cast<BYTE *>(p);
				v.size = sz;
			}
			else
			{
				memset(&v, 0, sizeof(T));
				memcpy(&v, p, sz < sizeof(T) ? sz : sizeof(T));
			}
			return v;
		}
	} // namespace detail

	template <class... Args>
	void callRaw(uint32_t id, HANDLE pipe, const Args &...args)
	{
		uint32_t payload = (0u + ... + (4u + detail::dataLen(args)));
		if (sizeof(Header) + payload > PIPE_BUFFER_SIZE)
			return;
		std::unique_ptr<BYTE[]> buf(new BYTE[sizeof(Header) + payload]);
		BYTE *base = buf.get();
		uint32_t off = sizeof(Header);
		auto put = [&](const auto &v)
		{ off += detail::putArg(base + off, v); };
		(put(args), ...);
		Header h{id, payload};
		memcpy(base, &h, sizeof(Header));
		DWORD written = 0;
		WriteFile(pipe, base, sizeof(Header) + payload, &written, nullptr);
	}

	inline void callRawBlob(uint32_t id, HANDLE pipe, const RpcBlob &blob)
	{
		uint32_t payload = 4u + blob.size;
		if (sizeof(Header) + payload > PIPE_BUFFER_SIZE)
			return;
		BYTE *base = blob.data - BLOB_PREFIX;
		Header h{id, payload};
		memcpy(base, &h, sizeof(Header));
		uint32_t n = blob.size;
		memcpy(base + sizeof(Header), &n, 4);
		DWORD written = 0;
		WriteFile(pipe, base, sizeof(Header) + payload, &written, nullptr);
	}

	using Handler = std::function<void(const BYTE *payload, uint32_t size, DWORD ctx)>;
	inline std::array<Handler, (size_t)Id::COUNT> &registry()
	{
		static std::array<Handler, (size_t)Id::COUNT> r;
		return r;
	}
	inline uint32_t dispatch(const BYTE *msg, uint32_t total, DWORD ctx=0)
	{
		Header h;
		memcpy(&h, msg, sizeof(Header));
		if (h.payloadSize + sizeof(Header) <= total && h.id < (uint32_t)Id::COUNT)
			if (auto &fn = registry()[h.id])
				fn(msg + sizeof(Header), h.payloadSize, ctx);
		return h.id;
	}

	namespace detail
	{
		template <class Sig>
		struct sig_params;
		template <class... A>
		struct sig_params<void(A...)>
		{
			static constexpr size_t arity = sizeof...(A);
			template <size_t I>
			using arg = std::tuple_element_t<I, std::tuple<A...>>;
		};

		template <class Sig, class Tuple, class Idx>
		struct args_convertible;
		template <class Sig, class... A, size_t... I>
		struct args_convertible<Sig, std::tuple<A...>, std::index_sequence<I...>>
		{
			static constexpr bool value = (std::is_convertible_v<A, typename sig_params<Sig>::template arg<I>> && ...);
		};

		template <class... A>
		struct Invoke;
		template <>
		struct Invoke<>
		{
			template <class H>
			static void run(H &h, const BYTE *&, const BYTE *) { h(); }
		};
		template <class Head, class... Tail>
		struct Invoke<Head, Tail...>
		{
			template <class H>
			static void run(H &h, const BYTE *&cur, const BYTE *end)
			{
				if (cur + 4 > end)
					return;
				uint32_t sz;
				memcpy(&sz, cur, 4);
				const BYTE *val = cur + 4;
				if (val + sz > end)
					return;
				cur = val + sz;
				Head arg = detail::makeArg<Head>(val, sz); // sequenced before the recursive call below
				auto rest = [&, arg = std::move(arg)](Tail... t) mutable
				{ h(std::move(arg), std::move(t)...); };
				Invoke<Tail...>::run(rest, cur, end);
			}
		};

		template <class Sig>
		struct is_single_blob : std::false_type {};
		template <class A>
		struct is_single_blob<void(A)> : std::is_same<A, RpcBlob> {};

		template <class Sig, class F>
		struct make_handler;
		template <class... A, class F>
		struct make_handler<void(A...), F>
		{
			static Handler build(F fn)
			{
				static_assert(std::is_invocable_v<F, A...>, "rpc::on: handler is not callable with the declared argument types");
				return [h = std::move(fn)](const BYTE *p, uint32_t size, DWORD)
				{
					const BYTE *cur = p;
					detail::Invoke<A...>::run(h, cur, p + size);
				};
			}
		};
		template <class Sig, class F>
		struct make_handler_ctx;
		template <class... A, class F>
		struct make_handler_ctx<void(A...), F>
		{
			static Handler build(F fn)
			{
				static_assert(std::is_invocable_v<F, DWORD, A...>, "rpc::on_ctx: handler is not callable with (ctx, declared-args...)");
				return [h = std::move(fn)](const BYTE *p, uint32_t size, DWORD ctx)
				{
					const BYTE *cur = p;
					auto wrapper = [&](A... args)
					{ h(ctx, std::move(args)...); };
					detail::Invoke<A...>::run(wrapper, cur, p + size);
				};
			}
		};
	} // namespace detail

	template <Id I>
	struct Traits;
#define X(name, sig)        \
	template <>             \
	struct Traits<Id::name> \
	{                       \
		using sig_t = sig;  \
	};
	RPC_TABLE(X)
#undef X

	template <Id I, class F>
	void on(F f)
	{
		registry()[(uint32_t)I] = detail::make_handler<typename Traits<I>::sig_t, F>::build(std::move(f));
	}
	template <Id I, class F>
	void on_ctx(F f)
	{
		registry()[(uint32_t)I] = detail::make_handler_ctx<typename Traits<I>::sig_t, F>::build(std::move(f));
	}

	template <Id I, class... Args>
	void call(HANDLE pipe, Args &&...args)
	{
		using Sig = typename Traits<I>::sig_t;
		static_assert(sizeof...(Args) == detail::sig_params<Sig>::arity,
					  "rpc::call: wrong number of arguments for signature");
		static_assert(detail::args_convertible<Sig, std::tuple<Args...>, std::make_index_sequence<sizeof...(Args)>>::value,
					  "rpc::call: arguments not convertible to declared signature");
		if constexpr (detail::is_single_blob<Sig>::value)
			callRawBlob((uint32_t)I, pipe, std::forward<Args>(args)...);
		else
			callRaw((uint32_t)I, pipe, std::forward<Args>(args)...);
	}

#undef RPC_TABLE
} // namespace rpc
