import ROOT
import argparse
from rich.console import Console
import os
import numpy as np
import re
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff

console = Console()

def loadPlotSuite(theFile, sampleName):
    sample_CICADA_1p2p0 = theFile.Get(f'{sampleName}_CICADA_v1p2p0_score_cdf')
    sample_CICADA_2p2p0 = theFile.Get(f'{sampleName}_CICADA_v2p2p0_score_cdf')
    sample_CICADA_1p2p0N = theFile.Get(f'{sampleName}_CICADA_v1p2p0N_score_cdf')
    sample_CICADA_2p2p0N = theFile.Get(f'{sampleName}_CICADA_v2p2p0N_score_cdf')
    sample_HT = theFile.Get(f'{sampleName}_HT_cdf')
    return sample_CICADA_1p2p0, sample_CICADA_2p2p0, sample_CICADA_1p2p0N, sample_CICADA_2p2p0N, sample_HT

def makeROCCurveFromCDFs(backgroundCDF, sampleCDF):
    assert backgroundCDF.GetNbinsX() == sampleCDF.GetNbinsX()
    nPoints = backgroundCDF.GetNbinsX()
    rocGraph = ROOT.TGraph(nPoints)
    for i in range(0, nPoints):
        backgroundEff = backgroundCDF.GetBinContent(i+1)
        sampleEff = sampleCDF.GetBinContent(i+1)
        #console.log(f'\t\tBackground Eff: {backgroundEff}')
        #console.log(f'\t\tSignal Eff: {sampleEff}')
        #rocGraph.SetPointX(
        #    i,
        #    backgroundEff
        #)
        #rocGraph.SetPointY(
        #    i,
        #    sampleEff
        #)
        rocGraph.SetPoint(
            i,
            backgroundEff,
            sampleEff,
        )
    return rocGraph

def convertROCFromEffToRate(rocGraph):
    rateROC = rocGraph.Clone()
    nPoints = rocGraph.GetN()
    for i in range(0, nPoints):
        eff = rocGraph.GetPointX(i)
        rate = convertEffToRate(eff)
        rateROC.SetPointX(i, rate)
    return rateROC

