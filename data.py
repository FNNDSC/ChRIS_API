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

import  argparse
import  dataTree

import  C_snode

import  plugin

sys.path.append('components/faker')

import faker

class data(object):
    """
    This class implements a ChRIS style data object container, accessible
    in a tree like structure, i.e.:

            /dataView
            /dataView/files
            /dataView/files/4693293-270
            /dataView/files/4702512-431
            /dataView/files/4322849-145
            /fileView
            /fileView/files
            /fileView/files/4693293-270
            /fileView/files/4702512-431
            /fileView/files/4322849-145
            /plugin
            /plugin/available
            /plugin/available/tractography
            /plugin/available/mri_convert
            /plugin/available/zip
            /plugin/available/recon-all
            /plugin/run
            /plugin/run/0
            /plugin/run/0/info
            /plugin/run/0/parameters
            /plugin/run/0/results
            /plugin/run/0/results/dataView
            /plugin/run/0/results/dataView/files
            /plugin/run/0/results/dataView/files/4693293-365
            /plugin/run/0/results/dataView/files/4702512-713
            /plugin/run/0/results/dataView/files/4322849-292
            /plugin/run/0/results/fileView
            /plugin/run/0/results/fileView/files
            /plugin/run/0/results/fileView/files/4693293-365
            /plugin/run/0/results/fileView/files/4702512-713
            /plugin/run/0/results/fileView/files/4322849-292
            /plugin/run/0/results/plugin


    The data container encapsulates three components:

           o
            \
            +--- dataView
            \
            +--- plugin
    """

    __metaclass__   = abc.ABCMeta

    def __init__(self, **kwargs):

        self.contents   = C_snode.C_stree()
        self.contents.cd('/')
        self.fake       = faker.Faker()

    def contents_build_1(self, **kwargs):
        """
        Main entry point to constructing a data element.

        Build option "1".

        :param kwargs:
        :return:
        """

        SeriesFilesCount    = 10
        for key,val in kwargs.iteritems():
            if key == 'SeriesFilesCount':   SeriesFilesCount    = val

        # First, build a PACS_pull tree
        self.dataComponent_build(
                path                = '/',
                plugin              = 'PACSPull',
                SeriesFilesCount    = SeriesFilesCount
        )

        self.dataComponent_pluginBuild(
                path                = '/plugins'
        )


        # Now "run" an mri_convert to nifi
        # self.dataComponent_pluginRun(
        #         inputPath           = '/dataView/files',
        #         outputPath          = '/plugin/run',
        #         plugin              = 'mri_convert'
        # )


    def dataComponent_build(self, **kwargs):
        """
        This method builds a "single" dataComponent
        and adds to the internal tree at a specified
        path.

        A data component consists of:

            * dataView
                - actual "files" comprising dataView
            * plugin
                - list of plugins to choose from for this dataView
                - plugin that has been applied to the dataView
        :param kwargs:
        :return:
        """

        str_path            = '/'
        str_plugin          = 'PACSPull'
        ft_convertFrom      = None
        str_convertTo       = ''
        SeriesFilesCount    = 3
        dataTree            = None
        for key,val in kwargs.iteritems():
            if key == 'path':               str_path            = val
            if key == 'plugin':             str_plugin          = val
            if key == 'tree_convertFrom':   ft_convertFrom      = val
            if key == 'type_convertTo':     str_convertTo       = val
            if key == 'SeriesFilesCount':   SeriesFilesCount    = val

        s = self.contents

        if s.cd(str_path)['status']:
            s.mknode(['dataView', 'plugins'])
            if str_plugin.lower() == 'pacspull':
                dataTree = self.dataTree_PACSPull_build(
                                SeriesFilesCount   = SeriesFilesCount
                            )
            # print(dataTree)
            if str_plugin.lower() == 'mri_convert':
                if ft_convertFrom and len(str_convertTo):
                    dataTree = self.dataTree_mriConvert_build(
                        PACSPullTree    = ft_convertFrom,
                        convertTo       = str_convertTo
                    )
            if str_plugin.lower() == 'recon-all':
                dataTree    = self.dataTree_reconall()
            if str_plugin.lower() == 'tractography':
                dataTree    = self.dataTree_tractography()
            s.cd('dataView')
            s.graft(dataTree, '/files')
            s.cd('/')
            s.tree_metaData_print(False)

    def dataComponent_pluginBuild(self, **kwargs):
        """
        Build the plugin tree on a specific data component.
        :param kwargs: 'path'=<path>
        :return:
        """
        str_path    = '/plugins'
        self.PT     = plugin.Plugin_DS(within = self)
        P           = self.PT._pluginTree

        for key,val in kwargs.iteritems():
            if key == 'path':               str_path            = val

        s           = self.contents
        if s.cd(str_path)['status']:
            s.mknode(['run'])
            s.mkcd('available')
            for d in P.lstr_lsnode('/plugins'):
                s.graft(P, '/plugins/%s' % d)

    # def pluginList_withinFeed(self, **kwargs):
    #     """
    #     Creates the "available" directory in the plugin directory within
    #     the larger feed hierarchy.
    #
    #     This contains a list-ordered sub-tree, each with a plugin descriptor
    #     dictionary.
    #
    #
    #     :return:
    #     """
    #
    #     str_path    = '/plugin'
    #     for key,val in kwargs.iteritems():
    #         if key == 'path':           str_path        = val
    #
    #     s = self.contents
    #
    #     if s.cd(str_path)['status']:
    #         s.mkcd('available')
    #         s.mknode(data._dict_plugin.keys())
    #         for node in s.lstr_lsnode():
    #             s.cd(node)
    #             s.touch('detail', data._dict_plugin[node])
    #             s.cd('../')
    #         s.cd(str_path)
    #         s.mkcd('run')

    # def dataComponent_pluginRun(self, **kwargs):
    #     """
    #     'Run' a few fake plugins.
    #     :param kwargs: 'path'=<path>
    #     :return:
    #     """
    #     str_outputPath      = '/plugin'
    #     str_inputPath       = '/dataView/files'
    #
    #     str_plugin          = 'mri_convert'
    #     for key,val in kwargs.iteritems():
    #         if key == 'plugin':             str_plugin          = val
    #         if key == 'inputPath':          str_inputPath       = val
    #         if key == 'outputPath':         str_outputPath      = val
    #
    #     s = self.contents
    #
    #     if s.cd(str_outputPath)['status']:
    #         rand_date       = self.fake.date_time_this_decade()
    #         str_timestamp   = rand_date.isoformat()
    #         l_run           = s.lstr_lsnode()
    #         str_newRun      = str(len(l_run))
    #         s.mkcd(str_newRun)
    #         s.touch('timestamp', str_timestamp)
    #         s.mknode(['parameters', 'results', 'info'])
    #         s.touch('info/detail', {
    #             str_plugin: data._dict_plugin[str_plugin]
    #         })
    #         s.touch('parameters/input', {
    #             str_plugin:    '<some dictionary of all input parameters>'
    #         })
    #         s.cd('results')
    #         str_outputPath = s.cwd()
    #         if str_plugin.lower() != 'pacspull' and str_plugin.lower() != 'mri_convert':
    #             self.dataComponent_build(
    #                 path    = s.cwd(),
    #                 plugin  = str_plugin
    #             )
    #         if str_plugin.lower() == 'mri_convert':
    #             inputTree   = C_snode.C_stree()
    #             inputTree.cd('/')
    #             inputTree.graft(s, str_inputPath)
    #
    #             self.dataComponent_build(
    #                 path                = str_outputPath,
    #                 plugin              = str_plugin,
    #                 tree_convertFrom    = inputTree,
    #                 type_convertTo      = "nii"
    #             )

    def dataComponent_pluginRun(self, **kwargs):
        """
        'Run' a few fake plugins.

        This basically builds a new "data" object and grafts to a specific location
        on the current data object

        :param kwargs: 'path'=<path>
        :return:
        """
        str_outputPath      = '/plugin'
        str_inputPath       = '/dataView/files'

        str_plugin          = 'mri_convert'
        for key,val in kwargs.iteritems():
            if key == 'plugin':             str_plugin          = val
            if key == 'inputPath':          str_inputPath       = val
            if key == 'outputPath':         str_outputPath      = val

        s = self.contents

        s.cd('/plugins/run')
        rand_date       = self.fake.date_time_this_decade()
        str_timestamp   = rand_date.isoformat()
        s.mkcd('%s-mri_convert' % str_timestamp)

        output          = data()
        output.contents_build_1(SeriesFilesCount = 10)
        o               = output.contents
        s.graft(o, '/dataView')
        s.graft(o, '/plugins')

        # o.tree_metaData_print(False)
        # print(o)

        #
        # if s.cd(str_outputPath)['status']:
        #     rand_date       = self.fake.date_time_this_decade()
        #     str_timestamp   = rand_date.isoformat()
        #     l_run           = s.lstr_lsnode()
        #     str_newRun      = str(len(l_run))
        #     s.mkcd(str_newRun)
        #     s.touch('timestamp', str_timestamp)
        #     s.mknode(['parameters', 'results', 'info'])
        #     s.touch('info/detail', {
        #         str_plugin: data._dict_plugin[str_plugin]
        #     })
        #     s.touch('parameters/input', {
        #         str_plugin:    '<some dictionary of all input parameters>'
        #     })
        #     s.cd('results')
        #     str_outputPath = s.cwd()
        #     if str_plugin.lower() != 'pacspull' and str_plugin.lower() != 'mri_convert':
        #         self.dataComponent_build(
        #                 path    = s.cwd(),
        #                 plugin  = str_plugin
        #         )
        #     if str_plugin.lower() == 'mri_convert':
        #         inputTree   = C_snode.C_stree()
        #         inputTree.cd('/')
        #         inputTree.graft(s, str_inputPath)
        #
        #         self.dataComponent_build(
        #                 path                = str_outputPath,
        #                 plugin              = str_plugin,
        #                 tree_convertFrom    = inputTree,
        #                 type_convertTo      = "nii"
        #         )

    def dataTree_mriConvert_build(self, **kwargs):
        """
        Convert an input tree (typically from PACSPull) to
        a different format.

        :param kwargs: PACSPullTree = <Tree>, extention = <ext>
        :return: converted tree
        """
        ft_converted    = None
        ft_PACSPull     = None
        str_extension   = 'nii'
        for key, val in kwargs.iteritems():
            if key == 'PACSPullTree':   ft_PACSPull     = val
            if key == 'extension':      str_extension   = val

        ft_converted    = dataTree.dataTree_convert(
            PACSPullTree    = ft_PACSPull,
            convertTo       = str_extension
        )

        return ft_converted.FS

    def dataTree_PACSPull_build(self, **kwargs):
        """
        Build a PACSPull tree.
        :param kwargs:  SeriesFilesCount = <count>
        :return: PACSPull tree
        """

        SeriesFilesCount = 1
        for key,val in kwargs.iteritems():
            if key == 'SeriesFilesCount':       SeriesFilesCount = int(val)

        ft_PACSPull         = dataTree.dataTree_PACSPull(SeriesFilesCount = SeriesFilesCount)

        return ft_PACSPull.FS


    def __iter__(self):
        yield(self.contents)

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            --fileCount <numberOfFiles>


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' is a simple "data" object container for ChRIS. It encapsulates
        an interactive visual viewer and a file finder/explorer component,
        as well as plugin component.

    ARGS

       --fileCount <fileCount>
       The number of simulated files to generate.


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

def paths_print(atree):
    """
    Print all the paths in the <atree>.
    :param atree: tree whose paths should be printed
    :return:
    """

    l = atree.pathFromHere_explore('/')
    for d in l:
        print(d)

if __name__ == "__main__":

    parser      = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-f', '--SeriesFilesCount',
        help    =   "The number of simulated DICOM filenames to generate.",
        dest    =   'SeriesFilesCount',
        action  =   'store',
        default =   10
    )

    args        = parser.parse_args()

    container   = data()
    container.contents_build_1(SeriesFilesCount = args.SeriesFilesCount)

    container.dataComponent_pluginRun()

    print(container.contents)
    print(json.dumps(dict(container.contents.snode_root)))

    paths_print(container.contents)
