 
using System.Text;
using System.Runtime.InteropServices;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Globalization; 

namespace Aitalk
{
    public static class AitalkWrapper
    {
        /// <summary>
        /// AITalkを初期化する
        /// </summary>
        /// <param name="install_directory">VOICEROID2のインストールディレクトリ</param>
        /// <param name="authenticate_code">認証コード</param>
        public static void Initialize(string install_directory, string authenticate_code)
        {
            Finish();

            // aitalked.dllをロードするために
            // DLLの探索パスをVOICEROID2のディレクトリに変更する
            if ((InstallDirectory != null) && (InstallDirectory != install_directory))
            {
                throw new AitalkException($"インストールディレクトリを変更して再び初期化することはできません。");
            }
            InstallDirectory = install_directory;
            SetDllDirectory(InstallDirectory);

            // AITalkを初期化する
            AitalkCore.Config config;
            config.VoiceDbSampleRate = VoiceSampleRate;
            config.VoiceDbDirectory = $"{InstallDirectory}\\Voice";
            config.TimeoutMilliseconds = TimeoutMilliseconds;
            config.LicensePath = $"{InstallDirectory}\\aitalk.lic";
            config.AuthenticateCodeSeed = authenticate_code;
            config.ReservedZero = 0;
            Console.WriteLine(config.VoiceDbSampleRate);
            Console.WriteLine(config.VoiceDbDirectory);
            Console.WriteLine(config.TimeoutMilliseconds);
            Console.WriteLine(config.LicensePath);
            Console.WriteLine(config.AuthenticateCodeSeed);
            var result = AitalkCore.Result.Success;
            try
            {
                result = AitalkCore.Init(ref config);
            }
            catch (Exception e)
            {
                throw new AitalkException($"AITalkの初期化に失敗しました。", e);
            }
            if (result != AitalkCore.Result.Success)
            {
                throw new AitalkException($"AITalkの初期化に失敗しました。", result);
            }
            IsInitialized = true;
        }

        /// <summary>
        /// AITalkを終了する
        /// </summary>
        public static void Finish()
        {
            if (IsInitialized == true)
            {
                IsInitialized = false;
                AitalkCore.End();
            }
            CurrentLanguage = null;
            CurrentVoice = null;
        }

        /// <summary>
        /// 言語ライブラリの一覧。
        /// インストールディレクトリのLangディレクトリの中にあるフォルダ名から生成される。
        /// </summary>
        public static string[] LanguageList
        {
            get
            {
                List<string> result = new List<string>();
                try
                {
                    foreach (string path in Directory.GetDirectories($"{InstallDirectory}\\Lang"))
                    {
                        result.Add(Path.GetFileName(path));
                    }
                }
                catch (Exception) { }
                result.Sort(StringComparer.InvariantCultureIgnoreCase);
                return result.ToArray();
            }
        }

        /// <summary>
        /// ボイスライブラリの一覧。
        /// インストールディレクトリのVoiceディレクトリの中にあるフォルダ名から生成される。
        /// </summary>
        public static string[] VoiceDbList
        {
            get
            {
                List<string> result = new List<string>();
                try
                {
                    foreach (string path in Directory.GetDirectories($"{InstallDirectory}\\Voice"))
                    {
                        result.Add(Path.GetFileName(path));
                    }
                }
                catch (Exception) { }
                result.Sort(StringComparer.InvariantCultureIgnoreCase);
                return result.ToArray();
            }
        }

        /// <summary>
        /// 言語ライブラリを読み込む
        /// </summary>
        /// <param name="language_name">言語名</param>
        public static void LoadLanguage(string language_name)
        {
            if (language_name == CurrentLanguage)
            {
                return;
            }
            // 言語の設定をする際はカレントディレクトリを一時的にVOICEROID2のインストールディレクトリに変更する
            // それ以外ではLangLoad()はエラーを返す
            string current_directory = System.IO.Directory.GetCurrentDirectory();
            System.IO.Directory.SetCurrentDirectory(InstallDirectory);
            CurrentLanguage = null;
            AitalkCore.Result result;
            result = AitalkCore.LangClear();
            if ((result == AitalkCore.Result.Success) || (result == AitalkCore.Result.NotLoaded))
            {
                result = AitalkCore.LangLoad($"{InstallDirectory}\\Lang\\{language_name}");
            }
            System.IO.Directory.SetCurrentDirectory(current_directory);
            if (result != AitalkCore.Result.Success)
            {
                throw new AitalkException($"言語'{language_name}'の読み込みに失敗しました。", result);
            }
            CurrentLanguage = language_name;
        }

