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

import  C_snode
import  message

import  title
import  note
import  comment
import  data
import  plugin
import  branch

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
        self.within             = None                      # The feed or plugin this branch is within

        for key, val in kwargs.iteritems():
            if key == 'within': self.within     = val

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
        b_internalsCreate   = True
        Feed.__init__(self, **kwargs)
        for key, val in kwargs.iteritems():
            if key == 'internalsCreate':    b_internalsCreate   = val

        if b_internalsCreate: self.create(**kwargs)

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
        # sample.dataComponent_pluginRun()

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
        s.touch("REST", sample.contents.cat("REST"))
        # s.graft(sample.contents, '/')

        # return(dict(sample.contents))
        return(dict(sample.contents.snode_root))


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
        s.touch("REST", sample.contents.cat("REST"))
        # s.graft(sample.contents, '/contents')

        # return(dict(sample.contents))
        return(dict(sample.contents.snode_root))

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
    """
    Implements various operations on a collection (tree) of feed objects -- mostly access and
    search.
    """

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
        """Construct a tree -- typically there is one tree per user

        """
        self._feedTree          = C_snode.C_stree()
        self.feed               = C_snode.C_stree()

        self.BR                 = branch.BranchTree(within = self)

        self.plugin             = plugin.Plugin_homePage()
        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True
        self._log               = message.Message()
        self._log._b_syslog     = True
        self.__name             = "FeedTree"


class FeedTree_chrisUser(FeedTree):
    """
    A Feed Tree for a hypothetical user on the ChRIS system. Each user will
    have identical trees under this scenario.
    """

    def __init__(self, **kwargs):
        """
        Build the tree.

        :return:
        """
        FeedTree.__init__(self, **kwargs)

        b_constructAllFeeds    = True
        for key,val in kwargs.iteritems():
            if key == 'constructAllFeeds': b_constructAllFeeds    = val

        if b_constructAllFeeds:
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
                singleBranch  = Feed_FS(
                    name    = node,
                    id      = id
                )
                s = singleBranch._stree
                # Graft explicit parts of this singleBranch (s) to the tree of
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
