import threading
import json
import socket
import selectors
import time


# when using YDL, please do:
# from ydl import ydl_send, ydl_start_read
# since only those two methods are meant for public consumption

DEFAULT_YDL_ADDR = ('127.0.0.1', 5001) # doesn't need to be available on network

class YDLClient():
    def __init__(self, *receive_channels, put_json=False, socket_address=DEFAULT_YDL_ADDR):
        '''
        Takes in receiving channel names (strings).
        Takes whether to return received items as JSON or Python dict.
        Waits for connection to open.
        '''
        self.receive_channels = receive_channels
        self.put_json = put_json
        self.socket_address = socket_address
        self.lock = threading.Lock()
        self.conn = None
        self._new_connection()
        
    def send(self, target_channel, header, dic=None):
        '''
        Send header and dictionary to target channel (string)
        header: string
        dict: Python dictionary
        '''
        if dic is None:
            dic = {}
        json_str = json.dumps([header, dic])
        try:
            send_message(self.conn, target_channel, json_str)
        except BrokenPipeError:
            self._new_connection()
    
    def receive(self):
        '''
        Blocks while waiting for next message. Not entirely thread safe; 
        should be reseliant to concurrent send() calls but not concurrent receive() calls. 
        '''
        while True:
            while True:
                selobj_iter = iter(self.selobj)
                try:
                    target, message = next(selobj_iter)
                except StopIteration:
                    pass
                else:
                    if self.put_json:
                        return (target, message)
                    else:
                        return (target,) + tuple(json.loads(message))

                try: # try statement needed because windows sucks and throws an 10054 
                    # connection reset error rather than just returning a 0 byte.
                    data = self.conn.recv(1024)  # block
                except ConnectionResetError:
                    data = []
                if len(data) == 0:
                    break
                else:
                    self.selobj.inb += data
            self._new_connection()

    def _new_connection(self):
        self.lock.acquire()
        if self.conn is not None:
            self.conn.close()
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.selobj = ReadObject() # in case was in middle of receiving, want this reset
        while True:
            try:
                self.conn.connect(self.socket_address)
                break
            except ConnectionRefusedError:
                time.sleep(0.1)
        for rc in self.receive_channels:
            send_message(self.conn, rc, "")
            # sending an empty string is a special message that means "subscribe to channel"
        self.lock.release()


def send_message(conn, target, msg):
    '''
    (internal use only)
    Sends a message meant for the given target across conn
    The message format is (len1, len2, str1, str2)
    Note: all 4 components have to be in one conn.sendall call,
    otherwise bad things happen when multiple threads send messages
    at the same time
    '''
    conn.sendall(len(target).to_bytes(4, "little")
               + len(msg).to_bytes(4, "little")
               + target.encode("utf-8")
               + msg.encode("utf-8"))

class ReadObject:
    '''
    (internal use only)
    An iterable object for receiving messages
    Append incoming message bytes to self.inb,
    and then you can loop through the object to get the messages
    '''
    def __init__(self):
        self.inb = b''

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.inb) < 8:
            raise StopIteration
        len1 = int.from_bytes(self.inb[0:4], "little")
        len2 = int.from_bytes(self.inb[4:8], "little")
        if len(self.inb) < 8 + len1 + len2:
            raise StopIteration
        target_channel = self.inb[8: len1 + 8].decode("utf-8")
        message = self.inb[len1 + 8: len1 + len2 + 8].decode("utf-8")
        self.inb = self.inb[len1 + len2 + 8:]
        return (target_channel, message)

def accept(sel, sock, verbose):
    '''
    (server method - internal use only)
    When sock has a connection ready to accept,
    accept the connection and register it in sel
    Note that we want the new connections to be blocking,
    since dealing with non-blocking writes is a pain
    '''
    conn, addr = sock.accept()  # Should be ready
    if verbose:
        print('accepted connection from', addr)
    sel.register(conn, selectors.EVENT_READ, ReadObject())

def read(sel, subscriptions, conn, obj, verbose):
    '''
    (server method - internal use only)
    When conn has bytes ready to read, read those bytes and
    forward messages to the correct subscribers
    '''
    try: # try statement needed because windows sucks and throws an 10054 
         # connection reset error rather than just returning a 0 byte.
        data = conn.recv(1024)  # Should be ready
    except ConnectionResetError:
        data = []
    if len(data) == 0:
        if verbose:
            print('closing connection from socket')
        sel.unregister(conn)
        conn.close()
        for lst in subscriptions.values():
            while conn in lst:
                lst.remove(conn)
    else:
        obj.inb += data
        for target_channel, message in obj:
            subscriptions.setdefault(target_channel, [])
            if len(message) == 0:
                # an empty string is a special message that means "subscribe to channel"
                subscriptions[target_channel].append(conn)
            else:
                # forward message to correct subscribers
                for c in subscriptions[target_channel]:
                    send_message(c, target_channel, message)

def run_ydl_server(address=None, port=None, verbose=False):
    '''
    (server method - internal use only)
    Runs the YDL server that processes will use
    to communicate with each other
    '''
    if address is None:
        address = DEFAULT_YDL_ADDR[0]
    if port is None:
        port = DEFAULT_YDL_ADDR[1]
    if verbose:
        print("Starting YDL server at address:", (address, port))
    subscriptions = {} # a mapping of target names -> list of socket objects
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((address, port))
    sock.listen()
    sock.setblocking(False)
    sel = selectors.DefaultSelector()
    sel.register(sock, selectors.EVENT_READ, None)
    while True:
        events = sel.select(timeout=1) #Windows is bad and needs a timeout here.
        for key, _mask in events:
            if key.data is None:
                accept(sel, key.fileobj, verbose)
            else:
                read(sel, subscriptions, key.fileobj, key.data, verbose)