        /// <summary>
        /// フレーズ辞書を読み込む
        /// </summary>
        /// <param name="path">ファイルパス</param>
        public static void ReloadPhraseDictionary(string path)
        {
            AitalkCore.ReloadPhraseDic(null);
            if (path == null)
            {
                return;
            }
            AitalkCore.Result result;
            result = AitalkCore.ReloadPhraseDic(path);
            if (result == AitalkCore.Result.UserDictionaryNoEntry)
            {
                AitalkCore.ReloadPhraseDic(null);
            }
            else if (result != AitalkCore.Result.Success)
            {
                throw new AitalkException($"フレーズ辞書'{path}'の読み込みに失敗しました。", result);
            }
        }

        /// <summary>
        /// 単語辞書を読み込む
        /// </summary>
        /// <param name="path">ファイルパス</param>
        public static void ReloadWordDictionary(string path)
        {
            AitalkCore.ReloadWordDic(null);
            if (path == null)
            {
                return;
            }
            AitalkCore.Result result;
            result = AitalkCore.ReloadWordDic(path);
            if (result == AitalkCore.Result.UserDictionaryNoEntry)
            {
                AitalkCore.ReloadWordDic(null);
            }
            else if (result != AitalkCore.Result.Success)
            {
                throw new AitalkException($"単語辞書'{path}'の読み込みに失敗しました。", result);
            }
        }

        /// <summary>
        /// 記号ポーズ辞書を読み込む
        /// </summary>
        /// <param name="path">ファイルパス</param>
        public static void ReloadSymbolDictionary(string path)
        {
            AitalkCore.ReloadSymbolDic(null);
            if (path == null)
            {
                return;
            }
            AitalkCore.Result result;
            result = AitalkCore.ReloadSymbolDic(path);
            if (result == AitalkCore.Result.UserDictionaryNoEntry)
            {
                AitalkCore.ReloadSymbolDic(null);
            }
            else if (result != AitalkCore.Result.Success)
            {
                throw new AitalkException($"記号ポーズ辞書'{path}'の読み込みに失敗しました。", result);
            }
        }

        /// <summary>
        /// ボイスライブラリを読み込む
        /// </summary>
        /// <param name="voice_db_name">ボイスライブラリ名</param>
        public static void LoadVoice(string voice_db_name)
        {
            if (voice_db_name == CurrentVoice)
            {
                return;
            }

            CurrentVoice = null;
            AitalkCore.VoiceClear();
            if (voice_db_name == null)
            {
                return;
            }
            AitalkCore.Result result;
            result = AitalkCore.VoiceLoad(voice_db_name);
            if (result != AitalkCore.Result.Success)
            {
                throw new AitalkException($"ボイスライブラリ'{voice_db_name}'の読み込みに失敗しました。", result);
            }

            // パラメータを読み込む
            GetParameters(out var tts_param, out var speaker_params);
            tts_param.TextBufferCallback = TextBufferCallback;
            tts_param.RawBufferCallback = RawBufferCallback;
            tts_param.TtsEventCallback = TtsEventCallback;
            tts_param.PauseBegin = 0;
            tts_param.PauseTerm = 0;
            tts_param.ExtendFormatFlags = AitalkCore.ExtendFormat.JeitaRuby | AitalkCore.ExtendFormat.AutoBookmark;
            Parameter = new AitalkParameter(voice_db_name, tts_param, speaker_params);

            CurrentVoice = voice_db_name;
        }

