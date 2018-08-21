import z3
from pwn import u32, p32

BYTECODE = [16, 6, 65, 0, 0, 0, 16, 7, 80, 0, 0, 0, 16, 10, 8, 0, 0, 0, 5, 7, 10, 16, 8, 86, 0, 0, 0, 16, 10, 16, 0, 0, 0, 5, 8, 10, 16, 9, 69, 0, 0, 0, 16, 10, 24, 0, 0, 0, 5, 9, 10, 2, 6, 7, 2, 6, 8, 2, 6, 9, 17, 7, 3, 0, 7, 6, 17, 6, 2, 0, 6, 3, 16, 8, 14, 115, 2, 1, 0, 6, 8, 16, 5, 4, 170, 16, 3, 3, 5, 1, 0, 5, 2, 17, 8, 0, 16, 9, 1, 211, 240, 4, 4, 8, 9, 0, 8, 1, 2, 5, 6, 2, 5, 7, 2, 5, 8, 17, 0, 5, 255] 

class Buffer():
    def __init__(self, mem):
        self.offset = 0
        self.mem = mem

    def read_byte(self):
        res = self.mem[self.offset]
        self.offset+= 1
        return res

    def read_dword(self):
        res = self.mem[self.offset:self.offset+4]
        self.offset+= 4
        return u32(''.join(map(chr, res)))
        

def main():
    global BYTECODE

    regs = z3.BitVecs('r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12 r13 r14 r15', 32) 
    regs_b = regs[:]
    code = Buffer(BYTECODE)
    opcode = None
    
    while opcode != 255:
        opcode = code.read_byte()
        
        if opcode == 0:
            lh = code.read_byte()
            rh = code.read_byte()
            regs[lh] = regs[lh] ^ regs[rh]

        elif opcode == 2:
            lh = code.read_byte()
            rh = code.read_byte()
            regs[lh] = regs[lh] | regs[rh]

        elif opcode == 3:
            lh = code.read_byte()
            rh = code.read_byte()
            regs[lh] = regs[lh] + regs[rh]

        elif opcode == 4:
            lh = code.read_byte()
            rh = code.read_byte()
            regs[lh] = regs[lh] - regs[rh]

        elif opcode == 5:
            lh = code.read_byte()
            rh = code.read_byte()
            regs[lh] = regs[lh] << regs[rh]

        elif opcode == 16:
            lh = code.read_byte()
            rh = code.read_dword()
            regs[lh] = rh

        elif opcode == 17:
            lh = code.read_byte()
            rh = code.read_byte()
            regs[lh] = regs[rh]
    
    final_expr = z3.simplify(regs[0])

    s = z3.Solver()
    s.add((final_expr) == 0)
    if s.check() == z3.sat:
        m = s.model()
        key = ''.join(map(p32, [m[regs_b[i]].as_long() for i in xrange(4)]))
        print key
    else:
        print 'parasha kakaja-to'
    return



if __name__ == '__main__':
    main()
