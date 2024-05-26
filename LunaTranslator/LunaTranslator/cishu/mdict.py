import math


class FlexBuffer:

    def __init__(self):

        self.blockSize = None
        self.c = None
        self.l = None
        self.buf = None

    def require(self, n):

        r = self.c - self.l + n
        if r > 0:
            self.l = self.l + self.blockSize * math.ceil(r / self.blockSize)
            # tmp = bytearray(self.l)
            # for i in len(self.buf):
            #    tmp[i] = self.buf[i]
            # self.buf = tmp
            self.buf = self.buf + bytearray(self.l - len(self.buf))
        self.c = self.c + n
        return self.buf

    def alloc(self, initSize, blockSize):

        if blockSize:
            sz = blockSize
        else:
            sz = 4096
        self.blockSize = self.roundUp(sz)
        self.c = 0
        self.l = self.roundUp(initSize) | 0
        self.l += self.blockSize - (self.l % self.blockSize)
        self.buf = bytearray(self.l)
        return self.buf

    def roundUp(self, n):

        r = n % 4
        if r == 0:
            return n
        else:
            return n + 4 - r

    def reset(self):

        self.c = 0
        self.l = len(self.buf)

    def pack(self, size):

        return self.buf[0:size]


def _decompress(inBuf, outBuf):

    c_top_loop = 1
    c_first_literal_run = 2
    c_match = 3
    c_copy_match = 4
    c_match_done = 5
    c_match_next = 6

    out = outBuf.buf
    op = 0
    ip = 0
    t = inBuf[ip]
    state = c_top_loop
    m_pos = 0
    ip_end = len(inBuf)

    if t > 17:
        ip = ip + 1
        t = t - 17
        if t < 4:
            state = c_match_next
        else:
            out = outBuf.require(t)
            while True:
                out[op] = inBuf[ip]
                op = op + 1
                ip = ip + 1
                t = t - 1
                if not t > 0:
                    break
            state = c_first_literal_run

    while True:
        if_block = False

        ##
        if state == c_top_loop:
            t = inBuf[ip]
            ip = ip + 1
            if t >= 16:
                state = c_match
                continue
            if t == 0:
                while inBuf[ip] == 0:
                    t = t + 255
                    ip = ip + 1
                t = t + 15 + inBuf[ip]
                ip = ip + 1

            t = t + 3
            out = outBuf.require(t)
            while True:
                out[op] = inBuf[ip]
                op = op + 1
                ip = ip + 1
                t = t - 1
                if not t > 0:
                    break
            # emulate c switch
            state = c_first_literal_run

        ##
        if state == c_first_literal_run:
            t = inBuf[ip]
            ip = ip + 1
            if t >= 16:
                state = c_match
                continue
            m_pos = op - 0x801 - (t >> 2) - (inBuf[ip] << 2)
            ip = ip + 1
            out = outBuf.require(3)
            out[op] = out[m_pos]
            op = op + 1
            m_pos = m_pos + 1
            out[op] = out[m_pos]
            op = op + 1
            m_pos = m_pos + 1
            out[op] = out[m_pos]
            op = op + 1

            state = c_match_done
            continue

        ##
        if state == c_match:
            if t >= 64:
                m_pos = op - 1 - ((t >> 2) & 7) - (inBuf[ip] << 3)
                ip = ip + 1
                t = (t >> 5) - 1
                state = c_copy_match
                continue
            elif t >= 32:
                t = t & 31
                if t == 0:
                    while inBuf[ip] == 0:
                        t = t + 255
                        ip = ip + 1
                    t = t + 31 + inBuf[ip]
                    ip = ip + 1
                m_pos = op - 1 - ((inBuf[ip] + (inBuf[ip + 1] << 8)) >> 2)
                ip = ip + 2
            elif t >= 16:
                m_pos = op - ((t & 8) << 11)
                t = t & 7
                if t == 0:
                    while inBuf[ip] == 0:
                        t = t + 255
                        ip = ip + 1
                    t = t + 7 + inBuf[ip]
                    ip = ip + 1
                m_pos = m_pos - ((inBuf[ip] + (inBuf[ip + 1] << 8)) >> 2)
                ip = ip + 2
                if m_pos == op:
                    break
                m_pos = m_pos - 0x4000
            else:
                m_pos = op - 1 - (t >> 2) - (inBuf[ip] << 2)
                ip = ip + 1
                out = outBuf.require(2)
                out[op] = out[m_pos]
                op = op + 1
                m_pos = m_pos + 1
                out[op] = out[m_pos]
                op = op + 1
                state = c_match_done
                continue

            if t >= 6 and (op - m_pos) >= 4:
                if_block = True
                t += 2
                out = outBuf.require(t)
                while True:
                    out[op] = out[m_pos]
                    op += 1
                    m_pos += 1
                    t -= 1
                    if not t > 0:
                        break
            # emulate c switch
            state = c_copy_match

        ##
        if state == c_copy_match:
            if not if_block:
                t += 2
                out = outBuf.require(t)
                while True:
                    out[op] = out[m_pos]
                    op += 1
                    m_pos += 1
                    t -= 1
                    if not t > 0:
                        break
            # emulating c switch
            state = c_match_done

        ##
        if state == c_match_done:
            t = inBuf[ip - 2] & 3
            if t == 0:
                state = c_top_loop
                continue
            # emulate c switch
            state = c_match_next

        ##
        if state == c_match_next:
            out = outBuf.require(1)
            out[op] = inBuf[ip]
            op += 1
            ip += 1
            if t > 1:
                out = outBuf.require(1)
                out[op] = inBuf[ip]
                op += 1
                ip += 1
                if t > 2:
                    out = outBuf.require(1)
                    out[op] = inBuf[ip]
                    op += 1
                    ip += 1
            t = inBuf[ip]
            ip += 1
            state = c_match
            continue

    return bytes(outBuf.pack(op))


class lzo:

    def decompress(input, initSize=16000, blockSize=8192):
        output = FlexBuffer()
        output.alloc(initSize, blockSize)
        return _decompress(bytearray(input), output)


""" 
Copyright by https://github.com/zhansliu/writemdict

ripemd128.py - A simple ripemd128 library in pure Python.

Supports both Python 2 (versions >= 2.6) and Python 3.

Usage:
    from ripemd128 import ripemd128
    digest = ripemd128(b"The quick brown fox jumps over the lazy dog")
    assert(digest == b"\x3f\xa9\xb5\x7f\x05\x3c\x05\x3f\xbe\x27\x35\xb2\x38\x0d\xb5\x96")

"""


import struct


# follows this description: http://homes.esat.kuleuven.be/~bosselae/ripemd/rmd128.txt


def f(j, x, y, z):
    assert 0 <= j and j < 64
    if j < 16:
        return x ^ y ^ z
    elif j < 32:
        return (x & y) | (z & ~x)
    elif j < 48:
        return (x | (0xFFFFFFFF & ~y)) ^ z
    else:
        return (x & z) | (y & ~z)


def K(j):
    assert 0 <= j and j < 64
    if j < 16:
        return 0x00000000
    elif j < 32:
        return 0x5A827999
    elif j < 48:
        return 0x6ED9EBA1
    else:
        return 0x8F1BBCDC


def Kp(j):
    assert 0 <= j and j < 64
    if j < 16:
        return 0x50A28BE6
    elif j < 32:
        return 0x5C4DD124
    elif j < 48:
        return 0x6D703EF3
    else:
        return 0x00000000


def padandsplit(message):
    """
    returns a two-dimensional array X[i][j] of 32-bit integers, where j ranges
    from 0 to 16.
    First pads the message to length in bytes is congruent to 56 (mod 64),
    by first adding a byte 0x80, and then padding with 0x00 bytes until the
    message length is congruent to 56 (mod 64). Then adds the little-endian
    64-bit representation of the original length. Finally, splits the result
    up into 64-byte blocks, which are further parsed as 32-bit integers.
    """
    origlen = len(message)
    padlength = 64 - ((origlen - 56) % 64)  # minimum padding is 1!
    message += b"\x80"
    message += b"\x00" * (padlength - 1)
    message += struct.pack("<Q", origlen * 8)
    assert len(message) % 64 == 0
    return [
        [struct.unpack("<L", message[i + j : i + j + 4])[0] for j in range(0, 64, 4)]
        for i in range(0, len(message), 64)
    ]


def add(*args):
    return sum(args) & 0xFFFFFFFF


def rol(s, x):
    assert s < 32
    return (x << s | x >> (32 - s)) & 0xFFFFFFFF


r = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    7,
    4,
    13,
    1,
    10,
    6,
    15,
    3,
    12,
    0,
    9,
    5,
    2,
    14,
    11,
    8,
    3,
    10,
    14,
    4,
    9,
    15,
    8,
    1,
    2,
    7,
    0,
    6,
    13,
    11,
    5,
    12,
    1,
    9,
    11,
    10,
    0,
    8,
    12,
    4,
    13,
    3,
    7,
    15,
    14,
    5,
    6,
    2,
]
rp = [
    5,
    14,
    7,
    0,
    9,
    2,
    11,
    4,
    13,
    6,
    15,
    8,
    1,
    10,
    3,
    12,
    6,
    11,
    3,
    7,
    0,
    13,
    5,
    10,
    14,
    15,
    8,
    12,
    4,
    9,
    1,
    2,
    15,
    5,
    1,
    3,
    7,
    14,
    6,
    9,
    11,
    8,
    12,
    2,
    10,
    0,
    4,
    13,
    8,
    6,
    4,
    1,
    3,
    11,
    15,
    0,
    5,
    12,
    2,
    13,
    9,
    7,
    10,
    14,
]
s = [
    11,
    14,
    15,
    12,
    5,
    8,
    7,
    9,
    11,
    13,
    14,
    15,
    6,
    7,
    9,
    8,
    7,
    6,
    8,
    13,
    11,
    9,
    7,
    15,
    7,
    12,
    15,
    9,
    11,
    7,
    13,
    12,
    11,
    13,
    6,
    7,
    14,
    9,
    13,
    15,
    14,
    8,
    13,
    6,
    5,
    12,
    7,
    5,
    11,
    12,
    14,
    15,
    14,
    15,
    9,
    8,
    9,
    14,
    5,
    6,
    8,
    6,
    5,
    12,
]
sp = [
    8,
    9,
    9,
    11,
    13,
    15,
    15,
    5,
    7,
    7,
    8,
    11,
    14,
    14,
    12,
    6,
    9,
    13,
    15,
    7,
    12,
    8,
    9,
    11,
    7,
    7,
    12,
    7,
    6,
    15,
    13,
    11,
    9,
    7,
    15,
    11,
    8,
    6,
    6,
    14,
    12,
    13,
    5,
    14,
    13,
    13,
    7,
    5,
    15,
    5,
    8,
    11,
    14,
    14,
    6,
    14,
    6,
    9,
    12,
    9,
    12,
    5,
    15,
    8,
]


