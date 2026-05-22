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


def decompress(input, initSize=16000, blockSize=8192):
    output = FlexBuffer()
    output.alloc(initSize, blockSize)
    return _decompress(bytearray(input), output)
