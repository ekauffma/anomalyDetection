import ROOT
import subprocess
import os
from rich.console import Console

console = Console()

fileDirectory = '/hdfs/store/user/aloeliger/MCGeneration/SUEP2023_Paper_RAW_08Jan2024_1531'
outputDirectory = './outputs/'

os.makedirs(outputDirectory, exist_ok=True)

allFiles = []
for (root, dirs, files) in os.walk(fileDirectory, topdown=True):
    for fileName in files:
        allFiles.append(os.path.join(root, fileName))

#console.print(allFiles)
with console.status("Running files..."):
    for index, filePath in enumerate(allFiles):
        inputFileName = f'file:{filePath}'
        outputFileName = os.path.join(outputDirectory, f'AnalysisNtuple_{index}.root')
        #outputFileName = "file:"+outputFileName
        theCommand = f'cmsRun paperCode/python/makeCICADANtuplesFromRAW.py inputFiles={inputFileName} outputFile={outputFileName}'
        
        commandHistory = subprocess.run(
            [theCommand],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        theExitCode = commandHistory.returncode
        if theExitCode == 0:
            console.log(f'[green]\[SUCCESS][/green] File {index:>4d}')
        else:
            console.log(f'[red]\[FAIL][/red] File {index:>4d}')
            thestderr = commandHistory.stderr.decode()
            console.log(thestderr)