def ripemd128(message):
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    X = padandsplit(message)
    for i in range(len(X)):
        (A, B, C, D) = (h0, h1, h2, h3)
        (Ap, Bp, Cp, Dp) = (h0, h1, h2, h3)
        for j in range(64):
            T = rol(s[j], add(A, f(j, B, C, D), X[i][r[j]], K(j)))
            (A, D, C, B) = (D, C, B, T)
            T = rol(sp[j], add(Ap, f(63 - j, Bp, Cp, Dp), X[i][rp[j]], Kp(j)))
            (Ap, Dp, Cp, Bp) = (Dp, Cp, Bp, T)
        T = add(h1, C, Dp)
        h1 = add(h2, D, Ap)
        h2 = add(h3, A, Bp)
        h3 = add(h0, B, Cp)
        h0 = T

    return struct.pack("<LLLL", h0, h1, h2, h3)


def hexstr(bstr):
    return "".join("{0:02x}".format(b) for b in bstr)


#!/usr/bin/env python
# coding: utf-8

"""
    Copyright by https://github.com/zhansliu/writemdict

    pureSalsa20.py -- a pure Python implementation of the Salsa20 cipher, ported to Python 3

    v4.0: Added Python 3 support, dropped support for Python <= 2.5.
    
    // zhansliu

    Original comments below.

    ====================================================================
    There are comments here by two authors about three pieces of software:
        comments by Larry Bugbee about
            Salsa20, the stream cipher by Daniel J. Bernstein 
                 (including comments about the speed of the C version) and
            pySalsa20, Bugbee's own Python wrapper for salsa20.c
                 (including some references), and
        comments by Steve Witham about
            pureSalsa20, Witham's pure Python 2.5 implementation of Salsa20,
                which follows pySalsa20's API, and is in this file.

    Salsa20: a Fast Streaming Cipher (comments by Larry Bugbee)
    -----------------------------------------------------------

    Salsa20 is a fast stream cipher written by Daniel Bernstein 
    that basically uses a hash function and XOR making for fast 
    encryption.  (Decryption uses the same function.)  Salsa20 
    is simple and quick.  
    
    Some Salsa20 parameter values...
        design strength    128 bits
        key length         128 or 256 bits, exactly
        IV, aka nonce      64 bits, always
        chunk size         must be in multiples of 64 bytes
    
    Salsa20 has two reduced versions, 8 and 12 rounds each.
    
    One benchmark (10 MB):
        1.5GHz PPC G4     102/97/89 MB/sec for 8/12/20 rounds
        AMD Athlon 2500+   77/67/53 MB/sec for 8/12/20 rounds
          (no I/O and before Python GC kicks in)
    
    Salsa20 is a Phase 3 finalist in the EU eSTREAM competition 
    and appears to be one of the fastest ciphers.  It is well 
    documented so I will not attempt any injustice here.  Please 
    see "References" below.
    
    ...and Salsa20 is "free for any use".  
    
    
    pySalsa20: a Python wrapper for Salsa20 (Comments by Larry Bugbee)
    ------------------------------------------------------------------

    pySalsa20.py is a simple ctypes Python wrapper.  Salsa20 is 
    as it's name implies, 20 rounds, but there are two reduced 
    versions, 8 and 12 rounds each.  Because the APIs are 
    identical, pySalsa20 is capable of wrapping all three 
    versions (number of rounds hardcoded), including a special 
    version that allows you to set the number of rounds with a 
    set_rounds() function.  Compile the version of your choice 
    as a shared library (not as a Python extension), name and 
    install it as libsalsa20.so.
    
    Sample usage:
        from pySalsa20 import Salsa20
        s20 = Salsa20(key, IV)
        dataout = s20.encryptBytes(datain)   # same for decrypt
    
    This is EXPERIMENTAL software and intended for educational 
    purposes only.  To make experimentation less cumbersome, 
    pySalsa20 is also free for any use.      
    
    THIS PROGRAM IS PROVIDED WITHOUT WARRANTY OR GUARANTEE OF
    ANY KIND.  USE AT YOUR OWN RISK.  
    
    Enjoy,
      
    Larry Bugbee
    bugbee@seanet.com
    April 2007

    
    References:
    -----------
      http://en.wikipedia.org/wiki/Salsa20
      http://en.wikipedia.org/wiki/Daniel_Bernstein
      http://cr.yp.to/djb.html
      http://www.ecrypt.eu.org/stream/salsa20p3.html
      http://www.ecrypt.eu.org/stream/p3ciphers/salsa20/salsa20_p3source.zip

     
    Prerequisites for pySalsa20:
    ----------------------------
      - Python 2.5 (haven't tested in 2.4)


    pureSalsa20: Salsa20 in pure Python 2.5 (comments by Steve Witham)
    ------------------------------------------------------------------

    pureSalsa20 is the stand-alone Python code in this file.
    It implements the underlying Salsa20 core algorithm
    and emulates pySalsa20's Salsa20 class API (minus a bug(*)).

    pureSalsa20 is MUCH slower than libsalsa20.so wrapped with pySalsa20--
    about 1/1000 the speed for Salsa20/20 and 1/500 the speed for Salsa20/8,
    when encrypting 64k-byte blocks on my computer.

    pureSalsa20 is for cases where portability is much more important than
    speed.  I wrote it for use in a "structured" random number generator.

    There are comments about the reasons for this slowness in
          http://www.tiac.net/~sw/2010/02/PureSalsa20

    Sample usage:
        from pureSalsa20 import Salsa20
        s20 = Salsa20(key, IV)
        dataout = s20.encryptBytes(datain)   # same for decrypt

    I took the test code from pySalsa20, added a bunch of tests including
    rough speed tests, and moved them into the file testSalsa20.py.  
    To test both pySalsa20 and pureSalsa20, type
        python testSalsa20.py

    (*)The bug (?) in pySalsa20 is this.  The rounds variable is global to the
    libsalsa20.so library and not switched when switching between instances
    of the Salsa20 class.
        s1 = Salsa20( key, IV, 20 )
        s2 = Salsa20( key, IV, 8 )
    In this example,
        with pySalsa20, both s1 and s2 will do 8 rounds of encryption.
        with pureSalsa20, s1 will do 20 rounds and s2 will do 8 rounds.
    Perhaps giving each instance its own nRounds variable, which
    is passed to the salsa20wordtobyte() function, is insecure.  I'm not a 
    cryptographer.

    pureSalsa20.py and testSalsa20.py are EXPERIMENTAL software and 
    intended for educational purposes only.  To make experimentation less 
    cumbersome, pureSalsa20.py and testSalsa20.py are free for any use.

    Revisions:
    ----------
      p3.2   Fixed bug that initialized the output buffer with plaintext!
             Saner ramping of nreps in speed test.
             Minor changes and print statements.
      p3.1   Took timing variability out of add32() and rot32().
             Made the internals more like pySalsa20/libsalsa .
             Put the semicolons back in the main loop!
             In encryptBytes(), modify a byte array instead of appending.
             Fixed speed calculation bug.
             Used subclasses instead of patches in testSalsa20.py .
             Added 64k-byte messages to speed test to be fair to pySalsa20.
      p3     First version, intended to parallel pySalsa20 version 3.

    More references:
    ----------------
      http://www.seanet.com/~bugbee/crypto/salsa20/          [pySalsa20]
      http://cr.yp.to/snuffle.html        [The original name of Salsa20]
      http://cr.yp.to/snuffle/salsafamily-20071225.pdf [ Salsa20 design]
      http://www.tiac.net/~sw/2010/02/PureSalsa20
    
    THIS PROGRAM IS PROVIDED WITHOUT WARRANTY OR GUARANTEE OF
    ANY KIND.  USE AT YOUR OWN RISK.  

    Cheers,

    Steve Witham sw at remove-this tiac dot net
    February, 2010
"""
import sys

assert sys.version_info >= (2, 6)

if sys.version_info >= (3,):
    integer_types = (int,)
    python3 = True
else:
    integer_types = (int, long)
    python3 = False

from struct import Struct

little_u64 = Struct("<Q")  #    little-endian 64-bit unsigned.
#    Unpacks to a tuple of one element!

little16_i32 = Struct("<16i")  # 16 little-endian 32-bit signed ints.
little4_i32 = Struct("<4i")  #  4 little-endian 32-bit signed ints.
little2_i32 = Struct("<2i")  #  2 little-endian 32-bit signed ints.

_version = "p4.0"

# ----------- Salsa20 class which emulates pySalsa20.Salsa20 ---------------


