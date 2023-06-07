#Parts of Run C that has run on both mini and RAW both.
from .sample import sample
import os

hdfsPath = '/hdfs/store/user/aloelige/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/CICADA_Ztoee_wMINIAOD_RAW_DY_19May2023/'

theFiles = []
chains = [
    'L1TCaloSummaryTestNtuplizer/L1TCaloSummaryOutput',
    'electronInformationAnalyzer/ElectronInformation'    
]

for root, dirs, files in os.walk(hdfsPath, topdown=True):
    for name in files:
        theFiles.append(os.path.join(root, name))

RunCSample = sample(
    listOfFiles=theFiles,
    listOfChains=chains,
)