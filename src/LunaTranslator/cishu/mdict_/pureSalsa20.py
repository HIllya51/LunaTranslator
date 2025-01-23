# coding: utf-8
# mypy: ignore-errors

# Copyright (C) 2016-2023 Saeed Rasooli on https://github.com/ilius/pyglossary/
# Copyright (C) 2015 Z. H. Liu on https://github.com/zhansliu/writemdict

# pureSalsa20.py -- a pure Python implementation of the Salsa20 cipher,
# ported to Python 3

# v4.0: Added Python 3 support, dropped support for Python <= 2.5.

# // zhansliu

# Original comments below.

# ====================================================================
# There are comments here by two authors about three pieces of software:
# 	comments by Larry Bugbee about
# 		Salsa20, the stream cipher by Daniel J. Bernstein
# 				(including comments about the speed of the C version) and
# 		pySalsa20, Bugbee's own Python wrapper for salsa20.c
# 				(including some references), and
# 	comments by Steve Witham about
# 		pureSalsa20, Witham's pure Python 2.5 implementation of Salsa20,
# 			which follows pySalsa20's API, and is in this file.

# Salsa20: a Fast Streaming Cipher (comments by Larry Bugbee)
# -----------------------------------------------------------

# Salsa20 is a fast stream cipher written by Daniel Bernstein
# that basically uses a hash function and XOR making for fast
# encryption.  (Decryption uses the same function.)  Salsa20
# is simple and quick.

# Some Salsa20 parameter values...
# 	design strength    128 bits
# 	key length         128 or 256 bits, exactly
# 	IV, aka nonce      64 bits, always
# 	chunk size         must be in multiples of 64 bytes

# Salsa20 has two reduced versions, 8 and 12 rounds each.

# One benchmark (10 MB):
# 	1.5GHz PPC G4     102/97/89 MB/sec for 8/12/20 rounds
# 	AMD Athlon 2500+   77/67/53 MB/sec for 8/12/20 rounds
# 		(no I/O and before Python GC kicks in)

# Salsa20 is a Phase 3 finalist in the EU eSTREAM competition
# and appears to be one of the fastest ciphers.  It is well
# documented so I will not attempt any injustice here.  Please
# see "References" below.

# ...and Salsa20 is "free for any use".


# pySalsa20: a Python wrapper for Salsa20 (Comments by Larry Bugbee)
# ------------------------------------------------------------------

# pySalsa20.py is a simple ctypes Python wrapper.  Salsa20 is
# as it's name implies, 20 rounds, but there are two reduced
# versions, 8 and 12 rounds each.  Because the APIs are
# identical, pySalsa20 is capable of wrapping all three
# versions (number of rounds hardcoded), including a special
# version that allows you to set the number of rounds with a
# set_rounds() function.  Compile the version of your choice
# as a shared library (not as a Python extension), name and
# install it as libsalsa20.so.

# Sample usage:
# 	from pySalsa20 import Salsa20
# 	s20 = Salsa20(key, IV)
# 	dataout = s20.encryptBytes(datain)   # same for decrypt

# This is EXPERIMENTAL software and intended for educational
# purposes only.  To make experimentation less cumbersome,
# pySalsa20 is also free for any use.

# THIS PROGRAM IS PROVIDED WITHOUT WARRANTY OR GUARANTEE OF
# ANY KIND.  USE AT YOUR OWN RISK.

# Enjoy,

# Larry Bugbee
# bugbee@seanet.com
# April 2007


# References:
# -----------
# 	http://en.wikipedia.org/wiki/Salsa20
# 	http://en.wikipedia.org/wiki/Daniel_Bernstein
# 	http://cr.yp.to/djb.html
# 	http://www.ecrypt.eu.org/stream/salsa20p3.html
# 	http://www.ecrypt.eu.org/stream/p3ciphers/salsa20/salsa20_p3source.zip


# Prerequisites for pySalsa20:
# ----------------------------
# 	- Python 2.5 (haven't tested in 2.4)


# pureSalsa20: Salsa20 in pure Python 2.5 (comments by Steve Witham)
# ------------------------------------------------------------------

