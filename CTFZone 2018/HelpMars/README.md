# CTFZone 2018 -- Help Mars!
> **Category**: PPC, OSINT<br>
> **Description**:<br>
> Hello!<br>
> The Martians need your help. They are in contact with the H5N1 virus.
> We know that there is a universal vaccine (locus HW306977) on our planet.
> Find the substances on their planet that can be used to synthesize the vaccine.
> A large sample database is at your disposal.<br>
> [mars_dna_samples.zip](./mars_dna_samples.zip).<br>
> Your task is to select the right combination of samples (recipe). Result is
> the shortest (lowest count of samples used to synthesize the vaccine). If you
> find more than one shortest recipe - select the one, which has the longest code
> in each sample from start to end.<br>
> Example:<br>
> Code: 123456<br>
> Samples (id,code):<br>
> 1,4<br>
> 2,6<br>
> 3,12<br>
> 4,34<br>
> 5,56<br>
> 6,45<br>
> 7,123<br>
> Available combinations<br>
> 12-34-56<br>
> 123-45-6<br>
> 123-4-56<br>
> Solving: 123 + 45 + 6<br>
> Result: 7,6,2<br>
> Flag is ctfzone{md5(Result)}

# Writeup

## Googling
To get the flag you firstly need to find genom sequence of H5N1 virus. Unfortunately,
there're a lot of variation of this virus, and HW306977 hasn't been indexed by google.

So it took some time to find data archive of biology things, and here we found
a [record about HW306977](https://www.ncbi.nlm.nih.gov/nuccore/HW306977).

## Algorithm
### Method
The task is typical for [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming). 

We have a whole sequence and hashmap sample_seq -> sample_ind, lets write a recursive function
that returns the smallest sequence of samples (only theirs ids) for some suffix of the
sequence: `f(suffix)`.

### Cache
The most important thing in dynamic programming is caching result of `f(..)`. If you do your
algorithm is fast enough, if you don't it's polynomial asymptotic.

### Base case
If the suffix is empty, then the answer is obvious: `[]`.

### Body of recursion
After base case was checked, check that this prefix hasn't computed yet.
If it has, return the cached answer. If it hasn't, do this:

Now we just doing this:

```python
def f(suffix):
    # ... check for the base case
    # ... look for a computed value in cache
    best = None
    for i in xrange(1, min(max_sample_len, len(suffix))+1):
        if suffix[:i] not in sample_to_ind: continue
        current = f(suffix[i:])
        if (best is None and current is not None) or (best is not None and current is not None and len(best) > len(current)):
            current.append(sample_to_its_ind[suffix[:i]])
            best = current
    # ... caching
    return best
```

## Solver
[Here](./solve.py) you can take a look at my solver.
