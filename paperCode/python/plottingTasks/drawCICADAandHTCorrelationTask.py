# !/usr/bin/env python3

from pathlib import Path
from anomalyDetection.paperCode.plottingCore.plotTask import drawPlotTask
import ROOT
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

class drawCICADAandHTCorrelationTask(drawPlotTask):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: list,
            outputPath: Path = Path('/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/CICADA_HT_Plots/')
    ):
        super().__init__(taskName, dictOfFiles, outputPath)

    def parseHistogramName(self, histogramName):
        splitName = histogramName.split('_xxx_')
        sampleName, primaryScore, secondaryScore = splitName[0], splitName[1], splitName[2]
        return sampleName, primaryScore, secondaryScore
        
    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        correlationFile = self.dictOfFiles['correlation']
        theFile = ROOT.TFile(correlationFile)

        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        plots = {}
        for key in listOfKeys:
            #for right now, secondary score is only HT, and irrelevant
            sampleName, primaryScore, _ = self.parseHistogramName(key)
            if primaryScore not in plots:
                plots[primaryScore] = {}
            if sampleName not in plots[primaryScore]:
                plots[primaryScore][sampleName] = theFile.Get(key).Clone()

        for score in plots:
            for sample in plots[score]:
                theCanvas = ROOT.TCanvas(f"{sample}_{score}")

                plots[score][sample].Draw("COLZ")
                plots[score][sample].GetYaxis().SetTitle("HT")
                plots[score][sample].GetXaxis().SetTitle(score)
                
                quietROOTFunc(theCanvas.SaveAs)(
                    str(
                        self.outputPath / f'{sample}_xxx_{score}_xxx_HT_xxx_correlation.png'
                    )
                )
                
