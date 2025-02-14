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
test_duration = 960
actor_count = 80

sleepsecs = 0.25
flow_cumprobs = [
    (.002, '300M'),
    (.03, '3M',),
    (.26, '300K'),
    (1, '30K'),
]

flow_output = namedtuple('flow_output', ['time', 'output'])
flow_data = namedtuple('flow_data', ['time', 'size', 'throughput', 'start_at'])


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


async def main():
    start_event = asyncio.Event()
    stop_event = asyncio.Event()

    tasks = [asyncio.create_task(loop(start_event, stop_event)) for _ in range(actor_count)]

    await asyncio.sleep(spinup_duration)
    start_event.set()

    test_start_time = time()
    await asyncio.sleep(test_duration)
    stop_event.set()

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
