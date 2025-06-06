#include "xp_hstring.hpp"
#define MIDL_CONST_ID const __declspec(selectany)
typedef GUID IID;
typedef IID *LPIID;

typedef struct EventRegistrationToken
{
    __int64 value;
} EventRegistrationToken;
//////////////////////////////////OCR
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            enum class AsyncStatus
            {
                Started = 0,
                Completed,
                Canceled,
                Error,
            };
        }
    }
} // ABI::Windows:::Foundation

namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            struct SizeInt32
            {
                INT32 Width;
                INT32 Height;
            };
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            struct Rect
            {
                FLOAT X;
                FLOAT Y;
                FLOAT Width;
                FLOAT Height;
            };
        } /* Foundation */
    } /* Windows */
} /* ABI */
typedef enum
{
    BSOS_DEFAULT = 0,            // when creating a byte seeker over a stream, base randomaccessstream behavior on the STGM mode from IStream::Stat.
    BSOS_PREFERDESTINATIONSTREAM // in addition, utilize IDestinationStreamFactory::GetDestinationStream.
} BSOS_OPTIONS;

typedef /* [v1_enum] */
    enum TrustLevel
{
    BaseTrust = 0,
    PartialTrust = (BaseTrust + 1),
    FullTrust = (PartialTrust + 1)
} TrustLevel;
MIDL_INTERFACE("AF86E2E0-B12D-4c6a-9C5A-D7AA65101E90")
IInspectable : public IUnknown
{
public:
    virtual HRESULT STDMETHODCALLTYPE GetIids(
        /* [out] */ __RPC__out ULONG * iidCount,
        /* [size_is][size_is][out] */ __RPC__deref_out_ecount_full_opt(*iidCount) IID * *iids) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetRuntimeClassName(
        /* [out] */ __RPC__deref_out_opt HSTRING * className) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetTrustLevel(
        /* [out] */ __RPC__out TrustLevel * trustLevel) = 0;
};
namespace ABI
{
    namespace Windows
    {
        namespace Globalization
        {
            MIDL_INTERFACE("ea79a752-f7c2-4265-b1bd-c4dec4e4f080")
            ILanguage : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE get_LanguageTag(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DisplayName(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_NativeName(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Script(
                    HSTRING * value) = 0;
            };
        }
    }
}

namespace ABI
{
    namespace Windows
    {
        namespace Globalization
        {
            MIDL_INTERFACE("9b0252ac-0c27-44f8-b792-9793fb66c63e")
            ILanguageFactory : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE CreateLanguage(
                    HSTRING languageTag,
                    ABI::Windows::Globalization::ILanguage * *result) = 0;
            };
        }
    }
}
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Globalization_Language[] = L"Windows.Globalization.Language";
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Imaging
            {
                MIDL_INTERFACE("acef22ba-1d74-4c91-9dfc-9620745233e6")
                IBitmapDecoder : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_BitmapContainerProperties(
                        void **value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_DecoderInformation(
                        void **value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_FrameCount(
                        UINT32 * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetPreviewAsync(
                        void **asyncInfo) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetFrameAsync(
                        UINT32 frameIndex,
                        void **asyncInfo) = 0;
                };
            }
        }
    }
}
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Media_Ocr_OcrEngine[] = L"Windows.Media.Ocr.OcrEngine";

extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Graphics_Imaging_BitmapDecoder[] = L"Windows.Graphics.Imaging.BitmapDecoder";

extern "C" _Check_return_
    HRESULT
        WINAPI
        RoActivateInstance(
            _In_ HSTRING activatableClassId,
            _COM_Outptr_ IInspectable **instance);

extern "C" _Check_return_
    HRESULT
        WINAPI
        RoGetActivationFactory(
            _In_ HSTRING activatableClassId,
            _In_ REFIID iid,
            _COM_Outptr_ void **factory);

namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            // get activation factory
            template <class T>
            _Check_return_ __inline HRESULT GetActivationFactory(
                _In_ HSTRING activatableClassId,
                _COM_Outptr_ T **factory)
            {
                return RoGetActivationFactory(activatableClassId, IID_PPV_ARGS(factory));
            }
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Storage
        {
            namespace Streams
            {
                MIDL_INTERFACE("905a0fe1-bc53-11df-8c49-001e4fc686da")
                IRandomAccessStream : public IInspectable{

                                      };
            }
        }
    }
}

namespace ABI
{
    namespace Windows
    {
        namespace Globalization
        {
            class Language;
        } /* Globalization */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                MIDL_INTERFACE("3c2a477a-5cd9-3525-ba2a-23d1e0a68a1d")
                IOcrWord : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_BoundingRect(
                        ABI::Windows::Foundation::Rect * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_Text(
                        HSTRING * value) = 0;
                };
            }
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                class OcrWord;
            } /* Ocr */
        } /* Media */
    } /* Windows */
} /* ABI */

namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            namespace Internal
            {
                // LogicalType - the Windows Runtime type (eg, runtime class, inteface group, etc)
                //               being provided as an argument to an _impl template, when that type
                //               cannot be represented at the ABI.
                // AbiType     - the type used for marshalling, ie "at the ABI", for the logical type.
                template <class LogicalType, class AbiType>
                struct AggregateType
                {
                };

                // Gets the ABI type.  See AggregateType for description.
                template <class T>
                struct GetAbiType
                {
                    typedef T type;
                };

                template <class L, class A>
                struct GetAbiType<AggregateType<L, A>>
                {
                    typedef A type;
                };

                // Gets the LogicalType.  See AggregateType for description.
                template <class T>
                struct GetLogicalType
                {
                    typedef T type;
                };

                template <class L, class A>
                struct GetLogicalType<AggregateType<L, A>>
                {
                    typedef L type;
                };

            }
        }
    } // namespace Windows::Foundation::Internal
} // ABI

namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Imaging
            {
                class BitmapDecoder;
            } /* Imaging */
        } /* Graphics */
    } /* Windows */
} /* ABI */

namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            namespace Collections
            {

                namespace detail
                {
                    template <class T>
                    struct not_yet_specialized_placeholder
                    {
                        enum
                        {
                            value = false
                        };
                    };

                    template <class WasNotSpecialized>
                    struct not_yet_specialized
                    {
                        static_assert(
                            not_yet_specialized_placeholder<WasNotSpecialized>::value,
                            "This interface instance has not been specialized by MIDL."
                            " This may be caused by forgetting a '*' pointer on an interface"
                            " type, by omitting a necessary 'declare' clause in your idl"
                            " file, by forgetting to include one of the necessary MIDL"
                            " generated headers.");
                    };
                }
                template <class T>
                struct is_pointer
                {
                    enum
                    {
                        value = false
                    };
                };
                template <class T>
                struct is_pointer<T *>
                {
                    enum
                    {
                        value = true
                    };
                };

                template <class T>
                struct is_foundation_struct
                {
                    enum
                    {
                        value = false
                    };
                };

                template <class T>
                struct supports_cleanup
                {
                    typedef typename Windows::Foundation::Internal::GetAbiType<T>::type _abi_type;
                    enum
                    {
                        value = is_pointer<_abi_type>::value || is_foundation_struct<_abi_type>::value || !__is_class(_abi_type)
                    };
                };

                template <class T, bool isStruct = supports_cleanup<T>::value>
                struct IIterator_impl;

                template <class T>
                struct IIterable_impl;

                template <class T>
                struct IIterator
                    : IIterator_impl<T>,
                      detail::not_yet_specialized<IIterator<T>>
                {
                };

                template <class T>
                struct IIterable
                    : IIterable_impl<T>,
                      detail::not_yet_specialized<IIterable<T>>
                {
                };

                template <class T, bool isStruct = supports_cleanup<T>::value>
                struct IVectorView_impl;
                template <class T>
                struct IVectorView
                    : IVectorView_impl<T>,
                      detail::not_yet_specialized<IVectorView<T>>
                {
                };

                namespace Detail
                {

// known struct types get no-op cleanup
#define XWINRT_DEF_CLEANUP(type) \
    inline void _Cleanup(type * /* values[] */, unsigned /* actual */) {}
// XWINRT_DEF_CLEANUP(GUID);
// XWINRT_DEF_CLEANUP(Windows::Foundation::DateTime);
// XWINRT_DEF_CLEANUP(Windows::Foundation::TimeSpan);
// XWINRT_DEF_CLEANUP(Windows::Foundation::Point);
// XWINRT_DEF_CLEANUP(Windows::Foundation::Size);
// XWINRT_DEF_CLEANUP(Windows::Foundation::Rect);
#undef XWINRT_DEF_CLEANUP

                    // Template magic for number and enums
                    template <bool condition, class T = void *>
                    struct enable_if
                    {
                    };
                    template <class T>
                    struct enable_if<true, T>
                    {
                        typedef T type;
                    };

                    // numbers, enums get no-op cleanup.
                    template <class T>
                    void _Cleanup(T * /*values*/, unsigned /*actual*/, typename enable_if<!__is_class(T) && !(is_pointer<T>::value)>::type = 0) {}

                    template <class I, class Number>
                    void _Cleanup(_Inout_updates_(actual) I *values[], Number actual)
                    {
                        for (unsigned i = 0; i < actual; ++i)
                        {
                            values[i]->Release();
                            values[i] = nullptr;
                        }
                    }

                    // make this a template so that we don't deptend on WindowsDeleteString in this file
                    template <class Number>
                    inline void _Cleanup(_Inout_updates_(actual) HSTRING *values, Number actual)
                    {
                        for (unsigned i = 0; i < actual; ++i)
                        {
                            ::WindowsDeleteString(values[i]);
                            values[i] = nullptr;
                        }
                    }

                    // Note: Because structs require custom cleanup, the default implementation will not be
                    // available to custom collections of structs. They will need to provide their own
                    // implementations.
                    template <class U, class T>
                    HRESULT _VectorGetMany(
                        _In_ U *pThis,
                        _In_ unsigned startIndex,
                        _In_ unsigned capacity,
                        _Out_writes_to_(capacity, *actual) T *value,
                        _Out_ unsigned *actual)
                    {
                        unsigned index = 0;
                        HRESULT hr = S_OK;
                        unsigned size = 0;
                        unsigned copied = 0;

                        ZeroMemory(value, sizeof(*value) * capacity);
                        *actual = 0;

                        // Get the size of the vector so that we can do bounds checking
                        hr = pThis->get_Size(&size);

                        if (SUCCEEDED(hr))
                        {
                            if (startIndex > size)
                            {
                                // If we are more than one past the end, then we return E_BOUNDS;
                                hr = E_BOUNDS;
                            }
                            else
                            {
                                // we are guarenteed to be one past the end or less.  If we are one past the end
                                // we won't enter the for loop, and we'll get S_OK but nothing returned.
                                // If we are at the end or earlier, we'll actually get something in the output
                                for (index = 0; (index < capacity) && (index + startIndex < size); index++)
                                {
                                    hr = pThis->GetAt(index + startIndex, &value[index]);
                                    if (SUCCEEDED(hr))
                                    {
                                        copied += 1;
                                    }
                                    else
                                    {
                                        break;
                                    }
                                }
                            }
                        }

                        if (SUCCEEDED(hr))
                        {
                            *actual = index;
                        }

                        if (FAILED(hr))
                        {
                            Detail::_Cleanup(value, copied);
                        }
                        return hr;
                    }

                    template <class U, class T>
                    HRESULT _IteratorGetMany(_In_ U *pThis, _In_ unsigned capacity, _Out_writes_to_(capacity, *actual) T *value, _Out_ unsigned *actual)
                    {
                        HRESULT hr = S_OK;
                        ::boolean fHasCurrent = false;
                        unsigned count = 0;
                        ZeroMemory(value, sizeof(*value) * capacity);
                        *actual = 0;

                        hr = pThis->get_HasCurrent(&fHasCurrent);
                        while (SUCCEEDED(hr) && (fHasCurrent) && (count < capacity))
                        {
                            hr = pThis->get_Current(&value[count]);
                            if (SUCCEEDED(hr))
                            {
                                count++;
                                hr = pThis->MoveNext(&fHasCurrent);
                            }
                        }

                        if (SUCCEEDED(hr))
                        {
                            *actual = count;
                        }
                        else
                        {
                            // cleanup output paremeters on failure
                            // no need to zero out *actual as it is still
                            // initialized to zero.
                            Detail::_Cleanup(value, *actual);
                        }
                        return hr;
                    }

                }
                template <class T, bool isStruct>
                struct IVectorView_impl : IInspectable /* requires IIterable<T> */
                {
                private:
                    typedef typename Windows::Foundation::Internal::GetAbiType<T>::type T_abi;
                    typedef typename Windows::Foundation::Internal::GetLogicalType<T>::type T_logical;

                public:
                    typedef T T_complex;

                    virtual HRESULT STDMETHODCALLTYPE GetAt(_In_ unsigned index, _Out_ T_abi *item) = 0;
                    virtual /* propget */ HRESULT STDMETHODCALLTYPE get_Size(_Out_ unsigned *size) = 0;
                    virtual HRESULT STDMETHODCALLTYPE IndexOf(_In_opt_ T_abi value, _Out_ unsigned *index, _Out_ boolean *found) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetMany(_In_ unsigned startIndex, _In_ unsigned capacity, _Out_writes_to_(capacity, *actual) T_abi *value, _Out_ unsigned *actual)
                    {
                        return Detail::_VectorGetMany(this, startIndex, capacity, value, actual);
                    }
                };

                template <class T>
                struct IVectorView_impl<T, false> : IInspectable /* requires IIterable<T> */
                {
                private:
                    typedef typename Windows::Foundation::Internal::GetAbiType<T>::type T_abi;
                    typedef typename Windows::Foundation::Internal::GetLogicalType<T>::type T_logical;

                public:
                    typedef T T_complex;

                    virtual HRESULT STDMETHODCALLTYPE GetAt(_In_ unsigned index, _Out_ T_abi *item) = 0;
                    virtual /* propget */ HRESULT STDMETHODCALLTYPE get_Size(_Out_ unsigned *size) = 0;
                    virtual HRESULT STDMETHODCALLTYPE IndexOf(_In_opt_ T_abi value, _Out_ unsigned *index, _Out_ boolean *found) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetMany(_In_ unsigned startIndex, _In_ unsigned capacity, _Out_writes_to_(capacity, *actual) T_abi *value, _Out_ unsigned *actual) = 0;
                };

                template <class T>
                struct IIterable_impl : IInspectable
                {
                private:
                    typedef typename Windows::Foundation::Internal::GetAbiType<T>::type T_abi;
                    typedef typename Windows::Foundation::Internal::GetLogicalType<T>::type T_logical;

                public:
                    // For all types which are neither InterfaceGroups nor RuntimeClasses, the
                    // following three typedefs are synonyms for a single C++ type.  But for
                    // InterfaceGroups and RuntimeClasses, they are different types:
                    //   T_logical: The C++ Type for the InterfaceGroup or RuntimeClass, when
                    //              used as a template parameter.  Eg "RCFoo*"
                    //   T_abi:     The C++ type for the default interface used to represent the
                    //              InterfaceGroup or RuntimeClass when passed as a method parameter.
                    //              Eg "IFoo*"
                    //   T_complex: An instantiation of the Internal "AggregateType" template that
                    //              combines T_logical with T_abi. Eg "AggregateType<RCFoo*,IFoo*>"
                    // See the declaration above of Windows::Foundation::Internal::AggregateType
                    // for more details.
                    typedef T T_complex;

                    virtual HRESULT STDMETHODCALLTYPE First(_Outptr_result_maybenull_ IIterator<T_logical> **first) = 0;
                };

                // Note: There are two versions of this template.  The second will compile where T is a struct and the
                // first will compile in all other cases.  This approach is used to ensure that if T is a struct that
                // GetMany will be pure virtual (and must be overloaded), but in the other cases GetMany will
                // be handed by the default implementation.
                // Important Note!:  Both of these templates must have the same vtable!!!  Change one and you
                // must change the other
                template <class T, bool isStruct>
                struct IIterator_impl : IInspectable
                {
                private:
                    typedef typename Windows::Foundation::Internal::GetAbiType<T>::type T_abi;
                    typedef typename Windows::Foundation::Internal::GetLogicalType<T>::type T_logical;

                public:
                    typedef T T_complex;

                    virtual /* propget */ HRESULT STDMETHODCALLTYPE get_Current(_Out_ T_abi *current) = 0;
                    virtual /* propget */ HRESULT STDMETHODCALLTYPE get_HasCurrent(_Out_ boolean *hasCurrent) = 0;
                    virtual HRESULT STDMETHODCALLTYPE MoveNext(_Out_ boolean *hasCurrent) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetMany(_In_ unsigned capacity, _Out_writes_to_(capacity, *actual) T_abi *value, _Out_ unsigned *actual)
                    {
                        return Detail::_IteratorGetMany(this, capacity, value, actual);
                    }
                };

                template <class T>
                struct IIterator_impl<T, false> : IInspectable
                {
                private:
                    typedef typename Windows::Foundation::Internal::GetAbiType<T>::type T_abi;
                    typedef typename Windows::Foundation::Internal::GetLogicalType<T>::type T_logical;

                public:
                    typedef T T_complex;

                    virtual /* propget */ HRESULT STDMETHODCALLTYPE get_Current(_Out_ T_abi *current) = 0;
                    virtual /* propget */ HRESULT STDMETHODCALLTYPE get_HasCurrent(_Out_ boolean *hasCurrent) = 0;
                    virtual HRESULT STDMETHODCALLTYPE MoveNext(_Out_ boolean *hasCurrent) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetMany(_In_ unsigned capacity, _Out_writes_to_(capacity, *actual) T_abi *value, _Out_ unsigned *actual) = 0;
                };

            }
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <class TSender, class TArgs>
            struct ITypedEventHandler_impl;

            template <class TProgress>
            struct IAsyncOperation_impl;

            template <class TResult>
            struct IAsyncOperation
                : IAsyncOperation_impl<TResult>,
                  Windows::Foundation::Collections::detail::not_yet_specialized<IAsyncOperation<TResult>>
            {
            };

            template <class TResult>
            struct IAsyncOperationCompletedHandler_impl;

            template <class TResult>
            struct IAsyncOperationCompletedHandler
                : IAsyncOperationCompletedHandler_impl<TResult>,
                  Windows::Foundation::Collections::detail::not_yet_specialized<IAsyncOperationCompletedHandler<TResult>>
            {
            };
            template <class TResult>
            struct IAsyncOperationCompletedHandler_impl : IUnknown
            {
            private:
                typedef typename Windows::Foundation::Internal::GetAbiType<TResult>::type TResult_abi;
                typedef typename Windows::Foundation::Internal::GetLogicalType<TResult>::type TResult_logical;

            public:
                // For all types which are neither InterfaceGroups nor RuntimeClasses, the
                // following three typedefs are synonyms for a single C++ type.  But for
                // InterfaceGroups and RuntimeClasses, they are different types:
                //   T_logical: The C++ Type for the InterfaceGroup or RuntimeClass, when
                //              used as a template parameter.  Eg "RCFoo*"
                //   T_abi:     The C++ type for the default interface used to represent the
                //              InterfaceGroup or RuntimeClass when passed as a method parameter.
                //              Eg "IFoo*"
                //   T_complex: An instantiation of the Internal "AggregateType" template that
                //              combines T_logical with T_abi. Eg "AggregateType<RCFoo*,IFoo*>"
                // See the declaration above of Windows::Foundation::Internal::AggregateType
                // for more details.
                typedef TResult TResult_complex;

                virtual HRESULT STDMETHODCALLTYPE Invoke(IAsyncOperation<TResult_logical> *asyncInfo, Windows::Foundation::AsyncStatus status) = 0;
            };

            template <class TResult>
            struct IAsyncOperation_impl : IInspectable
            {
            private:
                typedef typename Windows::Foundation::Internal::GetAbiType<TResult>::type TResult_abi;
                typedef typename Windows::Foundation::Internal::GetLogicalType<TResult>::type TResult_logical;

            public:
                // For all types which are neither InterfaceGroups nor RuntimeClasses, the
                // following three typedefs are synonyms for a single C++ type.  But for
                // InterfaceGroups and RuntimeClasses, they are different types:
                //   T_logical: The C++ Type for the InterfaceGroup or RuntimeClass, when
                //              used as a template parameter.  Eg "RCFoo*"
                //   T_abi:     The C++ type for the default interface used to represent the
                //              InterfaceGroup or RuntimeClass when passed as a method parameter.
                //              Eg "IFoo*"
                //   T_complex: An instantiation of the Internal "AggregateType" template that
                //              combines T_logical with T_abi. Eg "AggregateType<RCFoo*,IFoo*>"
                // See the declaration above of Windows::Foundation::Internal::AggregateType
                // for more details.
                typedef TResult TResult_complex;

                virtual HRESULT STDMETHODCALLTYPE put_Completed(IAsyncOperationCompletedHandler<TResult_logical> *handler) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Completed(IAsyncOperationCompletedHandler<TResult_logical> **handler) = 0;
                virtual HRESULT STDMETHODCALLTYPE GetResults(TResult_abi *results) = 0;
            };

            template <class TSender, class TArgs>
            struct ITypedEventHandler
                : ITypedEventHandler_impl<TSender, TArgs>,
                  Windows::Foundation::Collections::detail::not_yet_specialized<ITypedEventHandler<TSender, TArgs>>
            {
            };

            template <class TSender, class TArgs>
            struct ITypedEventHandler_impl : IUnknown
            {
            private:
                typedef typename Windows::Foundation::Internal::GetAbiType<TSender>::type TSender_abi;
                typedef typename Windows::Foundation::Internal::GetLogicalType<TSender>::type TSender_logical;
                typedef typename Windows::Foundation::Internal::GetAbiType<TArgs>::type TArgs_abi;
                typedef typename Windows::Foundation::Internal::GetLogicalType<TArgs>::type TArgs_logical;

            public:
                // For all types which are neither InterfaceGroups nor RuntimeClasses, the
                // following three typedefs are synonyms for a single C++ type.  But for
                // InterfaceGroups and RuntimeClasses, they are different types:
                //   T_logical: The C++ Type for the InterfaceGroup or RuntimeClass, when
                //              used as a template parameter.  Eg "RCFoo*"
                //   T_abi:     The C++ type for the default interface used to represent the
                //              InterfaceGroup or RuntimeClass when passed as a method parameter.
                //              Eg "IFoo*"
                //   T_complex: An instantiation of the Internal "AggregateType" template that
                //              combines T_logical with T_abi. Eg "AggregateType<RCFoo*,IFoo*>"
                // See the declaration above of Windows::Foundation::Internal::AggregateType
                // for more details.
                typedef TSender TSender_complex;
                typedef TArgs TArgs_complex;

                virtual HRESULT STDMETHODCALLTYPE Invoke(_In_ TSender_abi sender, _In_ TArgs_abi args) = 0;
            };
        }
    }
}

