import os
import subprocess
import tempfile

import numpy as np

_CONTFIT_PATH = os.path.abspath('../PhFit/V1/classes/contfit')


def _contfit_run(input_file: str, body: int, tail: int, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            _CONTFIT_PATH,
            '3',  # Fitting a distribution given by samples
            input_file,  # name of file describing the distribution
            '1',  # type of file: 1: empirical cdf
            str(body),  # Number of Phases to Fit the Main Part
            '-0.01',  # Limit of Fitting the Main Part
            '1',  # Distance Measure: "1": Entropy
            str(tail),  # Number of Phases to Fit the Tail Part
            '-0.1',  # Lower Limit of Tail fitting
            '-0.001',  # Upper Limit of Tail Fitting
            '0.4',  # Distance of Adjacent Points
            '0',  # Special Tail: "0" No special tail
            '0',  # Parameter of the tail
            '0',  # Start of the tail (positive->itself, negative->quantile)
            '1',  # Number of round
            '200',  # Number of iterations in a round
            '10',  # Number of intervals for integrataion
        ],
        check=True,
        capture_output=True,
        text=True,
        **kwargs,
    )


def _parse_contfit_matrix_output(data: str):
    a_line, data = data.split('\n', 1)
    b_lines, _ = data.split('f=', 1)

    a = a_line.strip().removeprefix('a=[').removesuffix('];')
    a = [float(x) for x in a.split()]

    b = b_lines.strip().removeprefix('B=[').removesuffix(';\n];')
    b = [list(map(float, x.split())) for x in b.split(';') if x]

    return np.array(a), np.array(b)


def contfit(x, cdf, body: int, tail: int):
    """
    Fit a phase-type distribution to the given CDF.

    Parameters:
    x: Array of sample points
    cdf: Array of corresponding CDF values
    n: Number of phases for the main part
    m: Number of phases for the tail part

    Returns:
    a: Array of initial probabilities for the phases
    b: Sub-infinitesimal generator matrix
    """

    cdf_file_content = '\n'.join(f'{xi} {pi}' for xi, pi in zip(x, cdf) if 0 < pi < 1)

    with tempfile.TemporaryDirectory(prefix='phfit.') as tmpdir:
        with open(os.path.join(tmpdir, 'cdf.txt'), 'w') as file:
            file.write(cdf_file_content)

        _contfit_run('cdf.txt', body=body, tail=tail, cwd=tmpdir)

        with open(os.path.join(tmpdir, 'TEMPORARYPhFitFILE.matrix')) as file:
            matrix = file.read()

    a, b = _parse_contfit_matrix_output(matrix)
    return a, b