class Salsa20(object):
    def __init__(self, key=None, IV=None, rounds=20):
        self._lastChunk64 = True
        self._IVbitlen = 64  # must be 64 bits
        self.ctx = [0] * 16
        if key:
            self.setKey(key)
        if IV:
            self.setIV(IV)

        self.setRounds(rounds)

    def setKey(self, key):
        assert type(key) == bytes
        ctx = self.ctx
        if len(key) == 32:  # recommended
            constants = b"expand 32-byte k"
            ctx[1], ctx[2], ctx[3], ctx[4] = little4_i32.unpack(key[0:16])
            ctx[11], ctx[12], ctx[13], ctx[14] = little4_i32.unpack(key[16:32])
        elif len(key) == 16:
            constants = b"expand 16-byte k"
            ctx[1], ctx[2], ctx[3], ctx[4] = little4_i32.unpack(key[0:16])
            ctx[11], ctx[12], ctx[13], ctx[14] = little4_i32.unpack(key[0:16])
        else:
            raise Exception("key length isn't 32 or 16 bytes.")
        ctx[0], ctx[5], ctx[10], ctx[15] = little4_i32.unpack(constants)

    def setIV(self, IV):
        assert type(IV) == bytes
        assert len(IV) * 8 == 64, "nonce (IV) not 64 bits"
        self.IV = IV
        ctx = self.ctx
        ctx[6], ctx[7] = little2_i32.unpack(IV)
        ctx[8], ctx[9] = 0, 0  # Reset the block counter.

    setNonce = setIV  # support an alternate name

    def setCounter(self, counter):
        assert type(counter) in integer_types
        assert 0 <= counter < 1 << 64, "counter < 0 or >= 2**64"
        ctx = self.ctx
        ctx[8], ctx[9] = little2_i32.unpack(little_u64.pack(counter))

    def getCounter(self):
        return little_u64.unpack(little2_i32.pack(*self.ctx[8:10]))[0]

    def setRounds(self, rounds, testing=False):
        assert testing or rounds in [8, 12, 20], "rounds must be 8, 12, 20"
        self.rounds = rounds

    def encryptBytes(self, data):
        assert type(data) == bytes, "data must be byte string"
        assert self._lastChunk64, "previous chunk not multiple of 64 bytes"
        lendata = len(data)
        munged = bytearray(lendata)
        for i in range(0, lendata, 64):
            h = salsa20_wordtobyte(self.ctx, self.rounds, checkRounds=False)
            self.setCounter((self.getCounter() + 1) % 2**64)
            # Stopping at 2^70 bytes per nonce is user's responsibility.
            for j in range(min(64, lendata - i)):
                if python3:
                    munged[i + j] = data[i + j] ^ h[j]
                else:
                    munged[i + j] = ord(data[i + j]) ^ ord(h[j])

        self._lastChunk64 = not lendata % 64
        return bytes(munged)

    decryptBytes = encryptBytes  # encrypt and decrypt use same function


# --------------------------------------------------------------------------