        /// <summary>
        /// パラメータを取得する
        /// </summary>
        /// <param name="tts_param">パラメータ(話者パラメータを除く)</param>
        /// <param name="speaker_params">話者パラメータ</param>
        private static void GetParameters(out AitalkCore.TtsParam tts_param, out AitalkCore.TtsParam.SpeakerParam[] speaker_params)
        {
            // パラメータを格納するのに必要なバッファサイズを取得する
            AitalkCore.Result result;
            int size = 0;
            result = AitalkCore.GetParam(IntPtr.Zero, ref size);
            if ((result != AitalkCore.Result.Insufficient) || (size < Marshal.SizeOf<AitalkCore.TtsParam>()))
            {
                throw new AitalkException("動作パラメータの長さの取得に失敗しました。", result);
            }

            IntPtr ptr = Marshal.AllocCoTaskMem(size);
            try
            {
                // パラメータを読み取る
                Marshal.WriteInt32(ptr, (int)Marshal.OffsetOf<AitalkCore.TtsParam>("Size"), size);
                result = AitalkCore.GetParam(ptr, ref size);
                if (result != AitalkCore.Result.Success)
                {
                    throw new AitalkException("動作パラメータの取得に失敗しました。", result);
                }
                tts_param = Marshal.PtrToStructure<AitalkCore.TtsParam>(ptr);

                // 話者のパラメータを読み取る
                speaker_params = new AitalkCore.TtsParam.SpeakerParam[tts_param.NumberOfSpeakers];
                for (int index = 0; index < speaker_params.Length; index++)
                {
                    IntPtr speaker_ptr = IntPtr.Add(ptr, Marshal.SizeOf<AitalkCore.TtsParam>() + Marshal.SizeOf<AitalkCore.TtsParam.SpeakerParam>() * index);
                    speaker_params[index] = Marshal.PtrToStructure<AitalkCore.TtsParam.SpeakerParam>(speaker_ptr);
                }
            }
            finally
            {
                Marshal.FreeCoTaskMem(ptr);
            }
        }

        /// <summary>
        /// パラメータを設定する。
        /// param.Sizeおよびparam.NumberOfSpeakersは自動的に設定される。
        /// </summary>
        /// <param name="tts_param">パラメータ(話者パラメータを除く)</param>
        /// <param name="speaker_params">話者パラメータ</param>
        private static void SetParameters(AitalkCore.TtsParam tts_param, AitalkCore.TtsParam.SpeakerParam[] speaker_params)
        {
            // パラメータを格納するバッファを確保する
            int size = Marshal.SizeOf<AitalkCore.TtsParam>() + Marshal.SizeOf<AitalkCore.TtsParam.SpeakerParam>() * speaker_params.Length;
            IntPtr ptr = Marshal.AllocCoTaskMem(size);
            try
            {
                // パラメータを設定する
                tts_param.Size = size;
                tts_param.NumberOfSpeakers = speaker_params.Length;
                Marshal.StructureToPtr<AitalkCore.TtsParam>(tts_param, ptr, false);
                for (int index = 0; index < speaker_params.Length; index++)
                {
                    IntPtr speaker_ptr = IntPtr.Add(ptr, Marshal.SizeOf<AitalkCore.TtsParam>() + Marshal.SizeOf<AitalkCore.TtsParam.SpeakerParam>() * index);
                    Marshal.StructureToPtr<AitalkCore.TtsParam.SpeakerParam>(speaker_params[index], speaker_ptr, false);
                }
                AitalkCore.Result result;
                result = AitalkCore.SetParam(ptr);
                if (result != AitalkCore.Result.Success)
                {
                    throw new AitalkException("動作パラメータの設定に失敗しました。", result);
                }
            }
            finally
            {
                Marshal.FreeCoTaskMem(ptr);
            }
        }

        /// <summary>
        /// パラメータが更新されていれば反映する
        /// </summary>
        private static void UpdateParameter()
        {
            if (Parameter.IsParameterChanged == true)
            {
                // パラメータを更新する
                SetParameters(Parameter.TtsParam, Parameter.SpeakerParameters);
                Parameter.IsParameterChanged = false;
            }
        }

