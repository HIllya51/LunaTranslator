 
using System.Text; 
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;

namespace Aitalk
{
    public class AitalkParameter
    {
        /// <summary>
        /// コンストラクタ。
        /// </summary>
        /// <param name="voice_db_name">ボイスライブラリ名</param>
        /// <param name="tts_param">パラメータ</param>
        /// <param name="speaker_params">話者のパラメータリスト</param>
        internal AitalkParameter(string voice_db_name, AitalkCore.TtsParam tts_param, AitalkCore.TtsParam.SpeakerParam[] speaker_params)
        {
            VoiceDbName = voice_db_name;
            TtsParam = tts_param;
            SpeakerParameters = speaker_params;
            CurrentSpeakerName = SpeakerParameters[0].VoiceName;
            CurrentSpeakerParameter = SpeakerParameters[0];
        }

        /// <summary>
        /// JSON形式のバイト列に変換する
        /// </summary>
        /// <returns>JSON形式のバイト列</returns>
        public byte[] ToJson()
        {
            // 一時的な構造体にパラメータを格納する
            ParameterJson parameter;
            parameter.VoiceDbName = VoiceDbName;
            parameter.Speakers = SpeakerParameters;

            // JSONにシリアライズする
            using (var stream = new MemoryStream())
            {
                using (var writer = JsonReaderWriterFactory.CreateJsonWriter(stream, Encoding.UTF8, true, true, "  "))
                {
                    var serializer = new DataContractJsonSerializer(typeof(ParameterJson));
                    serializer.WriteObject(writer, parameter);
                    writer.Flush();
                }
                return stream.ToArray();
            }
        }

        /// <summary>
        /// パラメータが変更されたときにtrueになる
        /// </summary>
        public bool IsParameterChanged { get; internal set; } = true;

        /// <summary>
        /// 仮名変換時のバッファサイズ(バイト数)
        /// </summary>
        public int TextBufferCapacityInBytes
        {
            get { return TtsParam.TextBufferCapacityInBytes; }
        }

        /// <summary>
        /// 音声変換時のバッファサイズ(バイト数)
        /// </summary>
        public int RawBufferCapacityInBytes
        {
            get { return TtsParam.RawBufferCapacityInBytes; }
        }

        /// <summary>
        /// trueのとき仮名変換結果に文節終了位置を埋め込む
        /// </summary>
        public bool AutoBookmark
        {
            get { return (TtsParam.ExtendFormatFlags & AitalkCore.ExtendFormat.AutoBookmark) != 0; }
            set
            {
                IsParameterChanged |= (value != AutoBookmark);
                if (value == true)
                {
                    TtsParam.ExtendFormatFlags |= AitalkCore.ExtendFormat.AutoBookmark;
                }
                else
                {
                    TtsParam.ExtendFormatFlags &= ~AitalkCore.ExtendFormat.AutoBookmark;
                }

            }
        }

        /// <summary>
        /// trueのとき仮名変換結果にJEITA規格のルビを使う
        /// </summary>
        public bool JeitaRuby
        {
            get { return (TtsParam.ExtendFormatFlags & AitalkCore.ExtendFormat.JeitaRuby) != 0; }
            set
            {
                IsParameterChanged |= (value != JeitaRuby);
                if (value == true)
                {
                    TtsParam.ExtendFormatFlags |= AitalkCore.ExtendFormat.JeitaRuby;
                }
                else
                {
                    TtsParam.ExtendFormatFlags &= ~AitalkCore.ExtendFormat.JeitaRuby;
                }
            }
        }

        /// <summary>
        /// マスター音量(0～5)
        /// </summary>
        public double MasterVolume
        {
            get { return TtsParam.Volume; }
            set
            {
                float value_f = (float)Math.Max(MinMasterVolume, Math.Min(value, MaxMasterVolume));
                IsParameterChanged |= (value_f != TtsParam.Volume);
                TtsParam.Volume = value_f;
            }
        }
        public const double MaxMasterVolume = 5.0;
        public const double MinMasterVolume = 0.0;

        /// <summary>
        /// 話者の名前のリスト
        /// </summary>
        public string[] VoiceNames
        {
            get { return SpeakerParameters.Select(x => x.VoiceName).ToArray(); }
        }

        /// <summary>
        /// 選択中の話者
        /// </summary>
        public string CurrentSpeakerName
        {
            get { return TtsParam.VoiceName; }
            set
            {
                if (TtsParam.VoiceName == value)
                {
                    return;
                }
                var speaker_parameter = SpeakerParameters.FirstOrDefault(x => x.VoiceName == value);
                if (speaker_parameter == null)
                {
                    throw new AitalkException($"話者'{value}'は存在しません。");
                }
                CurrentSpeakerParameter = speaker_parameter;
                TtsParam.VoiceName = value;
                IsParameterChanged = true;
            }
        }

