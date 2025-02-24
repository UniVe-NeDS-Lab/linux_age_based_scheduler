#!/usr/bin/python3

import asyncio
import json
import sys
from collections import namedtuple
from random import Random
from time import time

server_address = 'server'
server_port = '5001'

spinup_duration = 10
test_duration = 1200
actor_count = 80

sleepsecs = 1
flow_weights = [
    (1000, '300K'),
    (178, '1.7M'),
    (31.6, '9.5M'),
    (5.62, '53M'),
    (1, '300M'),
]

flow_cumprobs = [(sum(w for w, _ in flow_weights[: i + 1]) / sum(w for w, _ in flow_weights), f) for i, (_, f) in enumerate(flow_weights)]

iface_name = 'enp0s31f6'
iface_metrics = ['tx_packets', 'tx_bytes']


flow_output = namedtuple('flow_output', ['time', 'output'])
stats_output = namedtuple('stats_output', ['time', 'values'])


def random_flowsize(r: Random) -> str:
    n = r.uniform(0, 1)
    for p, f in flow_cumprobs:
        if n <= p:
            return f


def random_sleeptime(r: Random) -> float:
    return r.expovariate(1 / sleepsecs)


def parse_iperf_output(output: bytes):
    for line in output.decode().splitlines()[::-1]:
        try:
            _, _, time, _, size, _, bandwidth, _ = line.split()

            time = float(time.split('-')[1])
            size = float(size)
            bandwidth = float(bandwidth)
        except ValueError:
            continue

        if bandwidth > 0:
            return time, int(size), int(bandwidth)


async def loop(start, stop, udp=False):
    r = Random()
    outputs = []
    while not stop.is_set():
        should_record = start.is_set()

        await asyncio.sleep(random_sleeptime(r))
        start_time = time()
        output = await iperf(random_flowsize(r), udp=udp)

        if should_record:
            outputs.append(flow_output(start_time, output))

    return outputs


async def iperf(flowsize, nodelay=True, udp=False):
    args = []
    if nodelay:
        args += ['--nodelay']
    if udp:
        args += ['--udp', '-b', '100M']

    p = await asyncio.create_subprocess_exec(
        'iperf2.2.1', '-c', server_address, '-p', server_port, '-f', 'b', '-n', flowsize, *args,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, _ = await p.communicate()
    return stdout


async def record_iface_stats(stop):
    stats = []
    loop = asyncio.get_running_loop()
    while not stop.is_set():
        await asyncio.sleep(0.1)
        stat_time = time()
        stat_values, _ = await asyncio.wait([loop.run_in_executor(None, get_iface_stat, iface_name, metric_name) for metric_name in iface_metrics])
        stats.append(stats_output(stat_time, [res.result() for res in stat_values]))
    return stats


def get_iface_stat(iface: str, metric: str) -> int:
    with open(f'/sys/class/net/{iface}/statistics/{metric}') as f:
        return int(f.read())


async def main():
    start_event = asyncio.Event()
    stop_event = asyncio.Event()

    tasks = [asyncio.create_task(loop(start_event, stop_event)) for _ in range(actor_count)]
    stats_task = asyncio.create_task(record_iface_stats(stop_event))

    await asyncio.sleep(spinup_duration)
    start_event.set()

    test_start_time = time()
    await asyncio.sleep(test_duration)
    stop_event.set()

    stats = []
    for t, stat_values in await stats_task:
        stats.append({'time': t - test_start_time, 'values': dict(zip(iface_metrics, stat_values))})

    res, _ = await asyncio.wait(tasks)

    data = []
    errors = 0
    for r in res:
        for start_time, output in r.result():
            try:
                t, s, bw = parse_iperf_output(output)
                data.append({'time': t, 'size': s, 'throughput': bw, 'start_at': start_time - test_start_time})
            except TypeError:
                errors += 1

    if errors:
        print(f'Errors: {errors}', file=sys.stderr)

    print(
        json.dumps(
            {
                'data': data,
                'stats': stats,
                'errors': errors,
                'metadata': {
                    'test_start': test_start_time,
                    'test_duration': test_duration,
                    'spinup_duration': spinup_duration,
                    'actor_count': actor_count,
                    'flow_cumprobs': flow_cumprobs,
                    'sleepsecs': sleepsecs,
                },
            }
        )
    )


if __name__ == '__main__':
    asyncio.run(main())
