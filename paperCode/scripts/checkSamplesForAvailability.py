from rich.table import Table
from rich.progress import track
from rich.console import Console
import subprocess
import re
import time

console = Console()

def filterCriteria(theString):
    if "Tape" not in theString:
        return True
    else:
        return False

def filterForLocations(theString):
    if re.match("T[0-9](_\w+)+", theString):
        return True
    else:
        return False

def isSiteAvailable(thePath):
    dasgoclientCommand = f'dasgoclient --query="site dataset={thePath}"'
    finalProcess = subprocess.run(
        dasgoclientCommand,
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output = finalProcess.stdout.decode()
    if output == "" or output == None:
        return False
    
    allSites = output.split("\n")
    allSites = allSites[:-1] 
    allSites = list(filter(filterForLocations, allSites))

    diskSites = list(filter(filterCriteria, allSites))
    
    if len(diskSites) > 0:
        return True
    else:
        return False

with open("metadata/listOfSamples.txt", "r") as theFile:
    theContents = theFile.read()
samples = theContents.split('\n')

theTable = Table(
    title="Sample availability"
)
theTable.add_column("Sample", style='bold white')
theTable.add_column("RAW", style='bold', justify='center')
theTable.add_column("Mini", style='bold', justify='center')

# for samplePath in samples:
for samplePath in track(samples, description="Samples"):
    sampleMatch = re.search("(?<=/).*?(?=/)", samplePath)
    sampleName = sampleMatch.group(0)
    miniAODSamplePath = re.sub("GEN-SIM-RAW","MINIAODSIM",samplePath)

    time.sleep(5)
    rawIsAvailable = isSiteAvailable(samplePath)
    time.sleep(5)
    miniIsAvailable = isSiteAvailable(miniAODSamplePath)

    if rawIsAvailable:
        rawStr = "[green]\[AVAILABLE][/green]"
    else:
        rawStr = "[red]\[UNAVAILABLE][/red]"
    
    if miniIsAvailable:
        miniStr = "[green]\[AVAILABLE][/green]"
    else:
        miniStr = "[red]\[UNAVAILABLE][/red]"
    
    theTable.add_row(sampleName, rawStr, miniStr)

console.print(theTable)