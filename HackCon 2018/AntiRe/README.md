## AntiRe

There were given a binary file and the address for sending flag. The binary file welcomes us with a line:
`I am a simple program give me the key which is also the flag for this question. \n`,
and asks:
`Enter key:`.

When you upload the binary to disassembler you can notice from the `main` function several key points:

1. The key is a string with the length of 16 bytes

```
0x40318E     lea     rdx, [rsp+188h+key]
0x403196     lea     rcx, a16s       ; "%16s"
0x40319D     call    scanf
```

2. The checking algorithm is like some virtual machine, and the verification code is into variable `bytecode`. Originally it's not initialized and we can notice by xref that it is initialized in the  `_GLOBAL__sub_I__ZN7Machine8do_stuffEv` function via bytes of `404010 _binary_keycheck_start` array. So, this way we can get a bytecode of verification function:

```
[16, 6, 65, 0, 0, 0, 16, 7, 80, 0, 0, 0, 16, 10, 8, 0, 0, 0, 5, 7, 10, 16, 8, 86, 0, 0, 0, 16, 10, 16, 0, 0, 0, 5, 8, 10, 16, 9, 69, 0, 0, 0, 16, 10, 24, 0, 0, 0, 5, 9, 10, 2, 6, 7, 2, 6, 8, 2, 6, 9, 17, 7, 3, 0, 7, 6, 17, 6, 2, 0, 6, 3, 16, 8, 14, 115, 2, 1, 0, 6, 8, 16, 5, 4, 170, 16, 3, 3, 5, 1, 0, 5, 2, 17, 8, 0, 16, 9, 1, 211, 240, 4, 4, 8, 9, 0, 8, 1, 2, 5, 6, 2, 5, 7, 2, 5, 8, 17, 0, 5, 255]
```

3. The virtual machine uses a 16 of 4-bytes registers where the first four is initialized by the key:

```
0x403219     movdqa  xmm1, xmmword ptr [rsp+188h+key]
0x403222     movaps  xmmword ptr [rsp+188h+regs], xmm1
```

4. Virtual machine opcodes are common arithmetic operations.

5. As a result, the first register must equal zero:

```
0x4032F8     cmp     dword ptr [rsp+188h+regs], 0
0x4032FD     jz      short loc_40334D
0x4032FF     lea     rcx, aNope      ; "Nope."
0x403306     call    puts

....

0x40334D loc_40334D:       
0x40334D     lea     rcx, aYup       ; "Yup."
0x403354     call    puts
0x403359     lea     rcx, Command    ; "cat flag"
0x403360     call    system
```
Recently I have read an article with a similar case. I liked the solution where was used z3 and I've decided to write something like this for the task.

[The script](./solver.py)  
[The article](http://0xeb.net/2018/03/using-z3-with-ida-to-simplify-arithmetic-operations-in-functions/)