def salsa20_wordtobyte(input, nRounds=20, checkRounds=True):
    """Do nRounds Salsa20 rounds on a copy of
        input: list or tuple of 16 ints treated as little-endian unsigneds.
    Returns a 64-byte string.
    """

    assert type(input) in (list, tuple) and len(input) == 16
    assert not (checkRounds) or (nRounds in [8, 12, 20])

    x = list(input)

    def XOR(a, b):
        return a ^ b

    ROTATE = rot32
    PLUS = add32

    for i in range(nRounds // 2):
        # These ...XOR...ROTATE...PLUS... lines are from ecrypt-linux.c
        # unchanged except for indents and the blank line between rounds:
        x[4] = XOR(x[4], ROTATE(PLUS(x[0], x[12]), 7))
        x[8] = XOR(x[8], ROTATE(PLUS(x[4], x[0]), 9))
        x[12] = XOR(x[12], ROTATE(PLUS(x[8], x[4]), 13))
        x[0] = XOR(x[0], ROTATE(PLUS(x[12], x[8]), 18))
        x[9] = XOR(x[9], ROTATE(PLUS(x[5], x[1]), 7))
        x[13] = XOR(x[13], ROTATE(PLUS(x[9], x[5]), 9))
        x[1] = XOR(x[1], ROTATE(PLUS(x[13], x[9]), 13))
        x[5] = XOR(x[5], ROTATE(PLUS(x[1], x[13]), 18))
        x[14] = XOR(x[14], ROTATE(PLUS(x[10], x[6]), 7))
        x[2] = XOR(x[2], ROTATE(PLUS(x[14], x[10]), 9))
        x[6] = XOR(x[6], ROTATE(PLUS(x[2], x[14]), 13))
        x[10] = XOR(x[10], ROTATE(PLUS(x[6], x[2]), 18))
        x[3] = XOR(x[3], ROTATE(PLUS(x[15], x[11]), 7))
        x[7] = XOR(x[7], ROTATE(PLUS(x[3], x[15]), 9))
        x[11] = XOR(x[11], ROTATE(PLUS(x[7], x[3]), 13))
        x[15] = XOR(x[15], ROTATE(PLUS(x[11], x[7]), 18))

        x[1] = XOR(x[1], ROTATE(PLUS(x[0], x[3]), 7))
        x[2] = XOR(x[2], ROTATE(PLUS(x[1], x[0]), 9))
        x[3] = XOR(x[3], ROTATE(PLUS(x[2], x[1]), 13))
        x[0] = XOR(x[0], ROTATE(PLUS(x[3], x[2]), 18))
        x[6] = XOR(x[6], ROTATE(PLUS(x[5], x[4]), 7))
        x[7] = XOR(x[7], ROTATE(PLUS(x[6], x[5]), 9))
        x[4] = XOR(x[4], ROTATE(PLUS(x[7], x[6]), 13))
        x[5] = XOR(x[5], ROTATE(PLUS(x[4], x[7]), 18))
        x[11] = XOR(x[11], ROTATE(PLUS(x[10], x[9]), 7))
        x[8] = XOR(x[8], ROTATE(PLUS(x[11], x[10]), 9))
        x[9] = XOR(x[9], ROTATE(PLUS(x[8], x[11]), 13))
        x[10] = XOR(x[10], ROTATE(PLUS(x[9], x[8]), 18))
        x[12] = XOR(x[12], ROTATE(PLUS(x[15], x[14]), 7))
        x[13] = XOR(x[13], ROTATE(PLUS(x[12], x[15]), 9))
        x[14] = XOR(x[14], ROTATE(PLUS(x[13], x[12]), 13))
        x[15] = XOR(x[15], ROTATE(PLUS(x[14], x[13]), 18))

    for i in range(len(input)):
        x[i] = PLUS(x[i], input[i])
    return little16_i32.pack(*x)


# --------------------------- 32-bit ops -------------------------------


def trunc32(w):
    """Return the bottom 32 bits of w as a Python int.
    This creates longs temporarily, but returns an int."""
    w = int((w & 0x7FFFFFFF) | -(w & 0x80000000))
    assert type(w) == int
    return w


def add32(a, b):
    """Add two 32-bit words discarding carry above 32nd bit,
    and without creating a Python long.
    Timing shouldn't vary.
    """
    lo = (a & 0xFFFF) + (b & 0xFFFF)
    hi = (a >> 16) + (b >> 16) + (lo >> 16)
    return (-(hi & 0x8000) | (hi & 0x7FFF)) << 16 | (lo & 0xFFFF)


def rot32(w, nLeft):
    """Rotate 32-bit word left by nLeft or right by -nLeft
    without creating a Python long.
    Timing depends on nLeft but not on w.
    """
    nLeft &= 31  # which makes nLeft >= 0
    if nLeft == 0:
        return w

    # Note: now 1 <= nLeft <= 31.
    #     RRRsLLLLLL   There are nLeft RRR's, (31-nLeft) LLLLLL's,
    # =>  sLLLLLLRRR   and one s which becomes the sign bit.
    RRR = ((w >> 1) & 0x7FFFFFFF) >> (31 - nLeft)
    sLLLLLL = -((1 << (31 - nLeft)) & w) | (0x7FFFFFFF >> nLeft) & w
    return RRR | (sLLLLLL << nLeft)


# --------------------------------- end -----------------------------------

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# readmdict.py
# Octopus MDict Dictionary File (.mdx) and Resource File (.mdd) Analyser
#
# Copyright (C) 2012, 2013, 2015 Xiaoqiang Wang <xiaoqiangwang AT gmail DOT com>
#
# This program is a free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# You can get a copy of GNU General Public License along this program
# But you can always get it from http://www.gnu.org/licenses/gpl.txt
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

from struct import pack, unpack
from io import BytesIO
import re
import sys
import json


# zlib compression is used for engine version >=2.0
import zlib

# LZO compression is used for engine version < 2.0
# try:
#     import lzo
# except ImportError:
#     lzo = None
#     print("LZO compression support is not available")

# 2x3 compatible
if sys.hexversion >= 0x03000000:
    unicode = str


def _unescape_entities(text):
    """
    unescape offending tags < > " &
    """
    text = text.replace(b"&lt;", b"<")
    text = text.replace(b"&gt;", b">")
    text = text.replace(b"&quot;", b'"')
    text = text.replace(b"&amp;", b"&")
    return text


def _fast_decrypt(data, key):
    b = bytearray(data)
    key = bytearray(key)
    previous = 0x36
    for i in range(len(b)):
        t = (b[i] >> 4 | b[i] << 4) & 0xFF
        t = t ^ previous ^ (i & 0xFF) ^ key[i % len(key)]
        previous = b[i]
        b[i] = t
    return bytes(b)


def _mdx_decrypt(comp_block):
    key = ripemd128(comp_block[4:8] + pack(b"<L", 0x3695))
    return comp_block[0:8] + _fast_decrypt(comp_block[8:], key)


def _salsa_decrypt(ciphertext, encrypt_key):
    s20 = Salsa20(key=encrypt_key, IV=b"\x00" * 8, rounds=8)
    return s20.encryptBytes(ciphertext)


def _decrypt_regcode_by_deviceid(reg_code, deviceid):
    deviceid_digest = ripemd128(deviceid)
    s20 = Salsa20(key=deviceid_digest, IV=b"\x00" * 8, rounds=8)
    encrypt_key = s20.encryptBytes(reg_code)
    return encrypt_key


def _decrypt_regcode_by_email(reg_code, email):
    email_digest = ripemd128(email.decode().encode("utf-16-le"))
    s20 = Salsa20(key=email_digest, IV=b"\x00" * 8, rounds=8)
    encrypt_key = s20.encryptBytes(reg_code)
    return encrypt_key


class MDict(object):
    """
    Base class which reads in header and key block.
    It has no public methods and serves only as code sharing base class.
    """

    def __init__(self, fname, encoding="", passcode=None):
        self._fname = fname
        self._encoding = encoding.upper()
        self._passcode = passcode

        self.header = self._read_header()
        try:
            self._key_list = self._read_keys()
        except:
            print("Try Brutal Force on Encrypted Key Blocks")
            self._key_list = self._read_keys_brutal()

    def __len__(self):
        return self._num_entries

    def __iter__(self):
        return self.keys()

    def keys(self):
        """
        Return an iterator over dictionary keys.
        """
        return (key_value for key_id, key_value in self._key_list)

    def _read_number(self, f):
        return unpack(self._number_format, f.read(self._number_width))[0]

    def _parse_header(self, header):
        """
        extract attributes from <Dict attr="value" ... >
        """
        taglist = re.findall(b'(\w+)="(.*?)"', header, re.DOTALL)
        tagdict = {}
        for key, value in taglist:
            tagdict[key] = _unescape_entities(value)
        return tagdict

    def _decode_key_block_info(self, key_block_info_compressed):
        if self._version >= 2:
            # zlib compression
            assert key_block_info_compressed[:4] == b"\x02\x00\x00\x00"
            # decrypt if needed
            if self._encrypt & 0x02:
                key_block_info_compressed = _mdx_decrypt(key_block_info_compressed)
            # decompress
            key_block_info = zlib.decompress(key_block_info_compressed[8:])
            # adler checksum
            adler32 = unpack(">I", key_block_info_compressed[4:8])[0]
            assert adler32 == zlib.adler32(key_block_info) & 0xFFFFFFFF
        else:
            # no compression
            key_block_info = key_block_info_compressed
        # decode
        key_block_info_list = []
        num_entries = 0
        i = 0
        if self._version >= 2:
            byte_format = ">H"
            byte_width = 2
            text_term = 1
        else:
            byte_format = ">B"
            byte_width = 1
            text_term = 0

        while i < len(key_block_info):
            # number of entries in current key block
            num_entries += unpack(
                self._number_format, key_block_info[i : i + self._number_width]
            )[0]
            i += self._number_width
            # text head size
            text_head_size = unpack(byte_format, key_block_info[i : i + byte_width])[0]
            i += byte_width
            # text head
            if self._encoding != "UTF-16":
                i += text_head_size + text_term
            else:
                i += (text_head_size + text_term) * 2
            # text tail size
            text_tail_size = unpack(byte_format, key_block_info[i : i + byte_width])[0]
            i += byte_width
            # text tail
            if self._encoding != "UTF-16":
                i += text_tail_size + text_term
            else:
                i += (text_tail_size + text_term) * 2
            # key block compressed size
            key_block_compressed_size = unpack(
                self._number_format, key_block_info[i : i + self._number_width]
            )[0]
            i += self._number_width
            # key block decompressed size
            key_block_decompressed_size = unpack(
                self._number_format, key_block_info[i : i + self._number_width]
            )[0]
            i += self._number_width
            key_block_info_list += [
                (key_block_compressed_size, key_block_decompressed_size)
            ]

        assert num_entries == self._num_entries

        return key_block_info_list

    def _decode_key_block(self, key_block_compressed, key_block_info_list):
        key_list = []
        i = 0
        for compressed_size, decompressed_size in key_block_info_list:
            start = i
            end = i + compressed_size
            # 4 bytes : compression type
            key_block_type = key_block_compressed[start : start + 4]
            # 4 bytes : adler checksum of decompressed key block
            adler32 = unpack(">I", key_block_compressed[start + 4 : start + 8])[0]
            if key_block_type == b"\x00\x00\x00\x00":
                key_block = key_block_compressed[start + 8 : end]
            elif key_block_type == b"\x01\x00\x00\x00":
                if lzo is None:
                    print("LZO compression is not supported")
                    break
                # decompress key block
                header = b"\xf0" + pack(">I", decompressed_size)
                key_block = lzo.decompress(
                    key_block_compressed[start + 8 : end],
                    initSize=decompressed_size,
                    blockSize=1308672,
                )
            elif key_block_type == b"\x02\x00\x00\x00":
                # decompress key block
                key_block = zlib.decompress(key_block_compressed[start + 8 : end])
            # extract one single key block into a key list
            key_list += self._split_key_block(key_block)
            # notice that adler32 returns signed value
            assert adler32 == zlib.adler32(key_block) & 0xFFFFFFFF

            i += compressed_size
        return key_list

    def _split_key_block(self, key_block):
        key_list = []
        key_start_index = 0
        while key_start_index < len(key_block):
            temp = key_block[key_start_index : key_start_index + self._number_width]
            # the corresponding record's offset in record block
            key_id = unpack(
                self._number_format,
                key_block[key_start_index : key_start_index + self._number_width],
            )[0]
            # key text ends with '\x00'
            if self._encoding == "UTF-16":
                delimiter = b"\x00\x00"
                width = 2
            else:
                delimiter = b"\x00"
                width = 1
            i = key_start_index + self._number_width
            while i < len(key_block):
                if key_block[i : i + width] == delimiter:
                    key_end_index = i
                    break
                i += width
            key_text = (
                key_block[key_start_index + self._number_width : key_end_index]
                .decode(self._encoding, errors="ignore")
                .encode("utf-8")
                .strip()
            )
            key_start_index = key_end_index + width
            key_list += [(key_id, key_text)]
        return key_list

    def _read_header(self):
        f = open(self._fname, "rb")
        # number of bytes of header text
        header_bytes_size = unpack(">I", f.read(4))[0]
        header_bytes = f.read(header_bytes_size)
        # 4 bytes: adler32 checksum of header, in little endian
        adler32 = unpack("<I", f.read(4))[0]
        assert adler32 == zlib.adler32(header_bytes) & 0xFFFFFFFF
        # mark down key block offset
        self._key_block_offset = f.tell()
        f.close()

        # header text in utf-16 encoding ending with '\x00\x00'
        header_text = header_bytes[:-2].decode("utf-16").encode("utf-8")
        header_tag = self._parse_header(header_text)
        if not self._encoding:
            encoding = header_tag[b"Encoding"]
            if sys.hexversion >= 0x03000000:
                encoding = encoding.decode("utf-8")
            # GB18030 > GBK > GB2312
            if encoding in ["GBK", "GB2312"]:
                encoding = "GB18030"
            self._encoding = encoding
        # 读取标题和描述
        if b"Title" in header_tag:
            self._title = header_tag[b"Title"].decode("utf-8")
        else:
            self._title = ""

        if b"Description" in header_tag:
            self._description = header_tag[b"Description"].decode("utf-8")
        else:
            self._description = ""
        pass
        # encryption flag
        #   0x00 - no encryption
        #   0x01 - encrypt record block
        #   0x02 - encrypt key info block
        if b"Encrypted" not in header_tag or header_tag[b"Encrypted"] == b"No":
            self._encrypt = 0
        elif header_tag[b"Encrypted"] == b"Yes":
            self._encrypt = 1
        else:
            self._encrypt = int(header_tag[b"Encrypted"])

        # stylesheet attribute if present takes form of:
        #   style_number # 1-255
        #   style_begin # or ''
        #   style_end # or ''
        # store stylesheet in dict in the form of
        # {'number' : ('style_begin', 'style_end')}
        self._stylesheet = {}
        if header_tag.get("StyleSheet"):
            lines = header_tag["StyleSheet"].splitlines()
            for i in range(0, len(lines), 3):
                self._stylesheet[lines[i]] = (lines[i + 1], lines[i + 2])

        # before version 2.0, number is 4 bytes integer
        # version 2.0 and above uses 8 bytes
        self._version = float(header_tag[b"GeneratedByEngineVersion"])
        if self._version < 2.0:
            self._number_width = 4
            self._number_format = ">I"
        else:
            self._number_width = 8
            self._number_format = ">Q"

        return header_tag

    def _read_keys(self):
        f = open(self._fname, "rb")
        f.seek(self._key_block_offset)

        # the following numbers could be encrypted
        if self._version >= 2.0:
            num_bytes = 8 * 5
        else:
            num_bytes = 4 * 4
        block = f.read(num_bytes)

        if self._encrypt & 1:
            if self._passcode is None:
                raise RuntimeError(
                    "user identification is needed to read encrypted file"
                )
            regcode, userid = self._passcode
            if isinstance(userid, unicode):
                userid = userid.encode("utf8")
            if self.header[b"RegisterBy"] == b"EMail":
                encrypted_key = _decrypt_regcode_by_email(regcode, userid)
            else:
                encrypted_key = _decrypt_regcode_by_deviceid(regcode, userid)
            block = _salsa_decrypt(block, encrypted_key)

        # decode this block
        sf = BytesIO(block)
        # number of key blocks
        num_key_blocks = self._read_number(sf)
        # number of entries
        self._num_entries = self._read_number(sf)
        # number of bytes of key block info after decompression
        if self._version >= 2.0:
            key_block_info_decomp_size = self._read_number(sf)
        # number of bytes of key block info
        key_block_info_size = self._read_number(sf)
        # number of bytes of key block
        key_block_size = self._read_number(sf)

        # 4 bytes: adler checksum of previous 5 numbers
        if self._version >= 2.0:
            adler32 = unpack(">I", f.read(4))[0]
            assert adler32 == (zlib.adler32(block) & 0xFFFFFFFF)

        # read key block info, which indicates key block's compressed and
        # decompressed size
        key_block_info = f.read(key_block_info_size)
        key_block_info_list = self._decode_key_block_info(key_block_info)
        assert num_key_blocks == len(key_block_info_list)

        # read key block
        key_block_compressed = f.read(key_block_size)
        # extract key block
        key_list = self._decode_key_block(key_block_compressed, key_block_info_list)

        self._record_block_offset = f.tell()
        f.close()

        return key_list

    def _read_keys_brutal(self):
        f = open(self._fname, "rb")
        f.seek(self._key_block_offset)

        # the following numbers could be encrypted, disregard them!
        if self._version >= 2.0:
            num_bytes = 8 * 5 + 4
            key_block_type = b"\x02\x00\x00\x00"
        else:
            num_bytes = 4 * 4
            key_block_type = b"\x01\x00\x00\x00"
        block = f.read(num_bytes)

        # key block info
        # 4 bytes '\x02\x00\x00\x00'
        # 4 bytes adler32 checksum
        # unknown number of bytes follows until '\x02\x00\x00\x00' which marks
        # the beginning of key block
        key_block_info = f.read(8)
        if self._version >= 2.0:
            assert key_block_info[:4] == b"\x02\x00\x00\x00"
        while True:
            fpos = f.tell()
            t = f.read(1024)
            index = t.find(key_block_type)
            if index != -1:
                key_block_info += t[:index]
                f.seek(fpos + index)
                break
            else:
                key_block_info += t

        key_block_info_list = self._decode_key_block_info(key_block_info)
        key_block_size = sum(list(zip(*key_block_info_list))[0])

        # read key block
        key_block_compressed = f.read(key_block_size)
        # extract key block
        key_list = self._decode_key_block(key_block_compressed, key_block_info_list)

        self._record_block_offset = f.tell()
        f.close()

        self._num_entries = len(key_list)
        return key_list


class MDD(MDict):
    """
    MDict resource file format (*.MDD) reader.
    >>> mdd = MDD('example.mdd')
    >>> len(mdd)
    208
    >>> for filename,content in mdd.items():
    ... print filename, content[:10]
    """

    def __init__(self, fname, passcode=None):
        MDict.__init__(self, fname, encoding="UTF-16", passcode=passcode)

    def items(self):
        """Return a generator which in turn produce tuples in the form of (filename, content)"""
        return self._decode_record_block()

    def _decode_record_block(self):
        f = open(self._fname, "rb")
        f.seek(self._record_block_offset)

        num_record_blocks = self._read_number(f)
        num_entries = self._read_number(f)
        assert num_entries == self._num_entries
        record_block_info_size = self._read_number(f)
        record_block_size = self._read_number(f)

        # record block info section
        record_block_info_list = []
        size_counter = 0
        for i in range(num_record_blocks):
            compressed_size = self._read_number(f)
            decompressed_size = self._read_number(f)
            record_block_info_list += [(compressed_size, decompressed_size)]
            size_counter += self._number_width * 2
        assert size_counter == record_block_info_size

        # actual record block
        offset = 0
        i = 0
        size_counter = 0
        for compressed_size, decompressed_size in record_block_info_list:
            record_block_compressed = f.read(compressed_size)
            # 4 bytes: compression type
            record_block_type = record_block_compressed[:4]
            # 4 bytes: adler32 checksum of decompressed record block
            adler32 = unpack(">I", record_block_compressed[4:8])[0]
            if record_block_type == b"\x00\x00\x00\x00":
                record_block = record_block_compressed[8:]
            elif record_block_type == b"\x01\x00\x00\x00":
                if lzo is None:
                    print("LZO compression is not supported")
                    break
                # decompress
                header = b"\xf0" + pack(">I", decompressed_size)
                record_block = lzo.decompress(
                    record_block_compressed[start + 8 : end],
                    initSize=decompressed_size,
                    blockSize=1308672,
                )
            elif record_block_type == b"\x02\x00\x00\x00":
                # decompress
                record_block = zlib.decompress(record_block_compressed[8:])

            # notice that adler32 return signed value
            assert adler32 == zlib.adler32(record_block) & 0xFFFFFFFF

            assert len(record_block) == decompressed_size
            # split record block according to the offset info from key block
            while i < len(self._key_list):
                record_start, key_text = self._key_list[i]
                # reach the end of current record block
                if record_start - offset >= len(record_block):
                    break
                # record end index
                if i < len(self._key_list) - 1:
                    record_end = self._key_list[i + 1][0]
                else:
                    record_end = len(record_block) + offset
                i += 1
                data = record_block[record_start - offset : record_end - offset]
                yield key_text, data
            offset += len(record_block)
            size_counter += compressed_size
        assert size_counter == record_block_size

        f.close()

        ### 获取 mdx 文件的索引列表，格式为
        ###  key_text(关键词，可以由后面的 keylist 得到)
        ###  file_pos(record_block开始的位置)
        ###  compressed_size(record_block压缩前的大小)
        ###  decompressed_size(解压后的大小)
        ###  record_block_type(record_block 的压缩类型)
        ###  record_start (以下三个为从 record_block 中提取某一调记录需要的参数，可以直接保存）
        ###  record_end
        ###  offset

    def get_index(self, check_block=True):
        f = open(self._fname, "rb")
        index_dict_list = []
        f.seek(self._record_block_offset)

        num_record_blocks = self._read_number(f)
        num_entries = self._read_number(f)
        assert num_entries == self._num_entries
        record_block_info_size = self._read_number(f)
        record_block_size = self._read_number(f)

        # record block info section
        record_block_info_list = []
        size_counter = 0
        for i in range(num_record_blocks):
            compressed_size = self._read_number(f)
            decompressed_size = self._read_number(f)
            record_block_info_list += [(compressed_size, decompressed_size)]
            size_counter += self._number_width * 2
        # todo:注意！！！
        assert size_counter == record_block_info_size

        # actual record block
        offset = 0
        i = 0
        size_counter = 0
        for compressed_size, decompressed_size in record_block_info_list:
            current_pos = f.tell()
            record_block_compressed = f.read(compressed_size)
            # 4 bytes: compression type
            record_block_type = record_block_compressed[:4]
            # 4 bytes: adler32 checksum of decompressed record block
            adler32 = unpack(">I", record_block_compressed[4:8])[0]
            if record_block_type == b"\x00\x00\x00\x00":
                _type = 0
                if check_block:
                    record_block = record_block_compressed[8:]
            elif record_block_type == b"\x01\x00\x00\x00":
                _type = 1
                if lzo is None:
                    print("LZO compression is not supported")
                    break
                # decompress
                header = b"\xf0" + pack(">I", decompressed_size)
                if check_block:
                    record_block = lzo.decompress(
                        record_block_compressed[start + 8 : end],
                        initSize=decompressed_size,
                        blockSize=1308672,
                    )
            elif record_block_type == b"\x02\x00\x00\x00":
                # decompress
                _type = 2
                if check_block:
                    record_block = zlib.decompress(record_block_compressed[8:])

            # notice that adler32 return signed value
            if check_block:
                assert adler32 == zlib.adler32(record_block) & 0xFFFFFFFF
                assert len(record_block) == decompressed_size
            # split record block according to the offset info from key block
            while i < len(self._key_list):
                ### 用来保存索引信息的空字典
                index_dict = {}
                index_dict["file_pos"] = current_pos
                index_dict["compressed_size"] = compressed_size
                index_dict["decompressed_size"] = decompressed_size
                index_dict["record_block_type"] = _type
                record_start, key_text = self._key_list[i]
                index_dict["record_start"] = record_start
                index_dict["key_text"] = key_text.decode("utf-8")
                index_dict["offset"] = offset
                # reach the end of current record block
                if record_start - offset >= decompressed_size:
                    break
                # record end index
                if i < len(self._key_list) - 1:
                    record_end = self._key_list[i + 1][0]
                else:
                    record_end = decompressed_size + offset
                index_dict["record_end"] = record_end
                i += 1
                if check_block:
                    data = record_block[record_start - offset : record_end - offset]
                index_dict_list.append(index_dict)
                # yield key_text, data
            offset += decompressed_size
            size_counter += compressed_size
        assert size_counter == record_block_size
        f.close()
        return index_dict_list


class MDX(MDict):
    """
    MDict dictionary file format (*.MDD) reader.
    >>> mdx = MDX('example.mdx')
    >>> len(mdx)
    42481
    >>> for key,value in mdx.items():
    ... print key, value[:10]
    """

    def __init__(self, fname, encoding="", substyle=False, passcode=None):
        MDict.__init__(self, fname, encoding, passcode)
        self._substyle = substyle

    def items(self):
        """Return a generator which in turn produce tuples in the form of (key, value)"""
        return self._decode_record_block()

    def _substitute_stylesheet(self, txt):
        # substitute stylesheet definition
        txt_list = re.split("`\d+`", txt)
        txt_tag = re.findall("`\d+`", txt)
        txt_styled = txt_list[0]
        for j, p in enumerate(txt_list[1:]):
            style = self._stylesheet[txt_tag[j][1:-1]]
            if p and p[-1] == "\n":
                txt_styled = txt_styled + style[0] + p.rstrip() + style[1] + "\r\n"
            else:
                txt_styled = txt_styled + style[0] + p + style[1]
        return txt_styled

    def _decode_record_block(self):
        f = open(self._fname, "rb")
        f.seek(self._record_block_offset)

        num_record_blocks = self._read_number(f)
        num_entries = self._read_number(f)
        assert num_entries == self._num_entries
        record_block_info_size = self._read_number(f)
        record_block_size = self._read_number(f)

        # record block info section
        record_block_info_list = []
        size_counter = 0
        for i in range(num_record_blocks):
            compressed_size = self._read_number(f)
            decompressed_size = self._read_number(f)
            record_block_info_list += [(compressed_size, decompressed_size)]
            size_counter += self._number_width * 2
        assert size_counter == record_block_info_size

        # actual record block data
        offset = 0
        i = 0
        size_counter = 0
        ###最后的索引表的格式为
        ###  key_text(关键词，可以由后面的 keylist 得到)
        ###  file_pos(record_block开始的位置)
        ###  compressed_size(record_block压缩前的大小)
        ###  decompressed_size(解压后的大小)
        ###  record_block_type(record_block 的压缩类型)
        ###  record_start (以下三个为从 record_block 中提取某一调记录需要的参数，可以直接保存）
        ###  record_end
        ###  offset
        for compressed_size, decompressed_size in record_block_info_list:
            record_block_compressed = f.read(compressed_size)
            ###### 要得到 record_block_compressed 需要得到 compressed_size (这个可以直接记录）
            ###### 另外还需要记录当前 f 对象的位置
            ###### 使用 f.tell() 命令/ 在建立索引是需要 f.seek()
            # 4 bytes indicates block compression type
            record_block_type = record_block_compressed[:4]
            # 4 bytes adler checksum of uncompressed content
            adler32 = unpack(">I", record_block_compressed[4:8])[0]
            # no compression
            if record_block_type == b"\x00\x00\x00\x00":
                record_block = record_block_compressed[8:]
            # lzo compression
            elif record_block_type == b"\x01\x00\x00\x00":
                if lzo is None:
                    print("LZO compression is not supported")
                    break
                # decompress
                header = b"\xf0" + pack(">I", decompressed_size)
                record_block = lzo.decompress(
                    record_block_compressed[8:],
                    initSize=decompressed_size,
                    blockSize=1308672,
                )
            # zlib compression
            elif record_block_type == b"\x02\x00\x00\x00":
                # decompress
                record_block = zlib.decompress(record_block_compressed[8:])
            ###### 这里比较重要的是先要得到 record_block, 而 record_block 是解压得到的，其中一共有三种解压方法
            ###### 需要的信息有 record_block_compressed, decompress_size,
            ###### record_block_type
            ###### 另外还需要校验信息 adler32
            # notice that adler32 return signed value
            assert adler32 == zlib.adler32(record_block) & 0xFFFFFFFF

            assert len(record_block) == decompressed_size
            # split record block according to the offset info from key block
            while i < len(self._key_list):
                record_start, key_text = self._key_list[i]
                # reach the end of current record block
                if record_start - offset >= len(record_block):
                    break
                # record end index
                if i < len(self._key_list) - 1:
                    record_end = self._key_list[i + 1][0]
                else:
                    record_end = len(record_block) + offset
                i += 1
                #############需要得到 record_block , record_start, record_end,
                #############offset
                record = record_block[record_start - offset : record_end - offset]
                # convert to utf-8
                record = (
                    record.decode(self._encoding, errors="ignore")
                    .strip("\x00")
                    .encode("utf-8")
                )
                # substitute styles
                #############是否替换样式表
                if self._substyle and self._stylesheet:
                    record = self._substitute_stylesheet(record)

                yield key_text, record
            offset += len(record_block)
            size_counter += compressed_size
        assert size_counter == record_block_size

        f.close()

    ### 获取 mdx 文件的索引列表，格式为
    ###  key_text(关键词，可以由后面的 keylist 得到)
    ###  file_pos(record_block开始的位置)
    ###  compressed_size(record_block压缩前的大小)
    ###  decompressed_size(解压后的大小)
    ###  record_block_type(record_block 的压缩类型)
    ###  record_start (以下三个为从 record_block 中提取某一调记录需要的参数，可以直接保存）
    ###  record_end
    ###  offset
    ### 所需 metadata
    ###
    def get_index(self, check_block=True):
        ###  索引列表
        index_dict_list = []
        f = open(self._fname, "rb")
        f.seek(self._record_block_offset)

        num_record_blocks = self._read_number(f)
        num_entries = self._read_number(f)
        assert num_entries == self._num_entries
        record_block_info_size = self._read_number(f)
        record_block_size = self._read_number(f)

        # record block info section
        record_block_info_list = []
        size_counter = 0
        for i in range(num_record_blocks):
            compressed_size = self._read_number(f)
            decompressed_size = self._read_number(f)
            record_block_info_list += [(compressed_size, decompressed_size)]
            size_counter += self._number_width * 2
        assert size_counter == record_block_info_size

        # actual record block data
        offset = 0
        i = 0
        size_counter = 0
        ###最后的索引表的格式为
        ###  key_text(关键词，可以由后面的 keylist 得到)
        ###  file_pos(record_block开始的位置)
        ###  compressed_size(record_block压缩前的大小)
        ###  decompressed_size(解压后的大小)
        ###  record_block_type(record_block 的压缩类型)
        ###  record_start (以下三个为从 record_block 中提取某一调记录需要的参数，可以直接保存）
        ###  record_end
        ###  offset
        for compressed_size, decompressed_size in record_block_info_list:
            current_pos = f.tell()
            record_block_compressed = f.read(compressed_size)
            ###### 要得到 record_block_compressed 需要得到 compressed_size (这个可以直接记录）
            ###### 另外还需要记录当前 f 对象的位置
            ###### 使用 f.tell() 命令/ 在建立索引是需要 f.seek()
            # 4 bytes indicates block compression type
            record_block_type = record_block_compressed[:4]
            # 4 bytes adler checksum of uncompressed content
            adler32 = unpack(">I", record_block_compressed[4:8])[0]
            # no compression
            if record_block_type == b"\x00\x00\x00\x00":
                _type = 0
                record_block = record_block_compressed[8:]
            # lzo compression
            elif record_block_type == b"\x01\x00\x00\x00":
                _type = 1
                if lzo is None:
                    print("LZO compression is not supported")
                    break
                # decompress
                header = b"\xf0" + pack(">I", decompressed_size)
                if check_block:
                    record_block = lzo.decompress(
                        record_block_compressed[8:],
                        initSize=decompressed_size,
                        blockSize=1308672,
                    )
            # zlib compression
            elif record_block_type == b"\x02\x00\x00\x00":
                # decompress
                _type = 2
                if check_block:
                    record_block = zlib.decompress(record_block_compressed[8:])
            ###### 这里比较重要的是先要得到 record_block, 而 record_block 是解压得到的，其中一共有三种解压方法
            ###### 需要的信息有 record_block_compressed, decompress_size,
            ###### record_block_type
            ###### 另外还需要校验信息 adler32
            # notice that adler32 return signed value
            if check_block:
                assert adler32 == zlib.adler32(record_block) & 0xFFFFFFFF
                assert len(record_block) == decompressed_size
            # split record block according to the offset info from key block
            while i < len(self._key_list):
                ### 用来保存索引信息的空字典
                index_dict = {}
                index_dict["file_pos"] = current_pos
                index_dict["compressed_size"] = compressed_size
                index_dict["decompressed_size"] = decompressed_size
                index_dict["record_block_type"] = _type
                record_start, key_text = self._key_list[i]
                index_dict["record_start"] = record_start
                index_dict["key_text"] = key_text.decode("utf-8")
                index_dict["offset"] = offset
                # reach the end of current record block
                if record_start - offset >= decompressed_size:
                    break
                # record end index
                if i < len(self._key_list) - 1:
                    record_end = self._key_list[i + 1][0]
                else:
                    record_end = decompressed_size + offset
                index_dict["record_end"] = record_end
                i += 1
                #############需要得到 record_block , record_start, record_end,
                #############offset
                if check_block:
                    record = record_block[record_start - offset : record_end - offset]
                    # convert to utf-8
                    record = (
                        record.decode(self._encoding, errors="ignore")
                        .strip("\x00")
                        .encode("utf-8")
                    )
                    # substitute styles
                    #############是否替换样式表
                    if self._substyle and self._stylesheet:
                        record = self._substitute_stylesheet(record)
                index_dict_list.append(index_dict)

            offset += decompressed_size
            size_counter += compressed_size
        # todo: 注意！！！
        # assert(size_counter == record_block_size)
        f.close
        # 这里比 mdd 部分稍有不同，应该还需要传递编码以及样式表信息
        meta = {}
        meta["encoding"] = self._encoding
        meta["stylesheet"] = json.dumps(self._stylesheet)
        meta["title"] = self._title
        meta["description"] = self._description

        return {"index_dict_list": index_dict_list, "meta": meta}


from struct import pack, unpack
from io import BytesIO
import re
import sys
import os
import sqlite3
import json

# zlib compression is used for engine version >=2.0
import zlib

# LZO compression is used for engine version < 2.0
# try:
#     import lzo
# except ImportError:
#     lzo = None
# print("LZO compression support is not available")

# 2x3 compatible
if sys.hexversion >= 0x03000000:
    unicode = str

version = "1.1"


class IndexBuilder(object):
    # todo: enable history
    def __init__(
        self,
        fname,
        encoding="",
        passcode=None,
        force_rebuild=False,
        enable_history=False,
        sql_index=True,
        check=False,
    ):
        self._mdx_file = fname
        self._mdd_file = ""
        self._encoding = ""
        self._stylesheet = {}
        self._title = ""
        self._version = ""
        self._description = ""
        self._sql_index = sql_index
        self._check = check
        _filename, _file_extension = os.path.splitext(fname)
        assert _file_extension == ".mdx"
        assert os.path.isfile(fname)
        self._mdx_db = _filename + ".mdx.db"
        # make index anyway
        if force_rebuild:
            self._make_mdx_index(self._mdx_db)
            if os.path.isfile(_filename + ".mdd"):
                self._mdd_file = _filename + ".mdd"
                self._mdd_db = _filename + ".mdd.db"
                self._make_mdd_index(self._mdd_db)

        if os.path.isfile(self._mdx_db):
            # read from META table
            conn = sqlite3.connect(self._mdx_db)
            # cursor = conn.execute("SELECT * FROM META")
            cursor = conn.execute('SELECT * FROM META WHERE key = "version"')
            # 判断有无版本号
            for cc in cursor:
                self._version = cc[1]
            ################# if not version in fo #############
            if not self._version:
                print("version info not found")
                conn.close()
                self._make_mdx_index(self._mdx_db)
                print("mdx.db rebuilt!")
                if os.path.isfile(_filename + ".mdd"):
                    self._mdd_file = _filename + ".mdd"
                    self._mdd_db = _filename + ".mdd.db"
                    self._make_mdd_index(self._mdd_db)
                    print("mdd.db rebuilt!")
                return None
            cursor = conn.execute('SELECT * FROM META WHERE key = "encoding"')
            for cc in cursor:
                self._encoding = cc[1]
            cursor = conn.execute('SELECT * FROM META WHERE key = "stylesheet"')
            for cc in cursor:
                self._stylesheet = json.loads(cc[1])

            cursor = conn.execute('SELECT * FROM META WHERE key = "title"')
            for cc in cursor:
                self._title = cc[1]

            cursor = conn.execute('SELECT * FROM META WHERE key = "description"')
            for cc in cursor:
                self._description = cc[1]

            # for cc in cursor:
            #    if cc[0] == 'encoding':
            #        self._encoding = cc[1]
            #        continue
            #    if cc[0] == 'stylesheet':
            #        self._stylesheet = json.loads(cc[1])
            #        continue
            #    if cc[0] == 'title':
            #        self._title = cc[1]
            #        continue
            #    if cc[0] == 'title':
            #        self._description = cc[1]
        else:
            self._make_mdx_index(self._mdx_db)

        if os.path.isfile(_filename + ".mdd"):
            self._mdd_file = _filename + ".mdd"
            self._mdd_db = _filename + ".mdd.db"
            if not os.path.isfile(self._mdd_db):
                self._make_mdd_index(self._mdd_db)
        pass

    def _replace_stylesheet(self, txt):
        # substitute stylesheet definition
        txt_list = re.split("`\d+`", txt)
        txt_tag = re.findall("`\d+`", txt)
        txt_styled = txt_list[0]
        for j, p in enumerate(txt_list[1:]):
            style = self._stylesheet[txt_tag[j][1:-1]]
            if p and p[-1] == "\n":
                txt_styled = txt_styled + style[0] + p.rstrip() + style[1] + "\r\n"
            else:
                txt_styled = txt_styled + style[0] + p + style[1]
        return txt_styled

    def make_sqlite(self):
        sqlite_file = self._mdx_file + ".sqlite.db"
        if os.path.exists(sqlite_file):
            os.remove(sqlite_file)
        mdx = MDX(self._mdx_file)
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        cursor.execute(
            """ CREATE TABLE MDX_DICT
                (key text not null,
                value text
                )"""
        )

        # remove '(pīnyīn)', remove `1`:
        aeiou = "āáǎàĀÁǍÀēéěèêềếĒÉĚÈÊỀẾīíǐìÍǏÌōóǒòŌÓǑÒūúǔùŪÚǓÙǖǘǚǜǕǗǙǛḾǹňŃŇ"
        pattern = r"`\d+`|[（\(]?['a-z%s]*[%s]['a-z%s]*[\)）]?" % (aeiou, aeiou, aeiou)
        tuple_list = [
            (key.decode(), re.sub(pattern, "", value.decode()))
            for key, value in mdx.items()
        ]

        cursor.executemany("INSERT INTO MDX_DICT VALUES (?,?)", tuple_list)

        returned_index = mdx.get_index(check_block=self._check)
        meta = returned_index["meta"]
        cursor.execute("""CREATE TABLE META (key text, value text)""")

        cursor.executemany(
            "INSERT INTO META VALUES (?,?)",
            [
                ("encoding", meta["encoding"]),
                ("stylesheet", meta["stylesheet"]),
                ("title", meta["title"]),
                ("description", meta["description"]),
                ("version", version),
            ],
        )

        if self._sql_index:
            cursor.execute(
                """
                CREATE INDEX key_index ON MDX_DICT (key)
                """
            )
        conn.commit()
        conn.close()

    def _make_mdx_index(self, db_name):
        if os.path.exists(db_name):
            os.remove(db_name)
        mdx = MDX(self._mdx_file)
        self._mdx_db = db_name
        returned_index = mdx.get_index(check_block=self._check)
        index_list = returned_index["index_dict_list"]
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            """ CREATE TABLE MDX_INDEX
               (key_text text not null,
                file_pos integer,
                compressed_size integer,
                decompressed_size integer,
                record_block_type integer,
                record_start integer,
                record_end integer,
                offset integer
                )"""
        )

        tuple_list = [
            (
                item["key_text"],
                item["file_pos"],
                item["compressed_size"],
                item["decompressed_size"],
                item["record_block_type"],
                item["record_start"],
                item["record_end"],
                item["offset"],
            )
            for item in index_list
        ]
        c.executemany("INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?,?)", tuple_list)
        # build the metadata table
        meta = returned_index["meta"]
        c.execute(
            """CREATE TABLE META
               (key text,
                value text
                )"""
        )

        # for k,v in meta:
        #    c.execute(
        #    'INSERT INTO META VALUES (?,?)',
        #    (k, v)
        #    )

        c.executemany(
            "INSERT INTO META VALUES (?,?)",
            [
                ("encoding", meta["encoding"]),
                ("stylesheet", meta["stylesheet"]),
                ("title", meta["title"]),
                ("description", meta["description"]),
                ("version", version),
            ],
        )

        if self._sql_index:
            c.execute(
                """
                CREATE INDEX key_index ON MDX_INDEX (key_text)
                """
            )

        conn.commit()
        conn.close()
        # set class member
        self._encoding = meta["encoding"]
        self._stylesheet = json.loads(meta["stylesheet"])
        self._title = meta["title"]
        self._description = meta["description"]

    def _make_mdd_index(self, db_name):
        if os.path.exists(db_name):
            os.remove(db_name)
        mdd = MDD(self._mdd_file)
        self._mdd_db = db_name
        index_list = mdd.get_index(check_block=self._check)
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            """ CREATE TABLE MDX_INDEX
               (key_text text not null unique,
                file_pos integer,
                compressed_size integer,
                decompressed_size integer,
                record_block_type integer,
                record_start integer,
                record_end integer,
                offset integer
                )"""
        )

        tuple_list = [
            (
                item["key_text"],
                item["file_pos"],
                item["compressed_size"],
                item["decompressed_size"],
                item["record_block_type"],
                item["record_start"],
                item["record_end"],
                item["offset"],
            )
            for item in index_list
        ]
        c.executemany("INSERT INTO MDX_INDEX VALUES (?,?,?,?,?,?,?,?)", tuple_list)
        if self._sql_index:
            c.execute(
                """
                CREATE UNIQUE INDEX key_index ON MDX_INDEX (key_text)
                """
            )

        conn.commit()
        conn.close()

    @staticmethod
    def get_data_by_index(fmdx, index):
        fmdx.seek(index["file_pos"])
        record_block_compressed = fmdx.read(index["compressed_size"])
        record_block_type = record_block_compressed[:4]
        record_block_type = index["record_block_type"]
        decompressed_size = index["decompressed_size"]
        # adler32 = unpack('>I', record_block_compressed[4:8])[0]
        if record_block_type == 0:
            _record_block = record_block_compressed[8:]
            # lzo compression
        elif record_block_type == 1:
            if lzo is None:
                print("LZO compression is not supported")
                # decompress
            header = b"\xf0" + pack(">I", index["decompressed_size"])
            _record_block = lzo.decompress(
                record_block_compressed[8:],
                initSize=decompressed_size,
                blockSize=1308672,
            )
            # zlib compression
        elif record_block_type == 2:
            # decompress
            _record_block = zlib.decompress(record_block_compressed[8:])
        data = _record_block[
            index["record_start"]
            - index["offset"] : index["record_end"]
            - index["offset"]
        ]
        return data

    def get_mdx_by_index(self, fmdx, index):
        data = self.get_data_by_index(fmdx, index)
        record = (
            data.decode(self._encoding, errors="ignore").strip("\x00").encode("utf-8")
        )
        if self._stylesheet:
            record = self._replace_stylesheet(record)
        record = record.decode("utf-8")
        return record

    def get_mdd_by_index(self, fmdx, index):
        return self.get_data_by_index(fmdx, index)

    @staticmethod
    def lookup_indexes(db, keyword, ignorecase=None):
        indexes = []
        if ignorecase:
            sql = 'SELECT * FROM MDX_INDEX WHERE lower(key_text) = lower("{}")'.format(
                keyword
            )
        else:
            sql = 'SELECT * FROM MDX_INDEX WHERE key_text = "{}"'.format(keyword)
        with sqlite3.connect(db) as conn:
            cursor = conn.execute(sql)
            for result in cursor:
                index = {}
                index["file_pos"] = result[1]
                index["compressed_size"] = result[2]
                index["decompressed_size"] = result[3]
                index["record_block_type"] = result[4]
                index["record_start"] = result[5]
                index["record_end"] = result[6]
                index["offset"] = result[7]
                indexes.append(index)
        return indexes

    def mdx_lookup(self, keyword, ignorecase=None):
        lookup_result_list = []
        indexes = self.lookup_indexes(self._mdx_db, keyword, ignorecase)
        with open(self._mdx_file, "rb") as mdx_file:
            for index in indexes:
                lookup_result_list.append(self.get_mdx_by_index(mdx_file, index))
        return lookup_result_list

    def mdd_lookup(self, keyword, ignorecase=None):
        lookup_result_list = []
        indexes = self.lookup_indexes(self._mdd_db, keyword, ignorecase)
        with open(self._mdd_file, "rb") as mdd_file:
            for index in indexes:
                lookup_result_list.append(self.get_mdd_by_index(mdd_file, index))
        return lookup_result_list

    @staticmethod
    def get_keys(db, query=""):
        if not db:
            return []
        if query:
            if "*" in query:
                query = query.replace("*", "%")
            else:
                query = query + "%"
            sql = 'SELECT key_text FROM MDX_INDEX WHERE key_text LIKE "' + query + '"'
        else:
            sql = "SELECT key_text FROM MDX_INDEX"
        with sqlite3.connect(db) as conn:
            cursor = conn.execute(sql)
            keys = [item[0] for item in cursor]
            return keys

    def get_mdd_keys(self, query=""):
        return self.get_keys(self._mdd_db, query)

    def get_mdx_keys(self, query=""):
        return self.get_keys(self._mdx_db, query)


