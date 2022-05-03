"""
Import ydl_send and stuff (TODO: docs)

    >>> from ydl import ydl_send, todo
    >>> ydl_send("process 2", "banana", {"data1":1, "data2":2})

"""

from ._core import YDLClient, DEFAULT_YDL_ADDR
from ._header import header