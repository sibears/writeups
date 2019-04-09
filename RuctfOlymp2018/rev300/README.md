# Carolus Magnus (rev300)

In this task we are given simple nolibc binary written on pure asm.
First of all, once you opened the binary in your favorite disassembler you can spot that the binary have a lot of encrypted functions, and it's decrypt them on runtime due flag checking. Well im lazy to write a lot of code so i decided just to run the binary under gdb wait until the binary is decrypt itself and then dump the encrypted memory:
```
b *0x8048136
r
dump memory dump.data 0x808f174 0x80d5173
```
Then patched the binary via IDAPython. Decrypted functions have same pattern:
```nasm
xor eax, eax
lea edx, [edi+FLAG_BYTE_OFFSET]
mov al, byte [edx]
xor ebx, ebx
lea edx, [edi+ACCS_DWORD_OFFSET]
mov ebx, dword [edx]
sub ebx, eax
mov dword [edx], ebx
mov eax, CONST1
mov ebx, CONST2
ret
```
Checking logic is simple:
- Make few substructions of flag bytes from accumulators values (like this ACCS[i] - flag[i0] * x0 - flag[i1] * x1 - flag[i2] * x2 etc. )
- Check if after all of substructions all the accs values is equal to zero

Well it's pretty simple linear equation system and can be easily solved by matrix method via sagemath or numpy. But i decided to solve it via z3.

Here is my z3 [solver](./solver.py).

Here is my [helper script](./helper.py) for patching bytes of decrypted functions and extract offsets from assembly.
