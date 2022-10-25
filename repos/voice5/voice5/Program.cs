// See https://aka.ms/new-console-template for more information
using System.Text;


namespace AA
{
    public class BB
    {
        static bool ByteToFile(byte[] byteArray, string fileName)
        {
            bool result = false;
            try
            {
                using (FileStream fs = new FileStream(fileName, FileMode.OpenOrCreate, FileAccess.Write))
                {
                    fs.Write(byteArray, 0, byteArray.Length);
                    result = true;
                }
            }
            catch
            {
                result = false;
            }
            return result;
        }
        public static void Main(string[] argv)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

            Aitalk.AitalkWrapper.Initialize("C:\\dataH\\Yukari2", "ORXJC6AIWAUKDpDbH2al");
            Aitalk.AitalkWrapper.LoadLanguage("standard");
            Aitalk.AitalkWrapper.LoadVoice("yukari_emo_44");
            //Aitalk.AitalkWrapper.Parameter.CurrentSpeakerName = "yukari_emo_44";

            string kana = Aitalk.AitalkWrapper.TextToKana("こんにちは。明日の天気は晴れの予報です");
            Console.WriteLine(kana);
            var stream = new MemoryStream();
            Aitalk.AitalkWrapper.KanaToSpeech(kana, stream);

            // 音声を返す
            byte[] result = stream.ToArray();
            ByteToFile(result, "1.wav");

        }
    }
}
