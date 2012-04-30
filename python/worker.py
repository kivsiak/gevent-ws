import os
from random import random
from time import sleep

__author__ = 'kivsiak'

import  gevent
import settings

from gevent.greenlet import Greenlet
from gevent_zeromq import zmq

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.connect(settings.BACK_RESULT)

def handler(type, worker_cls):
    sub = ctx.socket(zmq.PULL)
    sub.connect(settings.BACK_CMD)

    while True:
        msg = sub.recv_multipart()
        if len(msg) != 2:
            print "bad message" + msg
            continue
        worker = worker_cls(msg)
        worker.start()


class Worker(Greenlet):
    def __init__(self, msg):
        super(Worker, self).__init__()
        self.sid = msg[0]
        self.msg = msg[1]

    def _run(self):
        pub.send_multipart((self.sid,  str("got " + self.msg)))
        gevent.sleep(random()*10)
        pub.send_multipart((self.sid,  str("done some work with: " +self.msg )))


try:
    print os.getpid()
    gevent.joinall((
                    gevent.spawn(handler, "", Worker),))

except  KeyboardInterrupt:
    print("buy")

