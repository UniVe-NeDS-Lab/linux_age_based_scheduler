#!/usr/bin/python3

from queue import SimpleQueue
from random import Random
import subprocess as sp
from threading import Event, Thread
from time import sleep


server_address = 'server'
server_port = '5001'
duration = 480

q = SimpleQueue()
stop = Event()

# sleep_secs = 0.2
# large_flow_prob = 0.001

def loop(flowsize, sleepsecs):
    r = Random()
    while not stop.is_set():
        sleep(r.expovariate(1/sleepsecs))
        res = iperf(flowsize)
        q.put(res)

# def loop():
#     r = Random()
#     while not stop.is_set():
#         sleep(r.expovariate(1/sleep_secs))

#         if r.random() < large_flow_prob:
#             res = iperf('100M')
#         else:   
#             res = iperf('30K')

#         q.put(res)



def iperf(flowsize):
    r = sp.run(['iperf', '-c', server_address, '-p', server_port, '-f', 'b', '-n', flowsize, '--nodelay'], 
               check=True, capture_output=True)
    return r.stdout.splitlines()[-1].decode()



if __name__ == '__main__':
    q = SimpleQueue()

    threads = ([Thread(target=loop, args=('100M', 1)) for _ in range(5)] + 
               [Thread(target=loop, args=('30K', 0.2)) for _ in range(60)])
    # threads = [Thread(target=loop) for _ in range(20)]
    
    for t in threads:
        t.start()
        sleep(1)

    sleep(duration)
    stop.set()

    for t in threads:
        t.join()

    while not q.empty():
        r = q.get_nowait()
        print(r)
    # with open(os.argv[1], 'w') as f:


    
    