import md5
import re

data = ""
seq = ""

with open('mars_dna_samples.txt') as f:
    data = f.read().strip()
with open('seq.txt') as f:
    seq = f.read().strip().upper()
    seq = re.sub(r'[^ACGRT]', '', seq)

mlen = 0
hata = {}
hata_rev = {}

for line in data.split('\r\n'):
    try:
        line = line.split(',')
        if line[1] in hata:
            print("warn: {} is ambiguous".format(line[1]))
            continue
        hata[line[1]] = line[0]
        hata_rev[line[0]] = line[1]
        if mlen < len(line[1]):
            mlen = len(line[1])
    except Exception as e:
        print("Got an error on {}: {}".format(line, e))
        quit()

cache = {}
def solve(seq):
    if len(seq) == 0:
        return []
    if seq in cache:
        cached = cache[seq]
        if cached is not None:
            return list(cached)
        else:
            return None
    best = None
    for i in xrange(1, min(mlen, len(seq))+1):
        if seq[:i] not in hata: continue
        hres = solve(seq[i:])
        if (best is None and hres is not None) or (best is not None and hres is not None and len(best) > len(hres)):
            hres.append(seq[:i])
            best = hres

    if best is not None:
        cache[seq] = list(best)
    else:
        cache[seq] = None
    return best

res = solve(seq)
res.reverse()
prev = ''.join(res)
res = map(lambda s: hata[s], res)
res = ','.join(res)
m = md5.new()
m.update(res)
print('ctfzone{{{}}}'.format(m.hexdigest()))
