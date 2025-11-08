import numpy as np

LOG52 = np.log(5) / np.log(2)  # constant

def length_array(s):
    n, m = s
    return (2 ** n) * (5 ** m)

def next_s_np(s):
    n, m = s
    p_vals = np.arange(-m, np.floor((n + 1) / LOG52) + 1, dtype=int)
    q_vals = np.ceil(p_vals * LOG52).astype(int) - 1

    n_candidates = n - q_vals
    m_candidates = m + p_vals
    lengths = (2 ** n_candidates) * (5 ** m_candidates)

    # find minimal length and corresponding candidate
    min_idx = np.argmin(lengths)
    return (n_candidates[min_idx], m_candidates[min_idx])

def derive_s_array_np(Lmax):
    s_array = [(0, 0)]
    while True:
        s_next = next_s_np(s_array[-1])
        s_array.append(s_next)
        if length_array(s_next) >= Lmax:
            break
    return s_array

for s in derive_s_array_np(27):
    print(length_array(s))
