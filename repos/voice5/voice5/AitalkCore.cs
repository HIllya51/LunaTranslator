 
using System.Runtime.InteropServices;
using System.Runtime.Serialization;

namespace Aitalk
{
    internal static class AitalkCore
    {
        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_Init@4")]
        public static extern Result Init([In] ref Config config);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_End@0")]
        public static extern Result End();

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_LangLoad@4")]
        public static extern Result LangLoad(string language_name);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_LangClear@0")]
        public static extern Result LangClear();

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_VoiceLoad@4")]
        public static extern Result VoiceLoad(string voice_name);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_VoiceClear@0")]
        public static extern Result VoiceClear();

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_ReloadPhraseDic@4")]
        public static extern Result ReloadPhraseDic(string dictionary_path);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_ReloadSymbolDic@4")]
        public static extern Result ReloadSymbolDic(string dictionary_path);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_ReloadWordDic@4")]
        public static extern Result ReloadWordDic(string dictionary_path);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_GetParam@8")]
        public static extern Result GetParam(IntPtr param, ref int written_bytes);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_SetParam@4")]
        public static extern Result SetParam(IntPtr param);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_TextToKana@12")]
        public static extern Result TextToKana(out int job_id, [In] ref JobParam job_param, [In] byte[] text);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_GetKana@20")]
        public static extern Result GetKana(int job_id, [Out, MarshalAs(UnmanagedType.LPArray)] byte[] buffer, int buffer_capacity, out int read_bytes, out int position);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_CloseKana@8")]
        public static extern Result CloseKana(int job_id, int zero = 0);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_TextToSpeech@12")]
        public static extern Result TextToSpeech(out int job_id, [In] ref JobParam job_param, [In] byte[] text);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_GetData@16")]
        public static extern Result GetData(int job_id, [Out, MarshalAs(UnmanagedType.LPArray)] byte[] buffer, int buffer_capacity, out int read_samples);

        [DllImport("aitalked.dll", EntryPoint = "_AITalkAPI_CloseSpeech@8")]
        public static extern Result CloseSpeech(int job_id, int zero = 0);

        public enum EventReason
        {
            TextBufferFull = 101,
            TextBufferFlush = 102,
            TextBufferClose = 103,
            RawBufferFull = 201,
            RawBufferFlush = 202,
            RawBufferClose = 203,
            PhoneticLabel = 301,
            Bookmark = 302,
            AutoBookmark = 303
        }

        public enum Result
        {
            Success = 0,
            InternalError = -1,
            Unsupported = -2,
            InvalidArgument = -3,
            WaitTimeout = -4,
            NotInitialized = -10,
            AlreadyInitialized = 10,
            NotLoaded = -11,
            AlreadyLoaded = 11,
            Insufficient = -20,
            PartiallyRegistered = 21,
            LicenseAbsent = -100,
            LicenseExpired = -101,
            LicenseRejected = -102,
            TooManyJobs = -201,
            InvalidJobId = -202,
            JobBusy = -203,
            NoMoreData = 204,
            OutOfMemory = -206,
            FileNotFound = -1001,
            PathNotFound = -1002,
            ReadFault = -1003,
            CountLimit = -1004,
            UserDictionaryLocked = -1011,
            UserDictionaryNoEntry = -1012
        }

        public enum Status
        {
            WrongState = -1,
            InProgress = 10,
            StillRunning = 11,
            Done = 12
        }

        public enum JobInOut
        {
            PlainToWave = 11,
            KanaToWave = 12,
            JeitaToWave = 13,
            PlainToKana = 21,
            KanaToJeita = 32
        }

        [Flags]
        public enum ExtendFormat
        {
            None = 0x0,
            JeitaRuby = 0x1,
            AutoBookmark = 0x10
        }

        [StructLayout(LayoutKind.Sequential, Pack = 1, CharSet = CharSet.Ansi)]
        public struct Config
        {
            public int VoiceDbSampleRate;

            [MarshalAs(UnmanagedType.LPStr)]
            public string VoiceDbDirectory;

            public int TimeoutMilliseconds;

            [MarshalAs(UnmanagedType.LPStr)]
            public string LicensePath;

            [MarshalAs(UnmanagedType.LPStr)]
            public string AuthenticateCodeSeed;

            public int ReservedZero;
        }

        [StructLayout(LayoutKind.Sequential, Pack = 1)]
        public struct JobParam
        {
            public JobInOut ModeInOut;
            public IntPtr UserData;
        }

        [StructLayout(LayoutKind.Sequential, Pack = 1, CharSet = CharSet.Ansi)]
        public struct TtsParam
        {
            public const int VoiceNameLength = 80;

            public int Size;

            public TextBufferCallbackType TextBufferCallback;

            public RawBufferCallbackType RawBufferCallback;

            public TtsEventCallbackType TtsEventCallback;

            public int TextBufferCapacityInBytes;

            public int RawBufferCapacityInBytes;

            public float Volume;

            public int PauseBegin;

            public int PauseTerm;

            public ExtendFormat ExtendFormatFlags;

            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = VoiceNameLength)]
            public string VoiceName;

            public JeitaParam Jeita;

            public int NumberOfSpeakers;

            public int ReservedZero;

            [StructLayout(LayoutKind.Sequential, Pack = 1, CharSet = CharSet.Ansi)]
            public struct JeitaParam
            {
                public const int ControlLength = 12;

                [MarshalAs(UnmanagedType.ByValTStr, SizeConst = VoiceNameLength)]
                public string FemaleName;

                [MarshalAs(UnmanagedType.ByValTStr, SizeConst = VoiceNameLength)]
                public string MaleName;

                public int PauseMiddle;

                public int PauseLong;

                public int PauseSentence;

                /// <summary>
                /// JEITA TT-6004を参照せよ
                /// </summary>
                [MarshalAs(UnmanagedType.ByValTStr, SizeConst = ControlLength)]
                public string Control;
            }

            [StructLayout(LayoutKind.Sequential, Pack = 1, CharSet = CharSet.Ansi)]
            [DataContract]
            public class SpeakerParam
            {
                [DataMember]
                [MarshalAs(UnmanagedType.ByValTStr, SizeConst = VoiceNameLength)]
                public string VoiceName;

                [DataMember]
                public float Volume;

                [DataMember]
                public float Speed;

                [DataMember]
                public float Pitch;

                [DataMember]
                public float Range;

                [DataMember]
                public int PauseMiddle;

                [DataMember]
                public int PauseLong;

                [DataMember]
                public int PauseSentence;

                [DataMember]
                [MarshalAs(UnmanagedType.ByValTStr, SizeConst = VoiceNameLength)]
                public string StyleRate;
            }

            public delegate int TextBufferCallbackType(EventReason reason, int job_id, IntPtr user_data);

            public delegate int RawBufferCallbackType(EventReason reason, int job_id, long tick, IntPtr user_data);

            public delegate int TtsEventCallbackType(EventReason reason, int job_id, long tick, string name, IntPtr user_data);
        }
    }
}