# pureSalsa20 is the stand-alone Python code in this file.
# It implements the underlying Salsa20 core algorithm
# and emulates pySalsa20's Salsa20 class API (minus a bug(*)).

# pureSalsa20 is MUCH slower than libsalsa20.so wrapped with pySalsa20--
# about 1/1000 the speed for Salsa20/20 and 1/500 the speed for Salsa20/8,
# when encrypting 64k-byte blocks on my computer.

# pureSalsa20 is for cases where portability is much more important than
# speed.  I wrote it for use in a "structured" random number generator.

# There are comments about the reasons for this slowness in
# 		http://www.tiac.net/~sw/2010/02/PureSalsa20

# Sample usage:
# 	from pureSalsa20 import Salsa20
# 	s20 = Salsa20(key, IV)
# 	dataout = s20.encryptBytes(datain)   # same for decrypt

# I took the test code from pySalsa20, added a bunch of tests including
# rough speed tests, and moved them into the file testSalsa20.py.
# To test both pySalsa20 and pureSalsa20, type
# 	python testSalsa20.py

# (*)The bug (?) in pySalsa20 is this.  The rounds variable is global to the
# libsalsa20.so library and not switched when switching between instances
# of the Salsa20 class.
# 	s1 = Salsa20( key, IV, 20 )
# 	s2 = Salsa20( key, IV, 8 )
# In this example,
# 	with pySalsa20, both s1 and s2 will do 8 rounds of encryption.
# 	with pureSalsa20, s1 will do 20 rounds and s2 will do 8 rounds.
# Perhaps giving each instance its own nRounds variable, which
# is passed to the salsa20wordtobyte() function, is insecure.  I'm not a
# cryptographer.

# pureSalsa20.py and testSalsa20.py are EXPERIMENTAL software and
# intended for educational purposes only.  To make experimentation less
# cumbersome, pureSalsa20.py and testSalsa20.py are free for any use.

# Revisions:
# ----------
# 	p3.2   Fixed bug that initialized the output buffer with plaintext!
# 			Saner ramping of nreps in speed test.
# 			Minor changes and print statements.
# 	p3.1   Took timing variability out of add32() and rot32().
# 			Made the internals more like pySalsa20/libsalsa .
# 			Put the semicolons back in the main loop!
# 			In encryptBytes(), modify a byte array instead of appending.
# 			Fixed speed calculation bug.
# 			Used subclasses instead of patches in testSalsa20.py .
# 			Added 64k-byte messages to speed test to be fair to pySalsa20.
# 	p3     First version, intended to parallel pySalsa20 version 3.

# More references:
# ----------------
# 	http://www.seanet.com/~bugbee/crypto/salsa20/          [pySalsa20]
# 	http://cr.yp.to/snuffle.html        [The original name of Salsa20]
# 	http://cr.yp.to/snuffle/salsafamily-20071225.pdf [ Salsa20 design]
# 	http://www.tiac.net/~sw/2010/02/PureSalsa20

# THIS PROGRAM IS PROVIDED WITHOUT WARRANTY OR GUARANTEE OF
# ANY KIND.  USE AT YOUR OWN RISK.

# Cheers,

# Steve Witham sw at remove-this tiac dot net
# February, 2010


import operator
from struct import Struct

__all__ = ["Salsa20"]

little_u64 = Struct("<Q")  # little-endian 64-bit unsigned.
# Unpacks to a tuple of one element!

little16_i32 = Struct("<16i")  # 16 little-endian 32-bit signed ints.
little4_i32 = Struct("<4i")  # 4 little-endian 32-bit signed ints.
little2_i32 = Struct("<2i")  # 2 little-endian 32-bit signed ints.

_version = "p4.0"

# ----------- Salsa20 class which emulates pySalsa20.Salsa20 ---------------


