from gevent import monkey
import logging
import socket
from gevent.wsgi import WSGIServer
from gevent.pywsgi import WSGIHandler

from chaussette.util import create_socket

logger = logging.getLogger('werkzeug')

class GeventRequestHandler(WSGIHandler):

    def log_request(self):
        duration = int((self.time_finish - self.time_start) * 1000)
        try:
            length = self.response_length or '-'
            code = (getattr(self, 'status', None) or '000').split()[0]
            client_address = self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address
            logger._log(logging.INFO,
                        '%s - - %s' % (client_address or '-',
                                       '"%s" %s %s [%sms]' % (getattr(self, 'requestline', ''),
                                                                code, length, duration)), ())
        except BaseException:
            try:
                self.server.log.exception('%s %s %s %s %s', client_address, self.requestline, code, length, duration)
            except:
                pass

class Server(WSGIServer):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM

    def __init__(self, listener, application=None, backlog=None,
                 spawn='default', log='default', handler_class=GeventRequestHandler,
                 environ=None, socket_type=socket.SOCK_STREAM,
                 address_family=socket.AF_INET, **ssl_args):
        monkey.noisy = False
        monkey.patch_all()
        host, port = listener
        self.socket = create_socket(host, port, self.address_family,
                                    self.socket_type, backlog=backlog)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_address = self.socket.getsockname()
        super(Server, self).__init__(self.socket, application, None, spawn,
                                     log, handler_class, environ, **ssl_args)
