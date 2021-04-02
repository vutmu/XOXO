from aiohttp import web
import socketio
import aiohttp_jinja2
import jinja2
from xoxo import Game
import os
from dotenv import load_dotenv
from queue import Queue
import requests as r

import base64
from cryptography import fernet
from aiohttp_session import setup as setup_session, get_session, new_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

members = Queue()

sio = socketio.AsyncServer()


async def make_app():
    app = web.Application()
    sio.attach(app)
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup_session(app, EncryptedCookieStorage(secret_key))
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader('./templates'))
    app.router.add_static('/static', 'static')
    app.add_routes(
        [web.get('/', index)])
    return app


# games_pool = []

# async def index(request):
#     context = {'name': 'world!'}
#     response = aiohttp_jinja2.render_template(
#         'index.jinja2', request, context)
#     response.headers['Content-Language'] = 'ru'
#     return response

async def index(request):
    session = await get_session(request)
    if session:
        context = {'name': session['username']}
        response = aiohttp_jinja2.render_template('index.jinja2',
                                                  request,
                                                  context)
        return response
    else:
        if 'token' not in request.query:
            context = {'name': 'token not in request.query'}
            response = aiohttp_jinja2.render_template('404_not_found.jinja2',
                                                      request,
                                                      context)
        else:
            token = request.query['token']
            secret_key = 'very_secret_key'
            req = r.post(os.environ['CHECK_AUTH'], data={'token': token, 'secret_key': secret_key})
            resp = req.json()
            if resp['status'] == 'fail':
                context = {'name': resp['name']}
                response = aiohttp_jinja2.render_template('404_not_found.jinja2',
                                                          request,
                                                          context)
            else:
                session = await new_session(request)
                session['username'] = resp['name']
                print('это данные сессии', session)
                context = {'name': resp['name']}

                response = aiohttp_jinja2.render_template('index.jinja2',
                                                          request,
                                                          context)
        return response


# @aiohttp_jinja2.template('index.jinja2')
# def index(request):
#     if 'token' in request.query:
#         token = request.query['token']
#         req = r.post('http://127.0.0.1:5000/tokens', data={'token': token})
#         # TODO этот запрос небезопасен! переделать
#         name = req.json()
#         context = {'name': name}
#         return context
#     else:
#         return {'name': 'world'}


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
    first_player, second_player = members.get(), members.get()
    sio.enter_room(first_player, 'room_battle')
    sio.enter_room(second_player, 'room_battle')
    game = Game('room_battle', first_player, second_player)
    while game.state == 0:
        field = game.field.tolist()
        await sio.emit('set_field', {'field': field}, room='room_battle')
        sid = game.first_player
        approve_move = False
        while not approve_move:
            response = await sio.call('xoxo', data={'message': 'Ваш ход', 'field': field}, sid=sid)
            response = response['point']
            move = tuple(map(int, response.split(',')))
            approve_move = game.move(sid, move)
            if not approve_move:
                await sio.emit('game_message', data={'message': 'клетка уже занята!'}, room=sid)
        await sio.emit('set_field', {'field': field}, room='room_battle')
    field = game.field.tolist()
    await sio.emit('set_field', {'field': field}, room='room_battle')
    await sio.emit('game_message', {'message': approve_move}, room='room_battle')


web.run_app(make_app(), port=os.environ['PORT'])
