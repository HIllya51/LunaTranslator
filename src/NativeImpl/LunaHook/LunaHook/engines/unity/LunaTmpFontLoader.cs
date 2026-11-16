
using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;

namespace LunaTmpFontLoader
{
    public static class FontLoader
    {
        public static string BundleDir = @"";

        [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
        delegate void LogDelegate([MarshalAs(UnmanagedType.LPWStr)] string s);

        static LogDelegate ResolveLog()
        {
            try
            {
                string name = IntPtr.Size == 8 ? "LunaHook64" : "LunaHook32";
                IntPtr h = GetModuleHandle(name);
                if (h == IntPtr.Zero) return null;
                IntPtr p = GetProcAddress(h, "luna_internal_unity_font_log");
                if (p == IntPtr.Zero) return null;
                return (LogDelegate)Marshal.GetDelegateForFunctionPointer(p, typeof(LogDelegate));
            }
            catch { return null; }
        }

        static void Diag(string s)
        {
            try
            {
                var fn = ResolveLog();
                if (fn != null)
                    fn(s);
            }
            catch { }
        }

        [DllImport("kernel32", SetLastError = true)]
        static extern IntPtr GetModuleHandle(string lpModuleName);
        [DllImport("kernel32", SetLastError = true)]
        static extern IntPtr GetProcAddress(IntPtr hModule, string lpProcName);

        static bool _resolved;
        static Type _tFontAsset, _tTMP_Text, _tSettings;
        static Type _tUIText, _tUIFont;
        static Type _tAB, _tObject, _tApp;
        static MethodInfo _mLoadFromFile, _mLoadAllAssets, _mDontDestroy, _mFindObjectsOfType;
        static MethodInfo _mCreateDynFont, _mCreateFontAsset, _mHasCharUIFont;
        static PropertyInfo _pFontTMP, _pTextTMP, _pUnityVer, _pName, _pFallbackFonts, _pFallbackFontTable;
        static PropertyInfo _pFontUIText, _pTextUIText;
        static MethodInfo _mHasCharacter;

        static Type FindType(string fullName)
        {
            foreach (var a in AppDomain.CurrentDomain.GetAssemblies())
            {
                try { var t = a.GetType(fullName); if (t != null) return t; }
                catch { }
            }
            return null;
        }
        static MethodInfo FindMethod(Type t, string name, Type[] pts)
        {
            if (t == null) return null;
            try { var m = t.GetMethod(name, pts); if (m != null) return m; } catch { }
            foreach (var m in t.GetMethods())
            {
                if (m.Name != name) continue;
                var mp = m.GetParameters();
                if (mp.Length != pts.Length) continue;
                bool ok = true;
                for (int i = 0; i < pts.Length; i++) if (mp[i].ParameterType != pts[i]) { ok = false; break; }
                if (ok) return m;
            }
            return null;
        }

        static void ResolveTypes()
        {
            if (_resolved) return;
            _resolved = true;
            try
            {
                _tFontAsset = FindType("TMPro.TMP_FontAsset");
                _tTMP_Text = FindType("TMPro.TMP_Text");
                _tSettings = FindType("TMPro.TMP_Settings");
                _tUIText = FindType("UnityEngine.UI.Text");
                _tUIFont = FindType("UnityEngine.Font");
                _tAB = FindType("UnityEngine.AssetBundle");
                _tObject = FindType("UnityEngine.Object");
                _tApp = FindType("UnityEngine.Application");

                if (_tAB != null)
                {
                    _mLoadFromFile = FindMethod(_tAB, "LoadFromFile", new[] { typeof(string) });
                    foreach (var m in _tAB.GetMethods())
                        if (m.Name == "LoadAllAssets" && m.GetParameters().Length == 0) { _mLoadAllAssets = m; break; }
                }
                if (_tObject != null)
                {
                    _mDontDestroy = FindMethod(_tObject, "DontDestroyOnLoad", new[] { _tObject });
                    _pName = _tObject.GetProperty("name");
                    _mFindObjectsOfType = FindMethod(_tObject, "FindObjectsOfType", new[] { typeof(Type) });
                }
                if (_tApp != null)
                    _pUnityVer = _tApp.GetProperty("unityVersion");
                if (_tTMP_Text != null)
                {
                    _pFontTMP = _tTMP_Text.GetProperty("font");
                    _pTextTMP = _tTMP_Text.GetProperty("text");
                }
                if (_tUIFont != null)
                {
                    _mCreateDynFont = FindMethod(_tUIFont, "CreateDynamicFontFromOSFont", new[] { typeof(string[]), typeof(int) });
                    _mHasCharUIFont = FindMethod(_tUIFont, "HasCharacter", new[] { typeof(char) });
                }
                if (_tUIText != null)
                {
                    _pFontUIText = _tUIText.GetProperty("font");
                    _pTextUIText = _tUIText.GetProperty("text");
                }
                if (_tFontAsset != null)
                {
                    _mHasCharacter = FindMethod(_tFontAsset, "HasCharacter", new[] { typeof(char) });
                    if (_tUIFont != null)
                        _mCreateFontAsset = FindMethod(_tFontAsset, "CreateFontAsset", new[] { _tUIFont });
                    _pFallbackFontTable = _tFontAsset.GetProperty("fallbackFontAssetTable") ?? _tFontAsset.GetProperty("fallbackFontAssets");
                }
                if (_tSettings != null)
                    _pFallbackFonts = _tSettings.GetProperty("fallbackFontAssets");
            }
            catch (Exception e) { Diag("ResolveTypes: threw " + e.GetType().Name + ": " + e.Message); }
            Diag("ResolveTypes: FA=" + (_tFontAsset != null) + " TMP_Text=" + (_tTMP_Text != null)
                + " UIText=" + (_tUIText != null) + " UIFont=" + (_tUIFont != null)
                + " AB=" + (_tAB != null) + " Obj=" + (_tObject != null) + " App=" + (_tApp != null)
                + " HasChar=" + (_mHasCharacter != null) + " Fallback=" + (_pFallbackFonts != null));
        }

        static object _font;
        static object _dynFont;
        static object _osFont;

        public static void LoadFont(string bundleDir)
        {
            Diag("LoadFont: entered");
            BundleDir = bundleDir;
            try { LoadFontImpl(); }
            catch (Exception e) { Diag("LoadFont: caught " + e.GetType().FullName + ": " + e.Message); throw; }
        }

        static void LoadBundleFont()
        {
            if (string.IsNullOrEmpty(BundleDir) || _tAB == null || _mLoadFromFile == null || _mLoadAllAssets == null)
                return;

            string ver = "";
            try { if (_pUnityVer != null) ver = (string)_pUnityVer.GetValue(null, null); } catch { }
            string fn = PickBundle(ver);
            string path = Path.Combine(BundleDir, fn);
            bool fe = File.Exists(path);
            Diag("LoadBundleFont: Unity=" + ver + " path=" + path + " exists=" + fe);
            if (!fe) return;

            object ab;
            try { ab = _mLoadFromFile.Invoke(null, new object[] { path }); }
            catch (Exception e) { Diag("LoadBundleFont: LoadFromFile threw " + e.GetType().Name + ": " + e.Message); return; }
            if (ab == null) return;
            DontDestroy(ab);

            object arrObj;
            try { arrObj = _mLoadAllAssets.Invoke(ab, null); }
            catch (Exception e) { Diag("LoadBundleFont: LoadAllAssets threw " + e.GetType().Name + ": " + e.Message); return; }
            Array arr = arrObj as Array;
            if (arr == null) return;

            foreach (var o in arr)
            {
                if (o != null && _tFontAsset != null && _tFontAsset.IsInstanceOfType(o))
                {
                    _font = o;
                    DontDestroy(_font);
                    Diag("LoadBundleFont: font loaded (" + GetName(_font) + ")");
                    break;
                }
            }
        }

        static void LoadDynamicOSFont()
        {
            if (_mCreateDynFont == null) return;
            try
            {
                string[] osNames = new string[] { "Arial", "Tahoma", "Segoe UI", "Microsoft YaHei" };
                _osFont = _mCreateDynFont.Invoke(null, new object[] { osNames, 32 });
                if (_osFont != null)
                {
                    DontDestroy(_osFont);
                    Diag("LoadDynamicOSFont: osFont created");
                    if (_mCreateFontAsset != null)
                    {
                        _dynFont = _mCreateFontAsset.Invoke(null, new object[] { _osFont });
                        if (_dynFont != null)
                        {
                            DontDestroy(_dynFont);
                            Diag("LoadDynamicOSFont: dynFont TMP_FontAsset created");
                        }
                    }
                }
            }
            catch (Exception e) { Diag("LoadDynamicOSFont: " + e.GetType().Name + ": " + e.Message); }
        }

        static void AddToFontList(object list, object fontAsset)
        {
            if (list == null || fontAsset == null || _tFontAsset == null) return;
            try
            {
                var tList = list.GetType();
                var mContains = tList.GetMethod("Contains", new[] { _tFontAsset });
                var mAdd = tList.GetMethod("Add", new[] { _tFontAsset });
                if (mContains == null || mAdd == null) return;
                if (!(bool)mContains.Invoke(list, new object[] { fontAsset }))
                    mAdd.Invoke(list, new object[] { fontAsset });
            }
            catch { }
        }

        static void LoadFontImpl()
        {
            Diag("LoadFontImpl: start");
            ResolveTypes();
            LoadBundleFont();
            LoadDynamicOSFont();

            if (_font == null && _dynFont != null)
                _font = _dynFont;

            if (_font != null && _dynFont != null && _font != _dynFont && _pFallbackFontTable != null)
            {
                try
                {
                    object fbList = _pFallbackFontTable.GetValue(_font, null);
                    if (fbList == null)
                    {
                        fbList = Activator.CreateInstance(_pFallbackFontTable.PropertyType);
                        _pFallbackFontTable.SetValue(_font, fbList, null);
                    }
                    AddToFontList(fbList, _dynFont);
                }
                catch { }
            }

            RegisterFallback();
            ApplyToAllExisting();

            Diag("LoadFontImpl: done");
        }

        static void DontDestroy(object obj)
        {
            if (obj == null || _mDontDestroy == null) return;
            try { _mDontDestroy.Invoke(null, new object[] { obj }); } catch { }
        }
        static string GetName(object obj)
        {
            if (obj == null || _pName == null) return "?";
            try { return (string)_pName.GetValue(obj, null); } catch { return obj.GetType().Name; }
        }
        static string DescribeTypes(Array arr)
        {
            var sb = new StringBuilder();
            foreach (var o in arr) { if (sb.Length > 0) sb.Append(','); sb.Append(o == null ? "null" : o.GetType().FullName); }
            return sb.ToString();
        }

        static int _applyCalls, _applySets, _scanCount;
        static bool _scanned;
        static int _lastScanTick;

        public static void ApplyFont(object component)
        {
            if (_font == null && _osFont == null) return;
            if (!_resolved) ResolveTypes();
            if (component != null) SetFont(component, false);
            int now = Environment.TickCount;
            if (!_scanned || (now - _lastScanTick) >= 500)
            {
                _scanned = true;
                _lastScanTick = now;
                ApplyToAllExisting();
            }
        }

        static void SetFont(object component, bool selective)
        {
            if (component == null) return;
            if (_tUIText != null && _tUIText.IsInstanceOfType(component))
            {
                if (_osFont == null || _pFontUIText == null) return;
                try
                {
                    object cur = _pFontUIText.GetValue(component, null);
                    if (cur == _osFont) return;
                    if (selective && !MissingGlyphsUIText(component, cur)) return;
                    _pFontUIText.SetValue(component, _osFont, null);
                }
                catch (Exception e) { Diag("ApplyFont UIText: " + e.GetType().Name + ": " + e.Message); }
                return;
            }
            if (_font == null || _pFontTMP == null) return;
            _applyCalls++;
            if (_applyCalls == 1) Diag("ApplyFont: first call compType=" + component.GetType().FullName);
            try
            {
                object cur = _pFontTMP.GetValue(component, null);
                object targetFont = ChooseTmpFont(component);
                if (cur == targetFont) return;
                if (selective && !MissingGlyphs(component, cur)) return;
                _pFontTMP.SetValue(component, targetFont, null);
                _applySets++;
                if (_applySets <= 3) Diag("ApplyFont: set font (#" + _applySets + " on " + component.GetType().Name + ")");
            }
            catch (Exception e) { Diag("ApplyFont: " + e.GetType().Name + ": " + e.Message); }
        }

        static object ChooseTmpFont(object component)
        {
            if (_dynFont == null || _font == null || _font == _dynFont || _pTextTMP == null || _mHasCharacter == null)
                return _font;
            try
            {
                string text = (string)_pTextTMP.GetValue(component, null);
                if (!string.IsNullOrEmpty(text))
                {
                    foreach (char c in text)
                    {
                        if (c < 0x0080) continue;
                        if (!((bool)_mHasCharacter.Invoke(_font, new object[] { c })))
                            return _dynFont;
                    }
                }
            }
            catch { }
            return _font;
        }

        static bool MissingGlyphsUIText(object component, object font)
        {
            if (_pTextUIText == null || _mHasCharUIFont == null || font == null) return true;
            try
            {
                string text = (string)_pTextUIText.GetValue(component, null);
                if (string.IsNullOrEmpty(text)) return false;
                foreach (char c in text)
                {
                    if (c < 0x0080) continue;
                    if (!((bool)_mHasCharUIFont.Invoke(font, new object[] { c }))) return true;
                }
                return false;
            }
            catch { return true; }
        }

        static bool MissingGlyphs(object component, object font)
        {
            if (_pTextTMP == null || _mHasCharacter == null || font == null) return true;
            try
            {
                string text = (string)_pTextTMP.GetValue(component, null);
                if (string.IsNullOrEmpty(text)) return false;
                foreach (char c in text)
                {
                    if (c < 0x0080) continue;
                    if (!((bool)_mHasCharacter.Invoke(font, new object[] { c }))) return true;
                }
                return false;
            }
            catch { return true; }
        }

        static void ApplyToAllExisting()
        {
            if (_mFindObjectsOfType == null) return;
            if (_font != null && _tTMP_Text != null)
            {
                try
                {
                    var arrObj = _mFindObjectsOfType.Invoke(null, new object[] { _tTMP_Text });
                    Array arr = arrObj as Array;
                    if (arr != null)
                    {
                        int visited = 0;
                        foreach (var o in arr)
                            if (o != null) { SetFont(o, true); visited++; }
                        _scanCount++;
                        if (_scanCount <= 3) Diag("ApplyToAllExisting: found=" + arr.Length + " visited=" + visited);
                    }
                }
                catch (Exception e) { Diag("ApplyToAllExisting: " + e.GetType().Name + ": " + e.Message); }
            }
            if (_osFont != null && _tUIText != null)
            {
                try
                {
                    var arrObj = _mFindObjectsOfType.Invoke(null, new object[] { _tUIText });
                    Array arr = arrObj as Array;
                    if (arr != null)
                    {
                        foreach (var o in arr)
                            if (o != null) SetFont(o, true);
                    }
                }
                catch { }
            }
        }

        static void RegisterFallback()
        {
            if ((_font == null && _dynFont == null) || _tSettings == null || _pFallbackFonts == null)
            { Diag("RegisterFallback: not resolved"); return; }
            try
            {
                var list = _pFallbackFonts.GetValue(null, null);
                if (list == null) { Diag("RegisterFallback: fallbackFontAssets null"); return; }
                AddToFontList(list, _font);
                if (_dynFont != null && _dynFont != _font)
                    AddToFontList(list, _dynFont);
                Diag("RegisterFallback: ok");
            }
            catch (Exception e) { Diag("RegisterFallback: " + e.GetType().Name + ": " + e.Message); }
        }

        static string PickBundle(string ver)
        {
            int n = 0; bool any = false;
            foreach (char c in ver)
            {
                if (c >= '0' && c <= '9') { n = n * 10 + (c - '0'); any = true; }
                else if (any) break;
            }
            if (n == 6) return "arialuni_sdf_u6000";
            if (n >= 2022) return "arialuni_sdf_u2022";
            if (n == 2020 || n == 2021) return "arialuni_sdf_u2021";
            if (n == 2019) return "arialuni_sdf_u2019";
            if (n == 2018) return "arialuni_sdf_u2018";
            return "arialuni_sdf-u55to2017";
        }
    }
}
