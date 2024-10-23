from collections import defaultdict
from statistics import mean, median
import sys


def load_log_file(log_file_path):
    with open(log_file_path, 'r') as f:
        for l in f:
            try:
                _, _, time, _, size, _, bandwidth, _ = l.split()
            except ValueError:
                continue

            time = float(time.split('-')[1])
            size = float(size)
            bandwidth = float(bandwidth)

            yield time, size, bandwidth


split = 16 * 1024

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print(arg)

        r = defaultdict(list)
        for t, s, bw in load_log_file(arg):
            r[s].append(bw)

        for s, bw in r.items():
            print('', s, len(bw), mean(bw), median(bw))
