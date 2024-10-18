from statistics import mean
import sys


def load_log_file(log_file_path):
    with open(log_file_path, 'r') as f:
        f.readline()  # skip header
        h = 6  # number of header fields
        for l in f:
            l = l.split()
            conn = l[:h]
            data = dict(x.split(':') for x in l[h:] if ':' in x)
            flags = [x for x in l[h:] if ':' not in x]
            yield conn, data, flags


split = 4000

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print(arg)

        stats = [(int(d['bytes_sent']), float(d['rtt'].split('/')[0]))
                 for _, d, _ in load_log_file(arg)
                 if 'bytes_sent' in d and 'rtt' in d]
        small_n = sum(s < split for s, _ in stats)
        large_n = sum(s >= split for s, _ in stats)
        small_rtt = mean(rtt for s, rtt in stats if s < split)
        large_rtt = mean(rtt for s, rtt in stats if s >= split)

        print(f" Small streams: {small_n:4}, avg RTT: {small_rtt:.5f}")
        print(f" Large streams: {large_n:4}, avg RTT: {large_rtt:.5f}")
