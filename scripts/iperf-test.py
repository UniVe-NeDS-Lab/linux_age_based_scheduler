#!/usr/bin/python3

import asyncio
from random import Random
import sys


server_address = 'server'
server_port = '5001'
duration = 480


async def loop(flowsize, sleepsecs, stop, udp=False):
    r = Random()
    res = []
    while not stop.is_set():
        await asyncio.sleep(r.expovariate(1/sleepsecs))
        out = await iperf(flowsize, udp=udp)
        if out.startswith('[  1] 0.00'):
            res.append(out)
        else:
            print(out, file=sys.stderr)

    return res


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
    return stdout.splitlines()[-1].decode()


async def main():
    stop_event = asyncio.Event()

    # tasks = [asyncio.create_task(loop('1G', 2, stop_event)) for _ in range(5)]
    # await asyncio.sleep(2)
    # tasks += [asyncio.create_task(loop('300K', 1, stop_event, udp=True)) for _ in range(30)]

    tasks = [asyncio.create_task(loop('300M', 10, stop_event)) for _ in range(10)]
    await asyncio.sleep(10)
    tasks += [asyncio.create_task(loop('3M', 1, stop_event)) for _ in range(10)]
    tasks += [asyncio.create_task(loop('300K', 0.1, stop_event)) for _ in range(10)]
    tasks += [asyncio.create_task(loop('30K', 0.05, stop_event)) for _ in range(20)]

    await asyncio.sleep(duration)
    stop_event.set()

    res, _ = await asyncio.wait(tasks)

    print('\n'.join(l for r in res for l in r.result()))


if __name__ == '__main__':
    asyncio.run(main())
