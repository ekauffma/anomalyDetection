# !/usr/bin/env python3

from pathlib import Path
from anomalyDetection.paperCode.plottingCore.plotTask import drawPlotTask
import ROOT
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc
import math

class drawCICADAPurityContentsPlotsTask(drawPlotTask):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: dict,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/PaperPurityContentPlots/")
    ):
        super().__init__(taskName, dictOfFiles, outputPath)

    def parseHistogramName(self, histogramName):
        splitName = histogramName.split("_xxx_")
        if len(splitName) == 3: #contents histo
            plotType, score, rateStr = splitName[0], splitName[1], splitName[2]
            triggerGroup = None
            sample = "ZeroBias"
        elif len(splitName) == 4: #purity histo
            sample, score, plotType, triggerGroup = splitName[0], splitName[1], splitName[2], splitName[3]
            rateStr = None
        else:
            raise RuntimeError(f"CICADA Purity Contents couldn't parse histogram name: Got unexepcted number of values: {histogramName}")
        return sample, score, plotType, triggerGroup, rateStr

    def makePurityCurve(self, noOverlapHist, intersectionHist):
        nBins = noOverlapHist.GetNbinsX()
        purityGraph = ROOT.TGraphErrors(nBins)
        
        for i in range(1, nBins+1):
            pureEvents = noOverlapHist.Integral(i, nBins+1)
            allEvents = noOverlapHist.Integral(i, nBins+1) + intersectionHist.Integral(i ,nBins+1)

            pureEventError = math.sqrt(pureEvents)
            try:
                purity = pureEvents/allEvents
                purityError = pureEventError/allEvents
            except ZeroDivisionError:
                purity = 0.0
                purityError = 0.0
                
            purityPercent = purity*100.0
            totalError = purityError * 100.0
            scoreThreshold = noOverlapHist.GetXaxis().GetBinLowEdge(i)

            purityGraph.SetPoint(i-1, scoreThreshold, purityPercent)
            purityGraph.SetPointError(i-1, 0.0, totalError)
            
        return purityGraph

    def drawPurityCurve(self, purityGraph, sample, score, triggerGroup):
        canvasName = f"{sample}_xxx_{score}_xxx_{triggerGroup}_xxx_purityCurve"
        theCanvas = ROOT.TCanvas(canvasName)

        purityGraph.Draw("APZ")

        purityGraph.SetMarkerStyle(20)

        purityGraph.GetHistogram().GetXaxis().SetTitle(score)
        purityGraph.GetHistogram().GetYaxis().SetTitle("Purity (%)")
        purityGraph.GetHistogram().GetYaxis().SetRangeUser(0.0, 100.0)

        quietROOTFunc(theCanvas.SaveAs)(
            str(self.outputPath/f"{canvasName}.png")
        )

    def drawCICADAContentsPlots(self, overlapContentsHisto, rateStr, score):
        canvasName = f"{score}_{rateStr}_contents"
        theCanvas = ROOT.TCanvas(canvasName)
        theCanvas.SetLeftMargin(0.15)

        overlapContentsHisto.GetYaxis().SetTitle("Overlap (%)")

        overlapContentsHisto.Draw("HBAR")
        overlapContentsHisto.GetYaxis().SetRangeUser(0.0, 100.0)
        overlapContentsHisto.SetFillStyle(0)
        overlapContentsHisto.SetLineColor(ROOT.kBlack)
        overlapContentsHisto.SetLineWidth(2)
        overlapContentsHisto.SetTitle("")

        cmsLatex = ROOT.TLatex()
        cmsLatex.SetTextSize(0.05)
        cmsLatex.SetNDC(True)
        cmsLatex.SetTextAlign(32)
        cmsLatex.DrawLatex(0.9,0.92, "#font[61]{CMS} #font[52]{Preliminary}")

        for i in range(1, overlapContentsHisto.GetNbinsX()+1):
            textLatex = ROOT.TLatex()
            textLatex.SetTextSize(0.025)
            textLatex.SetTextAlign(12)
            textLatex.SetNDC(False)

            percentage = overlapContentsHisto.GetBinContent(i)
            textLatex.DrawLatex(percentage+1.0, i - 0.5, f"{percentage:4.2f}")

        quietROOTFunc(theCanvas.SaveAs)(
            str(self.outputPath/f"{canvasName}.png")
        )

    def processPurityCurves(self, overlapPlots, noOverlapPlots):
        for sample in overlapPlots:
            for score in overlapPlots[sample]:
                for triggerGroup in overlapPlots[sample][score]:
                    purityGraph = self.makePurityCurve(
                        noOverlapPlots[sample][score][triggerGroup],
                        overlapPlots[sample][score][triggerGroup],
                    )

                    self.drawPurityCurve(purityGraph, sample, score, triggerGroup)

    def processContentsPlots(self, contentsPlots):
        for rateStr in contentsPlots:
            for score in contentsPlots[rateStr]:
                self.drawCICADAContentsPlots(contentsPlots[rateStr][score], rateStr, score)

    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        purityFile = self.dictOfFiles["purity"]
        theFile = ROOT.TFile(purityFile)

        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        contentsPlots = {}
        overlapPlots = {}
        noOverlapPlots = {}

        for key in listOfKeys:
            sample, score, plotType, triggerGroup, rateStr = self.parseHistogramName(key)
            if plotType == "OverlapContents":
                if rateStr not in contentsPlots:
                    contentsPlots[rateStr] = {}
                if score not in contentsPlots[rateStr]:
                    contentsPlots[rateStr][score] = theFile.Get(key).Clone()
            elif plotType == "NoOverlap" or plotType == "Intersection":
                relevantDict = None
                if plotType == "NoOverlap":
                    relevantDict = noOverlapPlots
                elif plotType == "Intersection":
                    relevantDict = overlapPlots
                if sample not in relevantDict:
                    relevantDict[sample] = {}
                if score not in relevantDict[sample]:
                    relevantDict[sample][score] = {}
                if triggerGroup not in relevantDict[sample][score]:
                    relevantDict[sample][score][triggerGroup] = theFile.Get(key).Clone()
            else:
                continue
        self.processPurityCurves(overlapPlots, noOverlapPlots)
        self.processContentsPlots(contentsPlots)
    
