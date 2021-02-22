from aiohttp import web
import socketio
import threading
import multiprocessing as mp
import sys
import asyncio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


async def index(request):
    """Serve the client-side application."""
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.event
async def chat_message(data):
    print("message ", data)
    sio.emit('my event', {'data': data})


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


def ask(stdin):
    while True:
        print('Enter your message ', )
        data = stdin.readline().strip()
        if data == "exit":
            stdin.close()
            return
        else:
            asyncio.run(chat_message(data))


app.router.add_static('/static', 'static')
app.router.add_get('/', index)


def server():
    web.run_app(app)


if __name__ == '__main__':
    p1 = mp.Process(target=server)
    p1.start()
    t1 = threading.Thread(target=ask, args=(sys.stdin,))
    t1.start()
    p1.join()
    t1.join()
