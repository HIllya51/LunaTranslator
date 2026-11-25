using System;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace LunaCLRH
{
    public static class M
    {
        // arg: "TypeName|MethodName|ParamCount" - the type is searched in every
        // loaded assembly (the player exe is renamed per game, so the assembly
        // name cannot be assumed). Returns the native entry point of the
        // JIT-compiled method, or 0.
        public static int GetAddr(string arg)
        {
            try
            {
                string[] p = arg.Split('|');
                if (p.Length != 3)
                    return 0;
                int want;
                if (!int.TryParse(p[2], out want))
                    return 0;
                foreach (Assembly a in AppDomain.CurrentDomain.GetAssemblies())
                {
                    Type t = null;
                    try { t = a.GetType(p[0], false); }
                    catch { }
                    if (t == null)
                        continue;
                    foreach (MethodInfo m in t.GetMethods(BindingFlags.Public |
                                                           BindingFlags.NonPublic |
                                                           BindingFlags.Instance |
                                                           BindingFlags.Static |
                                                           BindingFlags.DeclaredOnly))
                    {
                        if (m.Name != p[1])
                            continue;
                        if (m.GetParameters().Length != want)
                            continue;
                        try { RuntimeHelpers.PrepareMethod(m.MethodHandle); }
                        catch { }
                        return unchecked((int)m.MethodHandle.GetFunctionPointer().ToInt64());
                    }
                }
            }
            catch { }
            return 0;
        }
    }
}
