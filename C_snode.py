#!/usr/bin/env python

"""
    NAME

        C_snode, C_snodeBranch, C_stree

    DESCRIPTION

        These three classes are used to construct tree-structures
        composed of 'C_snode' instances. Branches contain dictionaries
        of C_snodes, while leaves contain dictionaries of a specific
        external data class.

    HISTORY
        o 26 March 2008
          Initial design and coding

        o 25 February 2014
          Resurrection as part of the fnndsc-netmap app.

        o 27 February 2014
          Cleanup, refactoring, re-indenting.
          Fix class/instance variable mixups.
"""

# System modules
import  os
import  sys
import  re
from    string                  import  *

from    C_stringCore            import  *

import  itertools

# from    IPython.core.debugger   import Tracer; 

class C_meta:
        '''
        A "base" class containing 'meta' data pertinent to a node.
        '''

        def __init__(self, al_mustInclude          = [],
                           al_mustNotInclude       = []):
            self._hitCount              = 0
            self.l_canInclude           = []
            self.l_mustInclude          = al_mustInclude
            self.l_mustNotInclude       = al_mustNotInclude
            self.b_printPre             = False
            self.sCore                  = C_stringCore()
            self._depth                 = 0
            self.str_pre                = ' '

        def __iter__(self):
            for key in ['_depth']:
                yield(key, getattr(self, key))

        #
        ## Getters/setters

        def pre(self, *args):
            '''
            Get / set the str_pre
            '''
            if len(args):
                self.str_pre = args[0]
            else:
                return self.str_pre

        def mustInclude(self, *args):
            '''
            Get / set the [mustInclude].
            '''
            if len(args):
                self.l_mustInclude = args[0]
            else:
                return l_mustInclude

        def mustNotInclude(self, *args):
            '''
            Get / set the [mustInclude].
            '''
            if len(args):
                self.l_mustNotInclude = args[0]
            else:
                return l_mustNotInclude

        def canInclude(self, *args):
            '''
            Get / set the [mustInclude].
            '''
            if len(args):
                self.l_canInclude = args[0]
            else:
                return l_canInclude

        def depth(self, *args):
            '''
            Get/set the depth
            '''
            if len(args):
                self._depth = args[0]
            else:
                return self._depth

        #
        ## core overloads

        def __str__(self):
            self.sCore.write('%s   +--depth............ %d\n' % (self.str_pre, self._depth))
            self.sCore.write('%s   +--hitCount......... %d\n' % (self.str_pre, self._hitCount))
            self.sCore.write('%s   +--mustInclude...... %s\n' % (self.str_pre, self.l_mustInclude))
            self.sCore.write('%s   +--mustNotInclude... %s\n' % (self.str_pre, self.l_mustNotInclude))
            str_ret = self.sCore.strget()
            self.sCore.reset()
            return str_ret

