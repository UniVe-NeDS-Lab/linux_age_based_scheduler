import glob
import gzip
import re
from itertools import chain, count

import orjson
import pandas

testname_match_antler = re.compile(r'.*/([^/]+)/closedloop_([a-z\-]+)_streams.json')


def metadata_antler(filename):
    if match := testname_match_antler.match(filename):
        date, algorithm = match.groups()
        return 'antler', date, algorithm



def load_log_file(filename: str):
    with gzip.open(filename, 'rb') if filename.endswith('.gz') else open(filename, 'rb') as f:
        data = orjson.loads(f.read())
    return data.values() if isinstance(data, dict) else data



def iter_log_files(paths):
    if isinstance(paths, str):
        return glob.iglob(paths)
    else:
        return chain.from_iterable(glob.iglob(path) for path in paths)


def create_antler_df(filename, setup_cat, date_cat, algorithm_cat):
    # def _start_at(flow):
    #     return flow['Sent'][0]['T'] if 'Sent' in flow else flow['StartT']

    resultdata = load_log_file(filename)
    # df = pandas.DataFrame(
    #     [[f['Flow'], f['Length'], f['FCT'], _start_at(f)] for f in resultdata],
    #     columns=['flow', 'size', 'time', 'start_at'],
    # )
    df = pandas.DataFrame(resultdata)
    # df = pandas.read_json(filename, orient='records')
    df = df.rename(columns={'Flow': 'flow', 'Length': 'size', 'FCT': 'time', 'StartT': 'start_at'})
    df = df[['flow', 'size', 'time', 'start_at']]

    df['time'] = df['time'] / 1_000_000_000
    df['start_at'] = (df['start_at'] - df['start_at'].min()) / 1_000_000_000
    df['actor'] = df['flow'].str.split('-').str[0].str.removeprefix('actor').str.removeprefix('a').astype('uint8')
    setup, date, algorithm = metadata_antler(filename)
    df['setup'] = pandas.Categorical([setup] * len(df), categories=setup_cat)
    df['date'] = pandas.Categorical([date] * len(df), categories=date_cat)
    df['algorithm'] = pandas.Categorical([algorithm] * len(df), categories=algorithm_cat)
    return df


def load_antler_df(*file_paths):
    meta = [metadata_antler(log_file) for log_file in iter_log_files(file_paths)]
    setup_cat, date_cat, algorithm_cat = map(set, zip(*meta))
    logs = pandas.concat((create_antler_df(log_file, setup_cat, date_cat, algorithm_cat) 
                          for log_file in iter_log_files(file_paths) if 'latest' not in log_file),
                        ignore_index=True, copy=False, sort=False)
    return logs


def prettyprint_bytes(n: int | float) -> str:
    byte_units = ['B  ', 'KiB', 'MiB', 'GiB', 'TiB']
    for i in count():
        if n < 2 ** (i * 10):
            return f'{n / 2 ** (i * 10 - 10):.3g} {byte_units[i - 1]}'
