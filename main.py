from aiohttp import web
import socketio
import aiohttp_jinja2
import jinja2
from xoxo import Game
import os
from dotenv import load_dotenv

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


# games_pool = []

async def index(request):
    context = {'name': 'world!'}
    return aiohttp_jinja2.render_template(
        'index.jinja2', request, context
    )


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
@sio.event
async def game_driver(sid):
    print("game driver started")
    game = Game(4, sid, 'a7')
    while game.state == 0:
        field = game.field.tolist()
        response = await sio.call('xoxo', data={'message': 'Ваш ход', 'field': field}, sid=sid)
        response=response['point']
        move = tuple(map(int, response.split(',')))
        game.move(sid, move)
        print(game.field)
        print(game.state)

app.router.add_static('/static', 'static')
app.add_routes(
    [web.get('/', index)]
)

web.run_app(app, port=os.environ['PORT'])
