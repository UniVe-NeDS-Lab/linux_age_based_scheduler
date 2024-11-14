#!/usr/bin/python3

import asyncio
from random import Random


server_address = 'server'
server_port = '5001'
duration = 480

# sleep_secs = 0.2
# large_flow_prob = 0.001


async def loop(flowsize, sleepsecs, stop):
    r = Random()
    res = []
    while not stop.is_set():
        await asyncio.sleep(r.expovariate(1/sleepsecs))
        res.append(await iperf(flowsize))

    return res


async def iperf(flowsize):
    p = await asyncio.create_subprocess_exec(
        'iperf', '-c', server_address, '-p', server_port, '-f', 'b', '-n', flowsize, '--nodelay',
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, _ = await p.communicate()

    return stdout.splitlines()[-1].decode()


async def main():
    stop_event = asyncio.Event()

    tasks = [asyncio.create_task(loop('100M', 2, stop_event)) for _ in range(5)]
    await asyncio.sleep(2)
    tasks += [asyncio.create_task(loop('30K', 0.2, stop_event)) for _ in range(60)]

    await asyncio.sleep(duration)
    stop_event.set()

    res, _ = await asyncio.wait(tasks)

    print('\n'.join(l for r in res for l in r.result()))


if __name__ == '__main__':
    asyncio.run(main())