class C_snode:
        """
        A "container" node class. This container is the
        basic building block for larger tree-like database
        structures.

        The C_snode defines a single 'node' in this tree. It contains
        two lists, 'l_mustInclude' and 'l_mustNotInclude' that define
        the features described in the 'd_nodes' dictionary. This
        dictionary can in turn contain other C_snodes.
        """

        #
        # Methods
        #
        def __init__(self,      astr_nodeName           = "",
                                al_mustInclude          = [],
                                al_mustNotInclude       = []
                                ):
            #       - Core variables
            self.str_obj        = 'C_snode'      # name of object class
            self.str_name       = 'void'         # name of object variable
            self._id            = -1             # id of agent
            self._iter          = 0              # current iteration in an
                                                 #       arbitrary processing
                                                 #       scheme
            self._verbosity     = 0              # debug related value for
                                                 #       object
            self._warnings      = 0              # show warnings

            self.sCore          = C_stringCore()

            # The d_nodes is the basic building block of the C_snode container
            #+ class. It is simply a dictionary that contains 'nodes' that
            #+ satisfy a given feature set described by 'mustInclude' and
            #+ 'mustNotInclude'.
            #+
            #+ In general:
            #+  'snode_parent'      :       the parent node of this node -- useful
            #+                              for tree structuring.
            #+  '_hitCount'         :       count of hits for all items branching
            #+                              at this level. At the leaf level, this
            #+                              contains the length of 'contents'.
            #+  'l_mustInclude'     :       descriptive trait for specific feature
            #+                              level
            #+  'l_mustNotInclude'  :       exclusion trait for specific feature
            #+                              level
            #+  'd_nodes'           :       dictionary of child nodes branching
            #+                              from this node
            #+  'd_data'            :       a dictionary of data for *this* node
            #+
            #+ The pattern of 'mustInclude' and 'mustNotInclude' uniquely
            #+ characterizes a particular level. "Deeper" features (i.e. features
            #+ further along the dictionary tree) must satisfy the combined set
            #+ described by all the 'mustInclude' and 'mustNotInclude' traits of
            #+ each higher level.

            self.meta                   = C_meta()
            self.snode_parent           = None
            self.d_nodes                = {}
            self.d_data                 = {}
            self.b_printMetaData        = True
            self.b_printContents        = True
            self.b_printPre             = False
            self.str_nodeName           = astr_nodeName
            self.b_printPre             = False

        def __iter__(self):
            yield('meta', dict(self.meta))
            if len(self.d_data):
                for key in self.d_data.keys():
                    yield(key, self.d_data[key])
            for key in self.d_nodes:
                yield(self.d_nodes[key].str_nodeName, dict(self.d_nodes[key]))

        #
        # Getters and setters

        def metaData_print(self, *args):
            if len(args):
                self.b_printMetaData    = args[0]
                return True
            else:
                return self.b_printMetaData

        def depth(self, *args):
            '''
            Get/set the depth of this node.
            '''
            if len(args):
                self.meta.depth(args[0])
            else:
                return self.meta.depth()

        def printPre(self, *args):
            '''
            get/set the str_pre string.
            '''
            if len(args):
                self.b_printPre = args[0]
            else:
                return self.b_printPre

        @staticmethod
        def str_blockIndent(astr_buf, a_tabs=1, a_tabLength=4, **kwargs):
            """
            For the input string <astr_buf>, replace each '\n'
            with '\n<tab>' where the number of tabs is indicated
            by <a_tabs> and the length of the tab by <a_tabLength>

            Trailing '\n' are *not* replaced.
            """
            str_tabBoundary = " "
            for key, value in kwargs.iteritems():
              if key == 'tabBoundary':  str_tabBoundary = value
            b_trailN = False
            length = len(astr_buf)
            ch_trailN = astr_buf[length - 1]
            if ch_trailN == '\n':
              b_trailN = True
              astr_buf = astr_buf[0:length - 1]
            str_ret = astr_buf
            str_tab = ''
            str_Indent = ''
            for i in range(a_tabLength):
                str_tab = '%s ' % str_tab
            str_tab = "%s%s" % (str_tab, str_tabBoundary)
            for i in range(a_tabs):
                str_Indent = '%s%s' % (str_Indent, str_tab)
            str_ret = re.sub('\n', '\n%s' % str_Indent, astr_buf)
            str_ret = '%s%s' % (str_Indent, str_ret)
            if b_trailN: str_ret = str_ret + '\n'
            return str_ret

        def __str__(self):
            self.sCore.reset()
            str_pre     = ""
            if not self.depth():
                str_pre = "o"
            else:
                str_pre = "+"
            self.sCore.write('%s---%s\n' % (str_pre, self.str_nodeName))
            if self.b_printPre:
                str_pre = "|"
            else:
                str_pre = " "
            self.meta.pre(str_pre)
            if self.b_printMetaData: self.sCore.write('%s' % self.meta)

            for key, value in self.d_data.iteritems():
                self.sCore.write('%s   +--%-17s %s\n' % (str_pre, key, value))

            nodeCount     = len(self.d_nodes)
            if nodeCount and self.b_printContents:
                self.sCore.write('%s   +---+\n' % str_pre )
                elCount   = 0
                lastKey   = self.d_nodes.keys()[-1]
                for node in self.d_nodes.keys():
                    self.d_nodes[node].printPre(True)
                    if node == lastKey:
                        self.d_nodes[node].printPre(False)
                    str_contents = C_snode.str_blockIndent('%s' %
                        self.d_nodes[node], 1, 8, tabBoundary = "")
                    # str_contents = re.sub(r'                ', 'xxxxxxxx|xxxxxxx', str_contents)
                    if self.d_nodes[node].printPre():
                        str_contents = re.sub(r'                ', '        |       ', str_contents)
                    self.sCore.write(str_contents)
                    elCount   = elCount + 1
            return self.sCore.strget()

        #
        # Simple error handling
        def error_exit(self, astr_action, astr_error, astr_code):
            print("%s: FATAL error occurred"                % self.str_obj)
            print("While %s,"                               % astr_action)
            print("%s"                                      % astr_error)
            print("\nReturning to system with code %s\n"    % astr_code)
            sys.exit(astr_code)

        def node_branch(self, al_keys, al_values):
            """
            For each node in <al_values>, add to internal contents
            dictionary using key from <al_keys>.
            """
            if len(al_keys) != len(al_values):
                self.error_exit("adding branch nodes", "#keys != #values", 1)
            ldict = dict(zip(al_keys, al_values))
            self.node_dictBranch(ldict)

        def node_dictBranch(self, adict):
            """
            Expands the internal md_nodes with <adict>
            """
            self.d_nodes.update(adict)

