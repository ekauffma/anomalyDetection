# !/usr/bin/env python3

from pathlib import Path
from anomalyDetection.paperCode.plottingCore.plotTask import drawPlotTask
import ROOT
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc

class drawCICADATurnOnCurveTask(drawPlotTask):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: list,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/CICADATurnOnPlots/")
    ):
        super().__init__(taskName, dictOfFiles, outputPath)

    def parseHistogramName(self, key):
        splitName = key.split("_xxx_")
        sample, score, secondaryVariable = splitName[0], splitName[1], splitName[2]
        return sample, score, secondaryVariable

    def makeTurnOnCurve(self, histogram, debug=False):
        histogramName = f"{histogram.GetName()}_turn_on"
        turnOnHisto = histogram.Clone()
        turnOnHisto.SetNameTitle(
            histogramName,
            histogramName,
        )

        #okay. We have a secondary variable on the y-axis
        #and CICADA score on the x-axis
        #the idea here, is that for a cicada bin/threshold
        #we want to know at that HT, what percentage of events are above that CICADA threshold
        #We do that, by integrating total events at that HT versus just above the CICADA score
        nbins_y = histogram.GetNbinsY()
        nbins_x = histogram.GetNbinsX()

        #select a secondary variable bin
        for yBin in range(1, nbins_y+1):
            #okay, for this value and above, we should know the total number of CICADA scores
            #totalContents = histogram.Integral(1, nbins_x+1, yBin, nbins_y+1)
            totalContents = histogram.Integral(1, nbins_x+1, yBin, yBin)
            if totalContents == 0:
                continue
            #now, for each possible cicada threshold,
            for xBin in range(1, nbins_x+1):
                #we integrate above it, and divide to get an efficiency
                #aboveThreshold = histogram.Integral(xBin, nbins_x+1, yBin, nbins_y+1)
                aboveThreshold = histogram.Integral(xBin, nbins_x+1, yBin, yBin)
                eff = aboveThreshold/totalContents
                turnOnHisto.SetBinContent(
                    xBin,
                    yBin,
                    eff
                )
        return turnOnHisto

    def plotTurnOnCurve(self, histogram, sample, score, secondaryVariable):
        turnOnCurve = self.makeTurnOnCurve(histogram)
        
        canvasName = f'{sample}_xxx_{score}_xxx_{secondaryVariable}_xxx_turn_on'
        theCanvas = ROOT.TCanvas(canvasName)
        
        turnOnCurve.Draw('COLZ')

        turnOnCurve.GetXaxis().SetTitle(score)
        turnOnCurve.GetYaxis().SetTitle(secondaryVariable)

        quietROOTFunc(theCanvas.SaveAs)(
            str(self.outputPath/f"{canvasName}.png")
        )

    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        scoreFile = self.dictOfFiles["turnon"]
        theFile = ROOT.TFile(scoreFile)
        
        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        plots = {}
        for key in listOfKeys:
            sample, score, secondaryVariable = self.parseHistogramName(key)
            if sample not in plots:
                plots[sample] = {}
            if score not in plots[sample]:
                plots[sample][score] = {}
            if secondaryVariable not in plots[sample][score]:
                plots[sample][score][secondaryVariable] = theFile.Get(key).Clone()

        for sample in plots:
            for score in plots[sample]:
                for secondaryVariable in plots[sample][score]:
                    self.plotTurnOnCurve(plots[sample][score][secondaryVariable], sample, score, secondaryVariable)
