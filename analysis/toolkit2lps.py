from math import ceil, log, sqrt

import numpy as np
from scipy.integrate import quad

# ruff: noqa: E741


def convert_phfit(a, B, n, m):
    """
    Converts phase-type distribution parameters to generalized hyper-exponential distribution.

    Parameters:
    a: Initial probabilities
    B: Sub-infinitesimal generator matrix
    n: Number of phases for the body
    m: Number of phases for the tail

    Returns:
    p: Probabilities
    u: Rates
    """
    assert m + n == B.shape[1], 'Dimensions must agree'

    ashort = a[:n][::-1]  # Reverse the first n elements of a
    qshort = np.zeros(n)

    for i in range(1, n):
        qshort[i] = B[i, i - 1]
    qshort[0] = -B[0, 0]

    qshort = qshort[::-1]  # Reverse qshort

    # Convert to generalized hyper-exponential distribution
    p, u = convert_to_hyper(ashort, qshort)

    # Append tail probabilities and rates
    p = np.concatenate((p, a[n : n + m]))
    u = np.concatenate((u, -B.diagonal()[n : n + m]))

    return p, u


def convert_to_hyper(a, q):
    """
    Converts parameters to a generalized hyper-exponential distribution.

    Parameters:
    a: Array of initial probabilities
    q: Array of rates

    Returns:
    p: Probabilities
    u: Rates
    """
    n = len(a)
    u = q.copy()
    p = np.zeros(n)
    A = np.zeros((n, n))

    for j in range(n):
        for i in range(j + 1):
            A[j, i] = 1
            for t in range(i):
                A[j, i] *= q[t] - q[j]
            for t in range(i, n):
                A[j, i] *= q[t]
            for t in range(n):
                if t != j:
                    A[j, i] /= q[t] - q[j]

    p = np.sum(a * A, axis=1) / u

    return p, u


def optimal_threshold(a, b, body, tail, thmin, thmax, rho, tol=0.01):
    """
    This function computes the optimal threshold of the 2LPS and the
    corresponding expected response time.

    Parameters:
    A, B: Description of the phase type distribution
    body: Number of phases for the body
    tail: Number of phases for the tail
    thmin, thmax: Range of search for the optimal threshold
    rho: Load factor of the queue, 0 < rho < 1
    tol: Tolerance

    Returns:
    th: Optimal threshold
    resp: Corresponding expected response time
    """
    # Create the generalized hyper-exponential distribution
    p, u = convert_phfit(a, b, body, tail)

    # Compute the mean of the distribution (note: mu is not a rate)
    mu = np.sum(p / u)

    # Compute the arrival rate
    l = rho * (1 / mu)

    # Compute the optimal threshold using golden section search
    a = thmin
    b = thmax
    h = b - a

    if h <= tol:
        th = (a + b) / 2
        resp = average_r(u, p, l, th)
    else:
        invphi = (sqrt(5) - 1) / 2
        invphi2 = (3 - sqrt(5)) / 2
        n = ceil(log(tol / h) / log(invphi))

        c = a + invphi2 * h
        d = a + invphi * h
        yc = average_r(u, p, l, c)
        yd = average_r(u, p, l, d)

        for _ in range(n):
            if yc < yd:
                b = d
                d = c
                yd = yc
                h = invphi * h
                c = a + invphi2 * h
                yc = average_r(u, p, l, c)
            else:
                a = c
                c = d
                yc = yd
                h = invphi * h
                d = a + invphi * h
                yd = average_r(u, p, l, d)

        th = (a + d) / 2 if yc < yd else (c + b) / 2

        resp = average_r(u, p, l, th)

    return th, resp


def average_r(u, p, l, a):
    """
    Computes the average response time.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    l: Arrival rate
    a: Threshold

    Returns:
    resp: Average response time
    """
    t1 = average_response_smaller(u, p, a, l)
    a1 = alpha1(u, p, a, l)
    a2 = alpha2(u, p, a, l)

    mean = a * (1 - cumulative_hyper(u, p, a))

    for i in range(len(u)):
        mean += (1 - np.exp(-a * u[i]) * (1 + a * u[i])) * p[i] / u[i]

    rho1 = l * mean

    resp = t1 * cumulative_hyper(u, p, a) + a1 * (1 - cumulative_hyper(u, p, a)) + (1 / (1 - rho1)) * a2 * (1 - cumulative_hyper(u, p, a))

    return resp


def alpha1(u, p, a, l):
    """
    Computes the alpha1 value for the given parameters.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    a: Threshold
    l: Arrival rate

    Returns:
    a1: Computed alpha1 value
    """
    mean, variance = compute_mu1(u, p, a)

    rho1 = mean * l

    w1 = (rho1 + (l / mean) * variance) / (2 * (1 / mean - l))

    a1 = 1 / (1 - rho1) * (w1 + a)

    return a1


