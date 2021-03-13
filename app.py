from aiohttp import web
import socketio
# from aioconsole import ainput
#import asyncio
from xoxo import Game
import numpy as np

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
#games_pool = []



async def index(request):
    """Serve the client-side application."""
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
async def chat_message(sid, data):
    if data == 'create game':
        await game_driver(sid)
    else:
        print("message ", data)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


#
# @sio.event
# async def game_driver(sid, command):
#     if command == 'create game':
#         game = Game(4, sid, 'a7')
#         games_pool.append(game)
#         await sio.emit('xoxo', 'ваш ход типа 1,1', room=sid)
#     elif 'move' in command:
#         print('move', command)
#         game = games_pool.pop()
#         move = tuple(map(int, command['move'].split(',')))
#         game.move(sid, move)
#         print(game.field)
#         games_pool.append(game)
#     else:
#         print('else', command)
def callback(response):
    print('функция колбек работает!')
    print(response)


@sio.event
async def game_driver(sid):
    game = Game(4, sid, 'a7')
    while game.state == 0:
        field=game.field.tolist()
        response = await sio.call('xoxo', data={'message': 'Ваш ход','field':field}, sid=sid)
        move = tuple(map(int, response.split(',')))
        game.move(sid, move)
        print(game.field)
        print(game.state)


app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    # sio.start_background_task(chat_message)
    web.run_app(app)