template <>
struct __declspec(uuid("805a60c7-df4f-527c-86b2-e29e439a83d2"))
ABI::Windows::Foundation::Collections::IVectorView<ABI::Windows::Media::Ocr::OcrWord *> : IVectorView_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Media::Ocr::OcrWord *, ABI::Windows::Media::Ocr::IOcrWord *>>
{
    static const wchar_t *z_get_rc_name_impl()
    {
        return L"Windows.Foundation.Collections.IVectorView`1<Windows.Media.Ocr.OcrWord>";
    }
};

template <>
struct __declspec(uuid("144b0f3d-2d59-5dd2-b012-908ec3e06435"))
ABI::Windows::Foundation::Collections::IVectorView<ABI::Windows::Globalization::Language *> : IVectorView_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Globalization::Language *, ABI::Windows::Globalization::ILanguage *>>
{
    static const wchar_t *z_get_rc_name_impl()
    {
        return L"Windows.Foundation.Collections.IVectorView`1<Windows.Globalization.Language>";
    }
};

#define DEFINE_IASYNC_OPERATION_CALLBACK(operation, operationid, handler, handlerid, resulttype) \
    struct operation;                                                                            \
    MIDL_INTERFACE(handlerid)                                                                    \
    handler:                                                                                     \
    IUnknown                                                                                     \
    {                                                                                            \
    public:                                                                                      \
        virtual HRESULT STDMETHODCALLTYPE Invoke(operation * asyncInfo, AsyncStatus status) = 0; \
    };                                                                                           \
    MIDL_INTERFACE(operationid)                                                                  \
    operation:                                                                                   \