def compute_mu1(u, p, a):
    """
    Computes the mean and variance for the given parameters.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    a: Threshold

    Returns:
    mean: Computed mean
    variance: Computed variance
    """
    mean = 0
    variance = a**2 * (1 - cumulative_hyper(u, p, a))

    for i in range(len(u)):
        mean += (1 - np.exp(-a * u[i])) * p[i] / u[i]
        variance += (2 + np.exp(-a * u[i]) * (-2 - a * u[i] * (2 + a * u[i]))) * p[i] / (u[i] ** 2)

    variance -= mean**2

    return mean, variance


def alpha2(u, p, a, l):
    """
    Computes the alpha2 value for the given parameters.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    a: Threshold
    l: Arrival rate

    Returns:
    a2: Computed alpha2 value
    """
    asigned, b = compute_asigned(l, a, u, p)

    newp = rescale_hyper_exp(u, p, a)

    lu = bansal(u, newp, l, asigned, b)

    a2 = np.sum(lu * newp)

    return a2


def bansal(u, p, lambda_, asigned, b):
    """
    Solves for lu using the Bansal method.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    lambda_: Arrival rate
    asigned: Assigned value
    b: Computed b value

    Returns:
    lu: Solution vector
    """
    dim = len(u)

    A = np.zeros((dim, dim))
    B = np.zeros(dim)

    for r in range(dim):
        for c in range(dim):
            if r == c:
                elem = np.sum(p / (u[r] + u))
                elem = 1 - lambda_ * asigned * elem - lambda_ * asigned * p[r] / (2 * u[r])
                A[r, c] = elem
            else:
                A[r, c] = -lambda_ * asigned * p[c] / (u[r] + u[c])

        B[r] = np.sum(p / (u[r] + u))
        B[r] = B[r] * b + 1 / u[r]

    # Solve the linear system A * lu = B
    lu = np.linalg.solve(A, B)

    return lu


def rescale_hyper_exp(u, p, a):
    """
    Rescales the probabilities for a generalized hyper-exponential distribution.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    a: Threshold

    Returns:
    newp: Rescaled probabilities
    """
    T = np.sum(p * np.exp(-a * u))

    newp = p * np.exp(-a * u) / T

    return newp


def compute_asigned(l, a, u, p):
    """
    Computes the assigned value and b for the given parameters.

    Parameters:
    l: Arrival rate
    a: Threshold
    u: Array of rates
    p: Array of probabilities

    Returns:
    asigned: Computed assigned value
    b: Computed b value
    """
    Ba = 1 - cumulative_hyper(u, p, a)

    T = np.sum(p / u * (1 - np.exp(-a * u) * (a * u + 1)))

    asigned = Ba / (1 - Ba * l * a - l * T)

    T2 = np.sum(p / u**2 * (-(a**2) * np.exp(-a * u) * u**2 + 2 * (1 - np.exp(-a * u) * (a * u + 1))))

    b = l * (2 * Ba * a + l * a**2 * asigned * Ba + l * asigned * T2) / (1 - Ba * l * a - l * T)

    return asigned, b


def cumulative_hyper(u, p, x):
    """
    Computes the cumulative probability for a generalized hyper-exponential distribution.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    x: Threshold

    Returns:
    prob: Cumulative probability
    """
    return 1 - np.sum(p * np.exp(-u * x))


def average_response_smaller(u, p, a, l):
    """
    Computes the average response time for jobs smaller than the threshold.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    a: Threshold
    l: Arrival rate

    Returns:
    T1: Average response time for jobs smaller than the threshold
    """

    # Define the integrand function
    def integrand(t):
        return response_smaller(u, p, a, l, t) * density_hyper(u, p, t)

    # Perform the integration from 0 to a
    integral_result, _ = quad(integrand, 0, a, limit=100)

    # Compute T1
    T1 = integral_result / cumulative_hyper(u, p, a)

    return T1


def response_smaller(u, p, a, l, x):
    """
    Computes the conditioned response time for jobs smaller than the threshold.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    a: Threshold
    l: Arrival rate
    x: Job size

    Returns:
    r: Conditioned response time
    """
    assert np.all(x <= a), 'Conditioned response time for jobs smaller than the threshold: size of the job is larger than the threshold'

    size1 = a * (1 - cumulative_hyper(u, p, a)) + np.sum((1 - np.exp(-a * u) * (1 + a * u)) * p / u)

    rho1 = l * size1

    r = x / (1 - rho1)
    return r


def density_hyper(u, p, x):
    """
    Computes the density of a generalized hyper-exponential distribution.

    Parameters:
    u: Array of rates
    p: Array of probabilities
    x: Value at which to compute the density

    Returns:
    dens: Density value
    """
    return np.sum(p * u * np.exp(-u * x))
