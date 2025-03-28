import glob
import gzip
import re
from itertools import chain, count

import orjson
import pandas

testname_match = re.compile(r'.*/([^/]+)/iperf-log-(\d+)-([a-z]+)\..+')
testname_match_antler = re.compile(r'.*/([^/]+)/closedloop_([a-z\-]+)_streams.json')


def metadata(filename):
    if match := testname_match.match(filename):
        setup, date, algorithm = match.groups()
        return {'setup': setup, 'date': date, 'algorithm': algorithm}
    

def metadata_antler(filename):
    if match := testname_match_antler.match(filename):
        date, algorithm = match.groups()
        return {'setup': 'antler', 'date': date, 'algorithm': algorithm}



def load_log_file(filename: str):
    with gzip.open(filename, 'rb') if filename.endswith('.gz') else open(filename, 'rb') as f:
        return orjson.loads(f.read())



def iter_log_files(paths):
    if isinstance(paths, str):
        return glob.iglob(paths)
    else:
        return chain.from_iterable(glob.iglob(path) for path in paths)


def create_log_df(filename):
    testfile = load_log_file(filename)
    df = pandas.DataFrame(testfile['data'])
    df[['setup', 'date', 'algorithm']] = pandas.DataFrame(metadata(filename), index=df.index, dtype='category')
    df['seed'] = testfile['metadata'].get('seed')
    df['time'] = 8 * df['size'] / df['throughput']
    return df


def create_antler_df(filename):
    resultdata = load_log_file(filename)
    df = pandas.DataFrame(
        [[f['Flow'], f['Length'], f['FCT'], f['Sent'][0]['T']] for f in resultdata.values()],
        columns=['flow', 'size', 'time', 'start_at'],
    )
    df['time'] = df['time'] / 1_000_000_000
    df['start_at'] = (df['start_at'] - df['start_at'].min()) / 1_000_000_000
    df[['setup', 'date', 'algorithm']] = pandas.DataFrame(metadata_antler(filename), index=df.index, dtype='category')
    return df


def load_log_df(file_paths):
    logs = pandas.concat((create_log_df(log_file) for log_file in iter_log_files(file_paths)), ignore_index=True, copy=False, sort=True)
    logs[['setup', 'date', 'algorithm', 'seed']] = logs[['setup', 'date', 'algorithm', 'seed']].astype('category')
    return logs


def load_antler_df(file_paths):
    logs = pandas.concat((create_antler_df(log_file) for log_file in iter_log_files(file_paths) if 'latest' not in log_file),
                          ignore_index=True, copy=False, sort=True)
    logs[['setup', 'date', 'algorithm']] = logs[['setup', 'date', 'algorithm']].astype('category')
    return logs


def prettyprint_bytes(n: int | float) -> str:
    byte_units = ['B  ', 'KiB', 'MiB', 'GiB', 'TiB']
    for i in count():
        if n < 2 ** (i * 10):
            return f'{n / 2 ** (i * 10 - 10):.3g} {byte_units[i - 1]}'