class Salsa20:
	def __init__(self, key=None, IV=None, rounds=20) -> None:
		self._lastChunk64 = True
		self._IVbitlen = 64  # must be 64 bits
		self.ctx = [0] * 16
		if key:
			self.setKey(key)
		if IV:
			self.setIV(IV)

		self.setRounds(rounds)

	def setKey(self, key):
		assert isinstance(key, bytes)
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
			raise ValueError("key length isn't 32 or 16 bytes.")
		ctx[0], ctx[5], ctx[10], ctx[15] = little4_i32.unpack(constants)

	def setIV(self, IV):
		assert isinstance(IV, bytes)
		assert len(IV) * 8 == 64, "nonce (IV) not 64 bits"
		self.IV = IV
		ctx = self.ctx
		ctx[6], ctx[7] = little2_i32.unpack(IV)
		ctx[8], ctx[9] = 0, 0  # Reset the block counter.

	setNonce = setIV  # support an alternate name

	def setCounter(self, counter):
		assert isinstance(counter, int)
		assert 0 <= counter < 1 << 64, "counter < 0 or >= 2**64"
		ctx = self.ctx
		ctx[8], ctx[9] = little2_i32.unpack(little_u64.pack(counter))

	def getCounter(self):
		return little_u64.unpack(little2_i32.pack(*self.ctx[8:10]))[0]

	def setRounds(self, rounds, testing=False):
		assert testing or rounds in {8, 12, 20}, "rounds must be 8, 12, 20"
		self.rounds = rounds

	def encryptBytes(self, data: bytes) -> bytes:
		assert isinstance(data, bytes), "data must be byte string"
		assert self._lastChunk64, "previous chunk not multiple of 64 bytes"
		lendata = len(data)
		munged = bytearray(lendata)
		for i in range(0, lendata, 64):
			h = salsa20_wordtobyte(self.ctx, self.rounds, checkRounds=False)
			self.setCounter((self.getCounter() + 1) % 2**64)
			# Stopping at 2^70 bytes per nonce is user's responsibility.
			for j in range(min(64, lendata - i)):
				munged[i + j] = data[i + j] ^ h[j]

		self._lastChunk64 = not lendata % 64
		return bytes(munged)

	decryptBytes = encryptBytes  # encrypt and decrypt use same function


# --------------------------------------------------------------------------


def salsa20_wordtobyte(input_, nRounds=20, checkRounds=True):
	"""
	Do nRounds Salsa20 rounds on a copy of
			input: list or tuple of 16 ints treated as little-endian unsigneds.
	Returns a 64-byte string.
	"""
	assert isinstance(input_, list | tuple) and len(input_) == 16
	assert not checkRounds or nRounds in {8, 12, 20}

	x = list(input_)

	XOR = operator.xor

	ROTATE = rot32
	PLUS = add32

	for _ in range(nRounds // 2):
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

	for idx, item in enumerate(input_):
		x[idx] = PLUS(x[idx], item)
	return little16_i32.pack(*x)


# --------------------------- 32-bit ops -------------------------------


def trunc32(w):
	"""
	Return the bottom 32 bits of w as a Python int.
	This creates longs temporarily, but returns an int.
	"""
	w = int((w & 0x7FFFFFFF) | -(w & 0x80000000))
	assert isinstance(w, int)
	return w


def add32(a, b):
	"""
	Add two 32-bit words discarding carry above 32nd bit,
	and without creating a Python long.
	Timing shouldn't vary.
	"""
	lo = (a & 0xFFFF) + (b & 0xFFFF)
	hi = (a >> 16) + (b >> 16) + (lo >> 16)
	return (-(hi & 0x8000) | (hi & 0x7FFF)) << 16 | (lo & 0xFFFF)


def rot32(w, nLeft):
	"""
	Rotate 32-bit word left by nLeft or right by -nLeft
	without creating a Python long.
	Timing depends on nLeft but not on w.
	"""
	nLeft &= 31  # which makes nLeft >= 0
	if nLeft == 0:
		return w

	# Note: now 1 <= nLeft <= 31.
	# 	 RRRsLLLLLL   There are nLeft RRR's, (31-nLeft) LLLLLL's,
	# =>  sLLLLLLRRR   and one s which becomes the sign bit.
	RRR = ((w >> 1) & 0x7FFFFFFF) >> (31 - nLeft)
	sLLLLLL = -((1 << (31 - nLeft)) & w) | (0x7FFFFFFF >> nLeft) & w
	return RRR | (sLLLLLL << nLeft)


# --------------------------------- end -----------------------------------