        /// <summary>
        /// テキストを読み仮名に変換する
        /// </summary>
        /// <param name="text">テキスト</param>
        /// <param name="Timeout">タイムアウト[ms]。0以下はタイムアウト無しで待ち続ける。</param>
        /// <returns>読み仮名文字列</returns>
        public static string TextToKana(string text, int timeout = 0)
        {
            UpdateParameter();

            // ShiftJISに変換する
            UnicodeToShiftJis(text, out byte[] shiftjis_bytes, out int[] shiftjis_positions);

            // コールバックメソッドとの同期オブジェクトを用意する
            KanaJobData job_data = new KanaJobData();
            job_data.BufferCapacity = 0x1000;
            job_data.Output = new List<byte>();
            job_data.CloseEvent = new EventWaitHandle(false, EventResetMode.ManualReset);
            GCHandle gc_handle = GCHandle.Alloc(job_data);
            try
            {
                // 変換を開始する
                AitalkCore.JobParam job_param;
                job_param.ModeInOut = AitalkCore.JobInOut.PlainToKana;
                job_param.UserData = GCHandle.ToIntPtr(gc_handle);
                AitalkCore.Result result;
                result = AitalkCore.TextToKana(out int job_id, ref job_param, shiftjis_bytes);
                if (result != AitalkCore.Result.Success)
                {
                    throw new AitalkException($"仮名変換が開始できませんでした。[{string.Join(",", shiftjis_bytes)}]", result);
                }

                // 変換の終了を待つ
                // timeoutで与えられた時間だけ待つ
                bool respond;
                respond = job_data.CloseEvent.WaitOne((0 < timeout) ? timeout : -1);

                // 変換を終了する
                result = AitalkCore.CloseKana(job_id);
                if (respond == false)
                {
                    throw new AitalkException("仮名変換がタイムアウトしました。");
                }
                else if (result != AitalkCore.Result.Success)
                {
                    throw new AitalkException("仮名変換が正常に終了しませんでした。", result);
                }
            }
            finally
            {
                gc_handle.Free();
            }

            // 変換結果に含まれるIrq MARKのバイト位置を文字位置へ置き換える
            Encoding encoding = Encoding.GetEncoding(932);
            //return ReplaceIrqMark(encoding.GetString(job_data.Output.ToArray()), shiftjis_positions);
            return encoding.GetString(job_data.Output.ToArray());
        }

        /// <summary>
        /// UTF-16からShiftJISに文字列を変換し、文字位置の変換テーブルを生成する。
        /// 変換後のShiftJIS文字列と変換テーブルにはヌル終端の分の要素も含まれる。
        /// </summary>
        /// <param name="unicode_string">UTF-16文字列</param>
        /// <param name="shiftjis_string">ShiftJIS文字列</param>
        /// <param name="shiftjis_positions">ShiftJISのバイト位置と文字位置の変換テーブル</param>
        private static void UnicodeToShiftJis(string unicode_string, out byte[] shiftjis_string, out int[] shiftjis_positions)
        {
            // 文字位置とUTF-16上でのワード位置の変換テーブルを取得し、
            // ShiftJIS上でのバイト位置とUTF-16上でのワード位置の変換テーブルを計算する
            Encoding encoding = Encoding.GetEncoding(932);
            byte[] shiftjis_string_internal = encoding.GetBytes(unicode_string);
            int shiftjis_length = shiftjis_string_internal.Length;
            shiftjis_positions = new int[shiftjis_length + 1];
            char[] unicode_char_array = unicode_string.ToArray();
            int[] unicode_indexes = StringInfo.ParseCombiningCharacters(unicode_string);
            int char_count = unicode_indexes.Length;
            int shiftjis_index = 0;
            for (int char_index = 0; char_index < char_count; char_index++)
            {
                int unicode_index = unicode_indexes[char_index];
                int unicode_count = (((char_index + 1) < char_count) ? unicode_indexes[char_index + 1] : unicode_string.Length) - unicode_index;
                int shiftjis_count = encoding.GetByteCount(unicode_char_array, unicode_index, unicode_count);
                for (int offset = 0; offset < shiftjis_count; offset++)
                {
                    shiftjis_positions[shiftjis_index + offset] = char_index;
                }
                shiftjis_index += shiftjis_count;
            }
            shiftjis_positions[shiftjis_length] = char_count;

            // ヌル終端を付け加える
            shiftjis_string = new byte[shiftjis_length + 1];
            Buffer.BlockCopy(shiftjis_string_internal, 0, shiftjis_string, 0, shiftjis_length);
            shiftjis_string[shiftjis_length] = 0;
        }

