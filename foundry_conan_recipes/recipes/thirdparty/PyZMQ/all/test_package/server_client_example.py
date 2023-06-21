import os
import threading

for path in filter(None, os.getenv('FN_PYTHON_DLL_DIRECTORIES', '').split(os.pathsep)):
    os.add_dll_directory(path)

import zmq

context = zmq.Context()

g_received = 0
g_sent = 0


def server_func():
    global g_received

    socket = context.socket(zmq.REP)
    socket.bind('inproc://#1')

    g_received = 0
    while g_received != 100:
        message = socket.recv()
        assert message == b'Hello'
        g_received += 1
        socket.send(b'World')


def client_func():
    global g_sent

    socket = context.socket(zmq.REQ)
    socket.connect('inproc://#1')

    g_sent = 0
    while g_sent != 100:
        socket.send(b'Hello')
        g_sent += 1
        message = socket.recv()
        assert message == b'World'


server_thread = threading.Thread(target=server_func)
client_thread = threading.Thread(target=client_func)

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()

assert g_received == 100
assert g_sent == 100
