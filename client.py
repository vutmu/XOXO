import asyncio
import socketio
from aioconsole import ainput

sio = socketio.AsyncClient()


# TODO set connection timeout!


@sio.event
def connect():
    print('connection established')


@sio.event
def test(data):
    print('message received with ', data)
    # await sio.emit('my response', {'response': 'my response'})


@sio.event
async def disconnect():
    print('disconnected from server')


@sio.event
def connect_error(data):
    print("The connection failed!")
    print('сообщение из еррора', data)


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
    connected = False
    counter = 1
    while not connected:
        try:
            print(f'попытка соединения номер{counter}')
            #await sio.connect('https://wasmoh-xoxo.herokuapp.com/')
            await sio.connect('http://localhost:8080/')
            connected = True
        except:
            await sio.sleep(5)
        counter += 1

    await sio.wait()


if __name__ == '__main__':
    asyncio.run(main())
