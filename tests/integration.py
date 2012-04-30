import sys
import os
from random import random
import socket
from time import sleep

__author__ = 'kivsiak'

from websocket import create_connection

ws = create_connection("ws://localhost:8000/ws")


#todo rewrite in async style
while True:
    try:
        ws.send("hello world " + str(int(random()*100)))
        print ws.recv()
        print ws.recv()
        sleep(1)
    except  socket.error:
        print("remote host is closed")
        sys.exit()
    except  KeyboardInterrupt:
        print "closed by user"
        sys.exit()

