#!/usr/bin/env python

""" zeromq client example.

    Three clients are instantiated.
    Each client would generate a pair of numbers and send them to a server to be computed. 
    The computation is adding the two numbers together.
    Once the computed result is recieved from the server it would be printed to standard out. 

    Demonstrables:
        Multiple clients connecting to same server.
        ChRIS_DB_clients receiving correct response. """

# Adaprted heavily from great code by - Kasun Herath <kasunh01 at gmail.com>
# Source - https://github.com/kasun/zeromq-client-server.git

import  threading
import  argparse
import  os
import  sys
import  zmq
import  json
import  C_snode

class DContainer():
    """
    Simple class that "contains" a client and preserves data after the client scope expires.
    """
    def __init__(self, **kwargs):
        """
        constructor
        """

        self._stree         = C_snode.C_stree()
        self.id             = ""
        self.request        = ""
        self.saveTo         = ""
        self.loadFrom       = ""
        self.b_stdout       = ""

        self.b_dataReady    = False

        for key,val in kwargs.iteritems():
            if key == 'id':         self.id         = val
            if key == 'request':    self.request    = val
            if key == 'saveTo':     self.saveTo     = val
            if key == 'loadFrom':   self.loadFrom   = val
            if key == 'stdout':     self.b_stdout   = val

        self.client     = ChRIS_DB_client(
            id          = self.id,
            request     = self.request,
            saveTo      = self.saveTo,
            loadFrom    = self.loadFrom,
            stdout      = self.b_stdout,
            within      = self
        )

class ChRIS_DB_client(threading.Thread):
    """ Represents an example client. """
    def __init__(self, **kwargs):

        self.identity       = "0"
        self.request        = "NULL"
        self.b_saveResult   = False
        self.saveTo         = ""
        self.loadFrom       = ""
        self.b_loadFrom     = False
        self.b_stdout       = False
        self.within         = None

        self.b_dataReady    = False

        self.json_comms     = {}
        self.json_data      = {}
        self.b_json_data    = False

        for key,val in kwargs.iteritems():
            if key == 'id':         self.identity   = val
            if key == 'request':    self.request    = val
            if key == 'saveTo':     self.saveTo     = val
            if key == 'loadFrom':   self.loadFrom   = val
            if key == 'stdout':     self.b_stdout   = val
            if key == 'within':     self.within     = val
            if key == 'data':
                self.b_json_data    = True
                self.json_data      = val

        self.b_saveResult   = len(self.saveTo)
        self.b_loadFrom     = len(self.loadFrom)

        threading.Thread.__init__(self)

        self.zmq_context    = zmq.Context()
        self.stree         = C_snode.C_stree()

    def run(self):
        """ Connects to server. Send request for data tree """
        # print('ChRIS_DB_client ID - %s. Communicating with server.' % (self.identity))
        socket = self.get_connection()
        
        # Poller is used to check for availability of data before reading from a socket.
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        self.send(socket, self.request)

        # Infinitely poll for the result. 
        # Polling is used to check for sockets with data before reading because socket.recv() is blocking.
        while True:
            # Poll for 5 seconds. Return any sockets with data to be read.
            sockets = dict(poller.poll(5000))

            # If socket has data to be read.
            if socket in sockets and sockets[socket] == zmq.POLLIN:
                str_result  = self.receive(socket)
                json_result = json.loads(str_result)
                self.stree.initFromDict(json_result)
                if self.within:
                    self.within._stree  = self.stree
                if self.b_stdout: print(json.dumps(json_result))
                if self.b_saveResult:
                    with open(self.saveTo, 'w') as f:
                        json.dump(json_result, f)
                    f.close()
                break
        socket.close()
        if self.within: self.within.b_dataReady = True
        self.b_dataReady        = True
        self.zmq_context.term()

    def send(self, socket, data):
        """ Send data through provided socket. """

        # print(data)
        l_data  = data.split()
        self.json_comms['VERB'] = l_data[0]
        self.json_comms['URL']  = l_data[1]
        self.json_comms['data'] = {}

        # Should we read the data from external file
        if self.b_loadFrom:
            with open(self.loadFrom, 'r') as f:
                self.json_data = json.load(f)
            f.close()
            self.b_json_data    = True
            # self.json_comms['data'] = self.json_data

        if self.b_json_data:
            self.json_comms['data'] = self.json_data
        socket.send(json.dumps(self.json_comms))

    def receive(self, socket):
        """ Receive and return data through provided socket. """
        return socket.recv()

    def get_connection(self):
        """ Create a zeromq socket of type DEALER; set it's identity, connect to server and return socket. """

        # Socket type DEALER is used in asynchronous request/reply patterns.
        # It prepends identity of the socket with each message.
        socket = self.zmq_context.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, self.identity)
        socket.connect('tcp://127.0.0.1:5010')
        return socket

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            --workers   <numberOfWorkers>   \\
                            --request   <request>           \\
                            --saveTo    <JSONfile>          \\
                            --loadFrom  <JSONfile>


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' is a simple client comms tester that can interact with a server ChRIS_DB.

    ARGS

       --workers <numberOfWorkers>
       The number of internal workers to spawn.

       --request <request>
       The <request> to ask of the server. The following are understood:

            o QUIT now
                Tells the server to exit.

            o PULL <someObjectURL>
                Returns <someObjectURL> as JSON object.

            o PUSH <someObjectURL> <data>
                Puts <data> in <someObjectURL>.

            o SAVE [<fileDB>]
                Saves the DB current state to disk, in file <fileDB>.

       --saveTo <JSONfile>
       Save results to <JSONfile>.

       --loadFrom <JSONfile>
       Load from <JSONfile> and transmit this to server. Only sensical if the <request> is
       a PUSH verb.

       --stdout
       If specified, dump comms from server to stdout, otherwise client is silent.


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

if __name__ == '__main__':

    parser      = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-w', '--workers',
        help    =   "The number of internal workers to spawn.",
        dest    =   'workers',
        action  =   'store',
        default =   1
    )
    parser.add_argument(
        '-r', '--request',
        help    =   "The <request> to ask of the server.",
        dest    =   'request',
        action  =   'store',
        default =   "GET Feeds/"
    )
    parser.add_argument(
        '-s', '--saveTo',
        help    =   "Save the results of the server as JSON object.",
        dest    =   'saveTo',
        action  =   'store',
        default =   ""
    )
    parser.add_argument(
        '-l', '--loadFrom',
        help    =   "Load a JSON object from file.",
        dest    =   'loadFrom',
        action  =   'store',
        default =   ""
    )
    parser.add_argument(
        '--stdout',
        action  =   'store_true',
        dest    =   'b_stdout',
        help    =   'Echo comms from server to stdout.',
        default =   False
    )

    args        = parser.parse_args()

    # Instantiate three clients with different ID's.
    for i in range(1, args.workers+1):
        client = ChRIS_DB_client(
                    id          = str(i),
                    request     = args.request,
                    saveTo      = args.saveTo,
                    loadFrom    = args.loadFrom,
                    stdout      = args.b_stdout
        )
        client.start()
    #     container = DContainer(
    #         id          = str(i),
    #         request     = args.request,
    #         saveTo      = args.saveTo,
    #         loadFrom    = args.loadFrom,
    #         stdout      = args.b_stdout
    #     )
    #     container.client.start()
    # while not container.b_dataReady:
    #     pass
    # print(container._stree)
    while not client.b_dataReady:
        pass
    print(client.stree)
