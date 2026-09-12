import struct

SD = open('../SYSTEM.DAT', 'rb').read()
DESC = 0x456000
COUNT = struct.unpack('<I', SD[DESC:DESC+4])[0]
OFFS = [struct.unpack('<I', SD[DESC+4+i*4:DESC+8+i*4])[0] for i in range(COUNT)]
print('descriptor @0x%x count=%d' % (DESC, COUNT))
print('first offsets:', [hex(o) for o in OFFS[:6]])
print('last offset:', hex(OFFS[-1]))

def melt8Ex(src, size=0x120):
    # LZ+RLE decoder. src: list/bytes starting at token stream. Returns bytearray(size).
    out = bytearray()
    t1 = 0
    n = len(src)
    while len(out) < size:
        if t1 >= n:
            break
        a0 = src[t1]; t1 += 1
        if a0 & 0x80:
            if a0 & 0x40:
                # RLE run
                t2 = (a0 & 0x1f) + 2
                if a0 & 0x20:
                    b = src[t1]; t1 += 1
                    t2 += (b << 5)
                val = src[t1]; t1 += 1
                for _ in range(t2):
                    if len(out) >= size: break
                    out.append(val)
            else:
                # back-reference (LZ copy)
                b1 = src[t1]; t1 += 1
                length = ((a0 & 0x3c) >> 2) + 2
                dist = b1 + ((a0 & 3) << 8)
                sp = len(out) - dist - 1
                for _ in range(length):
                    if len(out) >= size: break
                    out.append(out[sp]); sp += 1
        else:
            if a0 & 0x40:
                # repeated literal block
                litcnt = (a0 & 0x3f) + 2
                repcnt = src[t1] + 1; t1 += 1
                block = src[t1:t1+litcnt]; t1 += litcnt
                for _ in range(repcnt):
                    for bb in block:
                        if len(out) >= size: break
                        out.append(bb)
            else:
                # literal run
                t2 = (a0 & 0x1f) + 1
                if a0 & 0x20:
                    b = src[t1]; t1 += 1
                    t2 += (b << 5)
                for _ in range(t2):
                    if len(out) >= size: break
                    out.append(src[t1]); t1 += 1
    return out

# decode glyph 0
for g in [0, 1, 2, 100, 500]:
    off = OFFS[g]
    src = SD[DESC+off:]
    # first byte is a flag (MESmeltFont skips 1 byte: addiu $a0,$a0,1)
    flag = src[0]
    dec = melt8Ex(src[1:], 0x120)
    print('\nglyph[%d] off=%#x flag=%#x decoded %d bytes' % (g, off, flag, len(dec)))
    print('  first 32:', dec[:32].hex())
    print('  nonzero count:', sum(1 for b in dec if b))
