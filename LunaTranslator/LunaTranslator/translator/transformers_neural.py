from translator.basetranslator import basetrans
import onnxruntime
from tokenizers import Tokenizer
import numpy as np

def cast_input(i):
    if not isinstance(i, np.ndarray):
        if isinstance(i, int):
            return np.array([i], dtype=np.int32)
        if isinstance(i, float):
            return np.array([i], dtype=np.float32)
    else:
        return i

class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def translate_sentence(self, sentence):
        input_enc = self.tokenizer.encode('<-ja2zh-> ' + sentence)
        input_ids = np.array(input_enc.ids)[np.newaxis, ...]
        self.input_feed['input_ids'] = input_ids
        sequences = self.session.run(['sequences'], input_feed=self.input_feed)
        output_ids = sequences[0][0][0]
        return self.tokenizer.decode(output_ids)

    def inittranslator(self):
        assert not self.checkempty(['模型路径','Tokenizer路径'])
        model_path = self.config['模型路径']
        tok_path = self.config['Tokenizer路径']
        self.input_feed = {'max_length': cast_input(1024), 'min_length': cast_input(1), 'num_beams': cast_input(8), 'num_return_sequences':cast_input(1), 'length_penalty':cast_input(1.1), 'repetition_penalty':cast_input(1.1)}

        self.session = onnxruntime.InferenceSession(model_path)
        self.tokenizer = Tokenizer.from_file(tok_path)

    def translate(self, content):
        translated = self.translate_sentence(content)
        return translated