        /// <summary>
        /// Irq MARKによる文節位置を実際の文字位置に置き換える
        /// </summary>
        /// <param name="input">文字列</param>
        /// <param name="shiftjis_positions">ShiftJISのバイト位置と文字位置の変換テーブル</param>
        /// <returns>変換された文字列</returns>
        private static string ReplaceIrqMark(string input, int[] shiftjis_positions)
        {
            StringBuilder output = new StringBuilder();
            int shiftjis_length = shiftjis_positions.Length;
            int index = 0;
            const string StartOfIrqMark = "(Irq MARK=_AI@";
            const string EndOfIrqMask = ")";
            while (true)
            {
                int start_pos = input.IndexOf(StartOfIrqMark, index);
                if (start_pos < 0)
                {
                    output.Append(input, index, input.Length - index);
                    break;
                }
                start_pos += StartOfIrqMark.Length;
                output.Append(input, index, start_pos - index);
                int end_pos = input.IndexOf(EndOfIrqMask, start_pos);
                if (end_pos < 0)
                {
                    output.Append(input, index, input.Length - start_pos);
                    break;
                }
                if (int.TryParse(input.Substring(start_pos, end_pos - start_pos), out int shiftjis_index) == false)
                {
                    throw new AitalkException("文節位置の取得に失敗しました。");
                }
                if ((shiftjis_index < 0) || (shiftjis_length <= shiftjis_index))
                {
                    throw new AitalkException("文節位置の特定に失敗しました。");
                }
                output.Append(shiftjis_positions[shiftjis_index]);
                output.Append(EndOfIrqMask);
                index = end_pos + EndOfIrqMask.Length;
            }
            Console.WriteLine(input);
            Console.WriteLine(output.ToString());
            return output.ToString();
        }

        /// <summary>
        /// 読み仮名変換時のコールバックメソッド
        /// </summary>
        /// <param name="reason">呼び出し要因</param>
        /// <param name="job_id">ジョブID</param>
        /// <param name="user_data">ユーザーデータ(KanaJobDataへのポインタ)</param>
        /// <returns>ゼロを返す</returns>
        private static int TextBufferCallback(AitalkCore.EventReason reason, int job_id, IntPtr user_data)
        {
            GCHandle gc_handle = GCHandle.FromIntPtr(user_data);
            KanaJobData job_data = gc_handle.Target as KanaJobData;
            if (job_data == null)
            {
                return 0;
            }

            // 変換できた分だけGetKana()で読み取ってjob_dataのバッファに格納する
            int buffer_capacity = job_data.BufferCapacity;
            byte[] buffer = new byte[buffer_capacity];
            AitalkCore.Result result;
            int read_bytes;
            do
            {
                result = AitalkCore.GetKana(job_id, buffer, buffer_capacity, out read_bytes, out _);
                if (result != AitalkCore.Result.Success)
                {
                    break;
                }
                job_data.Output.AddRange(new ArraySegment<byte>(buffer, 0, read_bytes));
            }
            while ((buffer_capacity - 1) <= read_bytes);
            if (reason == AitalkCore.EventReason.TextBufferClose)
            {
                job_data.CloseEvent.Set();
            }
            return 0;
        }

