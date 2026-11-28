using System;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

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

        // arg: "TypeName|MethodName|ParamCount|ArgIndex|FieldName" - resolves
        // the method like GetAddr, then returns the byte offset of the
        // instance field "FieldName" (must be a System.String) inside the
        // type of the method's ArgIndex-th parameter (1-based), or 0.
        public static int GetFieldOffset(string arg)
        {
            try
            {
                string[] p = arg.Split('|');
                if (p.Length != 5)
                    return 0;
                int want;
                if (!int.TryParse(p[2], out want))
                    return 0;
                int argidx;
                if (!int.TryParse(p[3], out argidx))
                    return 0;
                if (argidx < 1 || argidx > want)
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
                        Type pt = m.GetParameters()[argidx - 1].ParameterType;
                        FieldInfo f = pt.GetField(p[4], BindingFlags.Public |
                                                          BindingFlags.NonPublic |
                                                          BindingFlags.Instance);
                        if (f == null || f.FieldType != typeof(string))
                            return 0; // this game version does not match the expectation
                        return FieldOffsetByJit(pt, f);
                    }
                }
            }
            catch { }
            return 0;
        }

        // arg: "TypeName|FieldName" or "TypeName|FieldName|SubFieldName" -
        // returns the instance field offset (of ANY field type, not only
        // strings) on the named type, or 0. With SubFieldName the field is
        // resolved on the TYPE of the named field instead - used to resolve
        // e.g. the _items/_size offsets inside List<MessageParts> without
        // hardcoding managed collection layouts.
        public static int GetTypeFieldOffset(string arg)
        {
            try
            {
                string[] p = arg.Split('|');
                if (p.Length != 2 && p.Length != 3)
                    return 0;
                foreach (Assembly a in AppDomain.CurrentDomain.GetAssemblies())
                {
                    Type t = null;
                    try { t = a.GetType(p[0], false); }
                    catch { }
                    if (t == null)
                        continue;
                    FieldInfo f = t.GetField(p[1], BindingFlags.Public |
                                                   BindingFlags.NonPublic |
                                                   BindingFlags.Instance);
                    if (f == null)
                        return 0;
                    if (p.Length == 3)
                    {
                        FieldInfo sf = f.FieldType.GetField(p[2], BindingFlags.Public |
                                                                 BindingFlags.NonPublic |
                                                                 BindingFlags.Instance);
                        if (sf == null)
                            return 0;
                        return FieldOffsetByJit(f.FieldType, sf);
                    }
                    return FieldOffsetByJit(t, f);
                }
            }
            catch { }
            return 0;
        }

        // emits "static FType F(T o) { return o.field; }", lets the game's own
        // CLR JIT-compile it and reads the ldfld displacement from the code.
        // Reflection.Emit allows unverifiable IL, but the JIT still verifies
        // dynamic assemblies (ldflda/conv.i combos throw VerificationException),
        // so the emitted getter stays verifiable and only its machine code is
        // inspected - no object instance is ever needed.
        static int FieldOffsetByJit(Type t, FieldInfo f)
        {
            AssemblyName an = new AssemblyName("LunaCLRHProbe");
            AssemblyBuilder ab = AppDomain.CurrentDomain.DefineDynamicAssembly(an, AssemblyBuilderAccess.Run);
            ModuleBuilder mb = ab.DefineDynamicModule("LunaCLRHProbeMod");
            TypeBuilder tb = mb.DefineType("P", TypeAttributes.Public);
            MethodBuilder metb = tb.DefineMethod("F", MethodAttributes.Public | MethodAttributes.Static,
                                                 f.FieldType, new Type[] { t });
            ILGenerator il = metb.GetILGenerator();
            il.Emit(OpCodes.Ldarg_0);
            il.Emit(OpCodes.Ldfld, f);
            il.Emit(OpCodes.Ret);
            MethodInfo m = tb.CreateType().GetMethod("F");
            RuntimeHelpers.PrepareMethod(m.MethodHandle);
            IntPtr fp = m.MethodHandle.GetFunctionPointer();

            // the getter compiles to: prologue, an optional JIT helper call,
            // then the ldfld - the only memory-operand load in the method:
            //   8B /r        mov r32, [reg+disp]   (reference/int fields)
            //   8A /r        mov r8,  [reg+disp]   (bool/byte fields)
            //   F3 0F 10 /r  movss xmm, [reg+disp] (float fields, x64-style JIT)
            //   D9 /0        fld m32, [reg+disp]   (float fields, x87-style JIT
            //                                     used by .NET Framework x86)
            // followed immediately by the epilogue pop/ret. A displacement
            // byte inside a helper call's rel32 could mimic the opcode, so
            // additionally require the epilogue pop/ret behind the disp.
            for (int i = 0; i < 48; i++)
            {
                int modrmAt;
                byte b = Marshal.ReadByte(fp, i);
                if (b == 0x8B || b == 0x8A)
                    modrmAt = i + 1;
                else if (b == 0xF3 && Marshal.ReadByte(fp, i + 1) == 0x0F && Marshal.ReadByte(fp, i + 2) == 0x10)
                    modrmAt = i + 3;
                else if (b == 0xD9 && ((Marshal.ReadByte(fp, i + 1) >> 3) & 7) == 0)
                    modrmAt = i + 1; // fld m32
                else
                    continue;
                byte modrm = Marshal.ReadByte(fp, modrmAt);
                int mod = modrm >> 6, rm = modrm & 7;
                if (rm == 4 || rm == 5) // SIB / absolute address
                    continue;
                if (mod != 1 && mod != 2)
                    continue;
                int dispAt = modrmAt + 1;
                int tailAt = (mod == 1) ? dispAt + 1 : dispAt + 4;
                byte tail = Marshal.ReadByte(fp, tailAt);
                if ((tail >= 0x58 && tail <= 0x5F) || tail == 0xC3 || tail == 0xC2)
                    return (mod == 1) ? (sbyte)Marshal.ReadByte(fp, dispAt) : Marshal.ReadInt32(fp, dispAt);
            }
            return 0;
        }
    }
}
