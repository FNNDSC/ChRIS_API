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

This module simulates a "view" on some file system data, mapping
to a C_snode tree.
"""

import  abc
import  json
import  argparse

import  C_snode
import  random
import  sys
import  os

sys.path.append('components/faker')

import faker

class dataTree(object):
    """
    This class emulates various types of file system trees with directories
    and files, mapped/contained with an C_snode object.
    """

    __metaclass__   = abc.ABCMeta

    def __init__(self, **kwargs):

        self.contents   = ""
        self.FS         = C_snode.C_stree()
        self.numFiles   = 10

        for key,val in kwargs.iteritems():
            if key == 'numFiles':   numFiles    = val

class dataTree_PACSPull(dataTree):
    """
    Sub-class emulating PACS_pull trees.
    """

    def MRN_generate(self):
        self.MRN = 10000000 + random.randint(0, 1000000)
        return self.MRN

    def dbID_generate(self):
        self.id = random.randint(0, 1000)
        return self.id

    def StudyDescriptions_generate(self):
        with open('StudyDescription.lst') as f:
            self.l_StudyDescription = f.read().splitlines()
        return self.l_StudyDescription

    def SeriesDescriptions_generate(self):
        with open('SeriesDescription.lst') as f:
            self.l_SeriesDescription = f.read().splitlines()
        return self.l_SeriesDescription

    def treeBuild(self):
        FS  = self.FS
        FS.cd('/')
        for mrn in range(0, self.MRNCount):
            FS.mkcd('%d-%03d' % (self.MRN_generate(), self.dbID_generate()))
            for study in range(0, self.StudyCount):
                rand_date   = self.fake.date_time_this_decade()
                FS.mkcd('%s-%03dY-%s-%03d' % (
                                             rand_date.isoformat(),
                                             self.dbID_generate(),
                                             random.choice(self.l_StudyDescription),
                                             self.dbID_generate()
                                             ))
                for series in range(0, self.SeriesCount):
                    FS.mkcd('%s-%03d' % (random.choice(self.l_SeriesDescription).strip(),
                                         self.dbID_generate()))
                    FS.cd('../')
                FS.cd('../')
            FS.cd('/')

    def __init__(self, **kwargs):
        dataTree.__init__(self, **kwargs)

        self.fake                   = faker.Faker()

        self.MRNCount               = 3
        self.StudyCount             = 3
        self.SeriesCount            = 3
        self.SeriesFilesCount       = 10
        self.id                     = 0
        self.l_StudyDescription     = self.StudyDescriptions_generate()
        self.l_SeriesDescription    = self.SeriesDescriptions_generate()

        for key,val in kwargs.iteritems():
            if key == 'MRNcount':           self.MRNCount           = val
            if key == 'StudyCount':         self.StudyCount         = val
            if key == 'SeriesCount':        self.SeriesCount        = val
            if key == 'SeriesFilesCount':   self.SeriesFilesCount   = val

        self.treeBuild()


def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            --type <dataTreeType>


    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' implements a simple simulated file system tree with data
        suitable for ChRIS processing.

    ARGS

       --type <dataTreeType>
       The type of dataTree to simulate/build.


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

if __name__ == "__main__":

    parser      = argparse.ArgumentParser(description = synopsis(True))
    parser.add_argument(
        '-t', '--type',
        help    =   "The dataTreeType to generate.",
        dest    =   'dataTree',
        action  =   'store',
        default =   "PACS_pull"
    )

    args        = parser.parse_args()

    data        = dataTree_PACSPull()

    print(data.FS)