public                                                                                           \
    IInspectable                                                                                 \
    {                                                                                            \
    public:                                                                                      \
        virtual HRESULT STDMETHODCALLTYPE put_Completed(handler * handler) = 0;                  \
        virtual HRESULT STDMETHODCALLTYPE get_Completed(handler * *handler) = 0;                 \
        virtual HRESULT STDMETHODCALLTYPE GetResults(resulttype * *results) = 0;                 \
    };

namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("aa94d8e9-caef-53f6-823d-91b6e8340510"))
            IAsyncOperation<ABI::Windows::Graphics::Imaging::BitmapDecoder *> : IAsyncOperation_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Graphics::Imaging::BitmapDecoder *, ABI::Windows::Graphics::Imaging::IBitmapDecoder *>>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.IAsyncOperation`1<Windows.Graphics.Imaging.BitmapDecoder>";
                }
            };
            typedef IAsyncOperation<ABI::Windows::Graphics::Imaging::BitmapDecoder *> __FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder_t;
#define __FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder ABI::Windows::Foundation::__FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder_t
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("bb6514f2-3cfb-566f-82bc-60aabd302d53"))
            IAsyncOperationCompletedHandler<ABI::Windows::Graphics::Imaging::BitmapDecoder *> : IAsyncOperationCompletedHandler_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Graphics::Imaging::BitmapDecoder *, ABI::Windows::Graphics::Imaging::IBitmapDecoder *>>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.AsyncOperationCompletedHandler`1<Windows.Graphics.Imaging.BitmapDecoder>";
                }
            };
            // Define a typedef for the parameterized interface specialization's mangled name.
            // This allows code which uses the mangled name for the parameterized interface to access the
            // correct parameterized interface specialization.
            typedef IAsyncOperationCompletedHandler<ABI::Windows::Graphics::Imaging::BitmapDecoder *> __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CBitmapDecoder_t;
#define __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CBitmapDecoder ABI::Windows::Foundation::__FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CBitmapDecoder_t
/* Foundation */ } /* Windows */
    } /* ABI */
}
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Imaging
            {
                class SoftwareBitmap;
            } /* Imaging */
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Imaging
            {
                MIDL_INTERFACE("689e0708-7eef-483f-963f-da938818e073")
                ISoftwareBitmap : public IInspectable{

                                  };

            } /* Imaging */
        } /* Graphics */
    } /* Windows */
} /* ABI */

namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                class OcrLine;
            } /* Ocr */
        } /* Media */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                MIDL_INTERFACE("9bd235b2-175b-3d6a-92e2-388c206e2f63")
                IOcrResult : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_Lines(
                        ABI::Windows::Foundation::Collections::IVectorView<ABI::Windows::Media::Ocr::OcrLine *> * *value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_TextAngle(
                        void **value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_Text(
                        HSTRING * value) = 0;
                };
            }
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                class OcrResult;
            } /* Ocr */
        } /* Media */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("989c1371-444a-5e7e-b197-9eaaf9d2829a"))
            IAsyncOperationCompletedHandler<ABI::Windows::Media::Ocr::OcrResult *> : IAsyncOperationCompletedHandler_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Media::Ocr::OcrResult *, ABI::Windows::Media::Ocr::IOcrResult *>>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.AsyncOperationCompletedHandler`1<Windows.Media.Ocr.OcrResult>";
                }
            };
            // Define a typedef for the parameterized interface specialization's mangled name.
            // This allows code which uses the mangled name for the parameterized interface to access the
            // correct parameterized interface specialization.
            typedef IAsyncOperationCompletedHandler<ABI::Windows::Media::Ocr::OcrResult *> __FIAsyncOperationCompletedHandler_1_Windows__CMedia__COcr__COcrResult_t;
#define __FIAsyncOperationCompletedHandler_1_Windows__CMedia__COcr__COcrResult ABI::Windows::Foundation::__FIAsyncOperationCompletedHandler_1_Windows__CMedia__COcr__COcrResult_t
/* Foundation */ } /* Windows */
    } /* ABI */
}
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("c7d7118e-ae36-59c0-ac76-7badee711c8b"))
            IAsyncOperation<ABI::Windows::Media::Ocr::OcrResult *> : IAsyncOperation_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Media::Ocr::OcrResult *, ABI::Windows::Media::Ocr::IOcrResult *>>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.IAsyncOperation`1<Windows.Media.Ocr.OcrResult>";
                }
            };
            typedef IAsyncOperation<ABI::Windows::Media::Ocr::OcrResult *> __FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult_t;
