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
"""

str_desc = """

 _____ _    ______ _____ _____  _    _ _____
/  __ \ |   | ___ \_   _/  ___|| |  | /  ___|
| /  \/ |__ | |_/ / | | \ `--. | |  | \ `--.
| |   | '_ \|    /  | |  `--. \| |/\| |`--. \\
| \__/\ | | | |\ \ _| |_/\__/ /\  /\  /\__/ /
 \____/_| |_\_| \_|\___/\____/  \/  \/\____/
                           ______
                          |______|

'ChRIS_WS' -- ChRIS Web Service -- is a simple server that parses
raw socket input for /GET /xxx HTTP/ strings, dispatches input to
a ChRIS_SM instance, parses the resultant stdout, and transmits this
back to the caller.

Parts of the server infrastructure were adapted from:
http://thomasfischer.biz/python-simple-json-tcp-server-and-client/

"""

from    webob           import Response
from    urlparse        import urlparse, parse_qs

import  crun
import  SocketServer
import  json
import  argparse
import  os
import  sys
import  datetime

import  message
import  error
from    _colors         import Colors
import  serverInfo

class TCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class TCPServerHandler(SocketServer.BaseRequestHandler):

    #
    # Class member variables -- if declared here are shared
    # across all instances of this class
    #
    _dictErr = {
        'shellFailure'   : {
            'action'        : 'attempting to run shell job, ',
            'error'         : 'a failure was detected.',
            'exitCode'      : 11}
    }

    def log(self, *args):
        '''
        get/set the internal pipeline log message object.

        Caller can further manipulate the log object with object-specific
        calls.
        '''
        if len(args):
            self._log = args[0]
        else:
            return self._log

    def name(self, *args):
        '''
        get/set the descriptive name text of this object.
        '''
        if len(args):
            self.__name = args[0]
        else:
            return self.__name


    def URL_clientParamsPOST(self, al_inputRaw):
        """ Returns the string of client parameters embedded in the URL.

            This method handles POST calls from client, i.e. calls that
            push information TO the backend.

            Args:
                al_inputRaw (list): The raw socket data as list split on '\n'

            Returns:
                a string of client parameters.
        """
        str_GET         = al_inputRaw[0]
        l_URLargSpec    = str_GET.split('/')
        str_URLargs     = l_URLargSpec[1].split()[0]
        return str_URLargs

    def URL_clientParamsRPCGET(self, al_inputRaw):
        """ Returns the string of client parameters embedded in the URL.

            This method handles GET calls from client, i.e. calls that
            get information FROM the backend.

            Args:
                al_inputRaw (list): The raw socket data as list split on '\n'

            Returns:
                a string of client parameters.
        """
        str_GET         = al_inputRaw[0]
        str_REST        = str_GET.split()[1]

        print(str_REST)
        l_URLargSpec    = str_GET.split('/')
        str_URLargs     = l_URLargSpec[1].split()[0]
        print(str_URLargs)
        return str_URLargs

    def URL_clientParams_RPCGET(self, al_inputRaw):
        """ Returns the string of client parameters embedded in the URL.

            This method handles GET calls from client, i.e. calls that
            get information FROM the backend.

            Args:
                al_inputRaw (list): The raw socket data as list split on '\n'

            Returns:
                a string of client parameters.
        """
        str_GET         = al_inputRaw[0]
        str_RPC         = str_GET.split()[1]

        return str_RPC

    def URL_clientParams_RESTGET(self, al_inputRaw):
        """ Returns the string of client parameters embedded in the URL.

            This method handles GET calls from client, i.e. calls that
            get information FROM the backend.

            Args:
                al_inputRaw (list): The raw socket data as list split on '\n'

            Returns:
                a string of client parameters.
        """
        str_GET         = al_inputRaw[0]
        str_REST        = str_GET.split()[1]

        return str_REST


    def URL_serverProcess(self, astr_URLargs, **kwargs):
        """Call the server side entry point with the URLargs and sessionFile.

        Args:
            astr_URLargs (string):      The string of data from client.
            astr_sessionFile (string):  The sessionFile to use.

        Returns:
            string response from server process
        """


        shell = crun.crun()
        shell.waitForChild(True)
        shell.echoStdOut(False)
        shell.echoStdErr(False)
        shell.echo(False)

        self._log                       = message.Message()
        self._log._b_syslog             = True
        self.__name                     = "ChRIS_client"
        self._str_authority             = ""

        for key,val in kwargs.iteritems():
            if key == 'sessionFile':    astr_sessionFile    = val
            if key == 'authority':      self._str_authority = val

        if args.API == 'REST':
            cmd     = 'ChRIS_SM.py --APIcall \"%s\" --REST --authority %s' % (astr_URLargs, self._str_authority)

        if args.API == 'RPC':
            cmd     = 'ChRIS_SM.py --APIcall \"%s\" --RPC --stateFile %s' % (astr_URLargs, astr_sessionFile)


        print(Colors.CYAN_BCKGRND + "\n%s" % cmd + Colors.NO_COLOUR + "\n")

        try:
            shell(cmd)
        except:
            error.fatal(self, 'shellFailure',
                    '\nExecuting:\n\t%s\nstdout:\n-->\t%s\nstderr:\n-->%s' %
                    (shell._str_cmd, shell.stdout(), shell.stderr()))
        if shell._exitCode:
            error.fatal(self, 'shellFailure', '\nExit code failure:\t%s\n%s\n%s\n%s' %
                        (shell._exitCode, shell._str_cmd, shell.stdout(), shell.stderr()))

        return(json.loads(shell.stdout()))

    def HTTPresponse_sendClient(self, str_payload, **kwargs):
        """Send a properly formed HTTP response back to the client.
        """

        str_contentType = "text/html"
        for key, val in kwargs.iteritems():
            if key == "ContentType":   str_contentType = val

        res  = Response(str_payload)
        res.content_type = str_contentType

        str_HTTPpre = "HTTP 1.1 "
        # str_res     = "%s %s" % (str_HTTPpre, str(res))
        str_res     = "%s %s %s" % (str_HTTPpre,  "Access-Control-Allow-Origin: *", str(res))
        return str_res

    def byteSizeReturned(self, nbytes):
        """
        Return the <bytes> as a string in human
        readable format.
        :param bytes: input size in bytes
        :return: human readable string
        """
        suffixes = ['B', 'kB', 'MB', 'GB', 'TB', 'PB']
        if nbytes == 0: return '0 B'
        i = 0
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])

    def handle(self):
        str_authority   = ""
        str_raw         = self.request.recv(1024).strip()
        now             = datetime.datetime.today()
        str_timeStamp   = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        print("\n\n***********************************************")
        print("***********************************************")
        print("%s incoming data stream" % (str_timeStamp) )
        print("***********************************************")
        print("raw input:")
        print("***********************************************")
        print(Colors.CYAN + "%s\n" % (str_raw) + Colors.NO_COLOUR)
        print("***********************************************")
        l_raw           = str_raw.split('\n')
        FORMtype        = l_raw[0].split('/')[0]
        str_authority   = l_raw[1].split()[1]
        print(Colors.YELLOW)
        print('authority  = %s' % str_authority)
        print('API verb   = %s' % FORMtype)
        print('API object = %s' % l_raw[0].split()[1])
        print(Colors.NO_COLOUR)
        print("***********************************************")
        str_URL     = eval('self.URL_clientParams_%s%s(l_raw)' % (args.API, FORMtype))
        d_component     = parse_qs(urlparse(str_URL).query)
        print("parsed query component:")
        print("***********************************************")
        print(Colors.YELLOW)
        print(d_component)
        print(Colors.NO_COLOUR)
        print("***********************************************")
        print("CLI to remote service:")
        print("***********************************************")
        if 'sessionFile' in d_component.keys():
            str_sessionFile = d_component['sessionFile'][0]
            str_reply       = self.URL_serverProcess(str_URL, sessionFile = str_sessionFile)
        else:
            str_reply       = self.URL_serverProcess(str_URL, authority = str_authority)
        print("***********************************************")
        print("reply from remote service:")
        print("***********************************************")
        print(Colors.LIGHT_GREEN + json.dumps(str_reply) + Colors.NO_COLOUR)
        bytesReceived = sys.getsizeof(json.dumps(str_reply))
        print("***********************************************")
        print("Received %d bytes (%s)." % \
              (bytesReceived, self.byteSizeReturned(bytesReceived)))
        print("***********************************************")
        try:
            self.request.sendall(self.HTTPresponse_sendClient(json.dumps(str_reply),
                                                              ContentType = 'application/json'))
        except Exception, e:
            print "Exception while attempting to transmit receive message: ", e
        print(Colors.YELLOW + '\nChRIS Web Service listening on %s:%s.' % (args.host, args.port))
        print(Colors.YELLOW + 'API paradigm: ' + Colors.RED_BCKGRND + Colors.WHITE + args.API + Colors.NO_COLOUR)
        print(Colors.RED + '\nTo exit/kill this server, hit <ctrl>-c.\n')
        print(Colors.CYAN + "Use any client to send GET/POST requests to %s:%s." % (args.host, args.port))
        print(Colors.BLUE_BCKGRND + Colors.BLINK_BROWN + "\n\n\t\t\t\t\t. . . w a i t i n g . . .")
        print(Colors.NO_COLOUR)


def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            --hostIP <hostIP>       \\
                            --port <port>           \\
                            --API RPC|REST


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' is a thin server that connects a web browser
        to the ChRIS_SM.py machine.

        It essentially parses the raw URL inputs, then calls
        the ChRIS_SM.py, and returns JSON data back to the caller.

    ARGS

       --hostIP <hostIP>
       The IP of this host. If 'localhost' then only clients on this
       host can connect. If actual IP, then clients on other hosts
       can connect.

       --port <port> (defaults to '5555')
       The port for the server to listen on.

       --REST | --RPC
       The calling paradigm.


    EXAMPLES


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description


if __name__ == "__main__":
    """Start the server on arbitrary port.
    """

    parser  = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-a', '--API',
        help    =   "The API paradigm to use.",
        dest    =   'API',
        action  =   'store',
        default =   'REST'
    )
    parser.add_argument(
        '-p', '--port',
        help    =   "The <port> on which to listen.",
        dest    =   'port',
        action  =   'store',
        default =   5555
    )
    parser.add_argument(
        '-i', '--host',
        help    =   "The <host> name/IP on which to start the server.",
        dest    =   'host',
        action  =   'store',
        default =   "127.0.0.1"
    )


    args = parser.parse_args()

    print(str_desc)
    print(Colors.YELLOW + 'Starting Simple ChRIS Web Service on %s:%s.' % (args.host, args.port))
    print(Colors.YELLOW + 'API paradigm: ' + Colors.RED_BCKGRND + Colors.WHITE + args.API + Colors.NO_COLOUR)
    print(Colors.RED + '\nTo exit/kill this server, hit <ctrl>-c.\n')
    print(Colors.CYAN + "Use any client to send GET/POST requests to %s:%s." % (args.host, args.port))
    print(Colors.BLUE_BCKGRND + Colors.BLINK_BROWN + "\n\t\t\t. . . w a i t i n g . . .")
    print(Colors.NO_COLOUR)
    server = TCPServer((args.host, int(args.port)), TCPServerHandler)
    server.serve_forever()
