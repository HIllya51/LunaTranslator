import numpy as np
class process_pred(object):
    def __init__(self, character_dict_path=None,   use_space_char=False):
        self.character_str = ''
        with open(character_dict_path, 'rb') as fin:
            lines = fin.readlines()
            for line in lines:
                line = line.decode('utf-8').strip('\n').strip('\r\n')
                self.character_str += line
        if use_space_char:
            self.character_str += ' '
        dict_character = list(self.character_str)

        dict_character = self.add_special_char(dict_character)
        self.dict = {}
        for i, char in enumerate(dict_character):
            self.dict[char] = i
        self.character = dict_character

    def add_special_char(self, dict_character):
        dict_character = ['blank'] + dict_character
        return dict_character

    def decode(self, text_index, text_prob=None, is_remove_duplicate=False):
        result_list = []
        ignored_tokens = [0]
        batch_size = len(text_index)
        for batch_idx in range(batch_size):
            char_list = []
            conf_list = []
            for idx in range(len(text_index[batch_idx])):
                if text_index[batch_idx][idx] in ignored_tokens:
                    continue
                if is_remove_duplicate:
                    if idx > 0 and text_index[batch_idx][idx - 1] == text_index[batch_idx][idx]:
                        continue
                char_list.append(self.character[int(text_index[batch_idx][idx])])
                if text_prob is not None:
                    conf_list.append(text_prob[batch_idx][idx])
                else:
                    conf_list.append(1)
            text = ''.join(char_list)
            result_list.append((text, np.mean(conf_list)))
        return result_list

    def __call__(self, preds, label=None):
        if not isinstance(preds, np.ndarray):
            preds = np.array(preds)
        preds_idx = preds.argmax(axis=2)
        preds_prob = preds.max(axis=2)
        text = self.decode(preds_idx, preds_prob, is_remove_duplicate=True)
        if label is None:
            return text
        label = self.decode(label)
        return text, label