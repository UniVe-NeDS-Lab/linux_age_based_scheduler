import numpy as np


def paretoICDF(n, lb, ub, a=1.2):
    u = np.linspace(0, 1, n)

    lb, ub = np.power(lb, a), np.power(ub, a)

    x = - (u*ub - u*lb - ub) / (ub*lb)
    x = np.power(x, -1/a)
    x = np.round(x, 0).astype(int)

    return x

def paretoCDF(x, a=1.2, lb=None, ub=None):    
    if lb is None:
        lb = np.min(x)
    if ub is None:
        ub = np.max(x)

    x = np.round(x, 0).astype(int)
    p = (1 - np.power(lb, a)*np.power(x, -a)) / (1 - np.power(lb/ub, a))

    return x, p


def discretize(x, cdf):
    xx = np.convolve(x, [.5,.5], 'valid')
    pp = np.convolve(cdf, [1, -1], 'valid')
    xx = np.round(xx, 0).astype(int)
    return xx, pp