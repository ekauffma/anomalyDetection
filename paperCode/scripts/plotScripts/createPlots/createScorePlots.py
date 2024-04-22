import ROOT
import argparse
from anomalyDetection.paperCode.plottingUtilities.models import *
from anomalyDetection.paperCode.samples.paperSampleBuilder import reducedSamples as samples
from rich.console import Console
import os
from pathlib import Path

console = Console()

def makeAllScoreNamesFromGroups(listOfGroups):
    scoreNameList = []
    for group in listOfGroups:
        scoreNameList.append(group.teacherModel.scoreName)
        for studentModelName in group.studentModels:
            scoreNameList.append(group.studentModels[studentModelName].scoreName)
    return scoreNameList

def makePlotsForScores(theDataframe, listOfScores, baseName, nBins=100):
    resultPlots = []
    for scoreName in listOfScores:
        minScore = 0.0
        if scoreName != 'HT':
            if "teacher" in scoreName:
                maxScore = 125.0
            if "Input" in scoreName:
                maxScore = 7500.0
            else:
                maxScore = 256.0 # actually 255.99609375
        else:
            maxScore = 1500.0
        histName = f'{baseName}_{scoreName}_hist'
        theModel = ROOT.RDF.TH1DModel(
            histName,
            histName,
            nBins,
            minScore,
            maxScore
        )

        resultPlots.append(theDataframe.Histo1D(theModel, scoreName))
    return resultPlots

def main(args):
    # start this nonsense by grabbing all the possible samples, and separate out the data
    mcSampleNames = list(samples.keys())
    #debug
    #mcSampleNames = ["ZeroBias", "GluGluHToBB_M-125_TuneCP5_13p6TeV_powheg-pythia8",]
    try:
        mcSampleNames.remove('ZeroBias')
    except ValueError:
        console.log("Failed to find Zero Bias in list of samples and prune it out. Check the samples.", style='red')
        exit(1)

    cicadaScoreGroups = [
        CICADA_vXp2p0_Group,
        CICADA_vXp2p0N_Group,
        CICADA_vXp2p1_Group,
        CICADA_vXp2p1N_Group,
        CICADA_vXp2p2_Group,
        CICADA_vXp2p2N_Group,
        GADGET_v1p0p0_Group,
    ]
    scoreNames = makeAllScoreNamesFromGroups(cicadaScoreGroups)
    scoreNames.append(toyHTModel.scoreName)
    scoreNames.append("CICADA_v2p1p2")
    scoreNames.append(CICADAInputScore.scoreName)

    # Now, let's get the data sample, and prepare even/odd lumi dataframes
    # even lumi: training
    # odd lumi: test
    zeroBiasDataframe = samples['ZeroBias'].getNewDataframe()
    zeroBiasDataframe = toyHTModel.applyFrameDefinitions(zeroBiasDataframe)
    zeroBiasDataframe = CICADAInputScore.applyFrameDefinitions(zeroBiasDataframe)
    evenLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 0')
    oddLumiZBDataframe = zeroBiasDataframe.Filter('lumi % 2 == 1')

    if args.ForROCs:
        nBinsForPlots = 500
    else:
        nBinsForPlots = 100

    zeroBiasPlots = []
    zeroBiasPlots += makePlotsForScores(evenLumiZBDataframe, scoreNames, 'Train_ZeroBias', nBinsForPlots)
    zeroBiasPlots += makePlotsForScores(oddLumiZBDataframe, scoreNames, 'Test_ZeroBias', nBinsForPlots)
    console.log(f'Zero Bias: {len(samples["ZeroBias"].listOfFiles):>6d} Files')

    #
    # This runs into issues with too many open files
    #
    # mcDataframes = []
    # with console.status("Running through samples..."):
    #     for sampleName in mcSampleNames:
    #         theDataframe = samples[sampleName].getNewDataframe()
    #         console.log(f'{sampleName}: {len(samples[sampleName].listOfFiles):>6d} Files')
    #         theDataframe = toyHTModel.applyFrameDefinitions(theDataframe)
    #         theDataframe = CICADAInputScore.applyFrameDefinitions(theDataframe)
    #         allPlots += makePlotsForScores(
    #             theDataframe,
    #             scoreNames,
    #             sampleName,
    #             nBins = nBinsForPlots,
    #         )
    #         mcDataframes.append(theDataframe)
    # console.log('[bold green]\[Done][/bold green] Logging all plots to be made.')

    # # set-up an output location for all the plots that this is going to 
    # plotOutputLocation = '/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/'
    # os.makedirs(plotOutputLocation, exist_ok=True)
    # if args.ForROCs:
    #     outputFileName = 'scorePlotsForROCs.root'
    # else:
    #     outputFileName = 'scorePlots.root'
    # outputFileName = os.path.join(plotOutputLocation, outputFileName)
    # theOutputFile = ROOT.TFile(outputFileName, 'RECREATE')
    # with console.status('Writing plot file...'):
    #     for plot in allPlots:
    #         plot.Write()
    #     theOutputFile.Write()
    #     theOutputFile.Close()
    # console.log(f'[bold green]\[Done][/bold green] Writing files')
    plotOutputLocation = Path('/nfs_scratch/aloeliger/PaperPlotFiles/PlotFiles/')
    plotOutputLocation.mkdir(parents=True, exist_ok=True)
    if args.ForROCs:
        outputFileName = 'scorePlotsForROCs.root'
    else:
        outputFileName = 'scorePlots.root'
    finalPath = plotOutputLocation/outputFileName
    theOutputFile = ROOT.TFile(str(finalPath), 'RECREATE')

    for plot in zeroBiasPlots:
        plot.Write()
    del evenLumiZBDataframe
    del oddLumiZBDataframe
    
    for sampleName in mcSampleNames:
        theDataframe = samples[sampleName].getNewDataframe()
        console.log(f'{sampleName}: {len(samples[sampleName].listOfFiles):>6d} Files')
        theDataframe = toyHTModel.applyFrameDefinitions(theDataframe)
        theDataframe = CICADAInputScore.applyFrameDefinitions(theDataframe)
        thePlots = makePlotsForScores(
            theDataframe,
            scoreNames,
            sampleName,
            nBins = nBinsForPlots
        )
        for plot in thePlots:
            plot.Write()
        del theDataframe
    theOutputFile.Write()
    theOutputFile.Close()
    console.log(f'[bold green]\[Done][/bold green] Writing files')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create score plots from the paper samples")

    parser.add_argument(
        "--ForROCs",
        action="store_true",
        help="create score plots to be used in a ROC calculation, which changes binning and score location",
    )

    args = parser.parse_args()
    
    main(args)
