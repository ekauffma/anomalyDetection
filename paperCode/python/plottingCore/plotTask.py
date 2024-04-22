# !/usr/bin/env python3

# Utility class for making plots

from pathlib import Path
from abc import ABC, abstractmethod
import ROOT

# This will handle the actual "creation" of the plot
class createPlotTask(ABC):
    def __init__(
            self,
            taskName: str,
            outputFileName: str,
            dictOfSamples: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/"),
    ):
        self.taskName = taskName
        self.outputFileName = outputFileName
        self.outputPath = outputPath
        self.dictOfSamples = dictOfSamples
        self.plotsToBeWritten = []
        self.outputFile = None
        #self.console = Console()
        
    def executeTask(self):
        self.createPlots()
        self.writeOutPlots()

    # this is the individual task responsibility
    # it needs to provide a list of plots to plotsToBeWritten
    @abstractmethod
    def createPlots(self):
        pass

    def writeOutPlots(self):
        self.outputPath.mkdir(exist_ok=True, parents=True)
        self.outputFile = ROOT.TFile(
            str(self.outputPath / self.outputFileName),
            "RECREATE",
        )
        for plot in self.plotsToBeWritten:
            plot.Write()
        self.outputFile.Write()
        self.outputFile.Close()

# This will handle the drawing of the plot
class drawPlotTask(ABC):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: dict,
            outputPath: Path,
    ):
        self.taskName = taskName
        self.dictOfFiles = dictOfFiles
        self.outputPath = outputPath

    @abstractmethod
    def drawPlots(self):
        pass

# This can group creation and drawing tasks together
class createAndDrawTask():
    def __init__(
            self,
            taskName: str,
            theCreateTask: createPlotTask,
            theDrawTask: drawPlotTask,
    ):
        self.taskName = taskName
        self.theCreateTask = theCreateTask
        self.theDrawTask = theDrawTask

    
    def executeTask(self):
        self.theCreateTask.executeTask()
        self.theDrawTask.drawPlots()
