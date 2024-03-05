import asyncio
from ably import AblyRealtime
import time
from config import config

def listener(message):
    # Listener takes message data and stores it in shared queue
    data = parse_message(message.data)
    config.imu.put(data)

def parse_message(data):
    # Parser convets to x y z to float format
    split = str(data).split(': ', )
    split = (float(split[1][0:-6]), float(split[2][0:-6]), float(split[3][0:-9]))
    return split

async def imu_sub():
    # Ably script to set up subscriber
    ably = AblyRealtime('zsW-PQ.nSlItw:zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0')
    await ably.connection.once_async('connected')

    channel = ably.channels.get('controller:1')

    await channel.subscribe(listener)

    await asyncio.sleep(5000)

def run_imu_sub():
    asyncio.run(imu_sub())