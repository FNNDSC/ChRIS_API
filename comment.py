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

sys.path.append('components/rikeripsum/rikeripsum')
sys.path.append('components/names')
import  rikeripsum
import  names


class comment(object):
    """
    This class implements a ChRIS style comment object.
    """

    __metaclass__   = abc.ABCMeta

    def __init__(self, **kwargs):

        self.contents   = ""

    def contents_rikeripsumBuild(self, **kwargs):
        """
        Populate the contents with default noise.
        :return:
        """

        conversations = 1
        for key,val in kwargs.iteritems():
            if key == 'conversations':  conversations = int(val)

        d_stamp = {}

        for loop in range(0, conversations):
            now                     = datetime.datetime.today()
            timeStamp               = now.strftime('%Y-%m-%d_%H:%M')

            d_stamp[loop] = [timeStamp, names.get_full_name(), rikeripsum.generate_paragraph()]

        self.contents = d_stamp


    def __iter__(self):
        yield('comments', self.contents)

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

    print(json.dumps(dict(sample)))

