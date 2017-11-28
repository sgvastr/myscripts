import sys
import argparse
import os


class Gost28147_89:
    __sbox = (
                (0x4, 0xA, 0x9, 0x2, 0xd, 0x8, 0x0, 0xe, 0x6, 0xb, 0x1, 0xc, 0x7, 0xf, 0x5, 0x3),
                (0xe0, 0xb0, 0x40, 0xc0, 0x60, 0xe0, 0xf0, 0xa0, 0x20, 0x30, 0x80, 0x10, 0, 0x70, 0x50, 0x90),
                (0x500, 0x800, 0x100, 0xd00, 0xa00, 0x300, 0x400, 0x200, 0xe00, 0xf00, 0xc00, 0x700, 0x600, 0x0, 0x900, 0xb00),
                (0x7000, 0xd000, 0xa000, 0x1000, 0, 0x8000, 0x9000, 0xf000, 0xe000, 0x4000, 0x6000, 0xc000, 0xb000, 0x2000, 0x5000, 0x3000),
                (0x60000, 0xc0000, 0x70000, 0x10000, 0x50000, 0xf0000, 0xd0000, 0x80000, 0x40000, 0xa0000, 0x90000, 0xe0000, 0x0, 0x30000, 0xb0000, 0x20000),
                (0x400000, 0xb00000, 0xa00000, 0x0, 0x700000, 0x200000, 0x100000, 0xe00000, 0x300000, 0x600000, 0x800000, 0x500000, 0x900000, 0xc00000, 0xf00000, 0xe00000),
                (0xd000000, 0xb000000, 0x4000000, 0x1000000, 0x3000000, 0xf000000, 0x5000000, 0x9000000, 0, 0xa000000, 0xe000000, 0x7000000, 0x6000000, 0x8000000, 0x2000000, 0xc000000),
                (0x10000000, 0xf0000000, 0xd0000000, 0, 0x50000000, 0x70000000, 0xa0000000, 0x40000000, 0x90000000, 0x20000000, 0x30000000, 0xe0000000, 0x60000000, 0xb0000000, 0x80000000, 0xc0000000),
            )

    def __sbox_replace(self, v):
        v0 = v & 0xf
        v >>= 4
        v1 = v & 0xf
        v >>= 4
        v2 = v & 0xf
        v >>= 4
        v3 = v & 0xf
        v >>= 4
        v4 = v & 0xf
        v >>= 4
        v5 = v & 0xf
        v >>= 4
        v6 = v & 0xf
        v >>= 4
        v7 = v & 0xf
        a0 = self.__sbox[0][v0]
        a1 = self.__sbox[1][v1]
        a2 = self.__sbox[2][v2]
        a3 = self.__sbox[3][v3]
        a4 = self.__sbox[4][v4]
        a5 = self.__sbox[5][v5]
        a6 = self.__sbox[6][v6]
        a7 = self.__sbox[7][v7]
        r = a7 | a6 | a5 | a4 | a3 | a2 | a1 | a0
        return r

    def __round_shift(self, v):
        s = (v & 0xffe00000) >> 21
        v = ((v << 11) & 0xffffffff) | s
        return v

    def __f(self, l, key):
        m = (l + key) & 0xffffffff
        m = self.__sbox_replace(m)
        m = self.__round_shift(m)
        return m

    def __cipher(self, l, r, k):
        for i in range(32):
            rnd = i % 8
            r_key = int.from_bytes(k[rnd*4:rnd*4 + 4], byteorder="big")
            r = r ^ self.__f(l, r_key)
            l, r = r, l
        return r, l

    def __decrypt(self, l, r, k):
        for i in range(31, -1, -1):
            rnd = i % 8
            r_key = int.from_bytes(k[rnd*4:rnd*4 + 4], byteorder="big")
            r = r ^ self.__f(l, r_key)
            l, r = r, l
        return r, l

    def do(self, srcfile, dstfile, keyfile, action):
        func = None
        if action == "cipher":
            func = self.__cipher
        elif action == "decrypt":
            func = self.__decrypt
        else:
            print("action error")
            exit(1)

        size = os.path.getsize(srcfile)
        with open(srcfile, "rb") as src, open(dstfile, "wb") as dst, open(keyfile, "rb") as key:
            k = key.read(32)
            srcfile = src.read()
            dstfile = bytearray()
            i = 0
            while True:
                if i % 16000 == 0:
                    print('[{0}] {1}/{2}'.format('#' * int((i*100) / size), i, size), end="\r")
                data = srcfile[i:i+8]
                i += 8
                if data:
                    l = int.from_bytes(data[:4], byteorder="little")
                    r = int.from_bytes(data[4:8], byteorder="little")
                    l, r = func(l, r, k)
                    lb = l.to_bytes(4, byteorder="little")
                    rb = r.to_bytes(4, byteorder="little")
                    dstfile.extend(lb)
                    dstfile.extend(rb)
                else:
                    break
            dst.write(dstfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('srcfile', help='path to source file')
    parser.add_argument('dstfile', help='path to destination file')
    parser.add_argument('keyfile', help='path key file')
    parser.add_argument('-a', help='set action', choices=['cipher', 'decrypt'], default='cipher')

    if len(sys.argv) == 1:
            parser.print_help()
            exit(1)

    args = parser.parse_args()

    gost = Gost28147_89()
    gost.do(args.srcfile, args.dstfile, args.keyfile, args.a)
