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

	// ============================================================== RPC table
	// Each entry:  X(name, signature)
	//   name      - identifier, available as rpc::Id::name
	//   signature - function type, e.g. void(HookParam, std::string)
	// Add a line here to register a new RPC; both sides pick it up.
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
	X(OutputText, void(ThreadParam, HookParam, uint64_t, RpcBlob))

	enum class Id : uint32_t
	{
#define X(name, sig) name,
		RPC_TABLE(X)
#undef X
		COUNT
	};

	// ---------------------------------------------------------------- pack
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
				// blittable: structs (HookParam, SearchParam, ThreadParam),
				// scalars (uint64_t, DWORD, int) and enums (HOSTINFO, LANG_STRINGS_HOOK).
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
		T getArg(const BYTE *&cur)
		{
			uint32_t sz;
			memcpy(&sz, cur, 4);
			cur += 4;
			T v;
			if constexpr (std::is_same_v<T, std::string>)
				v.assign((const char *)cur, sz);
			else if constexpr (std::is_same_v<T, std::wstring>)
				v.assign((const wchar_t *)cur, sz / sizeof(wchar_t));
			else if constexpr (std::is_same_v<T, RpcBlob>)
			{
				v.data = const_cast<BYTE *>(cur);
				v.size = sz;
			}
			else
				memcpy(&v, cur, sz);
			cur += sz;
			return v;
		}
	} // namespace detail

	// ---------------------------------------------------------------- call
	template <class... Args>
	void callRaw(uint32_t id, HANDLE pipe, const Args &...args)
	{
		thread_local std::vector<BYTE> buf;
		uint32_t payload = (0u + ... + (4u + detail::dataLen(args)));
		buf.resize(sizeof(Header) + payload);
		BYTE *base = buf.data();
		uint32_t off = sizeof(Header);
		auto put = [&](const auto &v)
		{ off += detail::putArg(base + off, v); };
		(put(args), ...);
		Header h{id, payload};
		memcpy(base, &h, sizeof(Header));
		DWORD written = 0;
		WriteFile(pipe, base, sizeof(Header) + payload, &written, nullptr);
	}

	// ----------------------------------------------------- registry / dispatch
	// Handlers receive an opaque `ctx` (threaded through dispatch, e.g. the
	// source process id) so a receiver can address per-message context without
	// thread-local state.
	using Handler = std::function<void(const BYTE *payload, uint32_t size, DWORD ctx)>;
	inline std::array<Handler, (size_t)Id::COUNT> &registry()
	{
		static std::array<Handler, (size_t)Id::COUNT> r;
		return r;
	}
	// Dispatch one received message. `ctx` is forwarded to the handler.
	// Returns the function id (so a caller may react to specific ids — e.g.
	// Detach — without a registered handler).
	inline uint32_t dispatch(const BYTE *msg, uint32_t total, DWORD ctx=0)
	{
		Header h;
		memcpy(&h, msg, sizeof(Header));
		if (h.payloadSize + sizeof(Header) <= total && h.id < (uint32_t)Id::COUNT)
			if (auto &fn = registry()[h.id])
				fn(msg + sizeof(Header), h.payloadSize, ctx);
		return h.id;
	}

	// ----------------------------------------------------------- typed glue
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

		// Invoke h(args...) reading each argument sequentially from `cur`, in
		// argument order. Done by recursion (each level reads one arg, then
		// chains a continuation), which gives guaranteed left-to-right order
		// without std::tuple/std::apply — those trip an MSVC internal compiler
		// error on some signature/type combinations here.
		template <class... A>
		struct Invoke;
		template <>
		struct Invoke<>
		{
			template <class H>
			static void run(H &h, const BYTE *&) { h(); }
		};
		template <class Head, class... Tail>
		struct Invoke<Head, Tail...>
		{
			template <class H>
			static void run(H &h, const BYTE *&cur)
			{
				Head arg = detail::getArg<Head>(cur); // sequenced before the recursive call below
				auto rest = [&, arg = std::move(arg)](Tail... t) mutable
				{ h(arg, std::move(t)...); };
				Invoke<Tail...>::run(rest, cur);
			}
		};

		template <class Sig, class F>
		struct make_handler;
		template <class... A, class F>
		struct make_handler<void(A...), F>
		{
			static Handler build(F fn)
			{
				return [h = std::move(fn)](const BYTE *p, uint32_t, DWORD)
				{
					const BYTE *cur = p;
					detail::Invoke<A...>::run(h, cur);
				};
			}
		};
		// Variant whose handler takes the dispatch context as its first argument:
		//   on_ctx<Id::Foo>([](DWORD ctx, A... args){ ... })
		template <class Sig, class F>
		struct make_handler_ctx;
		template <class... A, class F>
		struct make_handler_ctx<void(A...), F>
		{
			static Handler build(F fn)
			{
				return [h = std::move(fn)](const BYTE *p, uint32_t, DWORD ctx)
				{
					const BYTE *cur = p;
					auto wrapper = [&](A... args)
					{ h(ctx, args...); };
					detail::Invoke<A...>::run(wrapper, cur);
				};
			}
		};
	} // namespace detail

	template <Id I>
	struct Traits; // specialized per RPC below
#define X(name, sig)        \
	template <>             \
	struct Traits<Id::name> \
	{                       \
		using sig_t = sig;  \
	};
	RPC_TABLE(X)
#undef X

	// Register a typed handler. The handler's parameter types must match the
	// RPC's declared signature. The dispatch context is ignored.
	template <Id I, class F>
	void on(F f)
	{
		registry()[(uint32_t)I] = detail::make_handler<typename Traits<I>::sig_t, F>::build(std::move(f));
	}
	// Like on(), but the handler receives the dispatch context (the value passed
	// to dispatch()) as its first argument. Use on the receiver side that needs
	// per-message context (e.g. the host, which passes the process id).
	template <Id I, class F>
	void on_ctx(F f)
	{
		registry()[(uint32_t)I] = detail::make_handler_ctx<typename Traits<I>::sig_t, F>::build(std::move(f));
	}

	// Call a remote function. Argument count and convertibility are checked
	// against the declared signature at compile time.
	template <Id I, class... Args>
	void call(HANDLE pipe, Args &&...args)
	{
		using Sig = typename Traits<I>::sig_t;
		static_assert(sizeof...(Args) == detail::sig_params<Sig>::arity,
					  "rpc::call: wrong number of arguments for signature");
		static_assert(detail::args_convertible<Sig, std::tuple<Args...>, std::make_index_sequence<sizeof...(Args)>>::value,
					  "rpc::call: arguments not convertible to declared signature");
		callRaw((uint32_t)I, pipe, std::forward<Args>(args)...);
	}

#undef RPC_TABLE
} // namespace rpc
