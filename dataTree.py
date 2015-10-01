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

        self.fake       = faker.Faker()
        self.contents   = ""
        self.FS         = C_snode.C_stree()
        self.numFiles   = 10

        for key,val in kwargs.iteritems():
            if key == 'numFiles':   self.numFiles    = val

    def MRN_generate(self):
        self.MRN = 4000000 + random.randint(0, 1000000)
        return self.MRN

    def dbID_generate(self, a_upperLimit = 1000):
        self.id = random.randint(0, a_upperLimit)
        return self.id


class dataTree_convert(dataTree):
    """
    Sub-class emulating the results of an 'mri_covert' on a
    PACSPull tree.
    """

    def __init__(self, **kwargs):
        dataTree.__init__(self, **kwargs)
        self.inputTree              = None
        self.b_processPACSPullInput = False
        for key,val in kwargs.iteritems():
            if key == 'PACSPullTree':
                self.inputTree              = val
                self.b_processPACSPullInput = True
            if key == 'convertTo':
                self.extension              = val

        self.treeConvert()
        self.FS.tree_metaData_print(False)

    def treeConvert(self, **kwargs):
        """
        Convert the input tree to another format.
        """
        f   = self.FS
        p   = self.inputTree
        if self.b_processPACSPullInput:
            # This basically creates a tree similar to the original
            # PACSpull, but the "images" container is just a
            # single file.
            f.cd('/')
            f.mkcd('files')
            p.cd('/files')
            for mrn in p.lstr_lsnode():
                p.cd(mrn)
                mrnOnly = mrn.split('-')[0]
                f.mkcd(mrnOnly + '-' + str(self.dbID_generate()))
                for study in p.lstr_lsnode():
                    p.cd(study)
                    f.mkcd('-'.join(study.split('-')[0:-1]) + '-' + str(self.dbID_generate()))
                    l_image = ['-'.join(s.split('-')[0:-1]) + '-' + str(self.dbID_generate())+\
                                '.' + self.extension for s in p.lstr_lsnode()]
                    f.touch('images', l_image)
                    f.cd('../')
                    p.cd('../')
                f.cd('../')
                p.cd('../')
            f.cd('../')
            p.cd('../')

class dataTree_tractography(dataTree):
    """
    Sub-class emulating a tractography set of results
    """
    def __init__(self, **kwargs):
        dataTree.__init__(self, **kwargs)

        f = self.FS
        f.cd('/')
        f.mkcd('files')
        f.mknode(['DIFFUSION_input', 'log', 'diffusionProcess', 'tract_meta-stage-2-dcm2trk.bash'])
        f.cd('tract_meta-stage-2-dcm2trk.bash')
        f.mknode([  'final-trackvis',
                    'stage-1-mri_convert',
                    'stage-2-eddy_correct',
                    'stage-3-dti_recon',
                    'stage-4-dti_tracker',
                    'stage-5-spline_filter'])
        self.FS.tree_metaData_print(False)

class dataTree_reconall(dataTree):
    """
    Sub-class emulating a recon-all set of results
    """
    def __init__(self, **kwargs):
        dataTree.__init__(self, **kwargs)

        f = self.FS
        f.cd('/')
        f.mkcd('files')
        f.mknode(['surf', 'stats', 'bem', 'label', 'mri', 'src', 'tmp', 'touch', 'trash'])

        self.FS.tree_metaData_print(False)

class dataTree_PACSPull(dataTree):
    """
    Sub-class emulating PACS_pull trees.
    """

    def StudyDescriptions_generate(self):
        with open('StudyDescription.lst') as f:
            self.l_StudyDescription = f.read().splitlines()
        return self.l_StudyDescription

    def SeriesDescriptions_generate(self):
        with open('SeriesDescription.lst') as f:
            self.l_SeriesDescription = f.read().splitlines()
        return self.l_SeriesDescription

    def SeriesInstanceUID_generate(self):
        """
        Build a "fake" SeriesInstanceUID
        :return: a "fake" SeriesInstanceUID
        """

        return '%d.%d.%02d.%d.%04d.%d.%d.%02d.%05d.%010d' % \
               (
                   self.fake.random_int(0,          9),
                   self.fake.random_int(0,          9),
                   self.fake.random_int(0,         99),
                   self.fake.random_int(0,          9),
                   self.fake.random_int(0,       9999),
                   self.fake.random_int(0,          9),
                   self.fake.random_int(0,          9),
                   self.fake.random_int(0,         99),
                   self.fake.random_int(0,      99999),
                   self.fake.random_int(0, 9999999999)
               )

    def treeBuild(self):
        FS  = self.FS
        FS.cd('/')
        FS.mkcd('files')
        for mrn in range(0, self.MRNCount):
            FS.mkcd('%d-%03d' % (self.MRN_generate(), self.dbID_generate()))
            for study in range(0, self.StudyCount):
                rand_date   = self.fake.date_time_this_decade()
                FS.mkcd('%s-%03dY-%s-%03d' % (
                                             rand_date.isoformat(),
                                             self.dbID_generate(100),
                                             random.choice(self.l_StudyDescription).strip(),
                                             self.dbID_generate()
                                             ))
                for series in range(0, self.SeriesCount):
                    FS.mkcd('%s-%03d' % (random.choice(self.l_SeriesDescription).strip(),
                                         self.dbID_generate()))
                    l_image = []
                    SeriesInstanceUID = self.SeriesInstanceUID_generate()
                    for image in range(1, self.SeriesFilesCount + 1):
                        l_image.append('%04d-%s.dcm' % \
                            (image, SeriesInstanceUID)
                        )
                    FS.touch('images', l_image)
                    FS.cd('../')
                FS.cd('../')
            FS.cd('../')

    def __init__(self, **kwargs):
        dataTree.__init__(self, **kwargs)

        self.MRNCount               = 3
        self.StudyCount             = 3
        self.SeriesCount            = 3
        self.SeriesFilesCount       = 10
        self.id                     = 0
        self.l_StudyDescription     = self.StudyDescriptions_generate()
        self.l_SeriesDescription    = self.SeriesDescriptions_generate()

        for key,val in kwargs.iteritems():
            if key == 'MRNcount':           self.MRNCount           = int(val)
            if key == 'StudyCount':         self.StudyCount         = int(val)
            if key == 'SeriesCount':        self.SeriesCount        = int(val)
            if key == 'SeriesFilesCount':   self.SeriesFilesCount   = int(val)

        self.treeBuild()
        self.FS.tree_metaData_print(False)

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                     \\
                            --type <dataTreeType>   \\
                            --SeriesFilesCount <SeriesFilesCount>


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
    parser.add_argument(
        '-f', '--SeriesFilesCount',
        help    =   "The number of simulated DICOM filenames to generate.",
        dest    =   'SeriesFilesCount',
        action  =   'store',
        default =   '10'
    )

    args        = parser.parse_args()

    data        = dataTree_PACSPull(SeriesFilesCount = args.SeriesFilesCount)

    print(data.FS)
    print(json.dumps(dict(data.FS.snode_root)))
