from ctypes import CDLL, c_size_t, c_void_p, POINTER, pointer, create_string_buffer
import gobject

_brotli = CDLL(gobject.GetDllpath("brotlicommon.dll"))
_brotli = CDLL(gobject.GetDllpath("brotlidec.dll"))
BrotliDecoderDecompress = _brotli.BrotliDecoderDecompress
BrotliDecoderDecompress.argtypes = c_size_t, c_void_p, POINTER(c_size_t), c_void_p


def decompress(data):
    size = c_size_t(1024)
    while 1:
        buff = create_string_buffer(size.value)
        succ = BrotliDecoderDecompress(len(data), data, pointer(size), buff)
        if succ == 0:
            size = c_size_t(size.value * 2)
        else:
            break
    return buff.raw[: size.value]
