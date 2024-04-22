# !/usr/bin/env python3

# task for creating paper worthy ROC plots
from pathlib import Path
from anomalyDetection.paperCode.plottingCore.plotTask import drawPlotTask
import ROOT
import itertools

class drawPaperROCPlotTask(drawPlotTask):
    def __init__(
            self,
            taskName: str,
            dictOfFiles: list,
            outputPath: Path = Path("/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/PaperROCs"),
    ):
        super().__init__(taskName, dictOfFiles, outputPath)

    def makeROC(theFile, signalKey, backgroundKey):
        signalHisto = theFile.Get(signalKey)
        backgroundHisto = theFile.Get(backgroundKey)

        assert (signalHisto.GetNbinsX() == backgroundHisto.GetNbinsX()), "signal and background are different length histograms"
        nBins = signalHisto.GetNbinsX()
        
        #for keeping track of signal efficiency points
        #We always start at 100 % efficiency
        #and end at 0.0
        signal_effs = [1.0]
        background_effs=[1.0]

        #Just doing .Integral() yields a fast computed integral that is often _wrong_
        #We do the full computation here
        signalIntegral = signalHisto.Integral(0,nBins+1)
        backgroundIntegral = backgroundHisto.Integral(0, nBins+1)

        for i in range(nBins, 0, -1):
            signal_effs.append(
                signalHisto.Integral(1, i) / signalIntegral
            )
            background_effs.append(
                backgroundHisto.Integral(1, i) / backgroundIntegral
            )
        signal_effs.append(0.0)
        background_effs.append(0.0)

        #Now let's form the graph out of these points
        #It might be more efficient to just do this in the previous loop.
        ROCCurve = ROOT.TGraph(len(signal_effs))
        for i in range(len(signal_effs)):
            ROCCurve.SetPoint(
                i,
                background_effs[i]
                signal_effs[i]
            )

        return ROCCurve

    def drawPlots(self):
        ROOT.gStyle.SetOptStat(0)
        scoreFile = self.dictOfFiles["scores"]
        theFile = ROOT.TFile(scoreFile)
        
        listOfKeys = list(theFile.GetListOfKeys())
        listOfKeys = [x.GetName() for x in listOfKeys]

        # We need to seperate these samples into signal samples,
        # and background samples
        # We also potentially need to separate these out by the type of score used
        # so let's get comprehensive lists of all of these things
        signalSamples = []
        backgroundSamples = []
        scores = []
        for key in listOfKeys:
            sampleName, scoreName = self.parseHistogramName(key)
            if ('ZeroBias' in sampleName) or ('SingleNeutrino' in sampleName):
                if sampleName not in backgroundSamples:
                    backgroundSamples.append(sampleName)
            else:
                if sampleName not in signalSamples:
                    signalSamples.append(sampleName)
            if scoreName not in scores:
                scores.append(scoreName)
        #Now we get all combinations of signal, background and scores
        ROCKeyCombinations = list(itertools.product(signalSamples, backgroundSamples, scores))
        

    def parseHistogramName(self, histoName):
        nameElements = histoName.split('_xxx_')
        sampleName, scoreName = nameElements[0], nameElements[1]
        return sampleName, scoreName

    def reconstructHistogramName(self, sampleName, scoreName):
        return f'{sampleName}_xxx_{scoreName}'
        
