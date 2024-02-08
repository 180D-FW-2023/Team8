import asyncio
from ably import AblyRealtime
import time

def listener(message):
    print('Received a greeting message in realtime: ' + message.data)
    #await ably.close()
    #print('Closed the connection to Ably.')

async def imu_sub():
    
    ably = AblyRealtime('zsW-PQ.nSlItw:zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0')
    await ably.connection.once_async('connected')
    print('Connected to Ably')

    channel = ably.channels.get('getting-started')
    await channel.subscribe(listener)

    while 1:
        await asyncio.sleep(5000)

asyncio.run(imu_sub())
'''

def listener(message):
    print('Received a greeting message in realtime: ' + message.data)

async def imu_sub():
    ably = AblyRealtime('zsW-PQ.nSlItw:zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0')
    await ably.connection.once_async('connected')
    print('Connected to Ably')

    channel = ably.channels.get('quickstart')
    await channel.subscribe(listener)

    # Keep the script running indefinitely (or implement your own logic to stop it)
    while True:
        await asyncio.sleep(3600)  # Sleep for a long time, effectively infinite

asyncio.run(imu_sub())
'''