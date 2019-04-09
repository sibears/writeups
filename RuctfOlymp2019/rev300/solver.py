from z3 import *


status_vals = [14073L, 15455L, 16345L, 17467L, 16123L, 15388L, 16235L, 14596L, 16142L, 17348L, 14593L, 14120L, 15400L, 14711L, 15540L, 16455L, 16206L, 17503L, 16771L, 17479L, 15636L, 19401L, 15085L, 14655L, 17215L, 15874L, 16301L, 16270L, 15976L, 17403L, 14774L, 16145L, 14349L, 16797L, 16696L, 16163L, 15523L, 16615L]

def main():
    flag_chars = [Int('f_%u' % i) for i in xrange(38)]
    accs = list()
    for i in xrange(len(status_vals)):
        accs.append(IntVal(status_vals[i]))
    
    s = Solver()
    s.add(flag_chars[0] == ord('R'))
    s.add(flag_chars[1] == ord('u'))
    s.add(flag_chars[2] == ord('C'))
    s.add(flag_chars[3] == ord('T'))
    s.add(flag_chars[4] == ord('F'))
    s.add(flag_chars[5] == ord('_'))

    for i in flag_chars[6:]:
        s.add(i >= ord('0'), i <= ord('f'))

    with open('vals.txt', 'r') as f:
        for line in f.xreadlines():
            line = line.strip().split(' ')
            v1, v2 = int(line[0]), int(line[1])
            accs[v2] = accs[v2] - flag_chars[v1]

    for i in xrange(len(accs)):
        s.add(simplify(accs[i]) == 0)

    
    if s.check() == sat:
        m = s.model()
        flag = ''.join(map(chr, [m[i].as_long() for i in flag_chars]))
        print flag

if __name__ == '__main__':
    main()