        /// <summary>
        /// 音量(0～2)
        /// </summary>
        public double VoiceVolume
        {
            get { return CurrentSpeakerParameter.Volume; }
            set
            {
                float value_f = (float)Math.Max(MinVoiceVolume, Math.Min(value, MaxVoiceVolume));
                IsParameterChanged |= (value_f != CurrentSpeakerParameter.Volume);
                CurrentSpeakerParameter.Volume = value_f;
            }
        }
        public const double MinVoiceVolume = 0.0;
        public const double MaxVoiceVolume = 2.0;

        /// <summary>
        /// 話速(0.5～4)
        /// </summary>
        public double VoiceSpeed
        {
            get { return CurrentSpeakerParameter.Speed; }
            set
            {
                float value_f = (float)Math.Max(MinVoiceSpeed, Math.Min(value, MaxVoiceSpeed));
                IsParameterChanged |= (value_f != CurrentSpeakerParameter.Speed);
                CurrentSpeakerParameter.Speed = value_f;
            }
        }
        public const double MinVoiceSpeed = 0.5;
        public const double MaxVoiceSpeed = 4.0;

        /// <summary>
        /// 高さ(0.5～2)
        /// </summary>
        public double VoicePitch
        {
            get { return CurrentSpeakerParameter.Pitch; }
            set
            {
                float value_f = (float)Math.Max(MinVoicePitch, Math.Min(value, MaxVoicePitch));
                IsParameterChanged |= (value_f != CurrentSpeakerParameter.Pitch);
                CurrentSpeakerParameter.Pitch = value_f;
            }
        }
        public const double MinVoicePitch = 0.5;
        public const double MaxVoicePitch = 2.0;

        /// <summary>
        /// 抑揚(0～2)
        /// </summary>
        public double VoiceEmphasis
        {
            get { return CurrentSpeakerParameter.Range; }
            set
            {
                float value_f = (float)Math.Max(MinVoiceEmphasis, Math.Min(value, MaxVoiceEmphasis));
                IsParameterChanged |= (value_f != CurrentSpeakerParameter.Range);
                CurrentSpeakerParameter.Range = value_f;
            }
        }
        public const double MinVoiceEmphasis = 0.0;
        public const double MaxVoiceEmphasis = 2.0;

        /// <summary>
        /// 短ポーズ時間[ms] (80～500)。PauseLong以下。
        /// </summary>
        public int PauseMiddle
        {
            get { return CurrentSpeakerParameter.PauseMiddle; }
            set
            {
                value = Math.Max(MinPauseMiddle, Math.Min(value, MaxPauseMiddle));
                IsParameterChanged |= (value != CurrentSpeakerParameter.PauseMiddle);
                CurrentSpeakerParameter.PauseMiddle = value;
                if (PauseLong < value)
                {
                    PauseLong = value;
                }
            }
        }
        public const int MinPauseMiddle = 80;
        public const int MaxPauseMiddle = 500;

        /// <summary>
        /// 長ポーズ時間[ms] (100～2000)。PauseMiddle以上。
        /// </summary>
        public int PauseLong
        {
            get { return CurrentSpeakerParameter.PauseLong; }
            set
            {
                value = Math.Max(MinPauseLong, Math.Min(value, MaxPauseLong));
                IsParameterChanged |= (value != CurrentSpeakerParameter.PauseLong);
                CurrentSpeakerParameter.PauseLong = value;
                if (value < PauseMiddle)
                {
                    PauseMiddle = value;
                }
            }
        }
        public const int MinPauseLong = 100;
        public const int MaxPauseLong = 2000;

        /// <summary>
        /// 文末ポーズ時間[ms] (0～10000)
        /// </summary>
        public int PauseSentence
        {
            get { return CurrentSpeakerParameter.PauseSentence; }
            set
            {
                value = Math.Max(MinPauseSentence, Math.Min(value, MaxPauseSentence));
                IsParameterChanged |= (value != CurrentSpeakerParameter.PauseSentence);
                CurrentSpeakerParameter.PauseSentence = value;
            }
        }
        public const int MinPauseSentence = 0;
        public const int MaxPauseSentence = 10000;

        /// <summary>
        /// ボイスライブラリ名
        /// </summary>
        internal string VoiceDbName;

        /// <summary>
        /// TTSパラメータ
        /// </summary>
        internal AitalkCore.TtsParam TtsParam;

        /// <summary>
        /// 話者パラメータのリスト
        /// </summary>
        internal AitalkCore.TtsParam.SpeakerParam[] SpeakerParameters;

        /// <summary>
        /// 選択されている話者のパラメータ
        /// </summary>
        private AitalkCore.TtsParam.SpeakerParam CurrentSpeakerParameter;

        /// <summary>
        /// JSONに変換するときに一時的に詰める構造体
        /// </summary>
        [DataContract]
        private struct ParameterJson
        {
            [DataMember]
            public string VoiceDbName;

            [DataMember]
            public AitalkCore.TtsParam.SpeakerParam[] Speakers;
        }
    }
}