from cishu.cishubase import cishubase
import re


class mdict(cishubase):
    def init(self):
        self.sql = None

        paths = self.config["path"]
        self.builders = []
        for f in paths.split("|"):
            if os.path.exists(f):
                try:
                    self.builders.append((IndexBuilder(f), f))
                    # with open('1.txt','a',encoding='utf8') as ff:
                    #     print(f,file=ff)
                    #     print(self.builders[-1][0].get_mdx_keys(),file=ff)
                    #     print(self.builders[-1][0].get_mdd_keys(),file=ff)
                except:
                    from traceback import print_exc

                    print_exc()

    def querycomplex(self, word, index):
        results = []
        diss = {}
        import winsharedutils

        for k in index("*" + word + "*"):
            dis = winsharedutils.distance(k, word)
            if dis <= self.config["distance"]:
                results.append(k)
                diss[k] = dis

        return sorted(results, key=lambda x: diss[x])

    def parse_strings(self, input_string):
        parsed_strings = []
        current_string = ""
        current_number = ""
        isin = False
        for c in input_string:
            if c == "`":

                isin = not isin
                if isin and len(current_number):
                    if len(current_string):
                        parsed_strings.append((int(current_number), current_string))
                        current_number = ""
                        current_string = ""
                    else:
                        isin = not isin
            elif c.isdigit() and isin:
                current_number += c
            else:
                current_string += c
        if current_string:
            if current_number:
                parsed_strings.append((int(current_number), current_string))
            else:
                parsed_strings.append(((current_number), current_string))

        return parsed_strings

    def parseashtml(self, item):

        items = self.parse_strings(item)

        html = ""

        for type_, string in items:
            ishtml = False
            if type_ == 1:
                htmlitem = f'<font color="#FF0000" size=5>{string}</font>'
            elif type_ == 3:
                htmlitem = (
                    f'<font color="#FB8C42" face="Droid Sans Fallback">{string}</font>'
                )
            elif type_ == 4:
                htmlitem = f"<font color=black>{string}</font>"
            elif type_ == 5:
                htmlitem = f'<font color="#04A6B5">{string}</font>'
            elif type_ == 6:
                htmlitem = f'<font color="#9900CC">{string}</font>'
            elif type_ == 7:
                htmlitem = f'<font color="#F27A04">{string}</font>'
            else:
                if str(type_).startswith("2"):
                    num = str(type_)[1:]
                    if len(num):
                        num += " "
                    htmlitem = f'<font color="#0000FF">{num}{string}</font>'
                elif str(type_).startswith("8"):
                    num = str(type_)[1:]
                    if len(num):
                        num += " "
                    htmlitem = f'<font color="#330099">{num}{string}</font>'
                elif (
                    str(type_).startswith("11")
                    or str(type_).startswith("9")
                    or str(type_).startswith("10")
                    or str(type_).startswith("12")
                ):
                    if str(type_).startswith("11"):
                        offset = 2
                        color = "9933FF"
                    elif str(type_).startswith("9"):
                        offset = 1
                        color = "046AA4"
                    elif str(type_).startswith("10"):
                        offset = 2
                        color = "006699"
                    elif str(type_).startswith("12"):
                        offset = 2
                        color = "F80AB8"
                    num = str(type_)[offset:]
                    if len(num):
                        idx = -1
                        for i in range(1, len(string)):
                            if string[i - 1] == " " and (not string[i].isalpha()):
                                idx = i
                                break
                        if idx != -1:
                            string = string[:idx] + num + string[idx:]
                    htmlitem = f'<font color="#{color}">{num}{string}</font>'
                else:
                    ishtml = True
                    htmlitem = string
                    # print(type_)
                # html
                # print(item)

            if not ishtml:
                htmlitem = htmlitem.replace("\r\n", "<br>")
                if not htmlitem.endswith("<br>"):
                    htmlitem += "<br>"
            html += htmlitem
        # print(html)
        return html

    def get_mime_type_from_magic(self, magic_bytes):
        if magic_bytes.startswith(b"OggS"):
            return "audio/ogg"
        elif magic_bytes.startswith(b"\x1A\x45\xDF\xA3"):  # EBML header (Matroska)
            return "video/webm"
        elif (
            magic_bytes.startswith(b"\x52\x49\x46\x46") and magic_bytes[8:12] == b"WEBP"
        ):
            return "image/webp"
        elif magic_bytes.startswith(b"\xFF\xD8\xFF"):
            return "image/jpeg"
        elif magic_bytes.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"):
            return "image/png"
        elif magic_bytes.startswith(b"GIF87a") or magic_bytes.startswith(b"GIF89a"):
            return "image/gif"
        elif magic_bytes.startswith(b"\x00\x00\x01\xBA") or magic_bytes.startswith(
            b"\x00\x00\x01\xB3"
        ):
            return "video/mpeg"
        elif magic_bytes.startswith(b"\x49\x44\x33") or magic_bytes.startswith(
            b"\xFF\xFB"
        ):
            return "audio/mpeg"
        else:
            return "application/octet-stream"

    def repairtarget(self, index, base, html_content):
        import base64

        src_pattern = r'src="([^"]+)"'
        href_pattern = r'href="([^"]+)"'

        src_matches = re.findall(src_pattern, html_content)
        href_matches = re.findall(href_pattern, html_content)

        for url in src_matches + href_matches:
            oked = False
            iscss = url.lower().endswith(".css")
            try:
                try:
                    with open(os.path.join(base, url), "rb") as f:
                        file_content = f.read()

                except:
                    url1 = url.replace("/", "\\")
                    if not url1.startswith("\\"):
                        url1 = "\\" + url1
                    try:
                        file_content = index.mdd_lookup(url1)[0]
                    except:
                        func = url.split(r"://")[0]
                        if func == "entry":
                            continue
                        url1 = url.split(r"://")[1]
                        url1 = url1.replace("/", "\\")

                        if not url1.startswith("\\"):
                            url1 = "\\" + url1
                        file_content = index.mdd_lookup(url1)[0]
                        if func == "sound":

                            base64_content = base64.b64encode(file_content).decode(
                                "utf-8"
                            )
                            import uuid

                            uid = str(uuid.uuid4())
                            # with open(uid+'.mp3','wb') as ff:
                            #     ff.write(file_content)
                            audio = f'<audio controls id="{uid}" style="display: none"><source src="data:{self.get_mime_type_from_magic(file_content)};base64,{base64_content}"></audio>'
                            html_content = audio + html_content.replace(
                                url,
                                f"javascript:document.getElementById('{uid}').play()",
                            )
                            file_content = None
                            oked = True
                        else:
                            print(url)
            except:
                file_content = None
            if file_content:
                base64_content = base64.b64encode(file_content).decode("utf-8")
                if iscss:
                    html_content = html_content.replace(
                        url, f"data:text/css;base64,{base64_content}"
                    )
                else:
                    html_content = html_content.replace(
                        url, f"data:application/octet-stream;base64,{base64_content}"
                    )
            elif not oked:
                print(url)
        return html_content

    def search(self, word):
        allres = []
        for index, f in self.builders:
            results = []
            # print(f)
            try:
                keys = self.querycomplex(word, index.get_mdx_keys)
                # print(keys)
                for k in keys:
                    content = index.mdx_lookup(k)[0]
                    match = re.match("@@@LINK=(.*)", content.strip())
                    if match:
                        match = match.groups()[0]
                        content = index.mdx_lookup(match)[0]
                    results.append(self.parseashtml(content))
            except:
                from traceback import print_exc

                print_exc()
            if len(results) == 0:
                continue

            for i in range(len(results)):
                results[i] = self.repairtarget(index, os.path.dirname(f), results[i])
            # <img src="/rjx0849.png" width="1080px"><br><center> <a href="entry://rjx0848">
            # /rjx0849.png->mddkey \\rjx0849.png entry://rjx0848->跳转到mdxkey rjx0849
            # 太麻烦，不搞了。
            allres.append((f, "".join(results)))
        if len(allres) == 0:
            return
        commonstyle = """
<script>
function onclickbtn_mdict_internal(_id) {
    tabPanes = document.querySelectorAll('.tab-widget_mdict_internal .tab-pane_mdict_internal');
    tabButtons = document.querySelectorAll('.tab-widget_mdict_internal .tab-button_mdict_internal');
        for (i = 0; i < tabButtons.length; i++)
            tabButtons[i].classList.remove('active');
        for (i = 0; i < tabPanes.length; i++)
            tabPanes[i].classList.remove('active');

        document.getElementById(_id).classList.add('active');

        tabId = document.getElementById(_id).getAttribute('data-tab');
        tabPane = document.getElementById(tabId);
        tabPane.classList.add('active');
    }
</script>
<style>
.centerdiv_mdict_internal {
    display: flex;
    justify-content: center;
}
.tab-widget_mdict_internal .tab-button_mdict_internals_mdict_internal {
    display: flex;
}

.tab-widget_mdict_internal .tab-button_mdict_internal {
    padding: 10px 20px;
    background-color: #ccc;
    border: none;
    cursor: pointer;
    display: inline-block;
}

.tab-widget_mdict_internal .tab-button_mdict_internal.active {
    background-color: #f0f0f0;
}

.tab-widget_mdict_internal .tab-content_mdict_internal .tab-pane_mdict_internal {
    display: none;
}

.tab-widget_mdict_internal .tab-content_mdict_internal .tab-pane_mdict_internal.active {
    display: block;
}
</style>
"""

        btns = []
        contents = []
        idx = 0
        for f, res in allres:
            idx += 1
            ff = os.path.basename(f)[:-4]
            btns.append(
                f"""<button type="button" onclick="onclickbtn_mdict_internal('buttonid_mdict_internal{idx}')" id="buttonid_mdict_internal{idx}" class="tab-button_mdict_internal" data-tab="tab_mdict_internal{idx}">{ff}</button>"""
            )
            contents.append(
                f"""<div id="tab_mdict_internal{idx}" class="tab-pane_mdict_internal">{res}</div>"""
            )
        res = f"""
    {commonstyle}
<div class="tab-widget_mdict_internal">
    <div class="centerdiv_mdict_internal">
        <div class="tab-buttons_mdict_internal" id="tab_buttons_mdict_internal">
        {''.join(btns)}
        </div>
    </div>
    <div>
        <div class="tab-content_mdict_internal" id="tab_contents_mdict_internal">
            {''.join(contents)}
        </div>
    </div>
</div>
<script>
if(document.querySelectorAll('.tab-widget_mdict_internal .tab-button_mdict_internal').length)
document.querySelectorAll('.tab-widget_mdict_internal .tab-button_mdict_internal')[0].click()
</script>
"""
        return res
