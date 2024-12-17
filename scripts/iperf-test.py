#!/usr/bin/python3

import asyncio
from random import Random
import sys
import json
import gzip


server_address = 'server'
server_port = '5001'
duration = 480

flow_cumprobs = [
    (.002, '300M'),
    (.03, '3M',),
    (.26, '300K'),
    (1, '30K'),
]


def random_flowsize(r: Random) -> str:
    n = r.uniform(0,1)
    for p, f in flow_cumprobs:
        if n <= p:
            return f
    

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


async def loop(sleepsecs, stop, udp=False):
    r = Random()
    outputs = []
    while not stop.is_set():
        await asyncio.sleep(r.expovariate(1/sleepsecs))
        output = await iperf(random_flowsize(r), udp=udp)
        outputs.append(output)
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
    stop_event = asyncio.Event()

    tasks = [asyncio.create_task(loop(0.2, stop_event)) for _ in range(80)]

    await asyncio.sleep(duration)
    stop_event.set()

    res, _ = await asyncio.wait(tasks)

    data = []
    errors = 0
    for r in res:
        for o in r.result():
            try:
                t, s, bw = parse_iperf_output(o)
                data.append({'time': t, 'size': s, 'throughput': bw})
            except TypeError:
                errors += 1

    if errors:
        print(f'Errors: {errors}', file=sys.stderr)
    print(json.dumps({'data': data, 'errors': errors}))


if __name__ == '__main__':
    asyncio.run(main())
