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

This module implements a server side logical branch/Tree interactor.

"""

import  abc
import  json
import  sys
import  datetime

import  C_snode
import  message
import  feed

import  title
import  note
import  comment
import  data
import  plugin


class BranchTree(object):
    """
    Implements various operations on a collection (tree) of branch objects
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
        self._branchTree        = C_snode.C_stree()         # This is the WHOLE tree
        self.branch             = C_snode.C_stree()         # This is a single branch
        self.debug              = message.Message(logTo = './debug.log')
        self.debug._b_syslog    = True
        self._log               = message.Message()
        self._log._b_syslog     = True
        self.__name             = "BranchTree"
        self.within             = None                      # The feed or plugin this branch is within

        for key, val in kwargs.iteritems():
            if key == 'within': self.within     = val


    def branch_existObjectName(self, astr_branchObjectName):
        """Check if a branch exists.

        Simply checks if a given branch with passed branchObjectName exists. The
        branchObjectName is the actual object record name in the snode tree.
        Searching on branch object name is much quicker than querying
        each branch for its ID.

        Args:
            astr_branchObjectName (string): The branch Object Name.

        Returns:
            exists (boolean): True if exists, False if not.

        """
        f = self._branchTree
        f.cd('/')
        if f.cd(astr_branchObjectName):
            return True
        else:
            return False

    def branch_existFeedID(self, astr_branchID):
        """Check if a branch exists.

        Simply checks if a given branch with passed ID exists. This method needs
        to loop over all branches and check their internal ID string.

        Args:
            astr_branchID (string): The Feed ID.

        Returns:
            exists (boolean): True if exists, False if not.

        """
        f = self._branchTree
        for branchNode in f.lstr_lsnode('/'):
            f.cd('/%s' % branchNode)
            str_ID = f.cat('ID')
            if str_ID == astr_branchID:
                return True
        return False

    def branch_GETURI(self, **kwargs):
        """
        The list of GET URIs at the current processing scope.
        :param kwargs:
        :return: The list of GET URIs at this scope referenced to current Feed context.
        """

        str_branchSpec  = ''
        str_ROOT        = ''
        str_path        = '/'
        for key,val in kwargs.iteritems():
            if key == 'ROOT':           str_ROOT            = val
            if key == 'branchSpec':     str_branchSpec      = val
            if key == 'path':           str_path            = val
        f           = self.branch
        f.cd(str_path)
        str_path    = f.cwd()
        if str_path == '/': str_path = ''
        l_branch    = f.lstr_lsnode(str_path)
        l_files     = f.lsf(str_path)
        l_elements  = l_branch + l_files
        l_URI       = []
        for node in l_elements:
            l_URI.append('%s/%s%s/%s' %     (str_ROOT, str_branchSpec, str_path, node))
        # Need to check this conditional?
        if not len(l_elements):
            for terminus in f.lsf(str_path):
                l_URI.append('%s/%s%s/%s' % (str_ROOT, str_branchSpec, str_path, terminus))
        return l_URI

    def branches_organize(self, **kwargs):
        """Basically "gets" the branch tree, possibly (re)organized according
        to kwargs.

        :param kwargs:
        :return:
        """
        b_returnAsDict  = False
        str_schema      = "default"
        str_ROOT        = ''

        for key,val in kwargs.iteritems():
            if key == 'ROOT':           str_ROOT        = val
            if key == "returnAsDict":   b_returnAsDict  = val
            if key == 'schema':         str_schema      = val

        l_keys = []

        # More logic needed here to possibly reorganize
        if str_schema == "default":
            # Generate a list of branch elements
            d_tree = dict(self._branchTree.snode_root)
            l_keys = d_tree.keys()

        l_URL = []
        for key in l_keys:
            l_URL.append('%s/NAME__%s' % (str_ROOT, key))

        return {
            'status':   True,
            'payload':  {'list': l_keys},
            'URL_GET':  l_URL,
            'URL_POST': []
        }

    def branch_branchList_fromTreeGet(self, **kwargs):
        """
        Process the main branchTree (i.e. the tree that has all the Feeds.
        :param kwargs: schema='name'|'id' -- how to return the list of Feeds.
        :return: a list of "hits" in URI format
        """
        str_searchType      = 'name'
        d_ret               = {
            'debug':        'branch_branchList_fromTreeGet(): ',
            'status':       False,
            'payload':      {},
            'URL_get':      []
        }

        for key,val in kwargs.iteritems():
            if key == 'searchType':     str_searchType      = val
            if key == 'd_ret':          d_ret               = val

        str_ROOT        = d_ret['ROOT']
        d_ret['debug']  = 'branch_branchList_fromTreeGet(): '
        l_URI   = []
        l_keys  = []

        F           = self._branchTree
        if F.cd('/%s' % str_ROOT.lower())['status']:
            if str_searchType.lower() == "name":
                # Generate a list of branch elements
                l_keys          = F.lstr_lsnode()
                l_URI           = [str_ROOT + '/NAME__' + name for name in l_keys]
                d_ret['status'] = True
            if str_searchType.lower() == 'id':
                for branchNode in F.lstr_lsnode():
                    F.cd('/%s/%s' % (str_ROOT.lower(), branchNode))
                    str_ID = F.cat('ID')
                    l_keys.append(str_ID)
                    l_URI.append(str_ROOT + '/ID__' + str_ID)
                d_ret['status'] = True
        d_ret['payload']    = l_keys
        d_ret['URL_get']    = l_URI

        return d_ret

    def branch_singleBranch_fromTreeGet(self, **kwargs):
        """
        Graft a single target branch from the branch tree to internal storage.

        This basically just "links" the branch to be processed to a convenience
        variable.

        :return:
        d_ret:      dictionary      various values
        """

        # Initialize the d_ret return dictionary
        d_ret               = {
            'branch':       None,
            'status':       False,
            'payload':      {},
            'URL_get':      []
        }

        for key,val in kwargs.iteritems():
            if key == 'searchType':     str_searchType      = val
            if key == 'searchTarget':   str_searchTarget    = val
            if key == 'schema':         str_schema          = val
            if key == 'd_ret':          d_ret               = val

        str_ROOT        = d_ret['ROOT']
        d_ret['debug']  = 'branch_singleBranch_fromTreeGet():'
        F               = self._branchTree
        F.cd('/%s' % str_ROOT.lower())

        self.branch   = C_snode.C_stree()
        s           = self.branch
        if d_ret['ROOT'] == 'Feeds':
            if str_searchType.lower() == 'name':
                if F.cd(str_searchTarget)['status']:
                    Froot = F.cwd()
                    s.graft(F, '%s/'      % Froot)
                    # s.graft(F, '%s/title'   % Froot)
                    # s.graft(F, '%s/note'    % Froot)
                    # s.graft(F, '%s/data'    % Froot)
                    # s.graft(F, '%s/comment' % Froot)
                    d_ret['status'] = True
                    d_ret['branch']   = s
                    s.tree_metaData_print(False)
            if str_searchType.lower() == 'id':
                for branchNode in f.lstr_lsnode('/'):
                    if F.cd('/feeds/%s' % branchNode)['status']:
                        if str_searchTarget == F.cat('ID'):
                            d_ret['status'] = True
                            # s.graft(F, '%s/'      % F.cwd())
                            s.graft(F, '%s/title'   % Froot)
                            s.graft(F, '%s/note'    % Froot)
                            s.graft(F, '%s/data'    % Froot)
                            s.graft(F, '%s/comment' % Froot)
                            d_ret['branch']   = s
                            break
        if d_ret['ROOT'] == 'Plugins':
            if str_searchType.lower() == 'name':
                if F.cd(str_searchTarget)['status']:
                    Froot = F.cwd()
                    # s.graft(F, '%s/'      % F.cwd())
                    s.graft(F, '%s/'        % Froot)
                    d_ret['status'] = True
                    d_ret['branch']   = s
                    s.tree_metaData_print(False)
        return d_ret

    def branch_singleBranch_process(self, **kwargs):
        """
        Assuming a branch has been grafted from the tree space, process this
        branch's components.

        :return:
        """

        d_ret               = {
            'branch':       None,
            'debug':        'branch_singleBranch_process(): ',
            'path':         '',
            'status':       False,
            'payload':      {},
            'URL_get':      []
        }

        for key,val in kwargs.iteritems():
            if key == 'VERB':           str_VERB            = val
            if key == 'pathInBranch':   str_pathInBranch    = val
            if key == 'd_ret':          d_ret               = val

        str_ROOT                = d_ret['ROOT']
        d_ret['b_returnTree']   = True
        d_ret['debug']         += 'str_pathInBranch = %s ' % str_pathInBranch
        s                       = d_ret['branch']
        d_cd                    = s.cd(str_pathInBranch)
        if d_cd['status']:
            # We are retrieving a directory
            d_ret['status']     = d_cd['status']
            d_ret['pathInBranch'] = d_cd['path']
            subTree             = C_snode.C_stree()
            if subTree.cd('/')['status']:
                subTree.graft(s, str_pathInBranch)
                d_ret['branch']   = subTree
        else:
            d_ret['b_returnTree']   = False
            # Check if we are in fact processing a "file"
            l_p                     = str_pathInBranch.split('/')
            str_dirUp               = '/'.join(l_p[0:-1])
            d_cd                    = s.cd(str_dirUp)
            if d_cd['status']:
                d_ret['debug']     += '../ = %s, file = %s' % (str_dirUp, l_p[-1])
                d_ret['status']     = d_cd['status']
                d_ret['pathInBranch'] = d_cd['path']
                str_fileName        = l_p[-1]
                if str_VERB != "GET":
                    self.branch_singleBranch_VERBprocess(**kwargs)
                    self.debug('%s\n' % l_p)
                contents            = s.cat(l_p[-1])
                if not contents:
                    d_ret['branch']   = {str_fileName: ''}
                else:
                    d_ret['branch']   = {str_fileName: contents}
                self.debug('Returning file contents in payload: "%s"\n' % d_ret)
        d_ret['payload'] = d_ret['branch']
        return d_ret

    # This method is the only point of contact between the simulated machine and the internal
    # data space and the external REST call.
    #
    # Processing of specific REST-like verbs are processed by appropriately named "sub" functions.
    def branch_singleBranch_VERBprocess(self, **kwargs):
        """
        Process specific cases of REST VERBS

        :return:
        """

        d_ret   = {
            'debug':    'branch_singleBranch_VERBprocess(): '
        }

        for key,val in kwargs.iteritems():
            if key == 'ROOT':           str_ROOT            = val
            if key == 'd_ret':          d_ret               = val

        str_ROOT        = d_ret['ROOT']

        # This signals the client to 'refresh' the display since POST operations
        # change GUI elements
        d_ret['refreshREST']    = True

        if d_ret['VERB'] == 'POST':
            self.debug('In branch_singleBranch_VERBprocess...\n')
            with open(d_ret['payloadFile']) as jf:
                d_payload   = json.load(jf)
                self.debug('Payload: %s\n' % d_payload)
                s = d_ret['branch']
                self.debug('location in branch tree: %s\n' % s.pwd() )
                action      = d_payload['POST']['action']

                # find the 'object' key (i.e. the key other than 'action')
                for key in d_payload['POST'].keys():
                    if key != 'action':
                        str_nodeType = key
                str_nodeName    = d_payload['POST'][str_nodeType].keys()[0]
                str_contents    = d_payload['POST'][str_nodeType][str_nodeName]
                d_ret['nodeName']   = str_nodeName
                d_ret['contents']   = str_contents

                if action == 'post' and str_nodeType == 'file':
                    self.branch_singleBranch_POSTprocess(   d_ret = d_ret)

                if action == 'del':
                    self.branch_singleBranch_DELprocess(    d_ret = d_ret)

                if action == 'clear':
                    self.branch_singleBranch_CLEARprocess(  d_ret = d_ret)

                if action == 'run':
                    self.branch_singleBranch_RUNprocess(    d_ret = d_ret)

    def branch_singleBranch_POSTprocess(self, **kwargs):
        """
        Process the "run" command from client

        :return:
        """
        d_ret   = {
            'debug':    'branch_singleBranch_POSTprocess(): '
        }

        for key,val in kwargs.iteritems():
            if key == 'd_ret':          d_ret               = val
        s               = d_ret['branch']
        self.debug('Pushing text contents into file %s\n' % d_ret['nodeName'])
        s.touch(d_ret['nodeName'],  d_ret['contents'])

    def branch_singleBranch_DELprocess(self, **kwargs):
        """
        Process the "run" command from client

        :return:
        """
        d_ret   = {
            'debug':    'branch_singleBranch_DELprocess(): '
        }
        for key,val in kwargs.iteritems():
            if key == 'd_ret':          d_ret               = val
        s               = d_ret['branch']
        self.debug('Deleting object %s\n' % d_ret['nodeName'])
        self.debug('path in stree: %s\n' % s.pwd())
        s.rm(d_ret['nodeName'])


    def branch_singleBranch_CLEARprocess(self, **kwargs):
        """
        Process the "run" command from client

        :return:
        """
        d_ret   = {
            'debug':    'branch_singleBranch_CLEARprocess(): '
        }
        for key,val in kwargs.iteritems():
            if key == 'd_ret':          d_ret               = val
        s               = d_ret['branch']
        self.debug('clearing object %s\n' % d_ret['nodeName'])
        self.debug('path in stree: %s\n' % s.pwd())
        s.touch(d_ret['nodeName'], '')


    def branch_singleBranch_RUNprocess(self, **kwargs):
        """
        Process the "run" command from client

        :return:
        """
        d_ret   = {
            'debug':    'branch_singleBranch_RUNprocess(): '
        }
        for key,val in kwargs.iteritems():
            if key == 'd_ret':          d_ret               = val
        s               = d_ret['branch']
        str_ROOT        = d_ret['ROOT']
        self.debug('Regenerating node %s\n' % d_ret['nodeName'])
        # Generate a new branch tree -- this following call generates
        # everything for a new branch! notes, title, comments, etc.
        # It's probably overkill.
        str_timeStamp   = str(datetime.datetime.now())
        str_timeStamp   = str_timeStamp.replace(':', '-')
        str_timeStamp   = str_timeStamp.replace(' ', '_')
        if d_ret['nodeName'] != 'timestamp':
            if str_ROOT     == 'Feeds':
                s_regen         = feed.Feed_FS()
                sr              = s_regen._stree
                str_path        = s.pwd()

                self.debug('Path in stree = %s\n' % str_path)
                if s.pwd(node=1) == 'title':
                    self.debug('Regenerating title...\n')
                    sr.cd('/title')
                    s.cd('/title')
                    s.rm('body')
                    s.touch('body', sr.cat('body'))
                if s.pwd(node=1) == 'note':
                    self.debug('Regenerating note...\n')
                    sr.cd('/note')
                    s.cd('/note')
                    s.rm('body')
                    s.touch('body', sr.cat('body'))
                if s.pwd(node=1) == 'comment':
                    self.debug('Regenerating comment %s at location %s...\n' % (d_ret['nodeName'], str_path))
                    sr.cd(str_path)
                    s.cd(str_path)
                    s.rm(d_ret['nodeName'])
                    s.touch(d_ret['nodeName'], sr.cat(d_ret['nodeName']))
                # "FS" plugins...
                if s.pwd(node=2) == 'executable':
                    str_name    = '%s-%s' % (d_ret['contents'], str_timeStamp)
                    self.debug('Running executable %s...\n' % (str_name))
                    F = self.within._feedTree
                    S = feed.Feed_FS()
                    s = S._stree
                    if F.cd('/feeds')['status']:
                        F.mkcd('Feed-' + str_name)
                        F.graft(s, '/note')
                        F.graft(s, '/title')
                        F.graft(s, '/comment')
                        F.graft(s, '/data')
                # "DS" plugins
                d_pluginRun = s.path_has(node = 'available')
                if d_pluginRun['found']:
                    nodeI               = d_pluginRun['indices'][-1]
                    str_exec            = s.pwd(node = nodeI+1)
                    l_path              = str_path.split('/')
                    p_path              = l_path[0:nodeI]
                    str_pathInFeedTree  = '/'.join(p_path)
                    self.debug('Running plugin %s in %s...\n' % (str_exec, str_pathInFeedTree))
                    if s.cd(str_pathInFeedTree + '/run')['status']:
                        s.mkcd(str_exec + '-'+ str_timeStamp)
                        newData         = data.data()
                        newData.contents_build_1()
                        n               = newData.contents
                        s.graft(n, '/dataView')
                        s.graft(n, '/plugins')

            if str_ROOT     == 'Plugins':
                if s.pwd(node=1) == 'executable':
                    str_name    = '%s-%s' % (d_ret['contents'], str_timeStamp)
                    self.debug('Running executable %s...\n' % (str_name))
                    F = self.within.within.FT._feedTree
                    S = feed.Feed_FS()
                    s = S._stree
                    if F.cd('/feeds')['status']:
                        F.mkcd('Feed-' + str_name)
                        F.graft(s, '/note')
                        F.graft(s, '/title')
                        F.graft(s, '/comment')
                        F.graft(s, '/data')
        self.debug('setting timeStamp to %s\n' % str_timeStamp)
        s.touch('timestamp', str_timeStamp)


    def REST_process(self, **kwargs):
        """
        Get a branch based on various criteria
        :param kwargs: searchType = 'name' | 'id', target = <target>
        :return: Feed conforming to search criteria
        """
        b_returnAsDict      = True

        str_searchType      = ''
        str_searchTarget    = ''
        str_pathInBranch      = ''

        d_ret               = {
            'VERB':             'GET',
            'payloadFile':      '',
            'branch':           None,
            'debug':            'branch_process(): ',
            'path':             '',
            'pathInBranch':     '',
            'b_status':         False,
            'payload':          {},
            'URL_get':          [],
            'b_returnTree':     True
        }

        for key,val in kwargs.iteritems():
            if key == 'VERB':           d_ret['VERB']           = val
            if key == 'ROOT':           d_ret['ROOT']           = val
            if key == 'payloadFile':    d_ret['payloadFile']    = val
            if key == 'returnAsDict':   b_returnAsDict          = val
            if key == 'searchType':     str_searchType          = val
            if key == 'searchTarget':   str_searchTarget        = val
            if key == 'pathInBranch':   str_pathInBranch        = val
            if key == 'schema':         str_schema              = val

        kwargs['d_ret'] = d_ret

        # First get the branch itself from the tree of Feeds...
        F               = self._branchTree
        F.cd('/%s' % str_ROOT.lower())
        str_branchSpec    = '%s_%s' % (str_searchType.upper(), str_searchTarget)

        # Check if we want a list of all branches for this user
        if not len(str_searchType) or not len(str_searchTarget) or str_searchTarget == '*':
            d_ret           = self.branch_branchList_fromTreeGet(**kwargs)
            d_ret['debug'] += "Search for '%s' on type '%s'" % (str_searchTarget, str_searchType)
        else:
            # Or if we just want one specific branch
            d_ret       = self.branch_singleBranch_fromTreeGet(**kwargs)

            # and now, check for any paths in the tree of this Feed
            if len(str_pathInBranch) and str_pathInBranch != '/':
                self.debug('Path in Feed: %s\n' % str_pathInBranch)
                d_ret           = self.branch_singleBranch_process(**kwargs)

            # b_returnTree is always True, unless a "file" is being returned
            if b_returnAsDict and d_ret['b_returnTree']:
                d_ret['branch']   = dict(d_ret['branch'].snode_root)
            d_ret['payload']    = d_ret['branch']
            d_ret['URL_get']    = self.branch_GETURI(branchSpec = str_branchSpec, path = str_pathInBranch)

        # Pop the "temp" key 'branch' from the return stack
        if 'branch' in d_ret: d_ret.pop('branch')

        # Set the 'path'
        d_ret['path']   = str_searchTarget + str_pathInBranch
        return d_ret

if __name__ == "__main__":
    branch  = BranchTree()
