#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""

 _____ _    ______ _____ _____   _   _ _ _
/  __ \ |   | ___ \_   _/  ___| | | | | | |
| /  \/ |__ | |_/ / | | \ `--.  | | | | | |_ _ __ ___  _ __
| |   | '_ \|    /  | |  `--. \ | | | | | __| '__/ _ \| '_ \
| \__/\ | | | |\ \ _| |_/\__/ / | |_| | | |_| | | (_) | | | |
 \____/_| |_\_| \_|\___/\____/   \___/|_|\__|_|  \___/|_| |_|



font generated by:
http://patorjk.com/software/taag/#p=display&f=Doom&t=ChRIS%20Ultron

This module implements a server side feed controller/model.

"""

import  abc
import  json
import  sys
import  datetime
import  os

import  threading
import  zmq
import  json
from    urlparse    import urlparse

import  C_snode
import  message

class ChRIS_DB(object):
    """
    The server class for the C_snode server

    """
    __metaclass__   = abc.ABCMeta


    def log(self, *args):
        """
        get/set the internal pipeline log message object.

        Caller can further manipulate the log object with object-specific
        calls.
        """
        if len(args):
            self._log = args[0]
        else:
            return self._log

    def name(self, *args):
        """
        get/set the descriptive name text of this object.
        """
        if len(args):
            self.__name = args[0]
        else:
            return self.__name


    def __init__(self, **kwargs):
        """

        """

        self._stree             = C_snode.C_stree()

        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True
        self._log               = message.Message()
        self._log._b_syslog     = True
        self.__name             = "ChRIS_DB"

        self._name              = ""
        self.within             = None                      # An encapsulating object

        # DB
        self.str_DBpath         = '/tmp/ChRIS_DB'
        self._stree             = C_snode

        # Comms
        self.str_protocol       = "tcp"
        self.str_IP             = "127.0.0.1"
        self.str_port           = "5001"

        self.DB_read()

        for key, val in kwargs.iteritems():
            if key == 'within': self.within     = val

        self.zmq_context        = zmq.Context()


    def DB_read(self, **kwargs):
        """
        Read the DB from filesystem
        """

        print("Reading DB from disk...")
        self.debug("Reading DB from disk...\n")
        self._stree = C_snode.C_stree.tree_load(
            pathDiskRoot    = self.str_DBpath,
            loadJSON        = False,
            loadPickle      = True)
        self.debug("DB read from disk...\n")
        print("DB read from disk...")

    def start(self):
        """
            Main execution.
            Instantiate workers, Accept client connections,
            distribute computation requests among workers and route computed results back to clients.
        """

        print("Starting server...")

        # Front facing socket to accept client connections.
        socket_front = self.zmq_context.socket(zmq.ROUTER)
        socket_front.bind('tcp://127.0.0.1:5010')

        # Backend socket to distribute work.
        socket_back = self.zmq_context.socket(zmq.DEALER)
        socket_back.bind('inproc://backend')

        # Start three workers.
        for i in range(1,2):
            worker = Worker(self.zmq_context, i, self._stree)
            worker.start()
            print("Threaded worker %d started..." % i)

        # Use built in queue device to distribute requests among workers.
        # What queue device does internally is,
        #   1. Read a client's socket ID and request.
        #   2. Send socket ID and request to a worker.
        #   3. Read a client's socket ID and result from a worker.
        #   4. Route result back to the client using socket ID.
        zmq.device(zmq.QUEUE, socket_front, socket_back)

    def __iter__(self):
        yield('Feed', dict(self._stree.snode_root))

    # @abc.abstractmethod
    # def create(self, **kwargs):
    #     """Create a new tree
    #
    #     """

    def __str__(self):
        """Print
        """
        return str(self.stree.snode_root)

    @property
    def stree(self):
        """STree Getter"""
        return self._stree

    @stree.setter
    def stree(self, value):
        """STree Getter"""
        self._stree = value

