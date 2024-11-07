from translator.basetranslator import basetrans
import ctypes
import os
import glob
import platform
import re


class TS(basetrans):
    def inittranslator(self):
        self.checkempty(["path"])
        path = self.config["path"]
        if os.path.exists(path) == False:
            raise Exception("OrtMTLib translator path incorrect")

        model_path_candidates = glob.glob(
            os.path.join(path, "translator_model", "*.onnx"), recursive=True
        )
        if len(model_path_candidates) > 0:
            model_path = model_path_candidates[0]
        else:
            raise Exception("onnx file not found!")

        tok_path_candidates = glob.glob(
            os.path.join(path, "tokenizer_model", "*.model")
        )
        if len(model_path_candidates) > 0:
            tok_path = tok_path_candidates[0]
        else:
            raise Exception("sentencepiece tokenizer file not found!")

        if platform.architecture()[0] == "64bit":
            self.setup_splib(os.path.join(path, "bin/x64/splib.dll"), tok_path)
        else:
            self.setup_splib(os.path.join(path, "bin/x86/splib.dll"), tok_path)

        if platform.architecture()[0] == "64bit":
            self.setup_ortmtlib(os.path.join(path, "bin/x64/ortmtlib.dll"), model_path)
        else:
            self.setup_ortmtlib(os.path.join(path, "bin/x86/ortmtlib.dll"), model_path)
        self.create_ort_tensors()

    def setup_splib(self, sp_dll_path, tok_path):
        self.splib = ctypes.CDLL(sp_dll_path)

        self.splib.create_sp_tokenizer.argtypes = (ctypes.c_char_p,)
        self.splib.create_sp_tokenizer.restype = ctypes.c_int

        self.splib.encode_as_ids.argtypes = (
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
            ctypes.POINTER(ctypes.c_size_t),
        )
        self.splib.encode_as_ids.restype = ctypes.c_int

        self.splib.decode_from_ids.argtypes = (
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char_p),
        )
        self.splib.decode_from_ids.restype = ctypes.c_int

        tok_path_ctypes = ctypes.c_char_p(bytes(tok_path, "utf8"))
        res = self.splib.create_sp_tokenizer(tok_path_ctypes)
        return

    def setup_ortmtlib(self, ort_dll_path, model_path):
        self.ort = ctypes.CDLL(
            os.path.join(os.path.dirname(ort_dll_path), "onnxruntime.dll")
        )
        self.ortmtlib = ctypes.CDLL(ort_dll_path)

        self.ortmtlib.create_ort_session.restype = ctypes.c_int
        self.ortmtlib.create_ort_session.argtypes = (ctypes.c_char_p, ctypes.c_int)

        self.ortmtlib.create_tensor_int32.restype = ctypes.c_int
        self.ortmtlib.create_tensor_int32.argtypes = (
            ctypes.POINTER(ctypes.c_int32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
        )

        self.ortmtlib.create_tensor_float.restype = ctypes.c_int
        self.ortmtlib.create_tensor_float.argtypes = (
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_void_p),
        )

        self.ortmtlib.run_session.argtypes = (
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
            ctypes.POINTER(ctypes.c_size_t),
        )
        self.ortmtlib.run_session.restype = ctypes.c_int

        model_path_ctypes = ctypes.c_char_p(bytes(model_path, "utf8"))
        n_threads_ctypes = ctypes.c_int(6)
        res = self.ortmtlib.create_ort_session(model_path_ctypes, n_threads_ctypes)
        return

    def create_ort_tensors(self):
        max_length = int(self.config["最大生成长度"])
        min_length = int(self.config["最小生成长度"])
        num_beams = int(self.config["柱搜索数"])
        num_return_sequences = int(self.config["序列数"])
        length_penalty = float(self.config["过长惩罚"])
        repetition_penalty = float(self.config["重复惩罚"])

        self.max_length_tensor = ctypes.c_void_p()
        self.min_length_tensor = ctypes.c_void_p()
        self.num_beams_tensor = ctypes.c_void_p()
        self.num_return_sequences_tensor = ctypes.c_void_p()
        self.length_penalty_tensor = ctypes.c_void_p()
        self.repetition_penalty_tensor = ctypes.c_void_p()

        self.shape_one = (ctypes.c_longlong * 1)(1)
        self.len_one = ctypes.c_size_t(1)

        self.max_length_ctypes = (ctypes.c_int32 * 1)(max_length)
        res = self.ortmtlib.create_tensor_int32(
            self.max_length_ctypes,
            self.len_one,
            self.shape_one,
            self.len_one,
            ctypes.byref(self.max_length_tensor),
        )

        self.min_length_ctypes = (ctypes.c_int32 * 1)(min_length)
        res = self.ortmtlib.create_tensor_int32(
            self.min_length_ctypes,
            self.len_one,
            self.shape_one,
            self.len_one,
            ctypes.byref(self.min_length_tensor),
        )

        self.num_beams_ctypes = (ctypes.c_int32 * 1)(num_beams)
        res = self.ortmtlib.create_tensor_int32(
            self.num_beams_ctypes,
            self.len_one,
            self.shape_one,
            self.len_one,
            ctypes.byref(self.num_beams_tensor),
        )

        self.num_return_sequences_ctypes = (ctypes.c_int32 * 1)(num_return_sequences)
        res = self.ortmtlib.create_tensor_int32(
            self.num_return_sequences_ctypes,
            self.len_one,
            self.shape_one,
            self.len_one,
            ctypes.byref(self.num_return_sequences_tensor),
        )

        self.length_penalty_ctypes = (ctypes.c_float * 1)(length_penalty)
        res = self.ortmtlib.create_tensor_float(
            self.length_penalty_ctypes,
            self.len_one,
            self.shape_one,
            self.len_one,
            ctypes.byref(self.length_penalty_tensor),
        )

        self.repetition_penalty_ctypes = (ctypes.c_float * 1)(repetition_penalty)
        res = self.ortmtlib.create_tensor_float(
            self.repetition_penalty_ctypes,
            self.len_one,
            self.shape_one,
            self.len_one,
            ctypes.byref(self.repetition_penalty_tensor),
        )
        return

    def encode_as_ids(self, content):
        input_str = ctypes.c_char_p(
            bytes(f"<-{self.srclang}2{self.tgtlang}-> " + content, "utf8")
        )
        token_ids = ctypes.POINTER(ctypes.c_int32)()
        n_tokens = ctypes.c_size_t()

        decoded_str = ctypes.c_char_p()
        res = self.splib.encode_as_ids(
            input_str, ctypes.byref(token_ids), ctypes.byref(n_tokens)
        )
        input_ids_len = n_tokens.value
        input_ids_py = [token_ids[i] for i in range(input_ids_len)]
        input_ids_py += [
            1
        ]  # add EOS token to notify the end of sentence and prevent repetition

        self.splib.free_ptr(token_ids)
        return input_ids_py

    def decode_from_ids(self, output_ids_py):
        output_len = len(output_ids_py)

        decoded_str = ctypes.c_char_p()
        output_ids_ctypes = (ctypes.c_int * output_len)(*output_ids_py)
        res = self.splib.decode_from_ids(
            output_ids_ctypes, output_len, ctypes.byref(decoded_str)
        )
        decoded_str_py = decoded_str.value.decode("utf8")

        self.splib.free_ptr(decoded_str)
        return decoded_str_py

    def run_session(self, input_ids_py):
        input_ids_len = len(input_ids_py)
        input_ids_tensor = ctypes.c_void_p()
        input_ids_ctypes = (ctypes.c_int32 * input_ids_len)(*input_ids_py)
        input_ids_len_ctypes = ctypes.c_size_t(input_ids_len)
        input_shape_ctypes = (ctypes.c_longlong * 2)(1, input_ids_len)
        input_shape_len_ctypes = ctypes.c_size_t(2)
        res = self.ortmtlib.create_tensor_int32(
            input_ids_ctypes,
            input_ids_len_ctypes,
            input_shape_ctypes,
            input_shape_len_ctypes,
            ctypes.byref(input_ids_tensor),
        )

        # self.ortmtlib.print_tensor_int32(input_ids_tensor)
        input_tensors = [
            input_ids_tensor,
            self.max_length_tensor,
            self.min_length_tensor,
            self.num_beams_tensor,
            self.num_return_sequences_tensor,
            self.length_penalty_tensor,
            self.repetition_penalty_tensor,
        ]
        input_tensors_ctypes = (ctypes.c_void_p * len(input_tensors))(*input_tensors)
        output_ids = ctypes.POINTER(ctypes.c_int)()
        output_len = ctypes.c_size_t()

        output_name = ctypes.c_char_p(bytes("sequences", "utf8"))
        res = self.ortmtlib.run_session(
            input_tensors_ctypes,
            output_name,
            ctypes.byref(output_ids),
            ctypes.byref(output_len),
        )

        output_ids_py = []
        for i in range(output_len.value):
            output_ids_py.append(output_ids[i])

        self.ortmtlib.release_ort_tensor(input_ids_tensor)
        self.ortmtlib.free_ptr(output_ids)
        return output_ids_py

    def translate(self, content):
        delimiters = ['.','。','\n',':','：','?','？','!','！','…','「','」',]
        raw_split = [i.strip() for i in re.split('(['+''.join(delimiters)+'])', content)]
        content_split = [i for i in raw_split if i]
        translated_list = []
        i = 0
        while i < len(content_split):
            sentence = content_split[i]
            while i + 1 < len(content_split):
                if content_split[i+1] not in delimiters:
                    break
                i += 1
                sentence += content_split[i]
            input_ids_py = self.encode_as_ids(sentence)
            output_ids_py = self.run_session(input_ids_py)
            translated_sentence = self.decode_from_ids(output_ids_py)
            translated_list.append(translated_sentence)
            i += 1
        translated = ''.join(translated_list)
        return translated

    def __del__(self):
        self.ortmtlib.release_ort_tensor(self.max_length_tensor)
        self.ortmtlib.release_ort_tensor(self.min_length_tensor)
        self.ortmtlib.release_ort_tensor(self.num_beams_tensor)
        self.ortmtlib.release_ort_tensor(self.num_return_sequences_tensor)
        self.ortmtlib.release_ort_tensor(self.length_penalty_tensor)
        self.ortmtlib.release_ort_tensor(self.repetition_penalty_tensor)
        self.ortmtlib.release_all_globals()