class C_snodeBranch:
        """
        The C_snodeBranch class is basically a dictionary collection
        of C_snodes. Conceptually, a C_snodeBranch is a single "layer"
        of C_snodes all branching from a common ancestor node.
        """
        #
        # Member variables
        #


        #
        # Methods
        #

        def __str__(self):
            self.sCore.reset()
            for node in self.dict_branch.keys():
              self.sCore.write('%s' % self.dict_branch[node])
            return self.sCore.strget()

        def __init__(self, al_branchNodes):
            '''
            Constructor.

            If instantiated with a list of nodes, will create/populate
            internal dictionary with appropriate C_snodes.
            '''

            self.str_obj                = 'C_snodeBranch';  # name of object class
            self.str_name               = 'void';           # name of object variable
            self._id                    = -1;               # id of agent
            self._iter                  = 0;                # current iteration in an
                                                            #       arbitrary processing
                                                            #       scheme
            self._verbosity             = 0;                # debug related value for
                                                            #       object
            self._warnings              = 0;                # show warnings

            self.dict_branch            = {}
            self.sCore                  = C_stringCore()
            element                     = al_branchNodes[0]
            if isinstance(element, C_snode):
              for node in al_branchNodes:
                self.dict_branch[node]  = node
            else:
              for node in al_branchNodes:
                self.dict_branch[node]  = C_snode(node)
        #
        # Simple error handling
        def error_exit(self, astr_action, astr_error, astr_code):
            print("%s: FATAL error occurred"                % self.str_obj)
            print("While %s,"                               % astr_action)
            print("%s"                                      % astr_error)
            print("\nReturning to system with code %s\n"    % astr_code)
            sys.exit(astr_code)

        def node_branch(self, astr_node, abranch):
            """
            Adds a branch to a node, i.e. depth addition. The given
            node's md_nodes is set to the abranch's mdict_branch.
            """
            self.dict_branch[astr_node].node_dictBranch(abranch.dict_branch)

