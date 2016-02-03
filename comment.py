#!/usr/bin/env python


"""

 _____ _    ______ _____ _____   _   _ _ _
/  __ \ |   | ___ \_   _/  ___| | | | | | |
| /  \/ |__ | |_/ / | | \ `--.  | | | | | |_ _ __ ___  _ __
| |   | '_ \|    /  | |  `--. \ | | | | | __| '__/ _ \| '_ \
| \__/\ | | | |\ \ _| |_/\__/ / | |_| | | |_| | | (_) | | | |
 \____/_| |_\_| \_|\___/\____/   \___/|_|\__|_|  \___/|_| |_|



font generated by:
http://patorjk.com/software/taag/#p=display&f=Doom&t=ChRIS%20Ultron

This module implements a simple comment-type class

"""

import  abc
import  json

import  os
import  sys
import  datetime

import  argparse
import  C_snode
import  message


sys.path.append('components/rikeripsum/rikeripsum')
sys.path.append('components/names')
import  rikeripsum
import  names


class comment(object):
    """
    This class implements a ChRIS style comment object.
    """

    __metaclass__   = abc.ABCMeta

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

    def __init__(self, **kwargs):

        self.contents           = C_snode.C_stree()

        self.d_REST = {
            'PUSH':  {
                'fullname':     'string',
                'timestamp':    'string',
                'comment':      'string'
            }
        }

        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True
        self._log               = message.Message()
        self._log._b_syslog     = True
        self.__name             = "comment"

        self.contents.cd('/')
        # self.contents.mkcd('contents')

    def contents_rikeripsumBuild(self, **kwargs):
        """
        Populate the contents with default noise.
        :return:
        """

        conversations = 1
        for key,val in kwargs.iteritems():
            if key == 'conversations':  conversations = int(val)

        c = self.contents
        c.cd('/')

        for loop in range(0, conversations):
            now                     = datetime.datetime.today()
            timeStamp               = now.strftime('%Y-%m-%d_%H:%M')

            c.mkcd(str(loop))
            c.touch('timestamp',    timeStamp)
            c.touch('fullname',     names.get_full_name())
            c.touch('comment',      rikeripsum.generate_paragraph())
            c.touch('REST', self.d_REST)
            c.cd('../')


    def __iter__(self):
        yield(self.contents)

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            --conversations <conversations>


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' is a simple "comment" object handler for ChRIS.

    ARGS

       --conversations <conversations>
       The number of simulated conversations to log.


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

if __name__ == "__main__":

    parser      = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-c', '--conversations',
        help    =   "The number of conversations to log.",
        dest    =   'conversations',
        action  =   'store',
        default =   10
    )

    args        = parser.parse_args()

    sample  = comment()
    sample.contents_rikeripsumBuild(conversations=args.conversations)

    print(sample.contents)

    print(json.dumps(dict(sample.contents.snode_root)))

