import numpy as np
from scipy.linalg import expm


def boundedParetoICDF(n, *, alpha, lb, ub):
    u = np.linspace(0, 1, n)

    lb, ub = np.power(lb, alpha), np.power(ub, alpha)

    x = -(u * ub - u * lb - ub) / (ub * lb)
    x = np.power(x, -1 / alpha)
    x = np.round(x, 0).astype(int)

    return x


def boundedParetoCDF(x, *, alpha, lb=None, ub=None):
    if lb is None:
        lb = np.min(x)
    if ub is None:
        ub = np.max(x)

    x = np.round(x, 0).astype(int)
    p = (1 - np.power(lb, alpha) * np.power(x, -alpha)) / (1 - np.power(lb / ub, alpha))

    return x, p


def paretoCDF(x, *, alpha, lb=None):
    if lb is None:
        lb = np.min(x)

    x = np.round(x, 0).astype(int)
    p = 1 - np.power(lb / x, alpha)

    return x, p


def phaseTypeCDF(x, a, b):
    return 1 - np.array([a @ expm(x * b) @ np.ones(len(b)) for x in np.asarray(x)])


def discretize(x, cdf):
    xx = (x[:-1] + x[1:]) / 2
    pp = np.diff(cdf)
    xx = np.round(xx, 0).astype(int)
    return xx, pp
