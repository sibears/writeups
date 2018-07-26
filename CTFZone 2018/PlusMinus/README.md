# CTFZone 2018 -- PlusMinus
> **Category**: PPC<br>
> **Description**:<br>
> To solve this task, you need to put arithmetic operators into expression in
the right order.<br>
> Allowed operators: + - / * (). Final expression must involve all the supplied
numbers and the number order must be the same as in original expression. The
last nuber in the line should be an answer.<br>
> nc ppc-01.v7frkwrfyhsjtbpfcppnu.ctfz.one 2445<br>
> Example:<br>
> 2 3 5 4 <br>
> (2-3)+5

# Writeup

## Performance
The described algorithm is polynomial asymptotic, so it's **very slow** and due to
the fact of the time limit, exploit gets a flag just with some probability. The 
suggested below script should be run via thread pool until the flag is gotten.

## Design
### Recursion
Recursion is good enough to define an algorithm that generates all valid expressions.
The arguments of a recursive function: possible movements, count of unclosed
parenthesis, a stack of unused numbers, current solution, a needed value of the expression.

### Basic version
If the stack of numbers is empty, we eval the current solution and return 
it if it's nearly equal to the needed value of the expression, otherwise return `None`.

### Movements
Valid movements: `['+', '-', '\*', '/', '(', "POP"]`. They describes what can we do at
current point of solving. There's no `)` because it isn't a typical case, so, we decided
to put it basing on count of unclosed parenthesis. `POP` indicates we can pop num from
the stack and put it at the end of the solution.

### The priority
I kept this putting order: `')', "POP", '+', '-', '\*', '/', '('`.`

The `(` has the least priority because we want to minimize the length of finding the 
solution. The rest of the priority order was chosen empirically.

### A little bit of optimizations
We shouldn't put `)` if the last put operator is `(` because expressions like
`a + (b)` don't make much sense.

Also, I didn't generate expressions with nested parentheses. I hoped the generating 
expressions by the server wouldn't be much difficult. I was lucky enough, so I got 
the flag after 2 hours of the running script in a thread pool.

## Numbers format
The server sometimes sends numbers in a specific format (e.g. `.0`) and 
expects you send number back in the same format (not `0` or `0.`), so 
you shouldn't lose original numbers.

## Exploit
[Here](./exploit.py) you can take a look at my exploit.

# Summary
I believe the best possible solution for this task exists. The suggested algorithm
that should be run on thread pool doesn't seem like the optimal.
