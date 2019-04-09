def _unxor_mem(addr1, addr2, size):
    for i in xrange(size):
        patch_byte(addr1 + i, Byte(addr1+i) ^ Byte(addr2+i))

    print 'Done: %#x %#x %d' % (addr1, addr2, size)

def unxor_blobs(blob1, blob2):
    _unxor_mem(blob1, blob2, 35)

def get_leas_from_blob(addr):
    instr = idautils.DecodeInstruction(addr+2)
    mnem = instr.get_canon_mnem()
    assert mnem == 'lea'
    op1 = instr.Op2
    assert op1.addr <= 76
    instr = idautils.DecodeInstruction(addr+12)
    mnem = instr.get_canon_mnem()
    assert mnem == 'lea'
    op2 = instr.Op2
    assert op2.addr <= 152
    assert (op2.addr % 4) == 0
    
    return op1.addr, (op2.addr >> 2)


def get_it_babe():
    start = 0x808F174
    with open('vals.txt', 'w') as f:
        for i in xrange(0x2000):
            v1, v2  = get_leas_from_blob(start + i*35)
            f.write('%u %u\n' % (v1, v2))
            


def patch_it_my_man():
    with open('dump', 'rb') as f:
        for i in xrange(286720):
            patch_byte(0x808F174 + i, ord(f.read(1)))
    print 'Done'
