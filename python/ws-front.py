#--coding
from Cookie import BaseCookie
import socket
from gevent.event import Event
import os

import sys
import gevent

import settings

__author__ = 'kivsiak'

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from beaker.middleware import SessionMiddleware

from gevent_zeromq import zmq

ctx = zmq.Context()

pub = ctx.socket(zmq.PUSH)
pub.connect(settings.FRONT_CMD)

sub = ctx.socket(zmq.SUB)
sub.connect(settings.FRONT_RESULT)


stats = {'total': 0}

events = {}


def cleanUp(sid):
    sub.setsockopt(zmq.UNSUBSCRIBE, sid)
    del events[sid]

def listenTopic():

    while True:
        sid, message = sub.recv_multipart()
        event = events.get(sid, None)
        if event:
            event["msg"] = message
            event["event"].set()

def listenCloud(ws, sid):

    events[sid] = {"msg": None,
                    "event": Event()}
    sub.setsockopt(zmq.SUBSCRIBE, sid)

    while ws.socket:
        events[sid]["event"].wait(5)
        if ws.socket:
            ws.send(events[sid]['msg'])
            events[sid]["event"].clear()


    stats['total'] -= 1


def sendToCloud(ws, sid):
    try:
        while True:
            message = ws.receive()
            if message is None:
                pub.send_multipart((sid, "closing"))
                break
            pub.send_multipart((sid, str(message)))
        ws.close()
    except  socket.error as e:
        print "channel closed by peer"
    cleanUp(sid)


def websocket_app(environ, start_response):
    if environ["PATH_INFO"] == '/ws':
        stats['total'] +=1
        print "got connection. total %s" % stats['total']
        websocket = environ["wsgi.websocket"]
        sid = environ['beaker.session'].id
        gevent.spawn(listenCloud, websocket, sid)
        gevent.spawn(sendToCloud, websocket, sid).join()



try :

    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': True,
        }

    print "myPID: %s" % os.getpid()

    gevent.spawn(listenTopic)

    server = pywsgi.WSGIServer(("", 8000), SessionMiddleware(websocket_app,session_opts),
                                            handler_class = WebSocketHandler)
    server.serve_forever()

except KeyboardInterrupt as e:
    print ("interupted")
    sys.exit()