#define __FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult ABI::Windows::Foundation::__FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult_t
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                MIDL_INTERFACE("5a14bc41-5b76-3140-b680-8825562683ac")
                IOcrEngine : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE RecognizeAsync(
                        ABI::Windows::Graphics::Imaging::ISoftwareBitmap * bitmap,
                        __FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult * *result) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_RecognizerLanguage(
                        ABI::Windows::Globalization::ILanguage * *value) = 0;
                };
            }
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("b699b653-33ed-5e2d-a75f-02bf90e32619"))
            IAsyncOperationCompletedHandler<ABI::Windows::Graphics::Imaging::SoftwareBitmap *> : IAsyncOperationCompletedHandler_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Graphics::Imaging::SoftwareBitmap *, ABI::Windows::Graphics::Imaging::ISoftwareBitmap *>>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.AsyncOperationCompletedHandler`1<Windows.Graphics.Imaging.SoftwareBitmap>";
                }
            };
            // Define a typedef for the parameterized interface specialization's mangled name.
            // This allows code which uses the mangled name for the parameterized interface to access the
            // correct parameterized interface specialization.
            typedef IAsyncOperationCompletedHandler<ABI::Windows::Graphics::Imaging::SoftwareBitmap *> __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CSoftwareBitmap_t;
#define __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CSoftwareBitmap ABI::Windows::Foundation::__FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CSoftwareBitmap_t
/* Foundation */ } /* Windows */
    } /* ABI */
}
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("c4a10980-714b-5501-8da2-dbdacce70f73"))
            IAsyncOperation<ABI::Windows::Graphics::Imaging::SoftwareBitmap *> : IAsyncOperation_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Graphics::Imaging::SoftwareBitmap *, ABI::Windows::Graphics::Imaging::ISoftwareBitmap *>>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.IAsyncOperation`1<Windows.Graphics.Imaging.SoftwareBitmap>";
                }
            };
            typedef IAsyncOperation<ABI::Windows::Graphics::Imaging::SoftwareBitmap *> __FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap_t;
#define __FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap ABI::Windows::Foundation::__FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap_t
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Imaging
            {
                MIDL_INTERFACE("438ccb26-bcef-4e95-bad6-23a822e58d01")
                IBitmapDecoderStatics : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_BmpDecoderId(
                        GUID * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_JpegDecoderId(
                        GUID * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_PngDecoderId(
                        GUID * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_TiffDecoderId(
                        GUID * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_GifDecoderId(
                        GUID * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_JpegXRDecoderId(
                        GUID * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_IcoDecoderId(
                        GUID * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetDecoderInformationEnumerator(
                        void **decoderInformationEnumerator) = 0;
                    virtual HRESULT STDMETHODCALLTYPE CreateAsync(
                        ABI::Windows::Storage::Streams::IRandomAccessStream * stream,
                        __FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder * *asyncInfo) = 0;
                    virtual HRESULT STDMETHODCALLTYPE CreateWithIdAsync(
                        GUID decoderId,
                        ABI::Windows::Storage::Streams::IRandomAccessStream * stream,
                        void **asyncInfo) = 0;
                };
            }
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                MIDL_INTERFACE("0043a16f-e31f-3a24-899c-d444bd088124")
                IOcrLine : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_Words(
                        ABI::Windows::Foundation::Collections::IVectorView<ABI::Windows::Media::Ocr::OcrWord *> * *value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_Text(
                        HSTRING * value) = 0;
                };
            }
        }
    }
}
template <>
struct __declspec(uuid("60c76eac-8875-5ddb-a19b-65a3936279ea"))
ABI::Windows::Foundation::Collections::IVectorView<ABI::Windows::Media::Ocr::OcrLine *> : IVectorView_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Media::Ocr::OcrLine *, ABI::Windows::Media::Ocr::IOcrLine *>>
{
    static const wchar_t *z_get_rc_name_impl()
    {
        return L"Windows.Foundation.Collections.IVectorView`1<Windows.Media.Ocr.OcrLine>";
    }
};

namespace ABI
{
    namespace Windows
    {
        namespace Media
        {
            namespace Ocr
            {
                MIDL_INTERFACE("5bffa85a-3384-3540-9940-699120d428a8")
                IOcrEngineStatics : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_MaxImageDimension(
                        UINT32 * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_AvailableRecognizerLanguages(
                        ABI::Windows::Foundation::Collections::IVectorView<ABI::Windows::Globalization::Language *> * *value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE IsLanguageSupported(
                        ABI::Windows::Globalization::ILanguage * language,
                        boolean * result) = 0;
                    virtual HRESULT STDMETHODCALLTYPE TryCreateFromLanguage(
                        ABI::Windows::Globalization::ILanguage * language,
                        ABI::Windows::Media::Ocr::IOcrEngine * *result) = 0;
                    virtual HRESULT STDMETHODCALLTYPE TryCreateFromUserProfileLanguages(
                        ABI::Windows::Media::Ocr::IOcrEngine * *result) = 0;
                };
            }
        }
    }
}
STDAPI CreateRandomAccessStreamOverStream(_In_ IStream *stream, _In_ BSOS_OPTIONS options, _In_ REFIID riid, _COM_Outptr_ void **ppv);
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Imaging
            {
                MIDL_INTERFACE("fe287c9a-420c-4963-87ad-691436e08383")
                IBitmapFrameWithSoftwareBitmap : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE GetSoftwareBitmapAsync(
                        __FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap * *value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetSoftwareBitmapConvertedAsync() = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetSoftwareBitmapTransformedAsync() = 0;
                };
            } /* Imaging */
        } /* Graphics */
    } /* Windows */
} /* ABI */

//////////////////////////////////OCR
//////////////////////////////////Capture
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace DirectX
            {
                namespace Direct3D11
                {
                    MIDL_INTERFACE("0bf4a146-13c1-4694-bee3-7abf15eaf586")
                    IDirect3DSurface : public IInspectable{};

                } /* Direct3D11 */
            } /* DirectX */
        } /* Graphics */
    } /* Windows */
} /* ABI */

namespace Windows
{
    namespace Graphics
    {
        namespace DirectX
        {
            namespace Direct3D11
            {

                struct __declspec(uuid("A9B3D012-3DF2-4EE3-B8D1-8695F457D3C1"))
                IDirect3DDxgiInterfaceAccess : public IUnknown
                {
                    IFACEMETHOD(GetInterface)(REFIID iid, _COM_Outptr_ void **p) = 0;
                };

            }
        }
    }
} /* Windows::Graphics::DirectX::Direct3D11 */
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                MIDL_INTERFACE("814e42a9-f70f-4ad7-939b-fddcc6eb880d")
                IGraphicsCaptureSession : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE StartCapture(void) = 0;
                };

            } /* Capture */
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                MIDL_INTERFACE("79c3f95b-31f7-4ec2-a464-632ef5d30760")
                IGraphicsCaptureItem : public IInspectable{};
            }
        }
    }
}

namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                MIDL_INTERFACE("fa50c623-38da-4b32-acf3-fa9734ad800e")
                IDirect3D11CaptureFrame : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_Surface(
                        ABI::Windows::Graphics::DirectX::Direct3D11::IDirect3DSurface * *value) = 0;
                };

            } /* Capture */
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace DirectX
            {
                namespace Direct3D11
                {
                    MIDL_INTERFACE("a37624ab-8d5f-4650-9d3e-9eae3d9bc670")
                    IDirect3DDevice : public IInspectable
                    {
                    public:
                        virtual HRESULT STDMETHODCALLTYPE Trim(void) = 0;
                    };

                } /* Direct3D11 */
            } /* DirectX */
        } /* Graphics */
    } /* Windows */
} /* ABI */

namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace DirectX
            {
                enum DirectXPixelFormat : int
                {
                    DirectXPixelFormat_Unknown = 0,
                    DirectXPixelFormat_R32G32B32A32Typeless = 1,
                    DirectXPixelFormat_R32G32B32A32Float = 2,
                    DirectXPixelFormat_R32G32B32A32UInt = 3,
                    DirectXPixelFormat_R32G32B32A32Int = 4,
                    DirectXPixelFormat_R32G32B32Typeless = 5,
                    DirectXPixelFormat_R32G32B32Float = 6,
                    DirectXPixelFormat_R32G32B32UInt = 7,
                    DirectXPixelFormat_R32G32B32Int = 8,
                    DirectXPixelFormat_R16G16B16A16Typeless = 9,
                    DirectXPixelFormat_R16G16B16A16Float = 10,
                    DirectXPixelFormat_R16G16B16A16UIntNormalized = 11,
                    DirectXPixelFormat_R16G16B16A16UInt = 12,
                    DirectXPixelFormat_R16G16B16A16IntNormalized = 13,
                    DirectXPixelFormat_R16G16B16A16Int = 14,
                    DirectXPixelFormat_R32G32Typeless = 15,
                    DirectXPixelFormat_R32G32Float = 16,
                    DirectXPixelFormat_R32G32UInt = 17,
                    DirectXPixelFormat_R32G32Int = 18,
                    DirectXPixelFormat_R32G8X24Typeless = 19,
                    DirectXPixelFormat_D32FloatS8X24UInt = 20,
                    DirectXPixelFormat_R32FloatX8X24Typeless = 21,
                    DirectXPixelFormat_X32TypelessG8X24UInt = 22,
                    DirectXPixelFormat_R10G10B10A2Typeless = 23,
                    DirectXPixelFormat_R10G10B10A2UIntNormalized = 24,
                    DirectXPixelFormat_R10G10B10A2UInt = 25,
                    DirectXPixelFormat_R11G11B10Float = 26,
                    DirectXPixelFormat_R8G8B8A8Typeless = 27,
                    DirectXPixelFormat_R8G8B8A8UIntNormalized = 28,
                    DirectXPixelFormat_R8G8B8A8UIntNormalizedSrgb = 29,
                    DirectXPixelFormat_R8G8B8A8UInt = 30,
                    DirectXPixelFormat_R8G8B8A8IntNormalized = 31,
                    DirectXPixelFormat_R8G8B8A8Int = 32,
                    DirectXPixelFormat_R16G16Typeless = 33,
                    DirectXPixelFormat_R16G16Float = 34,
                    DirectXPixelFormat_R16G16UIntNormalized = 35,
                    DirectXPixelFormat_R16G16UInt = 36,
                    DirectXPixelFormat_R16G16IntNormalized = 37,
                    DirectXPixelFormat_R16G16Int = 38,
                    DirectXPixelFormat_R32Typeless = 39,
                    DirectXPixelFormat_D32Float = 40,
                    DirectXPixelFormat_R32Float = 41,
                    DirectXPixelFormat_R32UInt = 42,
                    DirectXPixelFormat_R32Int = 43,
                    DirectXPixelFormat_R24G8Typeless = 44,
                    DirectXPixelFormat_D24UIntNormalizedS8UInt = 45,
                    DirectXPixelFormat_R24UIntNormalizedX8Typeless = 46,
                    DirectXPixelFormat_X24TypelessG8UInt = 47,
                    DirectXPixelFormat_R8G8Typeless = 48,
                    DirectXPixelFormat_R8G8UIntNormalized = 49,
                    DirectXPixelFormat_R8G8UInt = 50,
                    DirectXPixelFormat_R8G8IntNormalized = 51,
                    DirectXPixelFormat_R8G8Int = 52,
                    DirectXPixelFormat_R16Typeless = 53,
                    DirectXPixelFormat_R16Float = 54,
                    DirectXPixelFormat_D16UIntNormalized = 55,
                    DirectXPixelFormat_R16UIntNormalized = 56,
                    DirectXPixelFormat_R16UInt = 57,
                    DirectXPixelFormat_R16IntNormalized = 58,
                    DirectXPixelFormat_R16Int = 59,
                    DirectXPixelFormat_R8Typeless = 60,
                    DirectXPixelFormat_R8UIntNormalized = 61,
                    DirectXPixelFormat_R8UInt = 62,
                    DirectXPixelFormat_R8IntNormalized = 63,
                    DirectXPixelFormat_R8Int = 64,
                    DirectXPixelFormat_A8UIntNormalized = 65,
                    DirectXPixelFormat_R1UIntNormalized = 66,
                    DirectXPixelFormat_R9G9B9E5SharedExponent = 67,
                    DirectXPixelFormat_R8G8B8G8UIntNormalized = 68,
                    DirectXPixelFormat_G8R8G8B8UIntNormalized = 69,
                    DirectXPixelFormat_BC1Typeless = 70,
                    DirectXPixelFormat_BC1UIntNormalized = 71,
                    DirectXPixelFormat_BC1UIntNormalizedSrgb = 72,
                    DirectXPixelFormat_BC2Typeless = 73,
                    DirectXPixelFormat_BC2UIntNormalized = 74,
                    DirectXPixelFormat_BC2UIntNormalizedSrgb = 75,
                    DirectXPixelFormat_BC3Typeless = 76,
                    DirectXPixelFormat_BC3UIntNormalized = 77,
                    DirectXPixelFormat_BC3UIntNormalizedSrgb = 78,
                    DirectXPixelFormat_BC4Typeless = 79,
                    DirectXPixelFormat_BC4UIntNormalized = 80,
                    DirectXPixelFormat_BC4IntNormalized = 81,
                    DirectXPixelFormat_BC5Typeless = 82,
                    DirectXPixelFormat_BC5UIntNormalized = 83,
                    DirectXPixelFormat_BC5IntNormalized = 84,
                    DirectXPixelFormat_B5G6R5UIntNormalized = 85,
                    DirectXPixelFormat_B5G5R5A1UIntNormalized = 86,
                    DirectXPixelFormat_B8G8R8A8UIntNormalized = 87,
                    DirectXPixelFormat_B8G8R8X8UIntNormalized = 88,
                    DirectXPixelFormat_R10G10B10XRBiasA2UIntNormalized = 89,
                    DirectXPixelFormat_B8G8R8A8Typeless = 90,
                    DirectXPixelFormat_B8G8R8A8UIntNormalizedSrgb = 91,
                    DirectXPixelFormat_B8G8R8X8Typeless = 92,
                    DirectXPixelFormat_B8G8R8X8UIntNormalizedSrgb = 93,
                    DirectXPixelFormat_BC6HTypeless = 94,
                    DirectXPixelFormat_BC6H16UnsignedFloat = 95,
                    DirectXPixelFormat_BC6H16Float = 96,
                    DirectXPixelFormat_BC7Typeless = 97,
                    DirectXPixelFormat_BC7UIntNormalized = 98,
                    DirectXPixelFormat_BC7UIntNormalizedSrgb = 99,
                    DirectXPixelFormat_Ayuv = 100,
                    DirectXPixelFormat_Y410 = 101,
                    DirectXPixelFormat_Y416 = 102,
                    DirectXPixelFormat_NV12 = 103,
                    DirectXPixelFormat_P010 = 104,
                    DirectXPixelFormat_P016 = 105,
                    DirectXPixelFormat_Opaque420 = 106,
                    DirectXPixelFormat_Yuy2 = 107,
                    DirectXPixelFormat_Y210 = 108,
                    DirectXPixelFormat_Y216 = 109,
                    DirectXPixelFormat_NV11 = 110,
                    DirectXPixelFormat_AI44 = 111,
                    DirectXPixelFormat_IA44 = 112,
                    DirectXPixelFormat_P8 = 113,
                    DirectXPixelFormat_A8P8 = 114,
                    DirectXPixelFormat_B4G4R4A4UIntNormalized = 115,
                    DirectXPixelFormat_P208 = 130,
                    DirectXPixelFormat_V208 = 131,
                    DirectXPixelFormat_V408 = 132,
#if WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
                    DirectXPixelFormat_SamplerFeedbackMinMipOpaque = 189,
#endif // WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
#if WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
                    DirectXPixelFormat_SamplerFeedbackMipRegionUsedOpaque = 190,
#endif // WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
                };
            }
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                class GraphicsCaptureItem;
            } /* Capture */
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("e9c610c0-a68c-5bd9-8021-8589346eeee2"))
            ITypedEventHandler<ABI::Windows::Graphics::Capture::GraphicsCaptureItem *, IInspectable *> : ITypedEventHandler_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Graphics::Capture::GraphicsCaptureItem *, ABI::Windows::Graphics::Capture::IGraphicsCaptureItem *>, IInspectable *>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.TypedEventHandler`2<Windows.Graphics.Capture.GraphicsCaptureItem, Object>";
                }
            };
        }
    }
}
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                class Direct3D11CaptureFramePool;
            } /* Capture */
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                interface IDirect3D11CaptureFramePool;
            } /* Capture */
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            template <>
            struct __declspec(uuid("51a947f7-79cf-5a3e-a3a5-1289cfa6dfe8"))
            ITypedEventHandler<ABI::Windows::Graphics::Capture::Direct3D11CaptureFramePool *, IInspectable *> : ITypedEventHandler_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Graphics::Capture::Direct3D11CaptureFramePool *, ABI::Windows::Graphics::Capture::IDirect3D11CaptureFramePool *>, IInspectable *>
            {
                static const wchar_t *z_get_rc_name_impl()
                {
                    return L"Windows.Foundation.TypedEventHandler`2<Windows.Graphics.Capture.Direct3D11CaptureFramePool, Object>";
                }
            };
            // Define a typedef for the parameterized interface specialization's mangled name.
            // This allows code which uses the mangled name for the parameterized interface to access the
            // correct parameterized interface specialization.
            typedef ITypedEventHandler<ABI::Windows::Graphics::Capture::Direct3D11CaptureFramePool *, IInspectable *> __FITypedEventHandler_2_Windows__CGraphics__CCapture__CDirect3D11CaptureFramePool_IInspectable_t;