class Worker(threading.Thread):
    """ Workers accept computation requests from front facing server.
        Does computations and return results back to server. """

    def log(self, *args):
        """
        get/set the internal pipeline log message object.

        Caller can further manipulate the log object with object-specific
        calls.
        """
        if len(args):
            self._log = args[0]
        else:
            return self._log

    def name(self, *args):
        """
        get/set the descriptive name text of this object.
        """
        if len(args):
            self.__name = args[0]
        else:
            return self.__name

    def __init__(self, zmq_context, _id, stree):
        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True
        self._log               = message.Message()
        self._log._b_syslog     = True
        self.__name             = "Worker"

        threading.Thread.__init__(self)
        self.zmq_context    = zmq_context
        self.worker_id      = _id
        self._stree         = stree

    def run(self):
        """ Main execution. """
        # Socket to communicate with front facing server.
        socket = self.zmq_context.socket(zmq.DEALER)
        socket.connect('inproc://backend')

        while True:
            print("\n\nWorker ID - %s: run() - Ready to serve..." % self.worker_id)
            # First string received is socket ID of client
            client_id = socket.recv()
            request = socket.recv()
            print('Worker ID - %s: run() - Received comms from client.' % (self.worker_id))
            result = self.process(request)
            # try:
            #     result = self.process(request)
            # except:
            #     print('Worker ID - %s. some error was detected' % (self.worker_id))
            #     os._exit(1)
            print('Worker ID - %s: run() - Sending response to client.' % (self.worker_id))
            print(result)

            # For successful routing of result to correct client, the socket ID of client should be sent first.
            socket.send(client_id, zmq.SNDMORE)
            socket.send(result)

    def process(self, request):
        """ Process the call return result. 

        Since the client only ever processes a "single" feed, there is no need to
        ever send the whole data structure back and forth. Only the feed that
        is requested needs to be processed.

        This process() method in fact implements a mini-REST API of its own.

        """

        s                   = C_snode.C_stree()
        b_returnFeedList    = False

        s.cd('/')
        s.mkcd('users')
        s.mkcd('chris')
        s.graft(self._stree, '/users/chris/plugins')
        s.graft(self._stree, '/users/chris/login')

        print("Worker ID - %s: process() - request = '%s'" % (self.worker_id, request))

        d_request           = json.loads(request)
        str_verb            = d_request['VERB']
        str_URL             = d_request['URL']
        d_data              = d_request['data']

        o_URL               = urlparse(str_URL)
        str_path            = o_URL.path
        l_path              = str_path.split('/')[2:]

        if str_verb == 'QUIT':
            print('Shutting down server...')
            os._exit(1)

        # 'paths' are of form:
        #   /v1/Feeds/NAME__Feed-1
        #           -- or --
        #   /v1/Feeds/NAME
        str_feed    = l_path[1]

        # Strip out the NAME<__>
        str_feed    = str_feed.replace('NAME', '')
        str_feed    = str_feed.replace('__', '')

        if str_verb == 'PULL' or str_verb == 'GET':
            if len(l_path) >= 2 and len(str_feed):
                s.mkcd('feeds')
                s.graft(self._stree, '/users/chris/feeds/%s' % str_feed)
            if len(l_path) == 1:
                b_returnFeedList    = True
            if len(l_path) == 2 and not len(str_feed):
                b_returnFeedList    = True
            if b_returnFeedList:
                s.mkcd('feeds')
                self._stree.cd('/users/chris/feeds')
                l_feeds = self._stree.lstr_lsnode()
                s.mknode(l_feeds)

        if str_verb == 'PUSH':
            if len(l_path) >= 2 and len(str_feed):
                self._stree.cd('/users/chris/feeds')
                # self._stree.rm(str_feed)
                s.initFromDict(d_data)
                self._stree.graft(s, '/users/chris/feeds/%s' % str_feed)
            else:
                s.mkcd('feeds')
                self._stree.cd('/users/chris/feeds')
                l_feeds = self._stree.lstr_lsnode()
                s.mknode(l_feeds)

        # print(s)
        # print(dict(s.snode_root))
        return json.dumps(dict(s.snode_root))

if __name__ == "__main__":
    comm    = ChRIS_DB().start()
