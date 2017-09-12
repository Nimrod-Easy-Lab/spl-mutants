def print_progress(c, t):
    a_r = float(c) / t
    a_p = a_r * 100

    print(' ', end='\r')
    print('%c[2K' % 27, end='\r')
    print('%i/%i (%.2f%%)' % (c, t, a_p), end='', flush=True)


def pprint_progress(c, t, c_2, t_2):
    a_r = float(c) / t
    a_p = a_r * 100

    a_r_2 = float(c_2) / t_2
    a_p_2 = a_r_2 * 100

    print(' ', end='\r')
    print('%c[2K' % 27, end='\r')
    print('%i/%i (%.2f%%) - %i/%i (%.2f%%)' % (c, t, a_p, c_2, t_2, a_p_2),
          end='', flush=True)
