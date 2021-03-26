from aiohttp import web
import socketio
import aiohttp_jinja2
import jinja2
from xoxo import Game
import os
from dotenv import load_dotenv
from queue import Queue

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader('./templates')
)

members = Queue()


# games_pool = []

async def index(request):
    context = {'name': 'world!'}
    return aiohttp_jinja2.render_template(
        'index.jinja2', request, context
    )


@sio.event
def connect(sid, environ):
    members.put(sid)
    print("connect ", sid)


@sio.event
async def chat_message(sid, data):
    if data == 'create game' and members.qsize() == 2:
        await game_driver(members)
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
@sio.event
async def game_driver(members):
    print("game driver started")
    first_player, second_player = members.get(), members.get()
    sio.enter_room(first_player, 'room_battle')
    sio.enter_room(second_player, 'room_battle')
    game = Game('room_battle', first_player, second_player)
    while game.state == 0:
        field = game.field.tolist()
        await sio.emit('set_field', {'field': field}, room='room_battle')
        sid = game.first_player
        print(sid, 'этот должен ходить следующий')
        response = await sio.call('xoxo', data={'message': 'Ваш ход', 'field': field}, sid=sid)
        response = response['point']
        move = tuple(map(int, response.split(',')))
        game.move(sid, move)
        await sio.emit('set_field', {'field': field}, room='room_battle')
        print(game.field)
        print(game.state)


app.router.add_static('/static', 'static')
app.add_routes(
    [web.get('/', index)]
)

web.run_app(app, port=os.environ['PORT'])
