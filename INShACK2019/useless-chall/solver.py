import angr
import claripy


if __name__ == '__main__':
    proj = angr.Project('./hash')
    flag_chars = [claripy.BVS('flag_%d' % i, 8) for i in range(41)]
    flag = claripy.Concat(*flag_chars + [claripy.BVV(b'\x00')])

    state = proj.factory.entry_state(args=['./hash', flag], add_options=angr.options.unicorn, remove_options={angr.options.LAZY_SOLVES})
    state.solver.add(flag_chars[0] == ord('I'))
    state.solver.add(flag_chars[1] == ord('N'))
    state.solver.add(flag_chars[2] == ord('S'))
    state.solver.add(flag_chars[3] == ord('A'))
    state.solver.add(flag_chars[4] == ord('{'))
    state.solver.add(flag_chars[-1] == ord('}'))

    for i in flag_chars[5:-1]:
        state.solver.add(i < 127, i > 32)
        state.solver.add(i != ord('/'), i != ord("'"), i != ord(';'), i != ord(':'), i != ord('`'), i != ord('{'), i != ord('}'), i != ord('"'), i != ord('$'))
        state.solver.add(i != ord('('), i != ord(')'), i != ord('['), i != ord(']'), i != ord('|'), i != ord('^'), i != ord('~'), i != ord('>'), i != ord('<'))
        state.solver.add(i != ord('.'), i != ord(','), i != ord('!'), i != ord('?'), i != ord('*'), i != ord('\\'), i != ord('%'), i != ord('='), i != ord('@'))
        state.solver.add(i != ord('+'), i != ord('-'))

    sim = proj.factory.simulation_manager(state)
    to_find = 0x13f1 + proj.loader.main_object.min_addr
    #to_find = 0x13FF + proj.loader.main_object.min_addr
    to_avoid = [i + proj.loader.main_object.min_addr for i in [0x140D, 0x1420]]
    sim.explore(find=to_find, avoid=to_avoid)

    try:
        res = str()
        print(sim.found[0].solver.eval(flag))
        for i in flag_chars:
            res+= chr(sim.found[0].solver.eval(i))
        print(res)
        print(res)
        print(res)
    except:
        import IPython; IPython.embed()

