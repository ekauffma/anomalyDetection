from .paperSampleBuilder import samplePaths
import os

filePaths = {}
for sampleName in samplePaths:
    completeListOfFiles = []
    for root, dirs, files in os.walk(samplePaths[sampleName], topdown=True):
        for fileName in files:
            completeListOfFiles.append(os.path.join(root, fileName))
    filePaths[sampleName] = completeListOfFiles
