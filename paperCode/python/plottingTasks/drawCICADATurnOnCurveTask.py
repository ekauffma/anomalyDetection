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
        if len(splitName) == 5: #1D plot designation
            sample, score, secondaryVariable, plotType, rateStr = splitName[0], splitName[1], splitName[2], splitName[3], splitName[4]
        elif len(splitName) == 3:
            sample, score, secondaryVariable = splitName[0], splitName[1], splitName[2]
            plotType = "2D"
            rateStr = None
        else:
            raise RuntimeError(f"CICADATurnOnCurve Plot Task got a key it couldn't parse: {key}")
        return sample, score, secondaryVariable, plotType, rateStr

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

    def plot1DTurnOnCurve(self, rateHist, totalHist, sample, score, secondaryVariable, rateStr):
        canvasName = f"{sample}_xxx_{score}_xxx_{secondaryVariable}_xxx_{rateStr}_xxx_1D_turn_on"

        theCanvas = ROOT.TCanvas(canvasName)

        divideHisto = totalHist.Clone()
        for i in range(1, divideHisto.GetNbinsX()+1):
            divideHisto.SetBinError(i, 0.0)

        turnOnCurve = rateHist.Clone()
        turnOnCurve.Divide(divideHisto)

        turnOnCurve.SetMarkerStyle(20)
        turnOnCurve.SetMarkerColor(ROOT.kBlack)

        turnOnCurve.Draw("E1 x0")

        turnOnCurve.GetXaxis().SetTitle(secondaryVariable)
        turnOnCurve.GetYaxis().SetTitle(f"{score} Efficiency")
        turnOnCurve.SetTitle("")
        turnOnCurve.GetYaxis().SetRangeUser(0.0, 1.05)

        cmsLatex = ROOT.TLatex()
        cmsLatex.SetTextSize(0.05)
        cmsLatex.SetNDC(True)
        cmsLatex.SetTextAlign(32)
        cmsLatex.DrawLatex(0.9,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

        quietROOTFunc(theCanvas.SaveAs)(
            str(self.outputPath/f"{canvasName}.png")
        )

    def process1DPlots(self, plots1D):
        for sample in plots1D:
            for score in plots1D[sample]:
                for secondaryVariable in plots1D[sample][score]:
                    for rateStr in plots1D[sample][score][secondaryVariable]:
                        if rateStr == 'total':
                            continue
                        else:
                            self.plot1DTurnOnCurve(
                                plots1D[sample][score][secondaryVariable][rateStr],
                                plots1D[sample][score][secondaryVariable]['total'],
                                sample,
                                score,
                                secondaryVariable,
                                rateStr,
                            )

    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        scoreFile = self.dictOfFiles["turnon"]
        theFile = ROOT.TFile(scoreFile)
        
        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        plots2D = {}
        plots1D = {}
        for key in listOfKeys:
            sample, score, secondaryVariable, plotType, rateStr = self.parseHistogramName(key)
            if plotType == "2D":
                if sample not in plots2D:
                    plots2D[sample] = {}
                if score not in plots2D[sample]:
                    plots2D[sample][score] = {}
                if secondaryVariable not in plots2D[sample][score]:
                    plots2D[sample][score][secondaryVariable] = theFile.Get(key).Clone()
            elif plotType == "1D":
                if sample not in plots1D:
                    plots1D[sample] = {}
                if score not in plots1D[sample]:
                    plots1D[sample][score] = {}
                if secondaryVariable not in plots1D[sample][score]:
                    plots1D[sample][score][secondaryVariable] = {}
                if rateStr not in plots1D[sample][score][secondaryVariable]:
                    plots1D[sample][score][secondaryVariable][rateStr] = theFile.Get(key).Clone()

        for sample in plots2D:
            for score in plots2D[sample]:
                for secondaryVariable in plots2D[sample][score]:
                    self.plotTurnOnCurve(plots2D[sample][score][secondaryVariable], sample, score, secondaryVariable)
        self.process1DPlots(plots1D)