#define __FITypedEventHandler_2_Windows__CGraphics__CCapture__CDirect3D11CaptureFramePool_IInspectable ABI::Windows::Foundation::__FITypedEventHandler_2_Windows__CGraphics__CCapture__CDirect3D11CaptureFramePool_IInspectable_t
/* Foundation */ } /* Windows */
    } /* ABI */
}
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                MIDL_INTERFACE("24eb6d22-1975-422e-82e7-780dbd8ddf24")
                IDirect3D11CaptureFramePool : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE Recreate(
                        ABI::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice * device,
                        ABI::Windows::Graphics::DirectX::DirectXPixelFormat pixelFormat,
                        INT32 numberOfBuffers,
                        ABI::Windows::Graphics::SizeInt32 size) = 0;
                    virtual HRESULT STDMETHODCALLTYPE TryGetNextFrame(
                        ABI::Windows::Graphics::Capture::IDirect3D11CaptureFrame * *result) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_FrameArrived(
                        __FITypedEventHandler_2_Windows__CGraphics__CCapture__CDirect3D11CaptureFramePool_IInspectable * handler,
                        EventRegistrationToken * token) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_FrameArrived(
                        EventRegistrationToken token) = 0;
                    virtual HRESULT STDMETHODCALLTYPE CreateCaptureSession(
                        ABI::Windows::Graphics::Capture::IGraphicsCaptureItem * item,
                        ABI::Windows::Graphics::Capture::IGraphicsCaptureSession * *result) = 0;
                };
            };
        }
    }
}

namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                MIDL_INTERFACE("7784056a-67aa-4d53-ae54-1088d5a8ca21")
                IDirect3D11CaptureFramePoolStatics : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE Create(
                        ABI::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice * device,
                        ABI::Windows::Graphics::DirectX::DirectXPixelFormat pixelFormat,
                        INT32 numberOfBuffers,
                        ABI::Windows::Graphics::SizeInt32 size,
                        ABI::Windows::Graphics::Capture::IDirect3D11CaptureFramePool * *result) = 0;
                };

            } /* Capture */
        } /* Graphics */
    } /* Windows */
} /* ABI */

extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Graphics_Capture_Direct3D11CaptureFramePool[] = L"Windows.Graphics.Capture.Direct3D11CaptureFramePool";

#undef INTERFACE
#define INTERFACE IGraphicsCaptureItemInterop
DECLARE_INTERFACE_IID_(IGraphicsCaptureItemInterop, IUnknown, "3628E81B-3CAC-4C60-B7F4-23CE0E0C3356")
{
    IFACEMETHOD(CreateForWindow)(
        HWND window,
        REFIID riid,
        _COM_Outptr_ void **result) PURE;

    IFACEMETHOD(CreateForMonitor)(
        HMONITOR monitor,
        REFIID riid,
        _COM_Outptr_ void **result) PURE;
};

#undef INTERFACE

extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Graphics_Capture_GraphicsCaptureItem[] = L"Windows.Graphics.Capture.GraphicsCaptureItem";
namespace ABI
{
    namespace Windows
    {
        namespace Graphics
        {
            namespace Capture
            {
                MIDL_INTERFACE("2c39ae40-7d2e-5044-804e-8b6799d4cf9e")
                IGraphicsCaptureSession2 : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_IsCursorCaptureEnabled(
                        boolean * value) = 0;
                    virtual HRESULT STDMETHODCALLTYPE put_IsCursorCaptureEnabled(
                        boolean value) = 0;
                };
            } /* Capture */
        } /* Graphics */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            MIDL_INTERFACE("30d5a829-7fa4-4026-83bb-d75bae4ea99e")
            IClosable : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE Close(void) = 0;
            };
        }
    }
}

STDAPI CreateDirect3D11DeviceFromDXGIDevice(
    _In_ IDXGIDevice *dxgiDevice,
    _COM_Outptr_ IInspectable **graphicsDevice);
//////////////////////////////////Capture

namespace ABI
{
    namespace Windows
    {
        namespace Storage
        {
            MIDL_INTERFACE("4207a996-ca2f-42f7-bde8-8b10457a7f30")
            IStorageItem : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE RenameAsyncOverloadDefaultOptions() = 0;
                virtual HRESULT STDMETHODCALLTYPE RenameAsync() = 0;
                virtual HRESULT STDMETHODCALLTYPE DeleteAsyncOverloadDefaultOptions() = 0;
                virtual HRESULT STDMETHODCALLTYPE DeleteAsync() = 0;
                virtual HRESULT STDMETHODCALLTYPE GetBasicPropertiesAsync() = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Name(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Path(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Attributes() = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DateCreated() = 0;
                virtual HRESULT STDMETHODCALLTYPE IsOfType() = 0;
            };

            //  MIDL_CONST_ID IID &IID_IStorageItem = __uuidof(IStorageItem);
        } /* Storage */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Storage
        {
            MIDL_INTERFACE("72d1cb78-b3ef-4f75-a80b-6fd9dae2944b")
            IStorageFolder : public IInspectable{};

            MIDL_CONST_ID IID &IID_IStorageFolder = __uuidof(IStorageFolder);
        } /* Storage */
    } /* Windows */
} /* ABI */

namespace ABI
{
    namespace Windows
    {
        namespace ApplicationModel
        {
            typedef struct PackageVersion PackageVersion;
        } /* ApplicationModel */
    } /* Windows */
} /* ABI */

namespace ABI
{
    namespace Windows
    {
        namespace System
        {
            typedef enum ProcessorArchitecture : int ProcessorArchitecture;
        } /* System */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace ApplicationModel
        {
            MIDL_INTERFACE("1adb665e-37c7-4790-9980-dd7ae74e8bb2")
            IPackageId : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE get_Name(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Version(
                    ABI::Windows::ApplicationModel::PackageVersion * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Architecture(
                    ABI::Windows::System::ProcessorArchitecture * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_ResourceId(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Publisher(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PublisherId(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_FullName(
                    HSTRING * value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_FamilyName(
                    HSTRING * value) = 0;
            };

            //  MIDL_CONST_ID IID &IID_IPackageId = __uuidof(IPackageId);
        } /* ApplicationModel */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace ApplicationModel
        {
            class Package;
        } /* ApplicationModel */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace ApplicationModel
        {
            MIDL_INTERFACE("163c792f-bd75-413c-bf23-b1fe7b95d825")
            IPackage : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE get_Id(
                    ABI::Windows::ApplicationModel::IPackageId * *value) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_InstalledLocation(
                    ABI::Windows::Storage::IStorageFolder * *value) = 0;
            };

            MIDL_CONST_ID IID &IID_IPackage = __uuidof(IPackage);
        } /* ApplicationModel */
    } /* Windows */
} /* ABI */
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            namespace Collections
            {
                template <>
                struct __declspec(uuid("69ad6aa7-0c49-5f27-a5eb-ef4d59467b6d"))
                IIterable<ABI::Windows::ApplicationModel::Package *> : IIterable_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::ApplicationModel::Package *, ABI::Windows::ApplicationModel::IPackage *>>
                {
                    static const wchar_t *z_get_rc_name_impl()
                    {
                        return L"Windows.Foundation.Collections.IIterable`1<Windows.ApplicationModel.Package>";
                    }
                };
                // Define a typedef for the parameterized interface specialization's mangled name.
                // This allows code which uses the mangled name for the parameterized interface to access the
                // correct parameterized interface specialization.
                typedef IIterable<ABI::Windows::ApplicationModel::Package *> __FIIterable_1_Windows__CApplicationModel__CPackage_t;
#define __FIIterable_1_Windows__CApplicationModel__CPackage ABI::Windows::Foundation::Collections::__FIIterable_1_Windows__CApplicationModel__CPackage_t
/* Collections */ } /* Foundation */
        } /* Windows */
    } /* ABI */
}

namespace ABI
{
    namespace Windows
    {
        namespace Management
        {
            namespace Deployment
            {
                MIDL_INTERFACE("9a7d4b65-5e8f-4fc7-a2e5-7f6925cb8b53")
                IPackageManager : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE AddPackageAsync() = 0;
                    virtual HRESULT STDMETHODCALLTYPE UpdatePackageAsync() = 0;
                    virtual HRESULT STDMETHODCALLTYPE RemovePackageAsync() = 0;
                    virtual HRESULT STDMETHODCALLTYPE StagePackageAsync() = 0;
                    virtual HRESULT STDMETHODCALLTYPE RegisterPackageAsync() = 0;
                    virtual HRESULT STDMETHODCALLTYPE FindPackages() = 0;
                    virtual HRESULT STDMETHODCALLTYPE FindPackagesByUserSecurityId(
                        HSTRING userSecurityId,
                        __FIIterable_1_Windows__CApplicationModel__CPackage * *packageCollection) = 0;
                };

                MIDL_CONST_ID IID &IID_IPackageManager = __uuidof(IPackageManager);
            } /* Deployment */
        } /* Management */
    } /* Windows */
} /* ABI */
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Management_Deployment_PackageManager[] = L"Windows.Management.Deployment.PackageManager";
namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            namespace Collections
            {
                template <>
                struct __declspec(uuid("0217f069-025c-5ee6-a87f-e782e3b623ae"))
                IIterator<ABI::Windows::ApplicationModel::Package *> : IIterator_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::ApplicationModel::Package *, ABI::Windows::ApplicationModel::IPackage *>>
                {
                    static const wchar_t *z_get_rc_name_impl()
                    {
                        return L"Windows.Foundation.Collections.IIterator`1<Windows.ApplicationModel.Package>";
                    }
                };
                // Define a typedef for the parameterized interface specialization's mangled name.
                // This allows code which uses the mangled name for the parameterized interface to access the
                // correct parameterized interface specialization.
                typedef IIterator<ABI::Windows::ApplicationModel::Package *> __FIIterator_1_Windows__CApplicationModel__CPackage_t;
#define __FIIterator_1_Windows__CApplicationModel__CPackage ABI::Windows::Foundation::Collections::__FIIterator_1_Windows__CApplicationModel__CPackage_t
/* Collections */ } /* Foundation */
        } /* Windows */
    } /* ABI */
}