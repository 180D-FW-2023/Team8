import asyncio
from ably import AblyRealtime
import time
from config import config
import re

def listener(message):
    print(message.data)
    data = parse_message(message.data)
    config.imu.put(data)
    print(data)

def parse_message(data):
    values = re.findall(r'[-+]?\d*\.\d+|\d+', data)
    x, y, z, h = map(float, values)
    return (x, y, z)

async def imu_sub():
    
    ably = AblyRealtime('zsW-PQ.nSlItw:zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0')
    await ably.connection.once_async('connected')
    print('Connected to Ably')

    channel = ably.channels.get('controller:1')

    await channel.subscribe(listener)

    await asyncio.sleep(5000)

def run_imu_sub():
    asyncio.run(imu_sub())