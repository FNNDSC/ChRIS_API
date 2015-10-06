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

ChRIS_SM

'ChRIS_SM' is the 'ChRIS Simulated Machine' or 'ChRIS Simple Machine'
or ... :-) -- basically it is a simplified infrastructure for
developing / testing the API between the front end view and various
back-end services.

Essentially, 'ChRIS_SM' simulates the API behaviour on a synthetic
instance of ChRIS consisting of a single user (with password) and
a few feeds containing different data, views, results, notes, etc.


"""

from __future__ import print_function

import  abc
import  hashlib
import  argparse
import  os
import  sys
import  datetime
import  json

import  error

import  C_snode
import  message
import  feed
import  ChRIS_RPCAPI
import  ChRIS_RESTAPI
import  serverInfo

class ChRIS_SMUserDB(object):
    """A "DB" of users and passwords.

    """

    def DB_build(self):
        s               = self._stree
        s.cd('/')
        s.mkcd('users')
        s.mkcd('chris')
        s.touch("userName",     "chris")
        s.touch("fullName",     "ChRIS User")
        s.touch("passwd",       "chris1234")
        # s.mknode(['feed'])
        # The 'feeds' node is attached when the user is authenticated.
        s.mkcd('login')

    def user_checkAPIcanCall(self, **kwargs):
        """

        Authenticates (or not) the current call to the API.

        Need to pay attention to login call!
        """
        astr_user               = ""
        astr_sessionHash        = ""
        for key, value in kwargs.iteritems():
            if key == 'user':           astr_user           = value.translate(None, '\'\"')
            if key == 'hash':           astr_sessionHash    = value.translate(None, '\'\"')
        try:
            d_currentSessionInfo    = json.load(open("%s-login.json" % astr_user))
        except:
            return {'status':   False,
                    'code':     1,
                    'message':  'No login for user %s detected.' % astr_user}
        if not d_currentSessionInfo['loginStatus']:         return False
        str_sessionToken        = d_currentSessionInfo['sessionToken']
        str_sessionSeed         = d_currentSessionInfo['sessionSeed']
        str_hashInput           = '%s%s' % (str_sessionToken, str_sessionSeed)
        str_sessionHash         = self._md5.md5(str_hashInput).hexdigest()
        b_OK                    = (str_sessionHash == astr_sessionHash)
        if b_OK:
            d_currentSessionInfo['sessionToken']    = str_hashInput
            d_currentSessionInfo['sessionSeed']     = int(str_sessionSeed) + 1
            str_message         = "User '%s can call API." % astr_user
        else:
            str_message         = "User '%s' can not call API." % astr_user
        d_currentSessionInfo['APIcanCall']      = b_OK
        self.login_writePersistent( sessionInfo = d_currentSessionInfo,
                      #              user        = astr_user,
                                    **kwargs)
        self.user_attachFeedTree(   user        = astr_user)
        self.chris.homePage   = self._userTree
        return {'status':   b_OK,
                'code':     0,
                'message':  str_message}

    def user_getAuthInfo(self, **kwargs):
        """Gets the DB auth info of the user
        """
        # s                   = self._stree

        for key,value in kwargs.iteritems():
            if key == 'user':           str_user            = value.translate(None, '\'\"')
        try:
            d_authSession = json.load(open("%s-login.json" % str_user))
        except:
            return {'status':   False,
                    'code':     2,
                    'message':  'No login for user %s detected.' % str_user}
        rd_authInfo     = {}
        rd_authInfo['user']             = str_user
        rd_authInfo['sessionStatus']    = d_authSession['sessionStatus']
        rd_authInfo['sessionSeed']      = d_authSession['sessionSeed']
        return {'status':   True,
                'authInfo': rd_authInfo,
                'message':  "Authorization info for user '%s'." % str_user}

    def login_writePersistent(self, **kwargs):
        """Write persistent information about login to disk"""

        dict_sessionInfo    = {'login': 'unspecified'}
        str_user            = 'nobody'
        for key,value in kwargs.iteritems():
            if key == 'sessionInfo':    dict_sessionInfo    = value
            if key == 'user':           str_user            = value.translate(None, '\'\"')

        json.dump(dict_sessionInfo, open("%s-login.json" % str_user, "w"))

    def user_attachFeedTree(self, **kwargs):
        """Attach the feed tree for this user"""
        for key, val in kwargs.iteritems():
            if key == 'user':   astr_user   = val.translate(None, '\'\"')
        # Get the user's feed tree structure -- we only need to
        # do this *ONCE* per session/replay.
        if not self._userTree:
            feedTree                = feed.FeedTree_chrisUser()
            # and attach it to the stree of this object
            self._stree.cd('/users/%s' % astr_user)
            # self._stree.touch('tree', feedTree)
            self._stree.graft(feedTree._feedTree, '/')
            self._userTree          = feedTree

    def user_logout(self, **kwargs):
        """
        Log the current user out -- essentially remove the persistent
        JSON login file.
        """
        astr_user   = 'nobody'
        for key,val in kwargs.iteritems():
            if key == 'user':   astr_user   = val.translate(None, '\'\"')
        now                     = datetime.datetime.today()
        logoutStamp             = now.strftime('%Y-%m-%d_%H:%M:%S.%f')
        try:
            os.remove('%s-login.json' % astr_user)
        except:
            return {'status':   False,
                    'message':  'logout failed for %s at %s -- no prior login detected.' %
                                (astr_user, logoutStamp)}
        return {
                'status': True,
                'payload': {
                    'message':  "Successfully logged '%s' out at %s." % (astr_user, logoutStamp)
                    }
                }

    def user_login(self, **kwargs):
        """Log a user in.

        This method "logs" a user in, using the passwd.

        The login process writes a json object to persistent
        storage -- this object is read each time an API
        call is made, allowing for "stateless" post-login
        events.

        Args (kwargs):
            user (string): The user to login.
            passwd (string): The user passwd.

        Returns:
            adict (dictionary): dictionary of login and session info.

        """

        for key, val in kwargs.iteritems():
            if key == 'user':   astr_user   = val.translate(None, '\'\"')
            if key == 'passwd': astr_passwd = val.translate(None, '\'\"')
        s = self._stree
        s.cdnode('/users')

        # login/session/canCall structure
        ret                     = {}
        now                     = datetime.datetime.today()
        ret['loginTimeStamp']   = now.strftime('%Y-%m-%d_%H:%M:%S.%f')
        ret['loginStatus']      = False
        ret['loginMessage']     = ""
        ret['logoutMessage']    = ""
        ret['sessionStatus']    = False
        ret['sessionToken']     = "ABCDEF"
        ret['sessionSeed']      = "1"
        ret['APIcanCall']       = False

        s = self._stree
        s.cdnode('/users')
        if not s.cdnode(astr_user):
            ret['loginMessage']     = 'User %s not found in database.' % astr_user
        else:
            if s.cat('passwd') != astr_passwd:
                ret['loginMessage']     = 'Incorrect password.'
            else:
                ret['loginStatus']      = True
                ret['loginMessage']     = 'Successful login for user %s at %s.' % (astr_user, datetime.datetime.now())
                ret['logoutMessage']    = ""
                ret['sessionStatus']    = True
                ret['sessionToken']     = "ABCDEF"
                ret['sessionSeed']      = "1"

                self.debug("in login... writing persistent for user '%s'.\n" % astr_user)
                # print(ret)
                self.login_writePersistent( sessionInfo = ret,
                                            user        = astr_user)
        return {
                'status':   True,
                'payload':  {
                                'message':      'login credentials parsed',
                                'loginDetail':   ret
                            }
                }

    def __init__(self, **kwargs):
        # This class contains a reference back to the chris parent object that
        # contains this DB
        self.chris      = None
        for key,value in kwargs.iteritems():
            if key == "chris":  self.chris  = value
        self.debug              = message.Message(logTo = "./debug.log")
        self.debug._b_syslog    = True
        self._md5               = hashlib
        self._stree             = C_snode.C_stree()
        self._userTree          = None
        self.DB_build()

class ChRIS_SMCore(object):
    """The ChRIS_SM core

    """

    __metaclass__   = abc.ABCMeta

    def __init__(self, **kwargs):
        # This class contains a reference back to the chris parent object that
        # contains this Core
        self.chris      = None
        for key,value in kwargs.iteritems():
            if key == "chris":  self.chris  = value
        self.s_tree     = C_snode.C_stree()
        self._userDB    = ChRIS_SMUserDB(chris = self.chris)

    def login(self, **kwargs):
        return(self._userDB.user_login(**kwargs))

    def logout(self, **kwargs):
        return(self._userDB.user_logout(**kwargs))


class ChRIS_SM(object):
    """The ChRIS Simulated Machine


    """

    #
    # Class member variables -- if declared here are shared
    # across all instances of this class
    #
    _dictErr = {
        'subjectSpecFail'   : {
            'action'        : 'examining command line arguments, ',
            'error'         : 'it seems that no subjects were specified.',
            'exitCode'      : 10},
        'no_apiCall'   : {
            'action'        : 'examining command line arguemnts, ',
            'error'         : 'it seems that the required --apiCall is missing.',
            'exitCode'      : 11},
        'no_stateFile'   : {
            'action'        : 'examining command line arguemnts, ',
            'error'         : 'it seems that the required --stateFile is missing.',
            'exitCode'      : 12},
        'no_stateFileExist': {
            'action'        : 'checking on the <stateFile>, ',
            'error'         : 'a system error was encountered. Does the <stateFile> exist?',
            'exitCode'      : 20},
        'no_stateFileAccess': {
            'action'        : 'attempting to access the <stateFile>, ',
            'error'         : 'a system error was encountered. Does the <stateFile> exist?',
            'exitCode'      : 21},
        'no_authModuleSpec' : {
            'action'        : 'attempting to parse the API call, ',
            'error'         : 'the auth module was not specified',
            'exitCode'      : 30},
    }

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
        """The CHRIS_SM constructor.

        """

        self.__name                     = "ChRIS_SM"

        self._feedTree                  = C_snode.C_stree()
        self._SMCore                    = ChRIS_SMCore(chris = self)
        self._name                      = ""
        self._log                       = message.Message()
        self._log.tee(True)
        self._log.syslog(True)

        # Convenience members
        self.DB                         = self._SMCore._userDB

        # The "homePage" is essentially the user's feedTree object, created
        # in the underlying DB module.
        self.homePage                   = None

    @property
    def feedTree(self):
        """STree Getter"""
        return self._feedTree

    @feedTree.setter
    def feedTree(self, value):
        """STree Getter"""
        self._feedTree = value

    def login(self, **kwargs):
        loginStatus     = self._SMCore.login(**kwargs)
        return(loginStatus)

    def logout(self, **kwargs):
        logoutStatus     = self._SMCore.logout(**kwargs)
        return(logoutStatus)

    def feed_nextID(self):
        """Find the next ID in the Feed database

        Returns:
            nextID (string): The next ID to use for a Feed.
        """

class ChRIS_SM_RPC(ChRIS_SM):
    """ The ChRIS_SM_RPC subclass implements a ChRIS_SM using an RPC type
        API paradigm.
    """

    def __init__(self, **kwargs):
        """Constructor.

        This essentially calls up the chain to the base constructor.

        Also, set the 'API' field of the class to the RPC handler.

        Args:

        """
        ChRIS_SM.__init__(self, **kwargs)

        self.API    = ChRIS_RPCAPI.ChRIS_RPCAPI(chris = self, **kwargs)

class ChRIS_SM_REST(ChRIS_SM):
    """ The ChRIS_SM_REST subclass implements a ChRIS_SM using a REST type
        API paradigm.
    """

    def __init__(self, **kwargs):
        """Constructor.

        This essentially calls up the chain to the base constructor.

        Also, set the 'API' field of the class to the RESTAPI handler.

        Args:

        """
        ChRIS_SM.__init__(self, **kwargs)

        # str_authority   = ""
        # for key,val in kwargs.iteritems():
        #     if key == 'authority':      str_authority   = val

        self.API        = ChRIS_RESTAPI.ChRIS_RESTAPI(chris = self, **kwargs)

class ChRIS_authenticate(object):
    """The ChRIS_authenticate object is responsible for authenticated valid
        access to the API

        This method is the main "gatekeeper" between external API
        calls and actual methods in ChRIS system. It serves as a
        central entry point for each call so that user token
        authentication can be verified, as well as any additional
        parsing on the actual attempt to exec code.

        Since this method calls the passed "function" without regard for
        scope, the called object must actually exist at the scope at which
        this auth is being wrapped.

    """
    _dictErr = {
        'no_loginFound'     : {
            'action'        : 'checking on API call, ',
            'error'         : 'it seems that the user has not logged in.',
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

    def __init__(self, achris_instance, aself_name):
        """Constructor.

        Builds a ChRIS_authenticate object. This object acts as a functor that calls
        into a ChRIS object after checking the authentication of the caller.

        Args:
            achris_instance (ChRIS):    the chris instance to authenticate against
            aself_name (string):        this object's string name
        """

        self._log                       = message.Message()
        self._log._b_syslog             = True
        self.__name                     = "ChRIS_authenticate"

        self.chris              = achris_instance
        self._name              = aself_name
        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True

    def __call__(self, f, **kwargs):
        """Call the object/method

        This functor actually wraps around the call, and is the main entry point to
        calling ANYTHING from ChRIS. It is here where the authentication of the
        caller/hash is verified before executing the actual object.method call

        Args:
            f (object.method):  The object.method to call.

        Returns:
            Whatever is returned by the call is returned back.
        """
        db = self.chris._SMCore._userDB

        d_ret = db.user_checkAPIcanCall(**kwargs)
        if not d_ret['status'] and d_ret['code'] == 1:
            error.fatal(self, 'no_loginFound')
        return f()


def warn(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            [--REST | --RPC --stateFile <stateFile>]       \\
                            [--authority <clientSideAuthority>]            \\
                            --APIcall <APIcall>


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' simulates a ChRIS machine, and specifically the
        web service interface to the machine.

    ARGS

       --authority <clientSideAuthority>
       The RFC 3986 URI authority. A string like "10.15.23.17:5555".

       --REST
       Use a REST API paradigm.

       --RPC --stateFile <stateFile>
       Use an RPC API paradigm. In this case, a <stateFile> is also
       required to track session history.

       API calls are logged to <stateFile> and replayed back when
       ChRIS_SM is instantiated. In this manner the machine state
       can be rebuilt. The current <APIcall> is appended to the
       <stateFile>.

       --APIcall <ACPIcall> (required)
       The actual API call to make, either REST or RPC type.

    NOTE

       Do not mix REST and RPC type calls in the same session, otherwise
       behaviour might be unpredictable / undefined.

    EXAMPLES


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description


if __name__ == "__main__":
    """Simulated session interacting with the ChRIS_SM

    Once logged in, the client and service use a hash to authenticate.
    Essentially, on first login, the system returns a token to the client
    and an initial seed. The client hashes the token and seed when
    communicating with the service. For each communication, the service
    returns a new seed that must be used in the next comms.

    State is preserved in the SM by tracking all "api" calls  to a
    stateful file, and replaying them in order on subsequent runs.
    The current "api" call is appended to this stateful file.

    """

    if len(sys.argv) == 1:
        print(synopsis())
        sys.exit(1)

    parser      = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '--REST',
        action  =   'store_true',
        dest    =   'b_REST',
        help    =   'Specify REST API paradigm.',
        default =   False
    )
    parser.add_argument(
        '--RPC',
        action  =   'store_true',
        dest    =   'b_RPC',
        help    =   'Specify RPC API paradigm.',
        default =   False
    )
    parser.add_argument(
        '-s', '--stateFile',
        help    =   "The <stateFile> keeps track of ChRIS state for RPC-type calling regimes.",
        dest    =   'str_stateFileName',
        action  =   'store',
        default =   "<void>"
    )
    parser.add_argument(
        '-a', '--APIcall',
        help    =   "The actual API call to make.",
        dest    =   'str_apiCall',
        action  =   'store',
        default =   "<void>"
    )
    parser.add_argument(
        '--authority',
        help    =   "The URI authority from the client perspective.",
        dest    =   'str_authority',
        action  =   'store',
        default =   ""
    )

    args            = parser.parse_args()

    if args.b_RPC:
        chris       = ChRIS_SM_RPC(
                            stateFile   = args.str_stateFileName
                      )
    if args.b_REST:
        chris       = ChRIS_SM_REST(
                            authority   = args.str_authority
                      )
    chris.API.auth  = ChRIS_authenticate(chris, 'auth')

    # Call the API and print the JSON formatted return.
    print(
        json.dumps(
            chris.API(
                APIcall = args.str_apiCall
            )
        )
    )

