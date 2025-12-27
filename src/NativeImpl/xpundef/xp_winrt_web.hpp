#define ____x_ABI_CWindows_CFoundation_CIPropertyValueStatics_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Foundation_IPropertyValueStatics[] = L"Windows.Foundation.IPropertyValueStatics";
namespace ABI {
    namespace Windows {
        namespace Foundation {
            MIDL_INTERFACE("629bdbc8-d932-4ff4-96b9-8d96c5c1e858")
            IPropertyValueStatics : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE CreateEmpty( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt8( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInt16( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt16( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInt32( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt32( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInt64( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt64( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateSingle( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateDouble( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateChar16( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateBoolean( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateString( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInspectable( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateGuid( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateDateTime( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateTimeSpan( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreatePoint( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateSize( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateRect(  
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt8Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInt16Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt16Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInt32Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt32Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInt64Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateUInt64Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateSingleArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateDoubleArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateChar16Array( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateBooleanArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateStringArray(
                    UINT32 valueLength,
                    HSTRING* value,
                    IInspectable** propertyValue
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateInspectableArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateGuidArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateDateTimeArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateTimeSpanArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreatePointArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateSizeArray( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateRectArray( 
                    ) = 0;
            };

            MIDL_CONST_ID IID& IID_IPropertyValueStatics = __uuidof(IPropertyValueStatics);
        } /* Foundation */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CFoundation_CIPropertyValueStatics;

#define ____x_ABI_CWindows_CFoundation_CIUriRuntimeClass_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Foundation_IUriRuntimeClass[] = L"Windows.Foundation.IUriRuntimeClass";
namespace ABI {
    namespace Windows {
        namespace Foundation {
            MIDL_INTERFACE("9e365e57-48b2-4160-956f-c7385120bbfc")
            IUriRuntimeClass : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE get_AbsoluteUri(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DisplayUri(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Domain(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Extension(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Fragment(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Host(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Password(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Path(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Query(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_QueryParsed( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_RawUri(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SchemeName(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_UserName(
                    HSTRING* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Port(
                    INT32* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Suspicious(
                    boolean* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE Equals( 
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CombineUri( 
                    ) = 0;
            };

            MIDL_CONST_ID IID& IID_IUriRuntimeClass = __uuidof(IUriRuntimeClass);
        } /* Foundation */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CFoundation_CIUriRuntimeClass;

#define ____x_ABI_CWindows_CFoundation_CIUriRuntimeClassFactory_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Foundation_IUriRuntimeClassFactory[] = L"Windows.Foundation.IUriRuntimeClassFactory";
namespace ABI {
    namespace Windows {
        namespace Foundation {
            MIDL_INTERFACE("44a9796f-723e-4fdf-a218-033e75b0c084")
            IUriRuntimeClassFactory : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE CreateUri(
                    HSTRING uri,
                    ABI::Windows::Foundation::IUriRuntimeClass** instance
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE CreateWithRelativeUri(
                    HSTRING baseUri,
                    HSTRING relativeUri,
                    ABI::Windows::Foundation::IUriRuntimeClass** instance
                    ) = 0;
            };

            MIDL_CONST_ID IID& IID_IUriRuntimeClassFactory = __uuidof(IUriRuntimeClassFactory);
        } /* Foundation */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CFoundation_CIUriRuntimeClassFactory;

namespace ABI {
    namespace Windows {
        namespace UI {
            struct Color
            {
                BYTE A;
                BYTE R;
                BYTE G;
                BYTE B;
            };
        } /* UI */
    } /* Windows */
} /* ABI */

#define ____x_ABI_CWindows_CUI_CIColorsStatics_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_UI_IColorsStatics[] = L"Windows.UI.IColorsStatics";
namespace ABI {
    namespace Windows {
        namespace UI {
            MIDL_INTERFACE("cff52e04-cca6-4614-a17e-754910c84a99")
            IColorsStatics : public IInspectable
            {
            public:
                virtual HRESULT STDMETHODCALLTYPE get_AliceBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_AntiqueWhite(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Aqua(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Aquamarine(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Azure(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Beige(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Bisque(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Black(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_BlanchedAlmond(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Blue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_BlueViolet(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Brown(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_BurlyWood(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_CadetBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Chartreuse(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Chocolate(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Coral(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_CornflowerBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Cornsilk(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Crimson(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Cyan(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkCyan(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkGoldenrod(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkGray(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkKhaki(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkMagenta(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkOliveGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkOrange(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkOrchid(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkRed(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkSalmon(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkSeaGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkSlateBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkSlateGray(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkTurquoise(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DarkViolet(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DeepPink(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DeepSkyBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DimGray(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_DodgerBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Firebrick(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_FloralWhite(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_ForestGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Fuchsia(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Gainsboro(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_GhostWhite(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Gold(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Goldenrod(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Gray(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Green(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_GreenYellow(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Honeydew(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_HotPink(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_IndianRed(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Indigo(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Ivory(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Khaki(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Lavender(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LavenderBlush(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LawnGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LemonChiffon(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightCoral(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightCyan(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightGoldenrodYellow(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightGray(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightPink(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightSalmon(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightSeaGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightSkyBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightSlateGray(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightSteelBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LightYellow(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Lime(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_LimeGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Linen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Magenta(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Maroon(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumAquamarine(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumOrchid(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumPurple(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumSeaGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumSlateBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumSpringGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumTurquoise(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MediumVioletRed(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MidnightBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MintCream(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_MistyRose(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Moccasin(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_NavajoWhite(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Navy(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_OldLace(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Olive(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_OliveDrab(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Orange(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_OrangeRed(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Orchid(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PaleGoldenrod(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PaleGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PaleTurquoise(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PaleVioletRed(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PapayaWhip(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PeachPuff(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Peru(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Pink(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Plum(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_PowderBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Purple(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Red(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_RosyBrown(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_RoyalBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SaddleBrown(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Salmon(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SandyBrown(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SeaGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SeaShell(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Sienna(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Silver(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SkyBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SlateBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SlateGray(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Snow(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SpringGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_SteelBlue(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Tan(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Teal(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Thistle(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Tomato(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Transparent(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Turquoise(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Violet(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Wheat(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_White(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_WhiteSmoke(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_Yellow(
                    ABI::Windows::UI::Color* value
                    ) = 0;
                virtual HRESULT STDMETHODCALLTYPE get_YellowGreen(
                    ABI::Windows::UI::Color* value
                    ) = 0;
            };

            MIDL_CONST_ID IID& IID_IColorsStatics = __uuidof(IColorsStatics);
        } /* UI */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CUI_CIColorsStatics;


#if !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControlSettings_INTERFACE_DEFINED__)
#define ____x_ABI_CWindows_CWeb_CUI_CIWebViewControlSettings_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Web_UI_IWebViewControlSettings[] = L"Windows.Web.UI.IWebViewControlSettings";
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                MIDL_INTERFACE("c9967fbf-5e98-4cfd-8cce-27b0911e3de8")
                IWebViewControlSettings : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE put_IsJavaScriptEnabled(
                        boolean value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_IsJavaScriptEnabled(
                        boolean* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE put_IsIndexedDBEnabled(
                        boolean value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_IsIndexedDBEnabled(
                        boolean* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE put_IsScriptNotifyAllowed(
                        boolean value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_IsScriptNotifyAllowed(
                        boolean* value
                        ) = 0;
                };

                MIDL_CONST_ID IID& IID_IWebViewControlSettings = __uuidof(IWebViewControlSettings);
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CWeb_CUI_CIWebViewControlSettings;
#endif /* !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControlSettings_INTERFACE_DEFINED__) */


#ifndef DEF___FIAsyncOperation_1_HSTRING_USE
#define DEF___FIAsyncOperation_1_HSTRING_USE
#if !defined(RO_NO_TEMPLATE_NAME)
namespace ABI { namespace Windows { namespace Foundation {
template <>
struct __declspec(uuid("3e1fe603-f897-5263-b328-0806426b8a79"))
IAsyncOperation<HSTRING> : IAsyncOperation_impl<HSTRING>
{
    static const wchar_t* z_get_rc_name_impl()
    {
        return L"Windows.Foundation.IAsyncOperation`1<String>";
    }
};
// Define a typedef for the parameterized interface specialization's mangled name.
// This allows code which uses the mangled name for the parameterized interface to access the
// correct parameterized interface specialization.
typedef IAsyncOperation<HSTRING> __FIAsyncOperation_1_HSTRING_t;
#define __FIAsyncOperation_1_HSTRING ABI::Windows::Foundation::__FIAsyncOperation_1_HSTRING_t
/* Foundation */ } /* Windows */ } /* ABI */ }

#endif // !defined(RO_NO_TEMPLATE_NAME)
#endif /* DEF___FIAsyncOperation_1_HSTRING_USE */


#ifndef DEF___FIIterable_1_HSTRING_USE
#define DEF___FIIterable_1_HSTRING_USE
#if !defined(RO_NO_TEMPLATE_NAME)
namespace ABI { namespace Windows { namespace Foundation { namespace Collections {
template <>
struct __declspec(uuid("e2fcc7c1-3bfc-5a0b-b2b0-72e769d1cb7e"))
IIterable<HSTRING> : IIterable_impl<HSTRING>
{
    static const wchar_t* z_get_rc_name_impl()
    {
        return L"Windows.Foundation.Collections.IIterable`1<String>";
    }
};
// Define a typedef for the parameterized interface specialization's mangled name.
// This allows code which uses the mangled name for the parameterized interface to access the
// correct parameterized interface specialization.
typedef IIterable<HSTRING> __FIIterable_1_HSTRING_t;
#define __FIIterable_1_HSTRING ABI::Windows::Foundation::Collections::__FIIterable_1_HSTRING_t
/* Collections */ } /* Foundation */ } /* Windows */ } /* ABI */ }

#endif // !defined(RO_NO_TEMPLATE_NAME)
#endif /* DEF___FIIterable_1_HSTRING_USE */

#if !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControlNavigationStartingEventArgs_INTERFACE_DEFINED__)
#define ____x_ABI_CWindows_CWeb_CUI_CIWebViewControlNavigationStartingEventArgs_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Web_UI_IWebViewControlNavigationStartingEventArgs[] = L"Windows.Web.UI.IWebViewControlNavigationStartingEventArgs";
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                MIDL_INTERFACE("0c9057c5-0a08-41c7-863b-71e3a9549137")
                IWebViewControlNavigationStartingEventArgs : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_Uri(
                        ABI::Windows::Foundation::IUriRuntimeClass** value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_Cancel(
                        boolean* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE put_Cancel(
                        boolean value
                        ) = 0;
                };

                MIDL_CONST_ID IID& IID_IWebViewControlNavigationStartingEventArgs = __uuidof(IWebViewControlNavigationStartingEventArgs);
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CWeb_CUI_CIWebViewControlNavigationStartingEventArgs;
#endif /* !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControlNavigationStartingEventArgs_INTERFACE_DEFINED__) */

namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                class WebViewControlNavigationStartingEventArgs;
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                class IWebViewControl;
            }
        }
    }
}

#ifndef DEF___FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs_USE
#define DEF___FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs_USE
#if !defined(RO_NO_TEMPLATE_NAME)

namespace ABI { namespace Windows { namespace Foundation {
template <>
struct __declspec(uuid("e92e0bcc-9ae9-5b9b-a684-83dd8ee57775"))
ITypedEventHandler<ABI::Windows::Web::UI::IWebViewControl*, ABI::Windows::Web::UI::WebViewControlNavigationStartingEventArgs*> : ITypedEventHandler_impl<ABI::Windows::Web::UI::IWebViewControl*, ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Web::UI::WebViewControlNavigationStartingEventArgs*, ABI::Windows::Web::UI::IWebViewControlNavigationStartingEventArgs*>>
{
    static const wchar_t* z_get_rc_name_impl()
    {
        return L"Windows.Foundation.TypedEventHandler`2<Windows.Web.UI.IWebViewControl, Windows.Web.UI.WebViewControlNavigationStartingEventArgs>";
    }
};
// Define a typedef for the parameterized interface specialization's mangled name.
// This allows code which uses the mangled name for the parameterized interface to access the
// correct parameterized interface specialization.
typedef ITypedEventHandler<ABI::Windows::Web::UI::IWebViewControl*, ABI::Windows::Web::UI::WebViewControlNavigationStartingEventArgs*> __FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs_t;
#define __FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs ABI::Windows::Foundation::__FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs_t
/* Foundation */ } /* Windows */ } /* ABI */ }

#endif // !defined(RO_NO_TEMPLATE_NAME)
#endif /* DEF___FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs_USE */


namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                class WebViewControlScriptNotifyEventArgs;
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

#if !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControlScriptNotifyEventArgs_INTERFACE_DEFINED__)
#define ____x_ABI_CWindows_CWeb_CUI_CIWebViewControlScriptNotifyEventArgs_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Web_UI_IWebViewControlScriptNotifyEventArgs[] = L"Windows.Web.UI.IWebViewControlScriptNotifyEventArgs";
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                MIDL_INTERFACE("491de57b-6f49-41bb-b591-51b85b817037")
                IWebViewControlScriptNotifyEventArgs : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_Uri(
                        ABI::Windows::Foundation::IUriRuntimeClass** value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_Value(
                        HSTRING* value
                        ) = 0;
                };

                MIDL_CONST_ID IID& IID_IWebViewControlScriptNotifyEventArgs = __uuidof(IWebViewControlScriptNotifyEventArgs);
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CWeb_CUI_CIWebViewControlScriptNotifyEventArgs;
#endif /* !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControlScriptNotifyEventArgs_INTERFACE_DEFINED__) */

#ifndef DEF___FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs_USE
#define DEF___FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs_USE
#if !defined(RO_NO_TEMPLATE_NAME)
namespace ABI { namespace Windows { namespace Foundation {
template <>
struct __declspec(uuid("ee8b81d3-bbc2-55b0-877b-6ba86e3ad899"))
ITypedEventHandler<ABI::Windows::Web::UI::IWebViewControl*, ABI::Windows::Web::UI::WebViewControlScriptNotifyEventArgs*> : ITypedEventHandler_impl<ABI::Windows::Web::UI::IWebViewControl*, ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Web::UI::WebViewControlScriptNotifyEventArgs*, ABI::Windows::Web::UI::IWebViewControlScriptNotifyEventArgs*>>
{
    static const wchar_t* z_get_rc_name_impl()
    {
        return L"Windows.Foundation.TypedEventHandler`2<Windows.Web.UI.IWebViewControl, Windows.Web.UI.WebViewControlScriptNotifyEventArgs>";
    }
};
// Define a typedef for the parameterized interface specialization's mangled name.
// This allows code which uses the mangled name for the parameterized interface to access the
// correct parameterized interface specialization.
typedef ITypedEventHandler<ABI::Windows::Web::UI::IWebViewControl*, ABI::Windows::Web::UI::WebViewControlScriptNotifyEventArgs*> __FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs_t;
#define __FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs ABI::Windows::Foundation::__FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs_t
/* Foundation */ } /* Windows */ } /* ABI */ }

#endif // !defined(RO_NO_TEMPLATE_NAME)
#endif /* DEF___FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs_USE */



#if !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControl_INTERFACE_DEFINED__)
#define ____x_ABI_CWindows_CWeb_CUI_CIWebViewControl_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Web_UI_IWebViewControl[] = L"Windows.Web.UI.IWebViewControl";
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                MIDL_INTERFACE("3f921316-bc70-4bda-9136-c94370899fab")
                IWebViewControl : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE get_Source(
                        ABI::Windows::Foundation::IUriRuntimeClass** value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE put_Source(
                        ABI::Windows::Foundation::IUriRuntimeClass* source
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_DocumentTitle(
                        HSTRING* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_CanGoBack(
                        boolean* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_CanGoForward(
                        boolean* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE put_DefaultBackgroundColor(
                        ABI::Windows::UI::Color value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_DefaultBackgroundColor(
                        ABI::Windows::UI::Color* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_ContainsFullScreenElement(
                        boolean* value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_Settings(
                        ABI::Windows::Web::UI::IWebViewControlSettings** value
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE get_DeferredPermissionRequests(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GoForward(void) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GoBack(void) = 0;
                    virtual HRESULT STDMETHODCALLTYPE Refresh(void) = 0;
                    virtual HRESULT STDMETHODCALLTYPE Stop(void) = 0;
                    virtual HRESULT STDMETHODCALLTYPE Navigate(
                        ABI::Windows::Foundation::IUriRuntimeClass* source
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE NavigateToString(
                        HSTRING text
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE NavigateToLocalStreamUri(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE NavigateWithHttpRequestMessage(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE InvokeScriptAsync(
                        HSTRING scriptName,
                        __FIIterable_1_HSTRING* arguments,
                        __FIAsyncOperation_1_HSTRING** operation
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE CapturePreviewToStreamAsync(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE CaptureSelectedContentToDataPackageAsync(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE BuildLocalStreamUri(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE GetDeferredPermissionRequestById(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_NavigationStarting(
                        __FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlNavigationStartingEventArgs* handler,
                        EventRegistrationToken* token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_NavigationStarting(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_ContentLoading(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_ContentLoading(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_DOMContentLoaded(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_DOMContentLoaded(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_NavigationCompleted(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_NavigationCompleted(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_FrameNavigationStarting(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_FrameNavigationStarting(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_FrameContentLoading(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_FrameContentLoading(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_FrameDOMContentLoaded(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_FrameDOMContentLoaded(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_FrameNavigationCompleted(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_FrameNavigationCompleted(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_ScriptNotify(
                        __FITypedEventHandler_2_Windows__CWeb__CUI__CIWebViewControl_Windows__CWeb__CUI__CWebViewControlScriptNotifyEventArgs* handler,
                        EventRegistrationToken* token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_ScriptNotify(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_LongRunningScriptDetected(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_LongRunningScriptDetected(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_UnsafeContentWarningDisplaying(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_UnsafeContentWarningDisplaying(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_UnviewableContentIdentified(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_UnviewableContentIdentified(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_PermissionRequested(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_PermissionRequested(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_UnsupportedUriSchemeIdentified(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_UnsupportedUriSchemeIdentified(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_NewWindowRequested(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_NewWindowRequested(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_ContainsFullScreenElementChanged(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_ContainsFullScreenElementChanged(
                        EventRegistrationToken token
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE add_WebResourceRequested(
                        ) = 0;
                    virtual HRESULT STDMETHODCALLTYPE remove_WebResourceRequested(
                        EventRegistrationToken token
                        ) = 0;
                };

                MIDL_CONST_ID IID& IID_IWebViewControl = __uuidof(IWebViewControl);
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CWeb_CUI_CIWebViewControl;
#endif /* !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControl_INTERFACE_DEFINED__) */

#if !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControl2_INTERFACE_DEFINED__)
#define ____x_ABI_CWindows_CWeb_CUI_CIWebViewControl2_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Web_UI_IWebViewControl2[] = L"Windows.Web.UI.IWebViewControl2";
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                MIDL_INTERFACE("4d3c06f9-c8df-41cc-8bd5-2a947b204503")
                IWebViewControl2 : public IInspectable
                {
                public:
                    virtual HRESULT STDMETHODCALLTYPE AddInitializeScript(
                        HSTRING script
                        ) = 0;
                };

                MIDL_CONST_ID IID& IID_IWebViewControl2 = __uuidof(IWebViewControl2);
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CWeb_CUI_CIWebViewControl2;
#endif /* !defined(____x_ABI_CWindows_CWeb_CUI_CIWebViewControl2_INTERFACE_DEFINED__) */
// Collection interface definitions
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                namespace Interop {
                    class WebViewControl;
                } /* Interop */
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

#ifndef DEF___FIAsyncOperation_1_Windows__CWeb__CUI__CInterop__CWebViewControl_USE
#define DEF___FIAsyncOperation_1_Windows__CWeb__CUI__CInterop__CWebViewControl_USE
#if !defined(RO_NO_TEMPLATE_NAME)
namespace ABI { namespace Windows { namespace Foundation {
template <>
struct __declspec(uuid("ac3d28ac-8362-51c6-b2cc-16f3672758f1"))
IAsyncOperation<ABI::Windows::Web::UI::Interop::WebViewControl*> : IAsyncOperation_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Web::UI::Interop::WebViewControl*, ABI::Windows::Web::UI::IWebViewControl*>>
{
    static const wchar_t* z_get_rc_name_impl()
    {
        return L"Windows.Foundation.IAsyncOperation`1<Windows.Web.UI.Interop.WebViewControl>";
    }
};
// Define a typedef for the parameterized interface specialization's mangled name.
// This allows code which uses the mangled name for the parameterized interface to access the
// correct parameterized interface specialization.
typedef IAsyncOperation<ABI::Windows::Web::UI::Interop::WebViewControl*> __FIAsyncOperation_1_Windows__CWeb__CUI__CInterop__CWebViewControl_t;
#define __FIAsyncOperation_1_Windows__CWeb__CUI__CInterop__CWebViewControl ABI::Windows::Foundation::__FIAsyncOperation_1_Windows__CWeb__CUI__CInterop__CWebViewControl_t
/* Foundation */ } /* Windows */ } /* ABI */ }

#endif // !defined(RO_NO_TEMPLATE_NAME)
#endif /* DEF___FIAsyncOperation_1_Windows__CWeb__CUI__CInterop__CWebViewControl_USE */

#if !defined(____x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlProcess_INTERFACE_DEFINED__)
#define ____x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlProcess_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Web_UI_Interop_IWebViewControlProcess[] = L"Windows.Web.UI.Interop.IWebViewControlProcess";
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                namespace Interop {
                    MIDL_INTERFACE("02c723ec-98d6-424a-b63e-c6136c36a0f2")
                    IWebViewControlProcess : public IInspectable
                    {
                    public:
                        virtual HRESULT STDMETHODCALLTYPE get_ProcessId(
                            UINT32* value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE get_EnterpriseId(
                            HSTRING* value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE get_IsPrivateNetworkClientServerCapabilityEnabled(
                            boolean* value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE CreateWebViewControlAsync(
                            INT64 hostWindowHandle,
                            ABI::Windows::Foundation::Rect bounds,
                            __FIAsyncOperation_1_Windows__CWeb__CUI__CInterop__CWebViewControl** operation
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE GetWebViewControls(
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE Terminate(void) = 0;
                        virtual HRESULT STDMETHODCALLTYPE add_ProcessExited(
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE remove_ProcessExited(
                            EventRegistrationToken token
                            ) = 0;
                    };

                    MIDL_CONST_ID IID& IID_IWebViewControlProcess = __uuidof(IWebViewControlProcess);
                } /* Interop */
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlProcess;
#endif /* !defined(____x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlProcess_INTERFACE_DEFINED__) */


namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                namespace Interop {
                    class WebViewControlProcess;
                } /* Interop */
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */


#if !defined(____x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlSite_INTERFACE_DEFINED__)
#define ____x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlSite_INTERFACE_DEFINED__
extern const __declspec(selectany) _Null_terminated_ WCHAR InterfaceName_Windows_Web_UI_Interop_IWebViewControlSite[] = L"Windows.Web.UI.Interop.IWebViewControlSite";
namespace ABI {
    namespace Windows {
        namespace Web {
            namespace UI {
                namespace Interop {
                    MIDL_INTERFACE("133f47c6-12dc-4898-bd47-04967de648ba")
                    IWebViewControlSite : public IInspectable
                    {
                    public:
                        virtual HRESULT STDMETHODCALLTYPE get_Process(
                            ABI::Windows::Web::UI::Interop::IWebViewControlProcess** value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE put_Scale(
                            DOUBLE value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE get_Scale(
                            DOUBLE* value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE put_Bounds(
                            ABI::Windows::Foundation::Rect value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE get_Bounds(
                            ABI::Windows::Foundation::Rect* value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE put_IsVisible(
                            boolean value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE get_IsVisible(
                            boolean* value
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE Close(void) = 0;
                        virtual HRESULT STDMETHODCALLTYPE MoveFocus(
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE add_MoveFocusRequested(
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE remove_MoveFocusRequested(
                            EventRegistrationToken token
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE add_AcceleratorKeyPressed(
                            ) = 0;
                        virtual HRESULT STDMETHODCALLTYPE remove_AcceleratorKeyPressed(
                            EventRegistrationToken token
                            ) = 0;
                    };

                    MIDL_CONST_ID IID& IID_IWebViewControlSite = __uuidof(IWebViewControlSite);
                } /* Interop */
            } /* UI */
        } /* Web */
    } /* Windows */
} /* ABI */

EXTERN_C const IID IID___x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlSite;
#endif /* !defined(____x_ABI_CWindows_CWeb_CUI_CInterop_CIWebViewControlSite_INTERFACE_DEFINED__) */

#ifndef RUNTIMECLASS_Windows_Foundation_PropertyValue_DEFINED
#define RUNTIMECLASS_Windows_Foundation_PropertyValue_DEFINED
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Foundation_PropertyValue[] = L"Windows.Foundation.PropertyValue";
#endif

#ifndef RUNTIMECLASS_Windows_Foundation_Uri_DEFINED
#define RUNTIMECLASS_Windows_Foundation_Uri_DEFINED
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Foundation_Uri[] = L"Windows.Foundation.Uri";
#endif

#ifndef RUNTIMECLASS_Windows_UI_Colors_DEFINED
#define RUNTIMECLASS_Windows_UI_Colors_DEFINED
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_UI_Colors[] = L"Windows.UI.Colors";
#endif

#ifndef RUNTIMECLASS_Windows_Web_UI_Interop_WebViewControlProcess_DEFINED
#define RUNTIMECLASS_Windows_Web_UI_Interop_WebViewControlProcess_DEFINED
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Web_UI_Interop_WebViewControlProcess[] = L"Windows.Web.UI.Interop.WebViewControlProcess";
#endif



#ifndef DEF___FIVectorView_1_HSTRING_USE
#define DEF___FIVectorView_1_HSTRING_USE
#if !defined(RO_NO_TEMPLATE_NAME)
namespace ABI { namespace Windows { namespace Foundation { namespace Collections {
template <>
struct __declspec(uuid("2f13c006-a03a-5f69-b090-75a43e33423e"))
IVectorView<HSTRING> : IVectorView_impl<HSTRING>
{
    static const wchar_t* z_get_rc_name_impl()
    {
        return L"Windows.Foundation.Collections.IVectorView`1<String>";
    }
};
// Define a typedef for the parameterized interface specialization's mangled name.
// This allows code which uses the mangled name for the parameterized interface to access the
// correct parameterized interface specialization.
typedef IVectorView<HSTRING> __FIVectorView_1_HSTRING_t;
#define __FIVectorView_1_HSTRING ABI::Windows::Foundation::Collections::__FIVectorView_1_HSTRING_t
/* Collections */ } /* Foundation */ } /* Windows */ } /* ABI */ }

#endif // !defined(RO_NO_TEMPLATE_NAME)
#endif /* DEF___FIVectorView_1_HSTRING_USE */


#ifndef DEF___FIAsyncOperationCompletedHandler_1_Windows__CWeb__CUI__CInterop__CWebViewControl_USE
#define DEF___FIAsyncOperationCompletedHandler_1_Windows__CWeb__CUI__CInterop__CWebViewControl_USE
#if !defined(RO_NO_TEMPLATE_NAME)
namespace ABI { namespace Windows { namespace Foundation {
template <>
struct __declspec(uuid("d61963d6-806d-50a8-a81c-75d9356ad5d7"))
IAsyncOperationCompletedHandler<ABI::Windows::Web::UI::Interop::WebViewControl*> : IAsyncOperationCompletedHandler_impl<ABI::Windows::Foundation::Internal::AggregateType<ABI::Windows::Web::UI::Interop::WebViewControl*, ABI::Windows::Web::UI::IWebViewControl*>>
{
    static const wchar_t* z_get_rc_name_impl()
    {
        return L"Windows.Foundation.AsyncOperationCompletedHandler`1<Windows.Web.UI.Interop.WebViewControl>";
    }
};
// Define a typedef for the parameterized interface specialization's mangled name.
// This allows code which uses the mangled name for the parameterized interface to access the
// correct parameterized interface specialization.
typedef IAsyncOperationCompletedHandler<ABI::Windows::Web::UI::Interop::WebViewControl*> __FIAsyncOperationCompletedHandler_1_Windows__CWeb__CUI__CInterop__CWebViewControl_t;
#define __FIAsyncOperationCompletedHandler_1_Windows__CWeb__CUI__CInterop__CWebViewControl ABI::Windows::Foundation::__FIAsyncOperationCompletedHandler_1_Windows__CWeb__CUI__CInterop__CWebViewControl_t
/* Foundation */ } /* Windows */ } /* ABI */ }

#endif // !defined(RO_NO_TEMPLATE_NAME)
#endif /* DEF___FIAsyncOperationCompletedHandler_1_Windows__CWeb__CUI__CInterop__CWebViewControl_USE */
