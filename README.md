# YDL

YDL is a simple inter-process communication framework. It is cross-platform and built on TCP sockets.

## Installation

You can install YDL from PyPI:
```
python -m pip install ydl-ipc
```

## How to use

TODO

Example (sender):
```
from ydl import YDLClient

YDL = YDLClient()
YDL.send("channel1", "cheese")
YDL.send("channel2", "message meant for some other receiver")
YDL.send("channel3", "wheeze", {"data": 1})
```

Example (receiver):
```
from ydl import YDLClient

YDL = YDLClient("channel1", "channel3")
print(YDL.receive())
# prints ('channel1', 'cheese', {})
print(YDL.receive())
# prints ('channel3', 'wheeze', {'data': 1})
```
