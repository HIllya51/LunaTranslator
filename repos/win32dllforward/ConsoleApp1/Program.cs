// See https://aka.ms/new-console-template for more information
 
using System.Runtime.InteropServices;
using System.Text; 

//TranslatorLibrary.DreyeTranslator dt = new TranslatorLibrary.DreyeTranslator();

//string path= Console.ReadLine();
//string s=Console.ReadLine();
//dt.TranslatorInit(path);
//Console.WriteLine(dt.TranslateAsync(s, "zh", "jp"));

  
  namespace DemoMainArgs
  {
      class Program
      {
          static void Main(string[] args)
          {
             
                System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);
                string path = args[0];
                string s = args[1];
                TranslatorLibrary.DreyeTranslator dt = new TranslatorLibrary.DreyeTranslator();

                dt.TranslatorInit(path);
                Console.WriteLine(dt.TranslateAsync(s, "zh", "jp"));
             

        }
    }
 } 
namespace TranslatorLibrary
{
    public interface ITranslator
    { 
        void TranslatorInit(string param1, string param2);
         
        string TranslateAsync(string sourceText, string desLang, string srcLang);
         
        string GetLastError();
    }
    public class DreyeTranslator
    {
        const int EC_DAT = 1;   //英中
        const int CE_DAT = 2;   //中英
        const int CJ_DAT = 3;   //中日
        const int JC_DAT = 10;  //日中


        public string FilePath;//文件路径
        private string errorInfo;//错误信息
         

        public string TranslateAsync(string sourceText, string desLang, string srcLang)
        { 

            Encoding shiftjis = Encoding.GetEncoding("shift-jis");
            Encoding gbk = Encoding.GetEncoding("gbk");
            Encoding utf8 = Encoding.GetEncoding("utf-8");
            string currentpath = Environment.CurrentDirectory;
            string workingDirectory = FilePath  ;
            string ret;
             
                Directory.SetCurrentDirectory(workingDirectory);
             

            [DllImport("TransCOM.dll", CallingConvention = CallingConvention.Cdecl)]
              static extern int MTInitCJ(int dat_index);

            [DllImport("TransCOM.dll", CallingConvention = CallingConvention.Cdecl)]
              static extern int MTEndCJ();

            [DllImport("TransCOM.dll", CallingConvention = CallingConvention.Cdecl)]
              static extern int TranTextFlowCJ(
                byte[] src,
                byte[] dest,
                int dest_size,
                int dat_index
                );

            MTInitCJ(JC_DAT); //返回值为-255
                byte[] src = shiftjis.GetBytes(sourceText);
                byte[] buffer = new byte[3000];
                TranTextFlowCJ(src, buffer, 3000, JC_DAT);

                ret = gbk.GetString(buffer);
                MTEndCJ();
                return ret;
             

            
        }

        public void TranslatorInit(string param1, string param2 = "")
        {
            FilePath = param1;
        }
    }


     
}
