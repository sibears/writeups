# CTFZone 2018 -- PlusMinus
> **Category**: PPC
> **Description**:
> To solve this task, you need to put arithmetic operators into expression in
the right order.
> Allowed operators: + - / * (). Final expression must involve all the supplied
numbers and the number order must be the same as in original expression. The
last nuber in the line should be an answer.
> nc ppc-01.v7frkwrfyhsjtbpfcppnu.ctfz.one 2445
> Example:
> 2 3 5 4
> (2-3)+5

# Writeup

## About performance
The describing algorithm is polynomial asymptotic, so it's **very slow** and
because of timelimit exploit gets flag with some probability. The script should
be run on thread pool until flag is gotten.

## Design
### Recursion
Recursion is good enough to express algorithm that generates all valid expressions.
The arguments of recursive function: possible movements, count of unclosed
parenthesis, stack of unused numbers, current solution, needed value of expression.

### Base case
When the numbers stack is empty, we just eval the current solution snd return
it if it's nearly equal to needed value of expression, otherwise return None.

### Movements
Valid movements: ['+', '-', '\*', '/', '(', "POP"]. They describes what can we
do at this point of solving. There's no ')' because it isn't regular case, we
decide to put it basing on count of unclosed parenthesis. "POP" indicates we
can pop num from stack and put it at the end of solution.

### Priority order
I kept this putting order: ')', "POP", '+', '-', '\*', '/', '('.

The ( is the least priority because we want to minimize length of finding solution.
The rest of priority order was chosen empirically.

### Micro optimizations
We shouldn't put ')' when the last put operator is '(', because expressions like
a + (b) don't make much sense.

Also I denied generating expressions with nested parentheses. I hoped the
generating expressions wouldn't be much difficult. I was quite lucky, so I
got the flag after 2 hours running script in thread pool.

## Numbers format
The server sometimes sends numbers in specific format (e.g. '.0') and
expects you send number back in the same format (not '0' or '0.'), so
you shouldn't lose original numbers.

## Exploit
[Here](./exploit.py) you can take a look at my exploit.

# Summary
I believe there's more optimal solution for this task. Algorithm that should be
run on thread pool doesn't seems like the best one.
