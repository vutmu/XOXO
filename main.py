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
import re
import ast
import redis

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

members = Queue()
Visitors = redis.from_url(os.environ.get("REDIS_URL"), db=1)

sio = socketio.AsyncServer()
fernet_key = bytes(os.environ['FERNET_KEY'], 'ascii')
secret_key = base64.urlsafe_b64decode(fernet_key)


async def make_app():
    app = web.Application()
    sio.attach(app)
    # setup_session(app, SimpleCookieStorage())
    setup_session(app, EncryptedCookieStorage(secret_key))
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader('./templates'))
    app.router.add_static('/static', 'static')
    app.add_routes(
        [web.get('/', index), web.get('/another', another_page)])
    return app


# games_pool = []

# async def index(request):
#     context = {'name': 'world!'}
#     response = aiohttp_jinja2.render_template(
#         'index.jinja2', request, context)
#     response.headers['Content-Language'] = 'ru'
#     return response


# async def middleware1(request, handler):
#     print('middleware1 запущен')
#     session = await get_session(request)

async def another_page(request):
    context = {'name': {i for i in Visitors}}  # this is wrong!
    response = aiohttp_jinja2.render_template('another_page.jinja2',
                                              request,
                                              context)
    return response


async def index(request):
    session = await get_session(request)
    if session:
        context = {'name': session['username'], 'avatar': session['avatar'], 'user_id': session['user_id']}
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
            wasmoh_key = 'very_secret_key'
            req = r.post(os.environ['CHECK_AUTH'], data={'token': token, 'secret_key': wasmoh_key})
            resp = req.json()
            if resp['status'] == 'fail':
                context = {'name': resp['name']}
                response = aiohttp_jinja2.render_template('404_not_found.jinja2',
                                                          request,
                                                          context)
            else:
                session = await new_session(request)
                session['username'] = resp['name']
                session['avatar'] = resp['avatar']
                session['user_id'] = resp['user_id']
                context = {'name': resp['name'], 'avatar': resp['avatar'], 'user_id': resp['user_id']}

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
async def connect(sid, environ):
    # members.put(sid)
    obj = ast.literal_eval(authenticate_user(environ))
    username = obj['session']['username']
    avatar = obj['session']['avatar']
    user_id = str(obj['session']['user_id'])
    print(username, avatar, user_id)
    await sio.save_session(sid, {'username': username, 'avatar': avatar, 'user_id': user_id})
    sio.enter_room(sid, 'Visitors')
    await sio.emit('add_visitor', {'data': (user_id, username, avatar)}, room='Visitors', skip_sid=sid)
    Visitors.set(user_id, f"{username}, {avatar}")
    print("connect ", sid, username)


def authenticate_user(environ):
    cookies = environ['HTTP_COOKIE'].split(';')
    print(cookies)
    regexp = '\s*AIOHTTP_SESSION='
    for i in cookies:
        if re.match(regexp, i):
            AIOHTTP_SESSION = re.findall('".*"', i)[-1]
    f = fernet.Fernet(fernet_key)
    return f.decrypt(bytes(AIOHTTP_SESSION, 'utf-8')).decode('utf-8')


@sio.event
async def chat_message(sid, data):
    if data == 'create game' and members.qsize() == 10:  # тут дб 2 чтобы игра стартовала
        await game_driver(members)
    elif data == 'get_visitors':
        session = await sio.get_session(sid)
        List = []
        for i in Visitors.keys():
            user_id = i.decode('utf-8')
            username, avatar = Visitors.get(i).decode('utf-8').split(', ')
            if session['user_id'] != user_id:
                List.append((user_id, username, avatar))
        print('это лист', List)
        return List  # TODO тут нужна пагинация!
    else:
        print("message ", data)


@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    username = session['username']
    user_id = session['user_id']
    Visitors.delete(user_id)
    await sio.emit('del_visitor', user_id, room='Visitors')
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