class C_stree:
        """
        The C_stree class provides methods for creating / navigating
        a tree composed of C_snodes.

        A C_stree is an ordered (and nested) collection of C_snodeBranch
        instances, with additional logic to match nodes with their parent
        node.

        The metaphor designed into the tree structure is that of a UNIX
        directory tree, with equivalent functions for 'cdnode', 'mknode'
        'lsnode'.
        """

        #
        # Methods
        #

        def metaData_print(self, *args):
            if len(args):
                self.b_printMetaData    = args[0]
                return True
            else:
                return self.b_printMetaData

        def __init__(self, al_rootBranch=[]):
            """
            Creates a tree structure and populates the "root"
            branch.
            """
            #
            # Member variables
            #
            #       - Core variables
            self.str_obj                = 'C_stree';    # name of object class
            self.str_name               = 'void';       # name of object variable
            self._id                    = -1;           # id of agent
            self._iter                  = 0;            # current iteration in an
                                                        #       arbitrary processing
                                                        #       scheme
            self._verbosity             = 0;            # debug related value for
                                                        #       object
            self._warnings              = 0;            # show warnings
            self.b_printMetaData        = False

            self.l_allPaths             = []            # Each time a new C_snode is
                                                        #+ added to the tree, its path
                                                        #+ list is appended to this
                                                        #+ list variable.
            if not len(al_rootBranch):
                al_rootBranch           = ['/']
            if len(al_rootBranch):
                if not isinstance(al_rootBranch, list):
                    al_rootBranch       = ['/']
            self.sCore                  = C_stringCore()
            str_treeRoot                = '/'
            self.l_cwd                  = [str_treeRoot]
            self.sbranch_root           = C_snodeBranch([str_treeRoot])
            self.snode_current          = None
            self.snode_root             = self.sbranch_root.dict_branch[str_treeRoot]
            self.snode_root.depth(0)
            self.snode_root.snode_parent = self.snode_root
            self.root()
            self.l_allPaths             = self.l_cwd[:]
            if len(al_rootBranch) and al_rootBranch != ['/']:
                self.mknode(al_rootBranch)

        def __str__(self):
            self.sCore.reset()
            self.sCore.write('%s' % self.snode_root)
            return self.sCore.strget()

        def root(self):
            """
            Reset all nodes and branches to 'root'.
            """
            str_treeRoot                = '/'
            self.l_cwd                  = [str_treeRoot]
            self.snode_current          = self.snode_root
            self.sbranch_current        = self.sbranch_root


        def cwd(self):
            '''
            Return a UNIX FS type string of the current working 'directory'.
            '''
            l_cwd                       = self.l_cwd[:]
            str_cwd                     = '/'.join(l_cwd)
            if len(str_cwd)>1: str_cwd  = str_cwd[1:]
            return str_cwd

        def pwd(self):
            '''
            Prints the cwd
            '''
            return self.cwd()

        def ptree(self):
            '''
            Return all the paths in the tree.
            '''
            return self.l_allPaths

        def node_mustNotInclude(self, al_mustNotInclude, ab_reset=False):
            """
            Either appends or resets the <mustNotInclude> list of snode_current
            depending on <ab_reset>.
            """
            if ab_reset:
                self.snode_current.l_mustNotInclude = al_mustNotInclude[:]
            else:
                l_current   = self.snode_current.l_mustNotInclude[:]
                l_total     = l_current + al_mustNotInclude
                self.snode_current.l_mustNotInclude = l_total[:]

        def node_mustInclude(self, al_mustInclude, ab_reset=False):
            """
            Either appends or resets the <mustInclude> list of snode_current
            depending on <ab_reset>.
            """
            if ab_reset:
                self.snode_current.l_mustInclude = al_mustInclude[:]
            else:
                l_current   = self.snode_current.l_mustInclude[:]
                l_total     = l_current + al_mustInclude
                self.snode_current.l_mustInclude = l_total[:]

        def paths_update(self, al_branchNodes):
            """
            Add each node in <al_branchNodes> to the self.ml_cwd and
            append the combined list to ml_allPaths. This method is
            typically not called by a user, but by other methods in
            this module.
            """
            for node in al_branchNodes:
                #print "appending %s" % node
                l_pwd       = self.l_cwd[:]
                l_pwd.append(node)
                #print "l_pwd: %s" % l_pwd
                #print "ml_cwd: %s" % self.ml_cwd
                self.l_allPaths.append(l_pwd)

        def mknode(self, al_branchNodes):
            """
            Create a set of nodes (branches) at current node. Analogous to
            a UNIX mkdir call, however nodes can be any type (i.e. not
            just "directories" but also "files")
            """
            b_ret = True
            # First check that none of these nodes already exist in the tree
            l_branchNodes = []
            for node in al_branchNodes:
                l_path      = self.l_cwd[:]
                l_path.append(node)
                #print l_path
                #print self.ml_allPaths
                #print self.b_pathOK(l_path)
                if not self.b_pathOK(l_path):
                    l_branchNodes.append(node)
            snodeBranch   = C_snodeBranch(l_branchNodes)
            for node in l_branchNodes:
                depth = self.snode_current.depth()
                # if (self.msnode_current != self.msnode_root):
                snodeBranch.dict_branch[node].depth(depth+1)
                snodeBranch.dict_branch[node].snode_parent = self.snode_current
            self.snode_current.node_dictBranch(snodeBranch.dict_branch)
            # Update the ml_allPaths
            self.paths_update(al_branchNodes)
            return b_ret

        def mkcd(self, astr_node):
            """Creates a single node and cd's into that node
            """
            self.mknode([astr_node])
            self.cdnode(astr_node)

        def cat(self, name):
            '''
            Returns the contents of the 'name'd element at this level.
            '''
            return self.snode_current.d_data[name]

        def touch(self, name, data):
            '''
            Put 'data' to the current node d_data dictionary under key 'name'
            '''
            b_OK = True
            # print("here!")
            # print(self.snode_current)
            # print(self.snode_current.d_nodes)
            self.snode_current.d_data[name] = data
            # print(self.snode_current)
            return b_OK

        def append(self, name, data):
            '''Append 'data' to the current node d_data

            This method appends 'data' to the current contents in the
            key named 'name'. The append assumes that the operation
            makes sense and that the data types can be appended to
            each other.

            '''
            b_OK = True
            self.snode_current.d_data[name] = self.snode_current.d_data[name] + data
            return b_OK


        def b_pathOK(self, al_path):
            """
            Checks if the absolute path specified in the al_path
            is valid for current tree
            """
            b_OK  = True
            try:          self.l_allPaths.index(al_path)
            except:       b_OK    = False
            return b_OK

        def b_pathInTree(self, astr_path):
            """
            Converts a string <astr_path> specifier to a list-based
            *absolute* lookup, i.e. "/node1/node2/node3" is converted
            to ['/' 'node1' 'node2' 'node3'].

            The method also understands a paths that start with: '..' or
            combination of '../../..' and is also aware that the root
            node is its own parent.

            If the path list conversion is valid (i.e. exists in the
            space of existing paths, l_allPaths), return True and the
            destination path list; else return False and the current
            path list.
            """
            if astr_path == '/':  return True, ['/']
            al_path               = astr_path.split('/')
            # Check for absolute path
            if not len(al_path[0]):
                al_path[0]          = '/'
                #print "returning %s : %s" % (self.b_pathOK(al_path), al_path)
                return self.b_pathOK(al_path), al_path
            # Here we are in relative mode...
            # First, resolve any leading '..'
            l_path        = self.l_cwd[:]
            if(al_path[0] == '..'):
                while(al_path[0] == '..' and len(al_path)):
                    l_path    = l_path[0:-1]
                    if(len(al_path) >= 2): al_path   = al_path[1:]
                    else: al_path[0] = ''
                    #print "l_path  = %s" % l_path
                    #print "al_path = %s (%d)" % (al_path, len(al_path[0]))
                if(len(al_path[0])):
                    #print "extending %s with %s" % (l_path, al_path)
                    l_path.extend(al_path)
            else:
                l_path      = self.l_cwd
                l_path.extend(al_path)
            #print "final path list = %s (%d)" % (l_path, len(l_path))
            if(len(l_path)>=1 and l_path[0] != '/'):      l_path.insert(0, '/')
            if(len(l_path)>1):            l_path[0]       = ''
            if(not len(l_path)):          l_path          = ['/']
            #TODO: Possibly check for trailing '/', i.e. list ['']
            str_path      = '/'.join(l_path)
            #print "final path str  = %s" % str_path
            b_valid, al_path = self.b_pathInTree(str_path)
            return b_valid, al_path

        def cdnode(self, astr_path):
            """Change working node to astr_path.

            The path is converted to a list, split on '/'. By performing a 'cd'
            all parent and derived nodes need to be updated relative to
            new location.

            Args:
                astr_path (string): The path to cd to.

            Returns:
                {"status" : True/False , "path": l_cwd -- the path as list}

            """

            # Start at the root and then navigate to the
            # relevant node
            l_absPath             = []
            b_valid, l_absPath    = self.b_pathInTree(astr_path)
            if b_valid:
                #print "got cdpath = %s" % l_absPath
                self.l_cwd              = l_absPath[:]
                self.snode_current      = self.snode_root
                self.sbranch_current    = self.sbranch_root
                #print l_absPath
                for node in l_absPath[1:]:
                    self.snode_current = self.snode_current.d_nodes[node]
                self.sbranch_current.dict_branch = self.snode_current.snode_parent.d_nodes
                return {"status": True, "path": self.l_cwd}
            return {"status": False, "path": []}

        def cd(self, astr_path):
            """Alias for cdnode()

            """
            return self.cdnode(astr_path)

        def ls(self, astr_path="", **kwargs):
            b_lsData    = True
            b_lsNodes   = True
            if len(astr_path): self.cdnode(astr_path)
            str_nodes   = self.str_lsnode(astr_path)
            d_data      = self.snode_current.d_data
            for key, val in kwargs.iteritems():
                if key == 'data':   b_lsData    = val
                if key == 'nodes':  b_lsNodes   = val
            if b_lsData and b_lsNodes:
                return str_nodes, d_data
            if b_lsData:
                return d_data
            if b_lsNodes:
                return str_nodes
            return str_nodes, d_data


        def str_lsnode(self, astr_path=""):
            """
            Print/return the set of nodes branching from current node as string
            """
            self.sCore.reset()
            str_cwd       = self.cwd()
            if len(astr_path): self.cdnode(astr_path)
            for node in self.snode_current.d_nodes.keys():
                self.sCore.write('%s\n' % node)
            str_ls = self.sCore.strget()
            print(str_ls)
            if len(astr_path): self.cdnode(str_cwd)
            return str_ls

        def lstr_lsnode(self, astr_path=""):
            """
            Return the string names of the set of nodes branching from
            current node as list of strings
            """
            self.sCore.reset()
            str_cwd       = self.cwd()
            if len(astr_path): self.cdnode(astr_path)
            lst = self.snode_current.d_nodes.keys()
            if len(astr_path): self.cdnode(str_cwd)
            return lst

        def lsbranch(self, astr_path=""):
            """
            Print/return the set of nodes in current branch
            """
            self.sCore.reset()
            str_cwd       = self.cwd()
            if len(astr_path): self.cdnode(astr_path)
            self.sCore.write('%s' % self.sbranch_current.dict_branch.keys())
            str_ls = self.sCore.strget()
            print(str_ls)
            if len(astr_path): self.cdnode(str_cwd)
            return str_ls

        def lstree(self, astr_path=""):
            """
            Print/return the tree from the current node.
            """
            self.sCore.reset()
            str_cwd       = self.cwd()
            if len(astr_path): self.cdnode(astr_path)
            str_ls        = '%s' % self.snode_current
            print(str_ls)
            if len(astr_path): self.cdnode(str_cwd)
            return str_ls

        def lsmeta(self, astr_path=""):
            """
            Print/return the "meta" information of the node, i.e.
                o mustInclude
                o mustNotInclude
                o hitCount
            """
            self.sCore.reset()
            str_cwd       = self.cwd()
            if len(astr_path): self.cdnode(astr_path)
            b_contentsFlag        = self.snode_current.b_printContents
            self.snode_current.b_printContents = False
            str_ls        = '%s' % self.snode_current
            print(str_ls)
            if len(astr_path): self.cdnode(str_cwd)
            self.snode_current.b_printContents  = b_contentsFlag
            return str_ls

        def tree_metaData_print(self, aval):
            self.metaData_print(aval)
            self.treeRecurse(self.treeNode_metaSet)

        def treeNode_metaSet(self, astr_path, **kwargs):
            '''
            Sets the metaData_print bit on node at <astr_path>.
            '''
            self.cdnode(astr_path)
            self.snode_current.metaData_print(self.b_printMetaData)
            return True

        def treeRecurse(self, afunc_nodeEval = None, astr_startPath = '/'):
            """
            Recursively walk through a C_stree, starting from node
            <astr_startPath>.

            The <afunc_nodeEval> is a function that is called on a node
            path. It is of form:

                afunc_nodeEval(astr_startPath, **kwargs)

            and must return either True or False.
            """
            [b_valid, l_path ] = self.b_pathInTree(astr_startPath)
            if b_valid and afunc_nodeEval:
                b_valid     = afunc_nodeEval(astr_startPath)
            #print 'processing node: %s' % astr_startPath
            if b_valid:
                for node in self.lstr_lsnode(astr_startPath):
                    if astr_startPath == '/': recursePath = "/%s" % node
                    else: recursePath = '%s/%s' % (astr_startPath, node)
                    self.treeRecurse(afunc_nodeEval, recursePath)

        #
        # Simple error handling
        def error_exit(self, astr_action, astr_error, astr_code):
            print("%s: FATAL error occurred" % self.str_obj)
            print("While %s," % astr_action)
            print("%s" % astr_error)
            print("\nReturning to system with code %s\n" % astr_code)
            sys.exit(astr_code)
