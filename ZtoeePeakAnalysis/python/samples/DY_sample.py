#!/usr/bin/env python3
from .sample import sample
import os

hdfsPath = "/hdfs/store/user/aloeliger/Ztoee_wminiCICADA/v_2/DY/"

theFiles = []
chains = [
    'basicEventInfoAnalyzer/basicInfo',
    #'miniCICADAAnalyzer/miniCICADAScoreTree',
    'miniCICADAAnalyzerCICADAv1/miniCICADAScoreTree',
    'electronInformationAnalyzer/ElectronInformation'
]

for root, dirs, files in os.walk(hdfsPath, topdown=True):
    for name in files:
        theFiles.append(os.path.join(root, name))

DYSample = sample(
    listOfFiles=theFiles,
    listOfChains=chains,
)

DYSample.xsec = 5379.0 #XSec from XSDB, in pb
DYSample.xsec_uncert = 40.44 #uncertainty taken from XSDB, in  pb.
DYSample.luminosity = 59.83e3 #Run 2018 luminosity, in pb^-1

def XSecWeighting(self, *otherArgs):
    totalEntries = self.GetEntries()
    weight = (self.xsec * self.luminosity)/totalEntries
    return weight

DYSample.weightingFunction = XSecWeighting