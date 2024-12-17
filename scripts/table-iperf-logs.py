#!/usr/bin/python3

from collections import defaultdict
from itertools import count, repeat
import re
from statistics import mean, median, stdev
import sys
import json
import gzip


def load_log_file(log_file_path):
    return json.load(gzip.open(log_file_path, 'rt'))['data']


testname_match = re.compile(r'.*-(\d+)-([a-z]+)\..+')
cw = 14

byte_units = ['B  ', 'KiB', 'MiB', 'GiB', 'TiB']


def prettyprint_bytes(n: int | float) -> str:
    for i in count():
        if n < 2**(i*10):
            return f'{int(n/2**(i*10-10))} {byte_units[i-1]}'


def make_row(iter):
    def tostr(x):
        match x:
            case float(): return f'{x:{cw}.4f}'
            case int(): return f'{x:{cw}d}'
            case str(): return x.rjust(cw)
            case None: return ' ' * cw
            case tuple(): return ' '.join(map(tostr, x))

    return ' '.join(map(tostr, iter)) + '\n'


if __name__ == '__main__':
    tests = defaultdict(dict)
    other = list()

    for arg in sys.argv[1:]:
        r = defaultdict(list)
        for l in load_log_file(arg):
            size, throughput = l['size'], l['throughput']
            time = 8*size/throughput
            r[size].append(time)

        if match := testname_match.match(arg):
            date, kind = match.groups()
            tests[int(date)][kind] = r
        else:
            other.append(r)

    # allkinds = {k for kinds in tests.values() for k in kinds.keys()}
    allkinds = ['fqcodel', 'codel', 'age', 'pfifo', 'pfifofast']

    table = make_row(['date', 'flowsize', *zip(repeat(None), allkinds)])
    table += make_row([None, None] + ['nflows', 'mean_time_s'] * len(allkinds))
    for date, test in tests.items():
        allsizes = {size for result in test.values() for size in result.keys()}
        table += '\n'
        for size in sorted(allsizes):
            table += make_row(
                [date, prettyprint_bytes(size)] +
                [(len(test[k][size]), mean(test[k][size]) if len(test[k][size]) > 0 else None)
                    if k in test
                    else (None, None)
                    for k in allkinds])

    print(table)