        /// <summary>
        /// 読み仮名を読み上げてWAVEファイルをストリームに出力する。
        /// なお、ストリームへの書き込みは変換がすべて終わった後に行われる。
        /// </summary>
        /// <param name="kana">読み仮名</param>
        /// <param name="wave_stream">WAVEファイルの出力先ストリーム</param>
        /// <param name="timeout">タイムアウト[ms]。0以下はタイムアウト無しで待ち続ける。</param>
        public static void KanaToSpeech(string kana, Stream wave_stream, int timeout =0)
        {
            UpdateParameter();

            // コールバックメソッドとの同期オブジェクトを用意する
            SpeechJobData job_data = new SpeechJobData();
            job_data.BufferCapacity = 176400;
            job_data.Output = new List<byte>();
            job_data.EventData = new List<TtsEventData>();
            job_data.CloseEvent = new EventWaitHandle(false, EventResetMode.ManualReset);
            GCHandle gc_handle = GCHandle.Alloc(job_data);
            try
            {
                // 変換を開始する
                AitalkCore.JobParam job_param;
                job_param.ModeInOut = AitalkCore.JobInOut.KanaToWave;
                job_param.UserData = GCHandle.ToIntPtr(gc_handle);
                AitalkCore.Result result;
                UnicodeToShiftJis(kana, out byte[] shiftjis_bytes, out int[] shiftjis_positions);
                for (var i = 0; i < shiftjis_bytes.Length; i++)
                {
                    Console.Write(shiftjis_bytes[i]);
                    Console.Write(" ");
                }
                
                result = AitalkCore.TextToSpeech(out int job_id, ref job_param, shiftjis_bytes);
                if (result != AitalkCore.Result.Success)
                {
                    throw new AitalkException("音声変換が開始できませんでした。", result);
                }

                // 変換の終了を待つ
                // timeoutで与えられた時間だけ待つ
                bool respond;
                respond = job_data.CloseEvent.WaitOne((0 < timeout) ? timeout : -1);

                // 変換を終了する
                result = AitalkCore.CloseSpeech(job_id);
                if (respond == false)
                {
                    throw new AitalkException("音声変換がタイムアウトしました。");
                }
                else if (result != AitalkCore.Result.Success)
                {
                    throw new AitalkException("音声変換が正常に終了しませんでした。", result);
                }
            }
            finally
            {
                gc_handle.Free();
            }

            // TTSイベントをJSONに変換する
            // 変換後の文字列にヌル終端がてら4の倍数の長さになるようパディングを施す
            MemoryStream event_stream = new MemoryStream();
            var serializer = new DataContractJsonSerializer(typeof(List<TtsEventData>));
            serializer.WriteObject(event_stream, job_data.EventData);
            int padding = 4 - ((int)event_stream.Length % 4);
            for (int cnt = 0; cnt < padding; cnt++)
            {
                event_stream.WriteByte(0x0);
            }
            byte[] event_json = event_stream.ToArray();

            // データをWAVE形式で出力する
            // phonチャンクとしてTTSイベントを埋め込む
            byte[] data = job_data.Output.ToArray();
            var writer = new BinaryWriter(wave_stream);
            writer.Write(new byte[4] { (byte)'R', (byte)'I', (byte)'F', (byte)'F' });
            writer.Write(44 + event_json.Length + data.Length);
            writer.Write(new byte[4] { (byte)'W', (byte)'A', (byte)'V', (byte)'E' });
            writer.Write(new byte[4] { (byte)'f', (byte)'m', (byte)'t', (byte)' ' });
            writer.Write(16);
            writer.Write((short)0x1);
            writer.Write((short)1);
            writer.Write(VoiceSampleRate);
            writer.Write(2 * VoiceSampleRate);
            writer.Write((short)2);
            writer.Write((short)16);
            writer.Write(new byte[4] { (byte)'p', (byte)'h', (byte)'o', (byte)'n' });
            writer.Write(event_json.Length);
            writer.Write(event_json);
            writer.Write(new byte[4] { (byte)'d', (byte)'a', (byte)'t', (byte)'a' });
            writer.Write(data.Length);
            Console.WriteLine(data.Length);
            writer.Write(data);
        }

        /// <summary>
        /// 音声変換時のデータコールバックメソッド
        /// </summary>
        /// <param name="reason">呼び出し要因</param>
        /// <param name="job_id">ジョブID</param>
        /// <param name="tick">時刻[ms]</param>
        /// <param name="user_data">ユーザーデータ(SpeechJobDataへのポインタ)</param>
        /// <returns>ゼロを返す</returns>
        private static int RawBufferCallback(AitalkCore.EventReason reason, int job_id, long tick, IntPtr user_data)
        {
            GCHandle gc_handle = GCHandle.FromIntPtr(user_data);
            SpeechJobData job_data = gc_handle.Target as SpeechJobData;
            if (job_data == null)
            {
                return 0;
            }

            // 変換できた分だけGetData()で読み取ってjob_dataのバッファに格納する
            int buffer_capacity = job_data.BufferCapacity;
            byte[] buffer = new byte[2 * buffer_capacity];
            AitalkCore.Result result;
            int read_samples;
            do
            {
                result = AitalkCore.GetData(job_id, buffer, buffer_capacity, out read_samples); 
                if (result != AitalkCore.Result.Success)
                {
                    break;
                } 
                job_data.Output.AddRange(new ArraySegment<byte>(buffer, 0, 2 * read_samples));
            }
            while ((buffer_capacity - 1) <= read_samples);
            if (reason == AitalkCore.EventReason.RawBufferClose)
            {
                job_data.CloseEvent.Set();
            }
            return 0;
        }