def main(args):
    ROOT.gStyle.SetOptStat(0)

    basePath = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    theFile = ROOT.TFile(
        os.path.join(basePath, 'fastROCCurves.root')
    )

    outputDirectory = '/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/ROCs'
    os.makedirs(outputDirectory, exist_ok=True)
    
    listOfKeys = list(theFile.GetListOfKeys())
    listOfKeys = [x.GetName() for x in listOfKeys]
    console.print(listOfKeys)

    samplePattern = re.compile('.*(?=_(CICADA|HT))')
    def sample_matched_substring(s):
        match = samplePattern.search(s)
        return match.group(0) if match else None
    vectorizedSampleNames = np.vectorize(sample_matched_substring, otypes=[object])
    sampleNames = vectorizedSampleNames(listOfKeys)
    sampleNames = list(np.unique(sampleNames))
    console.print(sampleNames)

    # we treat zero bias and single neutrino a bit differently, so let's single them out
    try:
        sampleNames.remove('Train_ZeroBias')
    except ValueError:
        console.log(f'Failed to find Train_ZeroBias in the list of samples', style='red')
        exit(1)

    try:
        sampleNames.remove('Test_ZeroBias')
    except ValueError:
        console.log(f'Failed to find Test_ZeroBias in the list of samples', style='red')
        exit(1)

    try:
        sampleNames.remove('SingleNeutrino_E-10-gun')
    except ValueError:
        console.log(f'Failed to find SingleNeutrino_E-10-gun in the list of samples', style='red')
        exit(1)
    
    backgroundNames = [
        "Train_ZeroBias",
        "Test_ZeroBias",
        "SingleNeutrino_E-10-gun",
    ]

    #okay, here's the trick # we want to draw a sample and a background combination as a 
    #single canvas. The 5 score options we can put on the same canvas
    # HT: black
    # 1p2p0: Blue
    # 2p2p0: Red
    # 1p2p0N: Green
    # 2p2p0N: Orange
    for backgroundName in backgroundNames:
        #We can't really operate in the usual way just looping scores I guess
        #Let's get them by name
        background_CICADA_1p2p0, background_CICADA_2p2p0, background_CICADA_1p2p0N, background_CICADA_2p2p0N, background_HT = loadPlotSuite(theFile, backgroundName)
        for sampleName in sampleNames:
            canvasName = f'{sampleName}_{backgroundName}'
            theCanvas = ROOT.TCanvas(
                canvasName,
                canvasName,
            )
            theCanvas.SetLogy()
            #console.log(f"{backgroundName} {sampleName}")
            sample_CICADA_1p2p0, sample_CICADA_2p2p0, sample_CICADA_1p2p0N, sample_CICADA_2p2p0N, sample_HT = loadPlotSuite(theFile, sampleName)
            #console.log(f"\tCICADA 1p2p0")
            roc_CICADA_1p2p0 = makeROCCurveFromCDFs(background_CICADA_1p2p0, sample_CICADA_1p2p0)
            #console.log(f"\tCICADA 2p2p0")
            roc_CICADA_2p2p0 = makeROCCurveFromCDFs(background_CICADA_2p2p0, sample_CICADA_2p2p0)
            #console.log(f"\tCICADA 1p2p0N")
            roc_CICADA_1p2p0N = makeROCCurveFromCDFs(background_CICADA_1p2p0N, sample_CICADA_1p2p0N)
            #console.log(f"\tCICADA 2p2p0N")
            roc_CICADA_2p2p0N = makeROCCurveFromCDFs(background_CICADA_2p2p0N, sample_CICADA_2p2p0N)
            #console.log(f"\tHT")
            roc_HT = makeROCCurveFromCDFs(background_HT, sample_HT)

            roc_CICADA_1p2p0 = convertROCFromEffToRate(roc_CICADA_1p2p0)
            roc_CICADA_2p2p0 = convertROCFromEffToRate(roc_CICADA_2p2p0)
            roc_CICADA_1p2p0N = convertROCFromEffToRate(roc_CICADA_1p2p0N)
            roc_CICADA_2p2p0N = convertROCFromEffToRate(roc_CICADA_2p2p0N)
            roc_HT = convertROCFromEffToRate(roc_HT)

            roc_CICADA_1p2p0.SetLineColor(ROOT.kBlue)
            roc_CICADA_2p2p0.SetLineColor(ROOT.kRed)
            roc_CICADA_1p2p0N.SetLineColor(ROOT.kGreen)
            roc_CICADA_2p2p0N.SetLineColor(ROOT.kOrange)
            roc_HT.SetLineColor(ROOT.kBlack)
            
            roc_CICADA_1p2p0.SetLineWidth(2)
            roc_CICADA_2p2p0.SetLineWidth(2)
            roc_CICADA_1p2p0N.SetLineWidth(2)
            roc_CICADA_2p2p0N.SetLineWidth(2)
            roc_HT.SetLineWidth(2)

            roc_CICADA_1p2p0.SetMarkerStyle(20)
            roc_CICADA_2p2p0.SetMarkerStyle(20)
            roc_CICADA_1p2p0N.SetMarkerStyle(20)
            roc_CICADA_2p2p0N.SetMarkerStyle(20)
            roc_HT.SetMarkerStyle(20)

            dummyHisto = ROOT.TH1D(
                "dummy",
                "dummy",
                100,
                0.0,
                100.0,
            )

            dummyHisto.Draw()

            dummyHisto.GetYaxis().SetRangeUser(1e-2,1.0)
            dummyHisto.GetXaxis().SetTitle("Overall Rate on Background Events (kHz)")
            dummyHisto.GetYaxis().SetTitle("Signal Efficiency")
            dummyHisto.SetTitle("")

            roc_CICADA_1p2p0.Draw("LP")
            roc_CICADA_2p2p0.Draw("LP")
            roc_CICADA_1p2p0N.Draw("LP")
            roc_CICADA_2p2p0N.Draw("LP")
            roc_HT.Draw("LP")

            theCanvas.SaveAs(
                os.path.join(outputDirectory, f'{canvasName}.png')
            )
    theFile.Close()
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Draw ROCs from the fast ROC script")

    args = parser.parse_args()
    
    main(args)
