#Script for making individual ROC curves compared to HT, instead of everything all at once, which makes crowded plots
import ROOT
import argparse
from rich.console import Console
from rich.progress import track
import pathlib
import numpy as np
import re
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff
from anomalyDetection.paperCode.plottingUtilities.models import *
from anomalyDetection.paperCode.samples.paperSampleBuilder import samples
from drawROCsFromScores import makeROCFromHists, convertROCFromEffToRate
from anomalyDetection.anomalyTriggerSkunkworks.plotSettings.utilities import convertEffToRate, convertRateToEff
from anomalyDetection.anomalyTriggerSkunkworks.utilities.decorators import quietROOTFunc
import itertools

console = Console()

def drawL1RangeROC(cicadaROC, HTROC, sampleName, backgroundName, cicadaScoreName, outputPath):
    canvasName = f'{sampleName}_{backgroundName}_{cicadaScoreName}_L1Range'
    theCanvas = ROOT.TCanvas(
        canvasName,
        canvasName,
    )
    theCanvas.SetLogy()
    theCanvas.SetLogx()

    cicadaROC.SetLineColor(ROOT.kRed)
    HTROC.SetLineColor(ROOT.kBlack)
    
    cicadaROC.SetLineWidth(2)
    HTROC.SetLineWidth(2)

    maxRate = 100.0
    dummyHistogram = ROOT.TH1D(
        f"dummy_{canvasName}",
        f"dummy_{canvasName}",
        100,
        0.0,
        maxRate,
    )
    dummyHistogram.Draw()
    
    cicadaROC.Draw("L")
    HTROC.Draw("L")

    dummyHistogram.GetXaxis().SetTitle("Overall Rate on Background Events (kHz)")
    dummyHistogram.GetYaxis().SetTitle("Signal Efficiency")
    dummyHistogram.GetYaxis().SetRangeUser(1e-3, 1.0)
    dummyHistogram.GetXaxis().SetRangeUser(1e-1, 100.0)
    dummyHistogram.SetTitle("")

    quietROOTFunc(theCanvas.SaveAs)(
        str(outputPath/f"{canvasName}.png")
    )

def drawUnNormalizedROC(cicadaROC, HTROC, sampleName, backgroundName, cicadaScoreName, outputPath):
    canvasName = f'{sampleName}_{backgroundName}_{cicadaScoreName}'

    theCanvas = ROOT.TCanvas(
        canvasName,
        canvasName,
    )

    cicadaROC.SetLineColor(ROOT.kRed)
    HTROC.SetLineColor(ROOT.kBlack)
    
    cicadaROC.SetLineWidth(2)
    HTROC.SetLineWidth(2)

    maxRate = convertEffToRate(1.0)
    dummyHistogram = ROOT.TH1D(
        f"dummy_{canvasName}",
        f"dummy_{canvasName}",
        100,
        0.0,
        maxRate
    )
    dummyHistogram.Draw()

    cicadaROC.Draw("L")
    HTROC.Draw("L")

    dummyHistogram.GetXaxis().SetTitle("Overall Rate on Background Events (kHz)")
    dummyHistogram.GetYaxis().SetTitle("Signal Efficiency")
    dummyHistogram.GetYaxis().SetRangeUser(0.0, 1.0)
    dummyHistogram.SetTitle("")

    quietROOTFunc(theCanvas.SaveAs)(
        str(outputPath/f"{canvasName}.png")
    )

def makeROCFromConfig(cicadaScoreName, sampleName, backgroundName, HTName, theFile, outputPath):
    sample_cicada = theFile.Get(f"{sampleName}_{cicadaScoreName}_hist").Clone()
    background_cicada = theFile.Get(f"{backgroundName}_{cicadaScoreName}_hist").Clone()
    sample_HT = theFile.Get(f"{sampleName}_{HTName}_hist").Clone()
    background_HT = theFile.Get(f"{backgroundName}_{HTName}_hist").Clone()

    cicadaROC = makeROCFromHists(background_cicada, sample_cicada)
    HTROC = makeROCFromHists(background_HT, sample_HT)

    cicadaROC = convertROCFromEffToRate(cicadaROC)
    HTROC = convertROCFromEffToRate(HTROC)

    drawUnNormalizedROC(cicadaROC, HTROC, sampleName, backgroundName, cicadaScoreName, outputPath)
    drawL1RangeROC(cicadaROC, HTROC, sampleName, backgroundName, cicadaScoreName, outputPath)

def makeAllScoreNamesFromGroups(listOfGroups):
    scoreNameList = []
    for group in listOfGroups:
        scoreNameList.append(group.teacherModel.scoreName)
        for studentModelName in group.studentModels:
            scoreNameList.append(group.studentModels[studentModelName].scoreName)
    return scoreNameList

def main(args):
    ROOT.gStyle.SetOptStat(0)
    console.log("Individual ROC curves")
    
    basePath = pathlib.Path('/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/')
    #inputFileName = basePath/"scorePlotsForROCs.root"
    inputFileName = basePath/"scorePlots.root"
    
    theFile = ROOT.TFile(
        str(inputFileName)
    )

    outputPath = pathlib.Path("/nfs_scratch/aloeliger/PaperPlotFiles/FinalizedPlots/IndividualROCs")
    outputPath.mkdir(parents=True, exist_ok=True)

    #let's figure out the file contents, so we can figure out what samples we have, and separate backgrounds
    listOfKeys = list(theFile.GetListOfKeys())
    listOfKeys = [x.GetName() for x in listOfKeys]

    samplePattern = re.compile('.*(?=_(anomalyScore|CICADA|HT))')
    def sample_matched_substring(s):
        match = samplePattern.search(s)
        return match.group(0) if match else None
    vectorizedSampleNames = np.vectorize(sample_matched_substring)
    sampleNames = vectorizedSampleNames(listOfKeys)
    sampleNames = list(np.unique(sampleNames))
    console.print(f"# of samples: {len(sampleNames):>6d}")
    
    backgrounds = [
        'Train_ZeroBias',
        'Test_ZeroBias',
        'SingleNeutrino_E-10-gun',
    ]
    for backgroundName in backgrounds:
        try: 
            sampleNames.remove(backgroundName)
        except ValueError:
            console.log(f'Failed to find {backgroundName} in the list of samples', style='red')
            exit(1)
    #debug
    #sampleNames = ["GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8"]


    cicadaScoreGroups = [
        CICADA_vXp2p0_Group,
        CICADA_vXp2p0N_Group,
        CICADA_vXp2p1_Group,
        CICADA_vXp2p1N_Group,
    ]
    cicadaScoreNames = makeAllScoreNamesFromGroups(cicadaScoreGroups)
    HTName = toyHTModel.scoreName

    # Okay, for each possible cicada score, sample, and background
    # We need to make a ROC curve
    rocConfigurations = list(
        itertools.product(
            cicadaScoreNames,
            sampleNames,
            backgrounds
        )
    )
    console.print(f"# of individual configurations: {len(rocConfigurations):>6d}")
    for config in track(rocConfigurations, description="Drawing ROCs..."):
        makeROCFromConfig(*config, HTName, theFile, outputPath)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Draw Individual ROC plots from score plots")
    
    args = parser.parse_args()
    
    main(args)
