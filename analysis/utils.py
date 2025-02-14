import glob
import gzip
import re
from itertools import chain, count

import orjson
import pandas

testname_match = re.compile(r'.*/([^/]+)/iperf-log-(\d+)-([a-z]+)\..+')


def metadata(filename):
    if match := testname_match.match(filename):
        setup, date, algorithm = match.groups()
        return {'setup': setup, 'date': date, 'algorithm': algorithm}


def load_log_file(filename):
    return orjson.loads(gzip.open(filename).read())['data']


def iter_log_files(paths):
    if isinstance(paths, str):
        return glob.iglob(paths)
    else:
        return chain.from_iterable(glob.iglob(path) for path in paths)


def create_log_df(filename):
    df = pandas.DataFrame(load_log_file(filename))
    df[['setup', 'date', 'algorithm']] = pandas.DataFrame(metadata(filename), index=df.index, dtype='category')
    df['time'] = 8 * df['size'] / df['throughput']
    return df


def load_log_df(file_paths):
    logs = pandas.concat((create_log_df(log_file) for log_file in iter_log_files(file_paths)), ignore_index=True, copy=False, sort=True)
    logs[['setup', 'date', 'algorithm']] = logs[['setup', 'date', 'algorithm']].astype('category')
    return logs


def prettyprint_bytes(n: int | float) -> str:
    byte_units = ['B  ', 'KiB', 'MiB', 'GiB', 'TiB']
    for i in count():
        if n < 2 ** (i * 10):
            return f'{int(n / 2 ** (i * 10 - 10))} {byte_units[i - 1]}'
