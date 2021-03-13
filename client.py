import asyncio
import socketio
from aioconsole import ainput

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('connection established')


@sio.event
def test(data):
    print('message received with ', data)
    # await sio.emit('my response', {'response': 'my response'})


@sio.event
async def disconnect():
    print('disconnected from server')


# @sio.event
# async def xoxo(data):
#     while data != 'game over':
#         print(data)
#         move = await ainput("Ваш ход")
#         await sio.emit('game_driver', {'move': move})
#     print(data)

@sio.event
async def xoxo(data):
    if data['message'] == 'Ваш ход':
        print(data['message'])
        print(data['field'])
        return await ainput('>>>')
    print('тут игра дб закончена')


async def chat_message():
    while True:
        text = await ainput(">>>")
        if text == 'exit':
            break
        elif text == 'create game':
            await sio.emit('chat_message', 'create game')
            break
        else:
            await sio.emit("chat_message", text)


async def main():
    sio.start_background_task(chat_message)
    await sio.connect('http://localhost:8080')
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(main())
