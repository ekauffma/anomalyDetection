import ROOT
import argparse
from rich.console import Console
import os
import numpy as np
import re
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff

console = Console()

def loadPlotSuite(theFile, sampleName):
    sample_CICADA_1p2p0 = theFile.Get(f'{sampleName}_CICADA_v1p2p0_score_hist')
    sample_CICADA_1p2p0N = theFile.Get(f'{sampleName}_CICADA_v1p2p0N_score_hist')
    sample_CICADA_2p2p0 = theFile.Get(f'{sampleName}_CICADA_v2p2p0_score_hist')
    sample_CICADA_2p2p0N = theFile.Get(f'{sampleName}_CICADA_v2p2p0N_score_hist')
    sample_HT = theFile.Get(f'{sampleName}_HT_hist')
    return sample_CICADA_1p2p0, sample_CICADA_2p2p0, sample_CICADA_1p2p0N, sample_CICADA_2p2p0N, sample_HT

def makeROCFromHists(backgroundHist, sampleHist):
    efficiencyPoints = []
    nBins = backgroundHist.GetNbinsX()
    for i in range(1,nBins+1):
        backgroundEff = backgroundHist.Integral(i,nBins) / backgroundHist.Integral()
        sampleEff = sampleHist.Integral(i,nBins) / sampleHist.Integral()
        efficiencyPoints.append((backgroundEff, sampleEff))
    efficiencyPoints.append((0.0, 0.0))
    efficiencyPoints.reverse()

    #console.print(efficiencyPoints)
    #exit(0)
    
    nPoints = len(efficiencyPoints)
    rocGraph = ROOT.TGraph(nPoints)
    for index, effPoint in enumerate(efficiencyPoints):
        rocGraph.SetPoint(
            index,
            effPoint[0],
            effPoint[1],
        )
    # let's also quickly calculate an AUC trapezoid rule style.
    AUC = 0.0
    for i in range(len(efficiencyPoints)-1):
        firstPoint = efficiencyPoints[i]
        secondPoint = efficiencyPoints[i+1]
        
        a = firstPoint[1]
        b = secondPoint[1]
        h = abs(secondPoint[0]-firstPoint[0]) #abs unnnecessary, just too lazy to get the order right
        area = ((a+b)/2)*h
        AUC += area

    return rocGraph, AUC

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

    if args.FineGrain:
        inputFileName = 'scorePlotsForROCs.root'
    else:
        inputFileName = 'scorePlots.root'
    basePath = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    theFile = ROOT.TFile(
        os.path.join(basePath, inputFileName)
    )

    if args.FineGrain:
        outputDirectory = '/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/ScoreROCsFineGrain/'
    else:
        outputDirectory = '/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/ScoreROCs/'
    os.makedirs(outputDirectory, exist_ok=True)
    
    listOfKeys = list(theFile.GetListOfKeys())
    listOfKeys = [x.GetName() for x in listOfKeys]

    scoreNames = [
        'CICADA_v1p2p0N_score_hist', 
        'CICADA_v1p2p0_score_hist', 
        'CICADA_v2p2p0N_score_hist', 
        'CICADA_v2p2p0_score_hist', 
        'HT_hist'
    ]

    samplePattern = re.compile('.*(?=_(CICADA|HT))')
    def sample_matched_substring(s):
        match = samplePattern.search(s)
        return match.group(0) if match else None
    vectorizedSampleNames = np.vectorize(sample_matched_substring, otypes=[object])
    sampleNames = vectorizedSampleNames(listOfKeys)
    sampleNames = list(np.unique(sampleNames))
    console.print(sampleNames)
    
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
        'Train_ZeroBias',
        'Test_ZeroBias',
        'SingleNeutrino_E-10-gun',
    ]
    
    for backgroundName in backgroundNames:
        background_CICADA_1p2p0, background_CICADA_2p2p0, background_CICADA_1p2p0N, background_CICADA_2p2p0N, background_HT = loadPlotSuite(theFile, backgroundName)
        for sampleName in sampleNames:
            canvasName = f'{sampleName}_{backgroundName}'
            theCanvas = ROOT.TCanvas(
                canvasName,
                canvasName,
            )
            if args.LogAxis:
                theCanvas.SetLogy()
                theCanvas.SetLogx()
            sample_CICADA_1p2p0, sample_CICADA_2p2p0, sample_CICADA_1p2p0N, sample_CICADA_2p2p0N, sample_HT = loadPlotSuite(theFile, sampleName)

            roc_CICADA_1p2p0, CICADA_1p2p0_AUC = makeROCFromHists(background_CICADA_1p2p0, sample_CICADA_1p2p0)
            roc_CICADA_1p2p0N, CICADA_1p2p0N_AUC = makeROCFromHists(background_CICADA_1p2p0N, sample_CICADA_1p2p0N)
            roc_CICADA_2p2p0, CICADA_2p2p0_AUC = makeROCFromHists(background_CICADA_2p2p0, sample_CICADA_2p2p0)
            roc_CICADA_2p2p0N, CICADA_2p2p0N_AUC = makeROCFromHists(background_CICADA_2p2p0N, sample_CICADA_2p2p0N)
            roc_HT, HT_AUC = makeROCFromHists(background_HT, sample_HT)

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
            

            if args.L1Axis:
                maxRate = 100.0
            else:
                maxRate = convertEffToRate(1.0)
            dummyHistogram = ROOT.TH1D(
                "dummy",
                "dummy",
                100000,
                0.0,
                maxRate,
            )

            dummyHistogram.Draw()

            roc_CICADA_1p2p0.Draw("L")
            roc_CICADA_2p2p0.Draw("L")
            roc_CICADA_1p2p0N.Draw("L")
            roc_CICADA_2p2p0N.Draw("L")
            if args.HT:
                roc_HT.Draw("L")


            dummyHistogram.GetXaxis().SetTitle("Overall Rate on Background Events (kHz)")
            dummyHistogram.GetYaxis().SetTitle("Signal Efficiency")
            dummyHistogram.GetYaxis().SetRangeUser(1e-3, 1.0)
            dummyHistogram.GetXaxis().SetRangeUser(1e-1, 100.0)
            dummyHistogram.SetTitle("")

            theCanvas.SaveAs(
                os.path.join(outputDirectory, f'{canvasName}.png')
            )
            console.print(f"Background: {backgroundName}")
            console.print(f"Sample: {sampleName}")
            console.print("AUCs:")
            console.print(f"CICADA 1p2p0: {CICADA_1p2p0_AUC:.4f}")
            console.print(f"CICADA 1p2p0N: {CICADA_1p2p0N_AUC:.4f}")
            console.print(f"CICADA 2p2p0: {CICADA_2p2p0_AUC:.4f}")
            console.print(f"CICADA 2p2p0N: {CICADA_2p2p0N_AUC:.4f}")
            console.print(f"HT: {HT_AUC:.4f}")
    theFile.Close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Draw ROC plots from score plots")

    parser.add_argument(
        "--HT",
        action="store_true",
        help="Draw an HT ROC curve"
    )
    parser.add_argument(
        "--FineGrain",
        action="store_true",
        help="Draw plots from fine grain score plots",
    )

    parser.add_argument(
        "--L1Axis",
        action="store_true",
        help="Force the axis to L1 ranges"
    )

    parser.add_argument(
        "--LogAxis",
        action="store_true",
        help="Force the axis to log scale"
    )

    args = parser.parse_args()

    main(args)
