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

import  C_snode
import  message

import  title
import  note
import  comment
import  data
import  plugin

class Feed(object):
    """The summary line for a class docstring should fit on one line.

    If the class has public attributes, they should be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section.

    Attributes:
      __metaclass__ (ABCMeta): Used for abstract classing.
      attr2 (list of str): Description of `attr2`.
      attr3 (int): Description of `attr3`.

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
        """Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        Note:
          Do not include the `self` parameter in the ``Args`` section.

        Args:
          param1 (str): Description of `param1`.
          param2 (list of str): Description of `param2`. Multiple
            lines are supported.
          param3 (int, optional): Description of `param3`, defaults to 0.

        """

        self._stree             = C_snode.C_stree()

        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True
        self._log               = message.Message()
        self._log._b_syslog     = True
        self.__name             = "Feed"

        self._name              = ""

    def __iter__(self):
        yield('Feed', dict(self._stree.snode_root))

    @abc.abstractmethod
    def create(self, **kwargs):
        """Create a new feed.

        A Feed "create" call. It requires an input source about which to
        create the feed. This input source is typically a reference to
        a location containing data.


        Args:
            **kwargs (user=): The user who is creating the feed

        Returns:
          True if successful, False otherwise.

        """

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

class Feed_FS(Feed):
    """The Feed_FS subclass implements Feed operations against a File System

    Feed operations create/read actual data from an underlying filesystem

    """

    def __init__(self, **kwargs):
        """Constructor.

        This essentially calls up the chain to the base constructor

        Args:
            astr_FeedRepo (string): A location on the file system that houses
                all the feeds.

        """
        Feed.__init__(self, **kwargs)
        self.create(**kwargs)

    def dataElement_create(self, **kwargs):
        """
        Creates the 'data' element container.

        :param kwargs: 'root' = <location>
        :return:
        """
        s                   = self._stree
        SeriesFilesCount    = 3
        str_root    = '/'
        for key, val in kwargs.iteritems():
            if key == 'root':               str_root            = val
            if key == 'SeriesFilesCount':   SeriesFilesCount    = val

        sample      = data.data()
        sample.contents_build_1(SeriesFilesCount = SeriesFilesCount)

        s.cd(str_root)
        l_data   = sample.contents.lstr_lsnode('/')
        if sample.contents.cd('/')['status']:
            for d in l_data:
                s.graft(sample.contents, '/%s' % d)

        return(dict(sample.contents.snode_root))

    def titleElement_create(self, **kwargs):
        """
        Creates the 'title' element container.

        :param kwargs: 'root' = <location>
        :return:
        """
        s = self._stree
        str_root    = '/'
        words       = 10
        for key, val in kwargs.iteritems():
            if key == 'root':   str_root    = val
            if key == 'words':  words       = val

        sample      = title.title()
        sample.contents_rikeripsumBuild(words = words)

        # self.debug("\n%s" % sample.contents)

        s.cd(str_root)
        s.touch("body", sample.contents.cat("body"))
        # s.graft(sample.contents, '/')

        return(dict(sample.contents))
        # return(dict(sample.contents.snode_root))


    def noteElement_create(self, **kwargs):
        """
        Creates the 'note' element container.

        :param kwargs: 'root' = <location>
        :return:
        """
        s = self._stree
        str_root    = '/'
        paragraphs  = 3
        for key, val in kwargs.iteritems():
            if key == 'root':           str_root        = val
            if key == 'paragraphs':     paragraphs      = val

        sample      = note.note()
        sample.contents_rikeripsumBuild(paragraphs=paragraphs)

        s.cd(str_root)
        s.touch("body", sample.contents.cat("body"))
        # s.graft(sample.contents, '/contents')

        return(dict(sample.contents))

    def commentElement_create(self, **kwargs):
        """
        Populate the comment component with simulated comments/conversations.
        :param kwargs:
        :return:
        """

        conversations = 1
        s = self._stree
        str_root    = '/'
        for key, val in kwargs.iteritems():
            if key == 'root':           str_root        = val
            if key == 'conversations':  conversations   = val

        sample     = comment.comment()
        sample.contents_rikeripsumBuild(conversations=conversations)

        s.cd(str_root)
        l_comment   = sample.contents.lstr_lsnode('/')
        if sample.contents.cd('/')['status']:
            for c in l_comment:
                s.graft(sample.contents, '/%s' % c)

        return(dict(sample.contents.snode_root))

    def create(self, **kwargs):
        """Create a new feed.

        A Feed "create" call. It requires an input source about which to
        create the feed. This input source is typically a reference to
        a location containing data.

        Creating a Feed entails building the directories and one-to-one
        objects:
            - title
            - note
            - data
            - comment


        Args:
          **kwargs (user=): The user creating the feed.
          **kwargs (str_ObjectID=): The string object reference used to access
            the Feed

        Returns:
          True if successful, False otherwise.

        """

        s = self._stree
        s.cd('/')
        s.mknode(['title', 'note', 'data', 'comment'])
        s.touch('status',       'Status of this Feed')
        s.touch('timestamp',    'DD-MM-YYYY HH:MM:SS')
        self.titleElement_create(   root='/title',      words=10)
        self.noteElement_create(    root='/note',       paragraphs=4)
        self.commentElement_create( root='/comment',    conversations=7)
        self.dataElement_create(    root='/data')

class FeedTree(object):
    '''
    Implements various operations on a collection (tree) of feed objects -- mostly access and
    search.
    '''

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
        '''Construct a tree -- typically there is one tree per user

        '''
        self._feedTree          = C_snode.C_stree()
        self.feed               = C_snode.C_stree()
        self.plugin             = plugin.Plugin_homePage()
        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True
        self._log               = message.Message()
        self._log._b_syslog     = True
        self.__name             = "FeedTree"

    def feed_existObjectName(self, astr_feedObjectName):
        """Check if a feed exists.

        Simply checks if a given feed with passed feedObjectName exists. The
        feedObjectName is the actual object record name in the snode tree.
        Searching on feed object name is much quicker than querying
        each feed for its ID.

        Args:
            astr_feedObjectName (string): The Feed Object Name.

        Returns:
            exists (boolean): True if exists, False if not.

        """
        f = self._feedTree
        f.cd('/')
        if f.cd(astr_feedObjectName):
            return True
        else:
            return False

    def feed_existFeedID(self, astr_feedID):
        """Check if a feed exists.

        Simply checks if a given feed with passed ID exists. This method needs
        to loop over all feeds and check their internal ID string.

        Args:
            astr_feedID (string): The Feed ID.

        Returns:
            exists (boolean): True if exists, False if not.

        """
        f = self._feedTree
        l_feed = f.lstr_lsnode('/')
        for feedNode in f.lstr_lsnode('/'):
            f.cd('/%s' % feedNode)
            str_ID = f.cat('ID')
            if str_ID == astr_feedID:
                return True
        return False

    def feed_GETURI(self, **kwargs):
        """
        The list of GET URIs at the current processing scope.
        :param kwargs:
        :return: The list of GET URIs at this scope referenced to current Feed context.
        """

        feedSpec    = ''
        str_path    = '/'
        for key,val in kwargs.iteritems():
            if key == 'feedSpec':   feedSpec    = val
            if key == 'path':       str_path    = val
        # f           = self.feed.DB
        f           = self.feed
        f.cd(str_path)
        str_path    = f.cwd()
        if str_path == '/': str_path = ''
        l_branch    = f.lstr_lsnode(str_path)
        l_URI       = []
        for node in l_branch:
            l_URI.append('Feeds/%s%s/%s' % (feedSpec, str_path, node))
        # Need to check this conditional?
        if not len(l_branch):
            for terminus in f.lsf(str_path):
                l_URI.append('Feeds/%s%s/%s' % (feedSpec, str_path, terminus))
        return l_URI

    def feeds_organize(self, **kwargs):
        """Basically "gets" the feed tree, possibly (re)organized according
        to kwargs.

        :param kwargs:
        :return:
        """
        b_returnAsDict  = False
        str_schema      = "default"

        for key,val in kwargs.iteritems():
            if key == "returnAsDict":   b_returnAsDict  = val
            if key == 'schema':         str_schema      = val

        l_keys = []

        # More logic needed here to possibly reorganize
        if str_schema == "default":
            # Generate a list of feed elements
            d_tree = dict(self._feedTree.snode_root)
            l_keys = d_tree.keys()

        l_URL = []
        for key in l_keys:
            l_URL.append('Feeds/NAME_%s' % (key))

        return {
            'status':   True,
            'payload':  {'list': l_keys},
            'URL_GET':  l_URL,
            'URL_POST': []
        }

    def feedTree_feedsGet(self, **kwargs):
        """
        Process the main feedTree (i.e. the tree that has all the Feeds.
        :param kwargs: schema='name'|'id' -- how to return the list of Feeds.
        :return: a list of "hits" in URI format
        """
        str_schema      = ''
        str_searchType  = 'name'
        b_status        = False

        for key,val in kwargs.iteritems():
            if key == 'schema':         str_schema          = val
            if key == 'searchType':     str_searchType      = val

        l_URI   = []
        l_keys  = []

        F           = self._feedTree
        if  F.cd('/feeds')['status']:
            if str_searchType.lower() == "name":
                # Generate a list of feed elements
                l_keys      = F.lstr_lsnode()
                l_URI       = ['Feeds/NAME_' + name for name in l_keys]
                b_status    = True
            if str_searchType.lower() == 'id':
                for feedNode in F.lstr_lsnode():
                    F.cd('/feeds/%s' % feedNode)
                    str_ID = F.cat('ID')
                    l_keys.append(str_ID)
                    l_URI.append('Feeds/ID_' + str_ID)
                b_status    = True

        return {
                'status':   b_status,
                'payload':  l_keys,
                'URL_GET':  l_URI
        }


    def feed_get(self, **kwargs):
        """
        Get a feed based on various criteria
        :param kwargs: searchType = 'name' | 'id', target = <target>
        :return: Feed conforming to search criteria
        """
        b_returnAsDict      = True

        str_searchType      = ''
        str_searchTarget    = ''
        str_pathInFeed      = ''
        str_schema          = ''

        ret_path            = []
        debugMessage        = None

        for key,val in kwargs.iteritems():
            if key == 'returnAsDict':   b_returnAsDict      = val
            if key == 'searchType':     str_searchType      = val
            if key == 'searchTarget':   str_searchTarget    = val
            if key == 'pathInFeed':     str_pathInFeed      = val
            if key == 'schema':         str_schema          = val

        # First get the feed itself from the tree of Feeds...
        F               = self._feedTree
        F.cd('/feeds')
        ret_status      = False
        ret_feed        = {}
        str_feedSpec    = '%s_%s' % (str_searchType.upper(), str_searchTarget)

        if not len(str_searchType) or not len(str_searchTarget) or str_searchTarget == '*':
            ret_feeds       = self.feedTree_feedsGet(searchType = str_searchType, schema = str_schema)
            debugMessage    = "Search for '%s' on type '%s'" % (str_searchTarget, str_searchType)
            ret_status      = ret_feeds['status']
            l_URL_get       = ret_feeds['URL_GET']
            ret_payload     = ret_feeds['payload']
        else:
            self.feed   = C_snode.C_stree()
            s           = self.feed
            if str_searchType.lower() == 'name':
                if F.cd(str_searchTarget)['status']:
                    Froot = F.cwd()
                    # s.graft(F, '%s/'      % F.cwd())
                    s.graft(F, '%s/title'   % Froot)
                    s.graft(F, '%s/note'    % Froot)
                    s.graft(F, '%s/data'    % Froot)
                    s.graft(F, '%s/comment' % Froot)
                    ret_status  = True
                    ret_feed    = s
                    s.tree_metaData_print(False)
            if str_searchType.lower() == 'id':
                for feedNode in f.lstr_lsnode('/'):
                    if F.cd('/feeds/%s' % feedNode)['status']:
                        if str_searchTarget == F.cat('ID'):
                            ret_status  = True
                            # s.graft(F, '%s/'      % F.cwd())
                            s.graft(F, '%s/title'   % Froot)
                            s.graft(F, '%s/note'    % Froot)
                            s.graft(F, '%s/data'    % Froot)
                            s.graft(F, '%s/comment' % Froot)
                            ret_feed    = s
                            break

            # and now, check for any paths in the tree of this Feed
            b_returnTree    = True
            if len(str_pathInFeed) and str_pathInFeed != '/':
                debugMessage    = 'str_pathInFeed = %s' % str_pathInFeed
                ret             = s.cd(str_pathInFeed)
                if ret['status']:
                    # We are retrieving a directory
                    ret_status  = ret['status']
                    ret_path    = ret['path']
                    subTree     = C_snode.C_stree()
                    if subTree.cd('/')['status']:
                        subTree.graft(s, str_pathInFeed)
                        ret_feed    = subTree
                else:
                    b_returnTree = False
                    # Check if we are in fact retrieving a "file"
                    l_p         = str_pathInFeed.split('/')
                    str_dirUp   = '/'.join(l_p[0:-1])
                    ret         = s.cd(str_dirUp)
                    if ret['status']:
                        debugMessage    = '../ = %s, file = %s' % (str_dirUp, l_p[-1])
                        ret_status      = ret['status']
                        ret_path        = ret['path']
                        str_fileName    = l_p[-1]
                        ret_feed        = {str_fileName: s.cat(l_p[-1])}
                        self.debug('Returning file contents in payload: "%s"' % ret_feed)
            if b_returnAsDict and b_returnTree:
                ret_feed = dict(ret_feed.snode_root)
            ret_payload     = ret_feed
            l_URL_get       = self.feed_GETURI(feedSpec = str_feedSpec, path = str_pathInFeed)

        return {
                'debug':        debugMessage,
                'path':         str_searchTarget + str_pathInFeed,
                'pathInFeed':   ret_path,
                'status':       ret_status,
                'payload':      ret_payload,
                'URL_get':      l_URL_get,
                'URL_post':     []
                }

class FeedTree_chrisUser(FeedTree):
    '''
    A Feed Tree for a hypothetical user on the ChRIS system. Each user will
    have identical trees under this scenario.
    '''

    def __init__(self, **kwargs):
        '''
        Build the tree.

        :return:
        '''
        FeedTree.__init__(self, **kwargs)
        F       = self._feedTree
        l_Feed  = ['Feed-1', 'Feed-2', 'Feed-3', 'Feed-4']
        l_FID   = ['000001', '000002', '000003', '000004']
        F.cd('/')
        F.mkcd('feeds')
        F.mknode(l_Feed)
        for node, id in zip(l_Feed, l_FID):
            F.cd('/feeds/%s' % node)
            F.touch("ID", id)
            # self.debug(f)
            singleFeed  = Feed_FS(
                name    = node,
                id      = id
            )
            s = singleFeed._stree
            # Graft explicit parts of this singleFeed (s) to the tree of
            # all Feeds (F) of this user, i.e.
            #   cd F:/feeds/Feed-<ID>
            #   ln -s s:/note .
            #   ln -s s:/title .
            #       ... etc ...
            F.graft(s, '/note')
            F.graft(s, '/title')
            F.graft(s, '/comment')
            F.graft(s, '/data')
        F.cd('/feeds')
        F.tree_metaData_print(False)
        # self.debug(F)

if __name__ == "__main__":
    feed    = Feed_FS()
    T       = FeedTree_chrisUser()
    print(T._feedTree.snode_root)

    print(T.plugin.getList())
    print(T.plugin.set('file_browser'))
    print(T.plugin.run())
