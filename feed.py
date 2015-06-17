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

import abc
import json

import C_snode

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
        self._name              = ""
        self._commentComponent  = {}
        self._dataviewComponet  = []
        self._noteComponent     = {}
        self._dateComponent     = []

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
        s = self.stree
        self._stree.mknode(['title', 'note', 'data', 'comment'])
        self._stree.cdnode('/data')
        self._stree.mknode(['visualView', 'fileView'])
        self._stree.cdnode('/comment')
        self._stree.touch("contents", "Hello, world.")

        for key, value in kwargs.iteritems():
            if key == 'desc':
                s.cd('/')
                s.touch('desc', value)
                s.cd('/comment')
                s.append('contents', ' Greetings and salutations from %s!' % value)

class FeedTree(object):
    '''
    Implements various operations on a collection (tree) of feed objects -- mostly access and
    search.
    '''

    def __init__(self, **kwargs):
        '''Construct a tree -- typically there is one tree per user

        '''
        self._feedTree  = C_snode.C_stree()

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

        return l_keys

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

    def feed_getFromObjectName(self, astr_feedObjectName, **kwargs):
        """Get a feed from its internal object name

        This returns a feed by directly returning the object
        in the snode tree with the given feedObjectName.

        Args:
            astr_feedObjectName (string): The Feed Object Name.

        Returns:
            Feed (Feed): The Feed itself if it exists, False if not.
        """

        b_returnAsDict = False

        for key,val in kwargs.iteritems():
            if key == "returnAsDict":   b_returnAsDict = val

        f = self._feedTree
        f.cd('/')
        if f.cd(astr_feedObjectName):
            if b_returnAsDict:
                return dict(f.cat('Feed'))
            else:
                return f.cat('Feed')
        else:
            return False

    def feed_getFromID(self, astr_feedID):
        """Get a feed from its internal ID string.

        :param astr_feedID: The ID of the Feed to get
        :return: False if not found, otherwise the Feed object
        """
        f = self._feedTree
        l_feed = f.lstr_lsnode('/')
        for feedNode in f.lstr_lsnode('/'):
            f.cd('/%s' % feedNode)
            str_ID = f.cat('ID')
            if str_ID == astr_feedID:
                return f.cat('Feed')
        return False

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
        f       = self._feedTree
        l_Feed  = ['Feed-1', 'Feed-2', 'Feed-3', 'Feed-4']
        l_FID   = ['000001', '000002', '000003', '000004']
        f.mknode(l_Feed)
        for node, id in zip(l_Feed, l_FID):
            f.cd('/%s' % node)
            f.touch("ID", id)
            f.touch("Feed", Feed_FS(
                                repo='Repo-%s' % node,
                                desc='Node Object Name: %s; Node FID: %s' % (node, id)))



if __name__ == "__main__":
    feed    = Feed_FS()
    T       = FeedTree_chrisUser()
    print(T._feedTree.snode_root)
