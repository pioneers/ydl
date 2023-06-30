"""YDL: interprocess communication over TCP sockets

Import the ydl module to initialize a YDL client or server:

Process 0:
    >>> from ydl import run_server
    >>> run_server()

Process 1:
    >>> from ydl import Client
    >>> yc = Client()
    >>> yc.send(("process 2", "stuff"))

Process 2:
    >>> from ydl import Client
    >>> yc = Client("process 2")
    >>> yc.receive()
    ('process 2', 'stuff')
"""

from ._core import DEFAULT_HOST, DEFAULT_PORT, Client, run_server
from ._header import header, Handler