        /// <summary>
        /// 音声変換時のイベントコールバックメソッド
        /// </summary>
        /// <param name="reason">呼び出し要因</param>
        /// <param name="job_id">ジョブID</param>
        /// <param name="tick">時刻[ms]</param>
        /// <param name="name">イベントの値</param>
        /// <param name="user_data">ユーザーデータ(SpeechJobDataへのポインタ)</param>
        /// <returns>ゼロを返す</returns>
        private static int TtsEventCallback(AitalkCore.EventReason reason, int job_id, long tick, string name, IntPtr user_data)
        {
            GCHandle gc_handle = GCHandle.FromIntPtr(user_data);
            SpeechJobData job_data = gc_handle.Target as SpeechJobData;
            if (job_data == null)
            {
                return 0;
            }
            switch (reason)
            {
                case AitalkCore.EventReason.PhoneticLabel:
                case AitalkCore.EventReason.Bookmark:
                case AitalkCore.EventReason.AutoBookmark:
                    job_data.EventData.Add(new TtsEventData(tick, name, reason));
                    break;
            }
            return 0;
        }

        /// <summary>
        /// パラメータ
        /// </summary>
        public static AitalkParameter Parameter { get; private set; }

        /// <summary>
        /// インストールディレクトリ
        /// </summary>
        public static string InstallDirectory { get; private set; }

        /// <summary>
        /// 初期化が成功したならtrueを返す
        /// </summary>
        public static bool IsInitialized { get; private set; } = false;

        /// <summary>
        /// 言語ライブラリが読み込まれているならtrueを返す
        /// </summary>
        public static bool IsLanguageLoaded { get { return CurrentLanguage != null; } }

        /// <summary>
        /// 読み込まれている言語ライブラリ名
        /// </summary>
        public static string CurrentLanguage { get; private set; }

        /// <summary>
        /// ボイスライブラリが読み込まれているならtrueを返す
        /// </summary>
        public static bool IsVoiceLoaded { get { return CurrentVoice != null; } }

        /// <summary>
        /// 読み込まれているボイスライブラリ名
        /// </summary>
        public static string CurrentVoice { get; private set; }

        /// <summary>
        /// 仮名変換のジョブを管理するクラス
        /// </summary>
        private class KanaJobData
        {
            public int BufferCapacity;
            public List<byte> Output;
            public EventWaitHandle CloseEvent;
        }

        /// <summary>
        /// 音声変換のジョブを管理するクラス
        /// </summary>
        private class SpeechJobData
        {
            public int BufferCapacity;
            public List<byte> Output;
            public List<TtsEventData> EventData;
            public EventWaitHandle CloseEvent;
        }

        /// <summary>
        /// TTSイベントのデータを格納する構造体
        /// </summary>
        [DataContract]
        public struct TtsEventData
        {
            [DataMember]
            public long Tick;

            [DataMember]
            public string Value;

            [DataMember]
            public string Type;

            internal TtsEventData(long tick, string value, AitalkCore.EventReason reason)
            {
                Tick = tick;
                Value = value;
                switch (reason)
                {
                    case AitalkCore.EventReason.PhoneticLabel:
                        Type = "Phonetic";
                        break;
                    case AitalkCore.EventReason.Bookmark:
                        Type = "Bookmark";
                        break;
                    case AitalkCore.EventReason.AutoBookmark:
                        Type = "AutoBookmark";
                        break;
                    default:
                        Type = "";
                        break;
                }
            }
        }

        /// <summary>
        /// ボイスライブラリのサンプルレート[Hz]
        /// </summary>
        private const int VoiceSampleRate = 44100;

        /// <summary>
        /// AITalkのタイムアウト[ms]
        /// </summary>
        private const int TimeoutMilliseconds = 1000;

        [DllImport("Kernel32.dll")]
        private static extern bool SetDllDirectory(string lpPathName);
    }

    /// <summary>
    /// AitalkWrapperの例外クラス
    /// </summary>
    [Serializable]
    public class AitalkException : Exception
    {
        public AitalkException() { }

        public AitalkException(string message)
            : base(message) { }

        internal AitalkException(string message, AitalkCore.Result result)
            : base($"{message}({result})") { }

        public AitalkException(string message, Exception inner)
            : base(message, inner) { }

        protected AitalkException(SerializationInfo info, StreamingContext context)
            : base(info, context) { }
    }
}
