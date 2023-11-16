from translator.basetranslator import basetrans
from tokenizers import Tokenizer
import subprocess

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def translate_sentence(self, sentence):
        input_enc = self.tokenizer.encode('<-ja2zh-> ' + sentence)
        input_ids = input_enc.ids
        int_seq = [len(input_ids)] + input_ids + ['\n']
        pipe_in = " ".join([str(i) for i in int_seq])
        self.proc.stdin.write(pipe_in)
        pipe_out = self.proc.stdout.readline()
        output_ids = [int(i) for i in pipe_out.split()]
        return self.tokenizer.decode(output_ids)

    def inittranslator(self):
        assert not self.checkempty(['模型路径','Tokenizer路径', '翻译器路径', '最大生成长度', '最小生成长度', '柱搜索数', '序列数', '过长惩罚', '重复惩罚'])
        model_path               = str(self.config['模型路径'])
        tok_path                 = str(self.config['Tokenizer路径'])
        ort_mt5_path             = str(self.config['翻译器路径'])
        max_length_int           = int(self.config['最大生成长度'])
        min_length_int           = int(self.config['最小生成长度'])
        num_beams_int            = int(self.config['柱搜索数'])
        num_return_sequences_int = int(self.config['序列数'])
        length_penalty_float     = float(self.config['过长惩罚'])
        repetition_penalty_float = float(self.config['重复惩罚'])
        self.proc = subprocess.Popen([ort_mt5_path, model_path, str(max_length_int), str(min_length_int), str(num_beams_int), str(num_return_sequences_int), str(length_penalty_float), str(repetition_penalty_float)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)

        self.tokenizer = Tokenizer.from_file(tok_path)

    def translate(self, content):
        translated = self.translate_sentence(content)
        return translated
